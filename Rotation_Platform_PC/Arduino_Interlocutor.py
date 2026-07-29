import time

import serial
import serial.tools.list_ports
from psychopy import gui

# Global parameters
default_port = "COM4" # Indicate here the port to which Arduino is connected the most part of the time

class ArduinoCommunicator:
    """Class to establish a direct communication with an Arduino. the Arduino has to be connected with the USB cable"""

    def select_board(self):
        # Listing all serial ports
        all_ports = serial.tools.list_ports.comports()
        ls_all_ports = [(port.name, port.description) for port in all_ports]

        # Offering the choice to the user
        control_panel = gui.Dlg(title="Arduino selection")
        control_panel.addField('Which Arduino are you going to use ?', choices=ls_all_ports)
        control_settings = control_panel.show() # show dialog and wait for OK or Cancel

        if control_panel.OK:  
            return control_settings[0][0]
        else:
            return default_port


    def establish_connection(self, baudrate=115200, timeout=.1):
        """This functions establish the connection :
        - baudrate : frequency of the communication, has to be the same on both sides
        - timeout : time it waits before stopping the connection if no signal"""
        self.serial_arduino = serial.Serial(port=self.port,  baudrate=baudrate, timeout=timeout)
    
    def close_connection(self):
        self.serial_arduino.close()

    def __init__(self):
        self.port = self.select_board()
        self.establish_connection()
        print("Connection établie, attente de démarrage de l'arduino")
        time.sleep(2)
        self.serial_arduino.reset_input_buffer()
        print("Arduino prêt")
        pass

    def send_order_to_the_arduino(self, message):
        """ Function to send a message to the arduino.
        Message must be one of those: reward, Punish, Stop. And it must en with a stop. 
        Therefore, you can only send : "Reward.", "Stop.", "Punish."
        """ 
        accepted_messages= ["Reward.", "Stop.", "Punish."]
        # Raising errors in case of misuse
        if message not in accepted_messages:
            raise ValueError("The message sent to the Arduino must be among : ", accepted_messages)
        
        try:
            self.serial_arduino.reset_input_buffer()
            self.serial_arduino.write(bytes(message,  'utf-8'))
            self.serial_arduino.flush()

        except Exception as e:
            print(f"[ERREUR SERRIE] Impossible d'envoyer le '{message}' à l'Arduino  {e}")

    def read_messages_from_arduino(self):
        """Get the messages"""
        message = self.serial_arduino.readline()
        decrypted_message = message

        return decrypted_message