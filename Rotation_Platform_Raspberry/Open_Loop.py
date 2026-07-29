from Steps_Motor import Motor
from Motor_Encoder import Motor_Encoder
from Wheel_Encoder import Wheel_Encoder 
from Sender import DataSender
import time
import gpiod
import os

#####################
# SCRIPT POUR DETECTER IMMEDIATEMENT QUELLE BROCHE EST LIBRE POUR LA PHOTODIODE
# REGLAGE DU CONFLIT ENTRE LA PHOTODIODE ET LE DRIVER POUR LES BROCHES DE LA RASPBERRY
#####################

PIN_PHOTODIODE_BCM = 27

chip = None
photodiode_line = None

# On liste toutes les puces gpiochip présentes dans le système (/dev/gpiochipX)
available_chips = sorted([f for f in os.listdir('/dev/') if f.startswith('gpiochip')])

if not available_chips:
    print("Aucune puce GPIO détectée dans /dev/")
else:
    # On teste les puces de la plus grande à la plus petite (priorité gpiochip4 sur RPi 5)
    for chip_name in reversed(available_chips):
        try:
            temp_chip = gpiod.Chip(chip_name)
            # On tente de récupérer la ligne pour voir si cette puce gère nos broches
            temp_line = temp_chip.get_line(PIN_PHOTODIODE_BCM)
            temp_line.request(consumer="Photodiode_Sync", type=gpiod.LINE_REQ_DIR_IN)
            
            # Puce trouvée
            chip = temp_chip
            photodiode_line = temp_line
            print(f"Photodiode initialisée sur /{chip_name} (GPIO {PIN_PHOTODIODE_BCM}).")
            break
        except Exception:
            # Echec -- essai avec puce suivante
            if 'temp_chip' in locals():
                temp_chip.close()

# Si aucune puce ne fonctionne - fermeture du script
if photodiode_line is None:
    raise RuntimeError("Impossible d'initialiser la photodiode sur les puces disponibles. Vérifier les permissions ou le numéro GPIO.")

# Initialize motor and encoder objects
motor = Motor()  # Object to control the motor
motor_encoder = Motor_Encoder()  # Encoder connected to the motor
wheel_encoder = Wheel_Encoder()  # Encoder connected to the wheel

# Parameter
detection_threshold = 5  # Number of ticks to exceed to detect rotation
ratio = 6
rotation_deg = 20  # (le nombre de degré voulu pour la plateforme)
steps_goal = int(rotation_deg * ratio / motor.get_anglePerImpulse())  # Calculate the number of steps to achieve the desired rotation
wait_after_rotation = 0.70  # Waiting time after rotation, in seconds
motor_ratio = motor_encoder.get_anglePerImpulse() / motor.get_anglePerImpulse()  # Ratio to correct for motor encoder differences
waiting_time_to_sync_visual_vestibular_stimuli = 0.1  # Time in seconds to make the platform waiting until the visual stimuli is launched on PC

# Code identification
clockwise = "Right."
counterclockwise = "Left."

statut_photodiode = False

def detect_rotation_direction():
    """
    Detects the direction of rotation based on wheel encoder ticks.
    Compares the number of ticks before and after a short delay to determine if rotation has occurred.
    """
    initial_ticks = wheel_encoder.get_position()  # Record the initial position
    time.sleep(0.01)  # Short delay to measure rotation
    final_ticks = wheel_encoder.get_position()  # Record the position after the delay
    delta_ticks = final_ticks - initial_ticks  # Calculate the change in ticks
    
    # Determine rotation direction based on the change in ticks
    if delta_ticks > detection_threshold:
        return clockwise  # Clockwise
    elif delta_ticks < -detection_threshold:
        return counterclockwise  # Counterclockwise
    else:
        return None  # No significant rotation detected

def move_motor(direction):
    """
    Moves the motor in the given direction using a sigmoid speed profile.
    """
    if direction == clockwise:
        motor.speed_sigmoid(direction=True, steps=steps_goal, duration=3.5, min_delay=0.00001) 
    elif direction == counterclockwise:
        motor.speed_sigmoid(direction=False, steps=steps_goal, duration=3.5, min_delay=0.00001) 

def correct_missed_steps():
    """
    Ensures the motor returns to the initial position by correcting any missed steps.
    Calculates the number of missed steps and pulses the motor to return to the initial position.
    """
    actual_steps = motor_encoder.get_position()  # Get the current encoder position
    position_error = int(actual_steps * motor_ratio)  # Calculate the position error

    if position_error != 0:
        print(f"Returning to initial position. Position error: {position_error} steps.")
        direction = True if position_error > 0 else False  # Determine the correction direction
        missed_steps = abs(position_error)  # Absolute number of missed steps

        # Pulse the motor to correct missed steps
        for _ in range(missed_steps):
            motor.pulse_line.set_value(1)
            time.sleep(0.001)
            motor.pulse_line.set_value(0)
            time.sleep(0.001)
            
            
####################
# LANCEMENT SCRIPT #
####################

try:
    correspondence_with_pc = DataSender(host='192.168.3.1', port=12345)
    correspondence_with_pc.start_client()
    correspondence_with_pc.client_socket.setblocking(False)

    print("Raspberry connectée, en attente du premier message du PC...")
    
