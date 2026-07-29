from psychopy import core, visual, colors, gui
import numpy as np
import warnings
from tqdm import tqdm
import time

wait_time_after_rotation = 0.5 
ratio_nb_of_notches_per_turn = 6400 

class JuxtaposedThreeIdenticalScreens:
    warnings.filterwarnings("ignore")

    def __init__(self, contrast=1):
        self.contrast = contrast
        # Colors
        color_space = "rgb"
        color_black = colors.Color(color=[-1*self.contrast,-1*self.contrast,-1*self.contrast], space=color_space)
        color_white = colors.Color(color=[1*self.contrast,1*self.contrast,1*self.contrast], space=color_space)

        excitation_color = color_white
        rest_color = color_black
        
        # Caracteristics of the screens
        self.refresh_rate_of_the_screen = 60 
        self.horizontal_resolution = 1024
        self.vertical_resolution = 768
        self.size_of_the_diode = 90 
        self.extra_width_pixels = 0

        # total width across all screens
        self.total_width = (3 * self.horizontal_resolution) + int(self.extra_width_pixels)

        # normalized diode dimensions
        self.normalized_dimensions_of_the_diode = [(self.size_of_the_diode / float(self.total_width)) * 2, (self.size_of_the_diode/self.vertical_resolution)*2]
        self.required_vertical_resolution = int(self.vertical_resolution/self.size_of_the_diode) 

        # Positionning of the screens and parameters
        self.left_screen_number = 2
        self.chosen_unit = "norm"
        self.color_space = color_space
        self.excitation_color = excitation_color
        self.rest_color = rest_color
        
        self.identify_positions_of_screens()
        self.set_up_method_called = False

    ## GESTION DES ECRANS
    def identify_positions_of_screens(self):
        test_window_1 = visual.Window(size=[200,100], pos=[200,100], screen=0, color=self.rest_color)
        test_number_1 = visual.TextStim(win=test_window_1, text=str(1), color=self.excitation_color, colorSpace=self.color_space, height=2, units=self.chosen_unit)
        test_number_1.draw()
        test_window_1.flip()

        test_window_2 = visual.Window(size=[200,100], pos=[200,100], screen=1, color=self.rest_color)
        test_number_2 = visual.TextStim(win=test_window_2, text=str(2), color=self.excitation_color, colorSpace=self.color_space, height=2, units=self.chosen_unit)
        test_number_2.draw()
        test_window_2.flip()

        test_window_3 = visual.Window(size=[200,100], pos=[200,100], screen=2, color=self.rest_color)
        test_number_3 = visual.TextStim(win=test_window_3, text=str(3), color=self.excitation_color, colorSpace=self.color_space, height=2, units=self.chosen_unit)
        test_number_3.draw()
        test_window_3.flip()

        test_window_4 = visual.Window(size=[200,100], pos=[200,100], screen=3, color=self.rest_color)
        test_number_4 = visual.TextStim(win=test_window_4, text=str(4), color=self.excitation_color, colorSpace=self.color_space, height=2, units=self.chosen_unit)
        test_number_4.draw()
        test_window_4.flip()

        panel = gui.Dlg(title="Screens order")
        panel.addField('Left screen:', choices=[1, 2, 3, 4])
        dialog_data = panel.show()

        test_window_1.close()
        test_window_2.close()
        test_window_3.close()
        test_window_4.close()

        time.sleep(0.2)

        if panel.OK and dialog_data is not None:
            self.left_screen_number = int(dialog_data[0]) - 1

        return self.left_screen_number
    
    def set_up_the_screens(self):
        # Window width uses total_width (3 screens plus optional extra pixels)
        self.window = visual.Window(size=[self.total_width, self.vertical_resolution], pos=[0,0], screen=self.left_screen_number, color = self.rest_color)
        self.set_up_method_called = True

    def close_the_window(self):

        if self.set_up_method_called == True:
            self.window.close()
            # self.window_central.close()
            # self.window_right.close()
            self.set_up_method_called = False

    ## STIMULI VISUELS # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def blackout(self):
        if self.set_up_method_called == False:
            raise Exception("The method \"set_up_the_screens\" must have been called before this method")

        # Executing the function
        self.window.flip()

    
    # 1 Flash - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def one_flash(self, location, duration):

        # Raising errors
        if location not in ["Left", "Middle", "Right"]:
            raise TypeError(f"location must be \"Left\", \"Middle\" or \"Right\" but {location} was given")
        
        if type(duration) not in [float, int] :
            raise TypeError("Only floats or integers are allowed")

        if duration < 0:
            raise ValueError("Duration can not be negative")
        

        if self.set_up_method_called == False:
            raise Exception("The method \"set_up_the_screens\" must have been called before this method")


        # Executing the function

        # We'll draw rectangles in pixel units to avoid normalization/scaling issues
        window = self.window
        total_w = int(self.total_width)
        total_h = int(self.vertical_resolution)

        extra = int(self.extra_width_pixels)
        grating_w = 3 * self.horizontal_resolution
        third_w = self.horizontal_resolution
        third_h = self.vertical_resolution

        # left edge of grating region in window-centered coordinates
        grating_left = - (total_w / 2.0) + extra

        # choose which third to flash (i = 0 -> left, 1 -> middle, 2 -> right)
        if location == "Left":
            i = 0
        elif location == "Middle":
            i = 1
        else:
            i = 2

        rect_center_x = grating_left + (i * third_w) + (third_w / 2.0)
        rect_center_y = 0

        # Draw the main flash rectangle (one third of the grating region) in pixels
        rectangle = visual.Rect(window, fillColor=self.excitation_color, size=[third_w, third_h], pos=[rect_center_x, rect_center_y], units='pix')
        rectangle.draw()

        # Draw the photo-diode small rectangle near the right edge of the grating region (in pixels)
        pd_size = int(self.size_of_the_diode)
        pd_margin = 5
        pd_center_x = grating_left + grating_w - (pd_size / 2.0) - pd_margin
        pd_center_y = (total_h / 2.0) - (pd_size / 2.0) - pd_margin
        photo_diode_rectangle = visual.Rect(window, fillColor=self.excitation_color, size=[pd_size, pd_size], pos=[pd_center_x, pd_center_y], units='pix')
        photo_diode_rectangle.draw()
        window.flip()
        core.wait(duration)

        window.flip()




