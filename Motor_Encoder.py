# motor_encoder.py
import gpiod
import time
import threading
import os
from datetime import datetime

class Motor_Encoder:

    def __init__(self, phase_a_PIN=18, phase_b_PIN=17, resolution=1200, mechanical_ratio=5, invert_direction=False):
        #Résolution = celle constructeur *2 car on mesure A haut et A bas
        # --- Paramètres de base ---
        self.phase_a_PIN = phase_a_PIN
        self.phase_b_PIN = phase_b_PIN
        self.position = 0
        self.direction = "motionless"
        self.resolution = resolution
        self.mechanical_ratio = float(mechanical_ratio) if mechanical_ratio is not None else 1.0
        # If True, flip sign of measured speed to correct wiring/polarity
        self.invert_direction = bool(invert_direction)
        self.angle_per_impulse = 360.0 / float(self.resolution)
        self.speed = 0.0
        self._prev_position = 0
        self._prev_time = time.time()

        # --- Initialisation GPIO ---
        self.chip = gpiod.Chip("gpiochip4")
        self.phase_a_line = self.chip.get_line(self.phase_a_PIN)
        self.phase_b_line = self.chip.get_line(self.phase_b_PIN)

        self.phase_a_line.request(
            consumer="StepsMotor Encoder",
            type=gpiod.LINE_REQ_EV_BOTH_EDGES,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP
        )
        self.phase_b_line.request(
            consumer="StepsMotor Encoder",
            type=gpiod.LINE_REQ_DIR_IN,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP
        )

        # --- Préparation du dossier de logs ---
        self.log_folder = "speed_logs"
        os.makedirs(self.log_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_filename = os.path.join(self.log_folder, f"speed_log_{timestamp}.csv")

        with open(self.log_filename, "w") as f:
            # Write platform-centric velocity log: epoch, elapsed, speed_imp, speed_deg, platform_speed_deg, position_deg
            f.write("epoch(s),time(s),speed(imp/s),speed(deg/s),platform_speed(deg/s),position(deg)\n")

        print(f"[INFO] Enregistrement dans : {self.log_filename}")

        # --- Lancement des threads ---
        self.event_thread = threading.Thread(target=self.monitor_events)
        self.event_thread.daemon = True
        self.event_thread.start()

        self.speed_thread = threading.Thread(target=self.update_speed)
        self.speed_thread.daemon = True
        self.speed_thread.start()

    # --- Détection des changements de phase ---
    def encoder_callback(self, channel=None):
        phase_a = self.phase_a_line.get_value()
        phase_b = self.phase_b_line.get_value()
        if phase_a == phase_b:
            self.position += 1
            self.direction = "counterclockwise"
        else:
            self.position -= 1
            self.direction = "clockwise"

    # --- Surveillance continue des événements ---
    def monitor_events(self):
        while True:
            event = self.phase_a_line.event_wait(sec=1)
            if event:
                _ = self.phase_a_line.event_read()
                self.encoder_callback(self.phase_a_line)

    # --- Calcul et enregistrement de la vitesse ---
    def update_speed(self):
        start_time = time.time()
        while True:
            time.sleep(0.03)
            current_time = time.time()
            dt = current_time - self._prev_time
            dp = self.position - self._prev_position

            if dt > 0:
                # raw encoder impulse speed (imp/s)
                raw_speed = dp / dt
                # apply polarity correction if needed
                self.speed = -raw_speed if self.invert_direction else raw_speed

            self._prev_position = self.position
            self._prev_time = current_time

            # --- Enregistrement dans le fichier CSV ---
            elapsed_time = current_time - start_time
            epoch = current_time
            position_deg = self.position * self.angle_per_impulse
            with open(self.log_filename, "a") as f:
                speed_imp = self.speed 
                speed_deg = self.speed * self.angle_per_impulse
                # platform speed (deg/s)
                platform_speed_deg = speed_deg / self.mechanical_ratio if self.mechanical_ratio != 0 else speed_deg
                f.write(f"{epoch:.6f},{elapsed_time:.3f},{speed_imp:.3f},{speed_deg:.3f},{platform_speed_deg:.3f},{position_deg:.3f}\n")

    # --- Accesseurs utiles ---
    def get_position(self):
        return self.position

    def get_direction(self):
        return self.direction

    def get_speed(self):
        return self.speed

    def get_speed_deg(self):
        return self.speed * self.angle_per_impulse

    def get_anglePerImpulse(self):
        return self.angle_per_impulse

    # --- Nettoyage ---
    def cleanup(self):
        self.phase_a_line.release()
        self.phase_b_line.release()
        print(f"[INFO] Données sauvegardées dans : {self.log_filename}")
