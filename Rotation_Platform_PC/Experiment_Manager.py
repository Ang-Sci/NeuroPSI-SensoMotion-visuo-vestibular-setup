from Data_Receiver import DataReceiver
from Visual_stimulation import *
from psychopy import gui, core
from Arduino_Interlocutor import *
from Sound_stimulation import *
import random as rd
import time
import numpy as np
from tqdm import tqdm
import pandas as pd

# Code identification
clockwise = "clockwise"
counterclockwise = "counterclockwise"

class ExperimentManager:
    """This class is used to manage experiments, and automate trials """

    def __init__(self):
        # Path to save data
        self.path_for_saving_data = "../../Experimental data/OpenLoop - Experimental Data PC - " + str(time.strftime("%Y-%b-%d %Hh%M", time.localtime()))

        # Attribute to check if functions have been correctly called
        self.set_up_method_called = False
        

    def set_up_the_experiment(self, screen_numbers=[0,1,2]):
        # Setting up the server
        self.data_receiver = DataReceiver() # Create a DataReceiver object
        self.data_receiver.start_server() # Start the server

        # Setting up the screens
        # self.screens.set_up_the_screens(screen_numbers)

        # Establishing communication with Arduino
        self.arduino_communicator = ArduinoCommunicator()

        # Attribute to check if functions have been correctly called
        self.set_up_method_called = True

    def end_the_experiment(self):
        self.screens.close_the_window()
        self.data_receiver.stop_server()
        self.arduino_communicator.close_connection()

#####################################################################################

## EXPERIMENTS ######################################################################