###################################################
##### ATTENTE DE LA DISTINCTION DU PREMIER TRIAL ##
###################################################

    message_from_pc = None
    while True:
        try:
            message_from_pc = correspondence_with_pc.receive_a_message().split(".")[-2]
            # Dès qu'on intercepte un mot clé valide, on valide l'initialisation
            if message_from_pc == "Ride" or message_from_pc.startswith("Turn"):
                break
        except (BlockingIOError, IndexError):
            time.sleep(0.005)
            
#### SI ESSAI ACTIF
    if message_from_pc == "Ride":
        print("1er Trial reçu : ACTIF")
        while True:
            direction = detect_rotation_direction()  # On écoute l'encodeur de la roue
            if direction:
                correspondence_with_pc.send_a_message_to_server(direction)
                time.sleep(waiting_time_to_sync_visual_vestibular_stimuli)
                move_motor(direction)
                time.sleep(wait_after_rotation)
            
                move_motor(clockwise if direction == counterclockwise else counterclockwise)
                time.sleep(wait_after_rotation)
                        
                correct_missed_steps()
                break
            else:
                print("No significant rotation detected.")
                time.sleep(1)  # Attente avant re-vérification
                
##### SI ESSAI PASSIF
    elif message_from_pc.startswith("Turn"):
        print(f"1er Trial reçu : PASSIF : ({message_from_pc})")
        if message_from_pc == "TurnRight":
            time.sleep(waiting_time_to_sync_visual_vestibular_stimuli)
            move_motor(clockwise)
            time.sleep(wait_after_rotation)
            move_motor(counterclockwise)
        elif message_from_pc == "TurnLeft":
            time.sleep(waiting_time_to_sync_visual_vestibular_stimuli)
            move_motor(counterclockwise)
            time.sleep(wait_after_rotation)
            move_motor(clockwise)
            
        time.sleep(wait_after_rotation)
        correct_missed_steps()
            
            
###### FIN
    print("1er trial terminé, attente blackout")
    if photodiode_line.get_value() != 0:
        print("blackout, attente trial suivant")
        print("En attente du flash")
        time.sleep(0.1)
        
###################################
### BOUCLES DES TRIALS SUIVANTS ###
###################################

    while True:
        try:
            message_from_pc = correspondence_with_pc.receive_a_message().split(".")[-2]
        except (BlockingIOError, IndexError):
            time.sleep(0.005)
            continue  # Recommencer la boucle tant qu'aucun message valide n'est reçu

#### SI ESSAI ACTIF - ORDRE RIDE ET FLASH ENVOYE
        if message_from_pc == "Ride":
            print("Trial reçu : ACTIF -- attente de la photodiode")
            while photodiode_line.get_value() != 1:
                time.sleep(0.001)
            print("FLASH DETECT")
            time.sleep(1)
            print("Début du trial ! Roue débloquée !")
            time.sleep(0.001)
            
            while True:
                direction = detect_rotation_direction()
                if direction:
                    correspondence_with_pc.send_a_message_to_server(direction)

                    # Mouvement induit par la souris/roue
                    time.sleep(waiting_time_to_sync_visual_vestibular_stimuli)
                    move_motor(direction)
                    time.sleep(wait_after_rotation)
                    
                    # Retour
                    move_motor(clockwise if direction == counterclockwise else counterclockwise)
                    time.sleep(wait_after_rotation)
                                
                    # Correction
                    correct_missed_steps()
                    break
                else:
                    print("No significant rotation detected.")
                    time.sleep(0.01)

            print("Trial terminé, attente du blackout")
            if photodiode_line.get_value() == 1:
                print("blackout, attente trial suivant")
                print("En attente du flash")
                time.sleep(0.01)

#### SI ESSAI PASSIF - ORDRE TURN ENVOYE
        elif message_from_pc.startswith("Turn"):
            print(f"Trial reçu : PASSIF : ({message_from_pc})")
            
            # On attend le flash pour synchro les gratings
            while photodiode_line.get_value() == 0:
                time.sleep(0.001)

            print("FLASH DETECTE -- En attente de la direction")
            
            if message_from_pc == "TurnRight":
                print("Ordre passif reçu : Right")
                time.sleep(waiting_time_to_sync_visual_vestibular_stimuli)
                move_motor(clockwise)
                time.sleep(wait_after_rotation)
                move_motor(counterclockwise)
                statut_photodiode = False
            
            elif message_from_pc == "TurnLeft":
                print("Ordre passif reçu : Left")
                time.sleep(waiting_time_to_sync_visual_vestibular_stimuli)
                move_motor(counterclockwise)
                time.sleep(wait_after_rotation)
                move_motor(clockwise)
                statut_photodiode = False

            time.sleep(wait_after_rotation)
            correct_missed_steps()
            
            print("Trial terminé, attente du blackout")
            if photodiode_line.get_value() == 1:
                print("blackout, attente trial suivant")
                print("En attente du flash")
                time.sleep(0.01)

except KeyboardInterrupt:
    print("Interrupted by the user")

finally:
    if photodiode_line is not None:
        photodiode_line.release()
    motor.cleanup()
    motor_encoder.cleanup()
    wheel_encoder.cleanup()
