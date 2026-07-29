from psychopy import gui
from Experiment_Manager import *

if __name__=="__main__":

    while True:
        control_panel = gui.Dlg(title="What's going to happen to Jerry ?")


        control_panel.addField('Experiment type:', choices=["Open Loop - General Experiment", "Closed Loop - General Experiment", "Train on SimpleFlash"])
        # control_panel.addField('Check screens order ?', choices=["No", "Yes"])


        control_settings = control_panel.show() # show dialog and wait for OK or Cancel


        if control_panel.OK:  # or if ok_data is not None

            if control_settings[0]== "Open Loop - General Experiment":
                experiment = GeneralExperimentOpenLoop()

            elif control_settings[0]== "Closed Loop - General Experiment":
                experiment = GeneralExperimentClosedLoop()
            
        else:
            print('Information : End of the day')
            break


# The following part of the code is only executed when you run "from MAIN_Interface import *" in the terminal
# It is a way to start the programs faster, as importing psychopy in the terminal seems to take less time than in a python file (don't know why)


def testing():
    """ This function is a copy_pase from the lines above"""
    while True:
        control_panel = gui.Dlg(title="What's going to happen to Jerry ?")


        control_panel.addField('Experiment type:', choices=["Open Loop - General Experiment", "Closed Loop - General Experiment", "Train on SimpleFlash"])
        # control_panel.addField('Check screens order ?', choices=["No", "Yes"])


        control_settings = control_panel.show() # show dialog and wait for OK or Cancel


        if control_panel.OK:  # or if ok_data is not None

            if control_settings[0]== "Open Loop - General Experiment":
                experiment = GeneralExperimentOpenLoop()

            elif control_settings[0]== "Closed Loop - General Experiment":
                experiment = GeneralExperimentClosedLoop()
                        
            
        else:
            print('Information : End of the day')
            break
            
testing()