class GeneralExperimentOpenLoop(ExperimentManager):
    """Specific to Open Loops"""
    
    def __init__(self):
        self.cancel_experiment = False
        self.decide_settings()

        if self.cancel_experiment == False:
            super().__init__()

            dialog_box_request = gui.Dlg(title="Human, obey me !")
            dialog_box_request.addText('Run the Open_Loop.py program on the Raspberry Pi please.')
            dialog_box_request.addText('Click on any button to continue ;)')
            dialog_box_request.show() # show dialog and wait for OK or Cancel
            
            self.set_up_the_experiment()
            
            

            self.run_experiment()
            self.end_the_experiment()

            dialog_box_request = gui.Dlg(title="Human, obey me !")
            dialog_box_request.addText('Stop the Open_Loop.py program on the Raspberry Pi please ;)')
            dialog_box_request.addText('Click on any button to continue ;)')
            dialog_box_request.show() # show dialog and wait for OK or Cancel

            


    def decide_settings(self):
        experiment_panel = gui.Dlg(title="Give more details about what Jerry will do")

        experiment_panel.addField('Number of trials :', 10)
        
        experiment_panel.addText('Inter-trials parameters')
        experiment_panel.addField('Minimum wait time between trials (in s):', 10)
        experiment_panel.addField('Maximum wait time between trials (in s):', 15)
        
        experiment_panel.addText('Visual stimuli parameters')
        experiment_panel.addField('Stimulus type:', choices=["Flash", "Moving Gratings"])
        experiment_panel.addField('Stimulus duration (in s):', 2)
        experiment_panel.addField('Contrast (from 0 to 1):', 1)

        experiment_panel.addField('Probability of a left stimulus (from 0 to 1):', 0.5)
        experiment_panel.addField('Probability of a middle stimulus (from 0 to 1):', 0.0)
        experiment_panel.addField('Probability of a right stimulus (must have a sum of 1 with two precedings values):', 0.5)

        experiment_panel.addField('Frequency of VOR deactivation (probability from 0 to 1):', 0.1)

        experiment_panel.addText('Reward parameters')
        experiment_panel.addField('Time granted for licking the reward (in s):', 12)

        experiment_panel.addText('Vestibular parameters')
        experiment_panel.addField('Percentage of passive situations (probability from 0 to 1):', 0)
    


        experiment_settings = experiment_panel.show() # show dialog and wait for OK or Cancel

        if experiment_panel.OK:
            self.nb_of_trials = int(experiment_settings[0])
            self.minimal_duration_black_out = float(experiment_settings[1])
            self.maximal_duration_black_out = float(experiment_settings[2])

            self.stimulus_type = experiment_settings[3]
            self.stimulus_duration = float(experiment_settings[4])
            self.contrast = float(experiment_settings[5])

            ls_probabilities_of_direction = [0,0,0]
            ls_probabilities_of_direction[0] = float(experiment_settings[6])
            ls_probabilities_of_direction[1] = float(experiment_settings[7])
            ls_probabilities_of_direction[2] = float(experiment_settings[8])
            self.ls_probabilities_of_direction = ls_probabilities_of_direction

            self.probability_of_paired_visual_flow =  1 - float(experiment_settings[9])

            self.time_granted_for_licking_the_reward = float(experiment_settings[10])

            self.probability_of_passive_situation = float(experiment_settings[11])
            

        else:
            self.cancel_experiment = True



    def run_experiment(self):
        if self.set_up_method_called == False:
            raise Exception("The method \"set_up_the_experiment\" must have been called before this method")

        # Variables to store experimental data and create a dataframe at the end
        start_time_of_experiment = time.time()
        self.ls_exprimental_data_trial_number = []
        self.ls_exprimental_data_active_or_passive_status = []
        self.ls_exprimental_data_vor_cancellation = []
        self.ls_exprimental_data_start_time_of_trial = []
        self.ls_exprimental_data_direction_of_stimulus = []
        self.ls_exprimental_data_stimulus_type = []
        self.ls_exprimental_data_direction_selected_by_the_mouse = []
        self.ls_exprimental_data_end_time_of_trial = []

        # Prepare the screens
        self.screens = PolarGrating(contrast=self.contrast)
        self.screens.set_up_the_screens()
        


        for trial_number in range(1,self.nb_of_trials+1):
            # Is this a passive or active ?
            passive_state = np.random.binomial(1,self.probability_of_passive_situation) 
            visual_flow_paired = np.random.binomial(1,self.probability_of_paired_visual_flow) 
            t_trial_start = time.time()
            print(f"[TIMING] Trial {trial_number} start @ {t_trial_start:.3f}")

            
            # Black-out period
            duration_black_out = self.minimal_duration_black_out + rd.random()*(self.maximal_duration_black_out - self.minimal_duration_black_out)
            self.screens.initialize_polar_grating() # self.screens.blackout()
            time.sleep(duration_black_out)
            print(f"[TIMING] Trial {trial_number} after blackout sleep ({duration_black_out:.3f}s) @ {time.time()-t_trial_start:.3f}s")

            # Start of the trial
            start_time_of_trial = time.time()
            self.screens.initialize_polar_grating()
            print(f"[TIMING] Trial {trial_number} after init polar grating @ {time.time()-t_trial_start:.3f}s")


            if passive_state==0: # Actif
                self.data_receiver.send_a_message_to_client("Essai actif")
                # Visual stimuli
                # Choise of direction
                ls_possible_directions = ["Left", "Middle", "Right"]
                random_direction = np.random.choice(ls_possible_directions, p=self.ls_probabilities_of_direction)
                # print("Requested by experimenter : ", random_direction)

                if self.stimulus_type == "Moving Gratings":
                    self.screens.one_stimulus(random_direction)

                elif self.stimulus_type == "Flash":
                    self.screens.one_flash(location=random_direction, duration=self.stimulus_duration)
                    self.screens.initialize_polar_grating() # we have to reinitialize polar gratings after showing a flash

                # Go tone
                SoundStimulator(frequence=5000, duration=0.5).playTheMusic()

                # Cleaning the buffer
                self.data_receiver.purge_messages()
                # Sending the signal to the platform to start the control by the mouse
                self.data_receiver.send_a_message_to_client("Ride.")
                print(f"[TIMING] Trial {trial_number} sent 'Ride.' @ {time.time()-t_trial_start:.3f}s")


                # What the mouse does
                direction_selected_by_the_mouse = self.data_receiver.read_messages().split(".")[-2]
                print(f"[TIMING] Trial {trial_number} got mouse choice '{direction_selected_by_the_mouse}' @ {time.time()-t_trial_start:.3f}s")
                if visual_flow_paired==1:
                    self.screens.one_stereotyped_turn(direction_selected_by_the_mouse)
                    print(f"[TIMING] Trial {trial_number} finished stereotyped turn @ {time.time()-t_trial_start:.3f}s")
                elif visual_flow_paired==0:
                    time.sleep(self.screens.duration_of_the_turn*2)
                    print(f"[TIMING] Trial {trial_number} waited (no visual flow) @ {time.time()-t_trial_start:.3f}s")

                # Offeting reward ?
                if direction_selected_by_the_mouse == random_direction:
                    
                    print(f"Information : Succès --> Reward")
                    self.arduino_communicator.send_order_to_the_arduino("Reward.")
                else:
                    print("Information : Echec --> Punish")
                    self.arduino_communicator.send_order_to_the_arduino("Punish.")

                # The mouse has a little bit of time to lick the reward
                time.sleep(self.time_granted_for_licking_the_reward)
                print(f"[TIMING] Trial {trial_number} reward window ended @ {time.time()-t_trial_start:.3f}s")
                self.arduino_communicator.send_order_to_the_arduino("Stop.")
        
            elif passive_state == 1: # Passif
                self.data_receiver.send_a_message_to_client("Essai passif")
                time.sleep(0.05) # Pause réseau entre les envois
                direction_selected_by_the_mouse = None

                # Choix de la direction
                ls_possible_directions = ["Left", "Middle", "Right"]
                random_direction = np.random.choice(ls_possible_directions, p=self.ls_probabilities_of_direction)

                # Envoie du mouvement choisi vers la raspberry
                self.data_receiver.send_a_message_to_client("Turn" + random_direction + ".")
                time.sleep(0.05) # Temps pour armement de la raspberry

                self.screens.initialize_polar_grating()
                print(f"[TIMING] Trial {trial_number} - Flash initial envoyé")

                # Envoi des gratings
                if visual_flow_paired==1:
                    self.screens.one_stereotyped_turn(random_direction)
                    print(f"[TIMING] Trial {trial_number} passive stereotyped turn done @ {time.time()-t_trial_start:.3f}s")
                elif visual_flow_paired==0:
                    time.sleep(self.screens.duration_of_the_turn*2)      
                    print(f"[TIMING] Trial {trial_number} passive waited (no visual flow) @ {time.time()-t_trial_start:.3f}s")

                # print("Passive movement : ", random_direction)

                
            end_time_of_trial = time.time()
            print(f"[TIMING] Trial {trial_number} end @ {end_time_of_trial - t_trial_start:.3f}s (wall {end_time_of_trial:.3f})")


            # Saving experimental data of this trial
            self.ls_exprimental_data_trial_number.append(trial_number)
            self.ls_exprimental_data_start_time_of_trial.append(start_time_of_trial - start_time_of_experiment)
            self.ls_exprimental_data_end_time_of_trial.append(end_time_of_trial - start_time_of_experiment)
            self.ls_exprimental_data_active_or_passive_status.append(1 - passive_state) # 1 si actif, 0 si passif
            self.ls_exprimental_data_vor_cancellation.append(1 - visual_flow_paired) # 1 if VOR is cancelled, 0 otherwise
            self.ls_exprimental_data_stimulus_type.append(self.stimulus_type)
            self.ls_exprimental_data_direction_of_stimulus.append(random_direction)
            self.ls_exprimental_data_direction_selected_by_the_mouse.append(direction_selected_by_the_mouse)
            

        df_experimental_data = pd.DataFrame({
            "Trial number" : self.ls_exprimental_data_trial_number,
            "Start time of trial" : self.ls_exprimental_data_start_time_of_trial,
            "End time of trial" : self.ls_exprimental_data_end_time_of_trial,
            "Active status": self.ls_exprimental_data_active_or_passive_status,
            "VOR cancellation": self.ls_exprimental_data_vor_cancellation,
            "Stimulus type" : self.ls_exprimental_data_stimulus_type,
            "Direction of stimulus" : self.ls_exprimental_data_direction_of_stimulus,
            "Direction selected by the mouse" : self.ls_exprimental_data_direction_selected_by_the_mouse
            
        })

        # Saving experimental data
        
        df_experimental_data.to_csv(self.path_for_saving_data + '.csv', index=False) 
        df_experimental_data.to_excel(self.path_for_saving_data + '.xlsx', index=False)

                    