class PolarGrating(JuxtaposedThreeIdenticalScreens):
    
    def __init__(self, spatial_frequence = 5, contrast=1):
        super().__init__(contrast=contrast)
        
        # Paramètres des gradients
        # Défini par l'utilisateur
        self.spatial_frequence = spatial_frequence
        # Pré-définis
        self.grating_phase = 0
        self.wait_time_after_rotation = wait_time_after_rotation
        self.ratio_nb_of_notches_per_turn = ratio_nb_of_notches_per_turn 

        # Support du gradient
        # Build grating for the 3 screens (grating_width) and pad a left region of extra pixels that will remain black
        grating_width = 3 * self.horizontal_resolution
        extra_pixels = int(self.extra_width_pixels)

        grating_absc = np.concatenate([
            np.linspace(-1, 1, self.horizontal_resolution),
            np.linspace(-1, 1, self.horizontal_resolution),
            np.linspace(-1, 1, self.horizontal_resolution)
        ])
        grating_absc = np.arctan(grating_absc) * 4
        # create grating grid for the grating region
        grating_grid = np.tile(grating_absc, (self.required_vertical_resolution, 1))
        # pad left with black columns (value -1) so the extra area is black
        if extra_pixels > 0:
            left_pad = np.full((self.required_vertical_resolution, extra_pixels), -1.0)
            self.grid = np.concatenate([left_pad, grating_grid], axis=1)
        else:
            self.grid = grating_grid

        self.grating_phase = 0
        # compute full initial template (left pad will be constant -1 -> black)
        self.initial_grating_template = np.cos(self.spatial_frequence*(self.grid + self.grating_phase)) * self.contrast
        # ensure diode area inside the grating region is set to white (ready state)
        cols = self.initial_grating_template.shape[1]
        cols_to_set = min(self.size_of_the_diode, cols)
        if cols_to_set > 0:
            self.initial_grating_template[-1, -cols_to_set:-1] = -1

        # Pré-calculs
        self.stereotyped_turn_pre_calculation()
        self.visual_environment_pre_calculation()
        self.stimulus_pre_calculation()
    
    ## --- méthode centralisée pour le pattern photodiode ---
    def photodiode_value(self, i):
        return 1 if i % 2 == 0 else -1
        
    ## PRE_CALCULATION
    def stereotyped_turn_pre_calculation(self):
        """Création flux visuel pour open-loop, sigmoidal"""
        self.duration_of_the_turn = 4 # In seconds
        visual_amplitude_of_the_turn = 20*np.pi/180
        angular_amplitude_of_the_turn = 4*visual_amplitude_of_the_turn # (Transformation mathématique obligatoire)

        nb_of_images_to_display = int(self.refresh_rate_of_the_screen * self.duration_of_the_turn)
        gradual_phase = self.grating_phase

        # Calcul par fonction sigmoidale
        steps = np.linspace(-10,10,nb_of_images_to_display)
        sigmoid_steps = self.sigmoid_derivative(steps)
        steps_phases = sigmoid_steps/np.sum(sigmoid_steps)*angular_amplitude_of_the_turn
        

        ls_frames_of_gratings_turn_to_right = [] # So, visual flows goes to left before coming back to right

        # === Turn to right ===
        for i, step_phase in enumerate(steps_phases):
            gradual_phase += step_phase
            # compute grating for grating region then pad left with black
            if self.total_width > self.grid.shape[1]:
                # grid already includes left pad; use it directly
                one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            else:
                one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            
            diode_value = self.photodiode_value(i)
            one_frame[-1][-self.size_of_the_diode:-1] = diode_value
            ls_frames_of_gratings_turn_to_right.append(one_frame)


        number_of_waiting_frames = int(self.wait_time_after_rotation * self.refresh_rate_of_the_screen)

        if number_of_waiting_frames > 0:
            last_frame = ls_frames_of_gratings_turn_to_right[-1].copy()
            last_frame[-1][-self.size_of_the_diode:-1] = -1
            for _ in range(number_of_waiting_frames):
                ls_frames_of_gratings_turn_to_right.append(last_frame)
        
        for i, step_phase in enumerate(reversed(steps_phases)):
            gradual_phase -= step_phase
            one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            diode_value = self.photodiode_value(i)
            one_frame[-1][-self.size_of_the_diode:-1] = diode_value
            ls_frames_of_gratings_turn_to_right.append(one_frame)

        self.stereotyped_visual_flow_right_turn = ls_frames_of_gratings_turn_to_right


        ls_frames_of_gratings_turn_to_left = [] # So, visual flows goes to right before coming back to left
        gradual_phase = self.grating_phase  # réinitialise la phase

        for i, step_phase in enumerate(steps_phases):
            gradual_phase -= step_phase
            one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            diode_value = self.photodiode_value(i)
            one_frame[-1][-self.size_of_the_diode:-1] = diode_value
            ls_frames_of_gratings_turn_to_left.append(one_frame)
        
        for i, step_phase in enumerate(reversed(steps_phases)):
            gradual_phase += step_phase
            one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            diode_value = self.photodiode_value(i)
            one_frame[-1][-self.size_of_the_diode:-1] = diode_value
            ls_frames_of_gratings_turn_to_left.append(one_frame)

        self.stereotyped_visual_flow_left_turn = ls_frames_of_gratings_turn_to_left

        return None
    

    def visual_environment_pre_calculation(self):
        """Calcul de toutes les positions possibles du champ visuel (6400 dents)"""

        nb_of_images_to_display = self.ratio_nb_of_notches_per_turn
        step_phase = 20*np.pi / nb_of_images_to_display
        gradual_phase = self.grating_phase

        ls_frames_of_gratings = []
        for frame_indice in range(nb_of_images_to_display):
            gradual_phase += step_phase
            one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            diode_value = self.photodiode_value(frame_indice)
            one_frame[-1][-self.size_of_the_diode:-1] = diode_value
            ls_frames_of_gratings.append(one_frame)


        self.visual_environment = ls_frames_of_gratings

        return None

    def stimulus_pre_calculation(self):
        """Création d'un stimulus en gratings"""
        self.duration_of_the_turn = 4 # In seconds
        visual_amplitude_of_the_stimulus = 20*np.pi/180
        angular_amplitude_of_the_stimulus = 4*visual_amplitude_of_the_stimulus # (Transformation mathématique obligatoire)

        nb_of_images_to_display = int(self.refresh_rate_of_the_screen * self.duration_of_the_turn)
        step_phase = angular_amplitude_of_the_stimulus / nb_of_images_to_display
        gradual_phase = self.grating_phase


        ls_frames_of_gratings = []
        for frame_indice in range(nb_of_images_to_display):
            gradual_phase += step_phase
            one_frame = np.cos(self.spatial_frequence*(self.grid + gradual_phase)) * self.contrast
            diode_value = self.photodiode_value(frame_indice)
            one_frame[-1][-self.size_of_the_diode:-1] = diode_value
            ls_frames_of_gratings.append(one_frame)


            



        self.left_stimulus = ls_frames_of_gratings.copy()
        self.right_stimulus = self.left_stimulus.copy()
        self.right_stimulus.reverse()

        return None
    
    def sigmoid_derivative(self, x):
        sigmoid = 1/(1+np.exp(-x))
        return sigmoid * (1 - sigmoid)
    
    # Polar Grating - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def initialize_polar_grating(self):
        # Gestion des erreurs
        if self.set_up_method_called == False:
            raise Exception("The method \"set_up_the_screens\" must have been called before this method")
        
        # Affichage
        self.grating = visual.GratingStim(win=self.window, tex=self.initial_grating_template, units=self.chosen_unit, pos=(0.0, 0.0), size=2, sf=1, contrast = self.contrast)
        # self.grating_central = visual.GratingStim(win=self.window_central, tex=self.grating_template, units=self.chosen_unit, pos=(0.0, 0.0), size=2, sf=1, contrast = self.contrast)
        # self.grating_right = visual.GratingStim(win=self.window_right, tex=self.grating_template, units=self.chosen_unit, pos=(0.0, 0.0), size=2, sf=1, contrast = self.contrast)

        self.grating.draw()
        # self.grating_central.draw()
        # self.grating_right.draw()

        self.window.flip()
        # self.window_central.flip()
        # self.window_right.flip()

    # Management of polar grating in open loop - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def one_stimulus(self, destination):
        """ Pour de l'open-loop"""

        # Raising errors
        if destination not in ["Left", "Middle", "Right"]:
            raise TypeError("destination must be \"Left\", \"Middle\" or \"Right\"")

        
        # Déterminer dans quel sens ira le gradient
        if destination == "Left":
            displayed_gratings = self.left_stimulus
        elif destination == "Right":
            displayed_gratings = self.right_stimulus
        else: 
            displayed_gratings = [self.right_stimulus[0] for i in range(len(self.right_stimulus))]
        

        for grating in displayed_gratings:
            # Affichage
            self.grating = visual.GratingStim(win=self.window, tex=grating, units=self.chosen_unit, pos=(0.0, 0.0), size=2, sf=1, contrast = self.contrast)

            self.grating.draw()

            self.window.flip()

    def one_stereotyped_turn(self, destination, paired=True):
        """ Pour de l'open-loop"""
        print(destination)
        # Raising errors
        if destination not in ["Left", "Middle", "Right"]:
            raise TypeError(f"destination must be \"Left\", \"Middle\" or \"Right\" but {destination} was given")
        if type(paired) != bool:
            raise TypeError("paired must be a boolena, i.e. True or False")
        
        
        # Déterminer dans quel sens ira le gradient
        if destination == "Left":
            displayed_gratings = self.stereotyped_visual_flow_left_turn
        elif destination == "Right":
            displayed_gratings = self.stereotyped_visual_flow_right_turn
        else :
            displayed_gratings = [self.stereotyped_visual_flow_right_turn[0] for i in range(len(self.stereotyped_visual_flow_right_turn))]
        

        for grating in displayed_gratings:
            # Affichage
            self.grating = visual.GratingStim(win=self.window, tex=grating, units=self.chosen_unit, pos=(0.0, 0.0), size=2, sf=1, contrast = self.contrast)

            self.grating.draw()

            self.window.flip()


    # Management of polar grating in closed loop - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def update_visual_environment(self, motor_position):
        """ Pour de l'open-loop"""

        # Raising errors
        if type(motor_position) not in [int] :
            raise TypeError("Only integers are allowed")

        frame_indice_to_display = motor_position % self.ratio_nb_of_notches_per_turn # Modulo

        grating = self.visual_environment[frame_indice_to_display]

        self.grating = visual.GratingStim(win=self.window, tex=grating, units=self.chosen_unit, pos=(0.0, 0.0), size=2, sf=1, contrast = self.contrast)

        self.grating.draw()

        self.window.flip()