class GeneralExperimentClosedLoop(ExperimentManager):
    """Class to manage closed loop only"""
    
    
    def __init__(self):
        self.cancel_experiment = False
        self.waiting_time_to_sync_visual_and_vestibular_stimuli = 0.5 # in seconds
        self.decide_settings()

        if self.cancel_experiment == False:
            
            super().__init__()

            dialog_box_request = gui.Dlg(title="Human, obey me !")
            dialog_box_request.addText('Run the Closed_Loop.py program on the Raspberry Pi please.')
            dialog_box_request.addText('Click on any button to continue ;)')
            dialog_box_request.show() # show dialog and wait for OK or Cancel

            self.set_up_the_experiment()

            self.run_experiment()
            self.end_the_experiment()

            dialog_box_request = gui.Dlg(title="Human, obey me !")
            dialog_box_request.addText('Stop the Closed_Loop.py program on the Raspberry Pi please ;)')
            dialog_box_request.addText('Click on any button to continue ;)')
            dialog_box_request.show() # show dialog and wait for OK or Cancel


    def decide_settings(self):
        experiment_panel = gui.Dlg(title="Give more details about what Jerry will do")

        experiment_panel.addField('Number of trials :', 10)
        
        experiment_panel.addText('Inter-trials parameters')
        experiment_panel.addField('Minimum wait time between trials (in s):', 10)
        experiment_panel.addField('Maximum wait time between trials (in s):', 15)
        
        experiment_panel.addText('Visual stimuli parameters')
        experiment_panel.addField('Stimulus type:', choices=["Flash", "Moving Gratings"])
        experiment_panel.addField('Stimulus duration (in s):', 2)
        experiment_panel.addField('Contrast (from 0 to 1):', 1)

        experiment_panel.addField('Probability of a left stimulus (from 0 to 1):', 0.5)
        experiment_panel.addField('Probability of a middle stimulus (from 0 to 1):', 0)
        experiment_panel.addField('Probability of a right stimulus (must have a sum of 1 with two precedings values):', 0.5)

        experiment_panel.addField('Frequency of VOR deactivation (probability from 0 to 1):', 0.1)

        experiment_panel.addText('Reward parameters')
        experiment_panel.addField('Time granted for licking the reward (in s):', 3)

        experiment_panel.addText('Vestibular parameters')
        experiment_panel.addField('Percentage of passive situations (probability from 0 to 1):', 0)
        experiment_panel.addField('Duration of one ride (in s):', 10)
        experiment_panel.addField('Required amplitude of platform movement (in number of PI):', 1/2) # En radians donc

        experiment_settings = experiment_panel.show() # show dialog and wait for OK or Cancel

        if experiment_panel.OK:
            self.nb_of_trials = int(experiment_settings[0])
            self.minimal_duration_black_out = float(experiment_settings[1])
            self.maximal_duration_black_out = float(experiment_settings[2])

            self.stimulus_type = experiment_settings[3]
            self.stimulus_duration = float(experiment_settings[4])
            self.contrast = float(experiment_settings[5])

            ls_probabilities_of_direction = [0,0,0]
            ls_probabilities_of_direction[0] = float(experiment_settings[6])
            ls_probabilities_of_direction[1] = float(experiment_settings[7])
            ls_probabilities_of_direction[2] = float(experiment_settings[8])
            self.ls_probabilities_of_direction = ls_probabilities_of_direction

            self.probability_of_paired_visual_flow =  1 - float(experiment_settings[9])

            self.time_granted_for_licking_the_reward = float(experiment_settings[10])

            self.probability_of_passive_situation = float(experiment_settings[11])
            
            
    
            self.duration_of_the_ride = float(experiment_settings[12])
            self.required_amplitude_of_wheel_movement = float(experiment_settings[13])*np.pi / (7200 * 2 * np.pi)  # = 7200 et pi En nombre de dents

        else:
            self.cancel_experiment = True


    def run_experiment(self):
        if self.set_up_method_called == False:
            raise Exception("The method \"set_up_the_experiment\" must have been called before this method")

        # Setting up the screens
        self.screens = PolarGrating(contrast=self.contrast)
        self.screens.set_up_the_screens()
        

        # Variables to store experimental data, in prevision of the creation of a dataframe
        start_time_of_experiment = time.time()
        self.ls_exprimental_data_trial_number = []
        self.ls_exprimental_data_active_or_passive_status = []
        self.ls_exprimental_data_vor_cancellation = []
        self.ls_exprimental_data_start_time_of_trial = []
        self.ls_exprimental_data_start_time_of_ride = []
        self.ls_exprimental_data_end_time_of_ride = []
        self.ls_exprimental_data_direction_of_stimulus = []
        self.ls_exprimental_data_stimulus_type = []
        self.ls_exprimental_data_direction_selected_by_the_mouse = []
        self.ls_exprimental_data_amplitude_of_movement_controled_by_the_mouse = []
        self.ls_exprimental_data_end_time_of_trial = []


        initial_motor_position = 0

        for trial_number in range(1,self.nb_of_trials+1):
            # Is this a passive or active ?
            passive_state = np.random.binomial(1,self.probability_of_passive_situation) 
            visual_flow_paired = np.random.binomial(1,self.probability_of_paired_visual_flow) 

            
            # Black-out
            duration_black_out = self.minimal_duration_black_out + rd.random()*(self.maximal_duration_black_out - self.minimal_duration_black_out)
            time.sleep(duration_black_out)



            start_time_of_trial = time.time()

            if passive_state==0: # Actif
                # Purging the buffer, to avoid long waiting list of messages
                self.data_receiver.purge_messages()
                self.data_receiver.send_a_message_to_client("Ride.")

                message_from_raspberry = self.data_receiver.read_messages()
                motor_position = -int(message_from_raspberry.split(".")[-2])
                initial_motor_position = motor_position

                # Go tone
                SoundStimulator(frequence=5000, duration=0.5).playTheMusic()

                # Visual stimulus
                ls_possible_directions = ["Left", "Middle", "Right"]
                random_direction = np.random.choice(ls_possible_directions, p=self.ls_probabilities_of_direction)
                if self.stimulus_type == "Moving Gratings":
                    self.screens.initialize_polar_grating()
                    # Choix de droite ou gauche
                    self.screens.one_stimulus(random_direction)

                elif self.stimulus_type == "Flash":
                    self.screens.one_flash(location=random_direction, duration=self.stimulus_duration)


                print("Requested by experimenter : ", random_direction)

                # What the mouse does
                start_time_of_the_ride = time.time()

                
                while (time.time() - start_time_of_the_ride) < self.duration_of_the_ride:
                    message_from_raspberry = self.data_receiver.read_messages()
                    motor_position = -int(message_from_raspberry.split(".")[-2])
                    
                    if visual_flow_paired==1:
                        self.screens.update_visual_environment(motor_position=motor_position)


                self.data_receiver.send_a_message_to_client("Freeze.")
                end_time_of_the_ride = time.time()
                

                # Letting time to the platform to go to the position requested by the mouse before going further in the trial
                former_motor_position = 0
                new_motor_position = motor_position
                # While the wheel continues to move, we continue to adapt the visual flow
                while former_motor_position !=new_motor_position:
                        former_motor_position = new_motor_position
                        
                        # Has the position of the wheel changed since we asked the platform to freeze ? (it may not have read it instantly)
                        message_from_raspberry = self.data_receiver.read_messages()
                        new_motor_position = -int(message_from_raspberry.split(".")[-2])

                        if visual_flow_paired==1:
                            self.screens.update_visual_environment(motor_position=motor_position)



                # Analysis of the variation of the wheel
                movement_of_the_motor = motor_position - initial_motor_position
                initial_motor_position = motor_position

                if movement_of_the_motor > self.required_amplitude_of_wheel_movement:
                    direction_selected_by_the_mouse = "Right"
                elif movement_of_the_motor < -self.required_amplitude_of_wheel_movement:
                    direction_selected_by_the_mouse = "Left"
                else:
                    direction_selected_by_the_mouse = "Middle"
                    
                # Offering reward ?
                if direction_selected_by_the_mouse == random_direction:
                    # print(f"Information : Reward")
                    self.arduino_communicator.send_order_to_the_arduino("Reward.")
                else:
                    # print(f"Information : ", random_direction, "asked but", direction_selected_by_the_mouse, 'obtained')
                    self.arduino_communicator.send_order_to_the_arduino("Punish.")

                # Letting time for the mouse to lick the reward
                time.sleep(self.time_granted_for_licking_the_reward)
                self.arduino_communicator.send_order_to_the_arduino("Stop.")
        
            elif passive_state == 1: # Passif
                # Purging the buffer, to avoid long waiting list of messages (and accelerate processing)
                self.data_receiver.purge_messages()
                direction_selected_by_the_mouse = None

                # Visual stimuli
                ls_possible_directions = ["Left", "Middle", "Right"]
                random_direction = np.random.choice(ls_possible_directions, p=self.ls_probabilities_of_direction)

                if random_direction != "Middle":
                    self.data_receiver.send_a_message_to_client("Turn" + random_direction + ".")

                    if visual_flow_paired==1:
                        self.screens.one_stereotyped_turn(random_direction)
                    elif visual_flow_paired==0:
                        time.sleep(self.screens.duration_of_the_turn*2)
                
            

            end_time_of_trial = time.time()
            


            # Saving data of the trial
            self.ls_exprimental_data_trial_number.append(trial_number)
            self.ls_exprimental_data_start_time_of_trial.append(start_time_of_trial - start_time_of_experiment)
            self.ls_exprimental_data_end_time_of_trial.append(end_time_of_trial - start_time_of_experiment)
            self.ls_exprimental_data_active_or_passive_status.append(1 - passive_state) # 1 si actif, 0 si passif
            self.ls_exprimental_data_vor_cancellation.append(1 - visual_flow_paired) # 1 if VOR is cancelled, 0 otherwise
            self.ls_exprimental_data_stimulus_type.append(self.stimulus_type)
            self.ls_exprimental_data_direction_of_stimulus.append(random_direction)
            
            if passive_state==1:
                self.ls_exprimental_data_direction_selected_by_the_mouse.append(None)
                self.ls_exprimental_data_start_time_of_ride.append(None)
                self.ls_exprimental_data_end_time_of_ride.append(None)
                self.ls_exprimental_data_amplitude_of_movement_controled_by_the_mouse.append(None)
            elif passive_state==0:
                self.ls_exprimental_data_direction_selected_by_the_mouse.append(direction_selected_by_the_mouse)
                self.ls_exprimental_data_start_time_of_ride.append(start_time_of_the_ride - start_time_of_experiment)
                self.ls_exprimental_data_end_time_of_ride.append(end_time_of_the_ride - start_time_of_experiment)
                self.ls_exprimental_data_amplitude_of_movement_controled_by_the_mouse.append(movement_of_the_motor)


        df_experimental_data = pd.DataFrame({
            "Trial number" : self.ls_exprimental_data_trial_number,
            "Start time of trial" : self.ls_exprimental_data_start_time_of_trial,
            "End time of trial" : self.ls_exprimental_data_end_time_of_trial,
            "Active status": self.ls_exprimental_data_active_or_passive_status,
            "VOR cancellation": self.ls_exprimental_data_vor_cancellation,
            "Stimulus type" : self.ls_exprimental_data_stimulus_type,
            "Direction of stimulus" : self.ls_exprimental_data_direction_of_stimulus,
            "Direction selected by the mouse" : self.ls_exprimental_data_direction_selected_by_the_mouse,

            "Start time of ride" : self.ls_exprimental_data_start_time_of_ride,
            "End time of ride" : self.ls_exprimental_data_end_time_of_ride,
            "Amplitude of platform movement" : self.ls_exprimental_data_amplitude_of_movement_controled_by_the_mouse
            
        })

        # Savine experimental data
        
        df_experimental_data.to_csv(self.path_for_saving_data + '.csv', index=False) 
        df_experimental_data.to_excel(self.path_for_saving_data + '.xlsx', index=False)
