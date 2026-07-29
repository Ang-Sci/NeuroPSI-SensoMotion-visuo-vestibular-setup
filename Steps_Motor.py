import gpiod
import time
import numpy as np
import csv
import os
from datetime import datetime
import threading


class Motor:
    def __init__(self, direction_PIN=20, pulse_PIN=21, resolution=6400, mechanical_ratio=5):

        # ----- Moteur -----
        self.direction_PIN = direction_PIN
        self.pulse_PIN = pulse_PIN
        self.cw_direction = 0
        self.ccw_direction = 1

        self.resolution = resolution
        self.mechanical_ratio = float(mechanical_ratio)
        self.angle_per_impulse = 360.0 / self.resolution

        # Compteurs globaux
        self._emitted_pulses_total = 0     # <-- cumulatif global
        self._current_set_vel_imp = 0.0
        self._current_set_vel_deg = 0.0

        # ----- GPIO -----
        self.chip = gpiod.Chip('gpiochip4')
        self.direction_line = self.chip.get_line(direction_PIN)
        self.pulse_line = self.chip.get_line(pulse_PIN)

        self.direction_line.request(consumer="direction", type=gpiod.LINE_REQ_DIR_OUT)
        self.pulse_line.request(consumer="pulse", type=gpiod.LINE_REQ_DIR_OUT)

        # ----- CSV de log -----
        os.makedirs("setpoint_logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.setpoint_path = f"setpoint_logs/setpoint_log_{timestamp}.csv"

        self._setpoint_file = open(self.setpoint_path, 'a', newline='')
        self._setpoint_writer = csv.writer(self._setpoint_file)

        self._setpoint_writer.writerow([
            'epoch(s)', 'time(s)',
            'speed(imp/s)', 'speed(deg/s)', 'platform_speed(deg/s)',
            'position(deg)', 'trial_id', 'dir'
        ])
        self._setpoint_file.flush()

        # ----- Thread de sampling -----
        self._sampling_interval = 0.1
        self._sampling_stop = threading.Event()

        self._sampling_trial_id = None
        self._sampling_dir_sign = 0
        self._sampling_trial_start = None

        self._sampler_thread = threading.Thread(target=self._persistent_sampler, daemon=True)
        self._sampler_thread.start()

        # Compteur d’essais
        self._trial_counter = 0



    # -------------------------------------------------------------
    #                 THREAD DE LOGGING CONTINU
    # -------------------------------------------------------------
    def _persistent_sampler(self):
        writer = self._setpoint_writer
        f = self._setpoint_file

        while not self._sampling_stop.is_set():

            now = time.time()
            elapsed = (now - self._sampling_trial_start) if self._sampling_trial_start else 0

            s_imp = self._current_set_vel_imp * self._sampling_dir_sign
            s_deg = self._current_set_vel_deg * self._sampling_dir_sign
            platform_speed = s_deg / self.mechanical_ratio

            position_deg = self._emitted_pulses_total * self.angle_per_impulse

            trial_id = self._sampling_trial_id if self._sampling_trial_id else ""

            writer.writerow([
                f"{now:.6f}",
                f"{elapsed:.3f}",
                f"{s_imp:.3f}",
                f"{s_deg:.3f}",
                f"{platform_speed:.3f}",
                f"{position_deg:.3f}",
                f"{trial_id}",
                f"{self._sampling_dir_sign}"
            ])
            f.flush()

            time.sleep(self._sampling_interval)



    # -------------------------------------------------------------
    #                     PROFIL SIGMOÏDE
    # -------------------------------------------------------------
    def logit_derivative(self, x):
        return 1/x + 1/(1-x)


    def speed_sigmoid(self, direction, steps, duration, min_delay=0.00001, encoder=None, trial_id=None):

        # ----- Détermination du sens -----
        dir_sign = 1 if not direction else -1
        self.direction_line.set_value(self.ccw_direction if direction else self.cw_direction)

        # ----- Identifiant trial -----
        if trial_id is None:
            self._trial_counter += 1
            trial_id = self._trial_counter
        else:
            trial_id = int(trial_id)

        # ----- Activation du sampler -----
        epoch_now = time.time()
        self._sampling_trial_id = trial_id
        self._sampling_dir_sign = dir_sign
        self._sampling_trial_start = epoch_now

        if encoder and hasattr(encoder, "start_trial"):
            encoder.start_trial(epoch=epoch_now, trial_id=trial_id)

        # ----- Calcul du profil sigmoïde -----
        t = np.linspace(0.001, 0.999, steps)
        pulsing_times = self.logit_derivative(t)
        pulsing_durations = pulsing_times / np.sum(pulsing_times) * duration

        deg_per_impulse = self.angle_per_impulse

        # ----- MOUVEMENT -----
        for pulsing_duration in pulsing_durations:

            period = pulsing_duration + 2 * min_delay

            # vitesses setpoint
            set_vel_deg = deg_per_impulse / period
            set_vel_imp = 1 / period

            # mise à jour valeurs pour sampler
            self._current_set_vel_deg = set_vel_deg
            self._current_set_vel_imp = set_vel_imp

            # --- pulse ---
            self.pulse_line.set_value(1)
            time.sleep(min_delay + pulsing_duration/2)
            self.pulse_line.set_value(0)
            time.sleep(min_delay + pulsing_duration/2)

            # ----- Mise à jour du compteur global cumulatif -----
            self._emitted_pulses_total += dir_sign



        # ---------------- FIN DE MOUVEMENT ----------------

        # vitesses à zéro
        self._current_set_vel_imp = 0
        self._current_set_vel_deg = 0

        # Écriture d’une dernière ligne synchrone
        epoch_end = time.time()
        pos_deg = self._emitted_pulses_total * self.angle_per_impulse

        self._setpoint_writer.writerow([
            f"{epoch_end:.6f}",
            f"{duration:.3f}",
            "0.000", "0.000", "0.000",
            f"{pos_deg:.3f}",
            f"{trial_id}",
            f"{dir_sign}"
        ])
        self._setpoint_file.flush()

        # Fin du trial pour sampler
        self._sampling_trial_id = None
        self._sampling_dir_sign = 0
        self._sampling_trial_start = None

        if encoder and hasattr(encoder, "end_trial"):
            encoder.end_trial()



    # -------------------------------------------------------------
    #                 MÉTHODES UTILITAIRES
    # -------------------------------------------------------------
    def get_anglePerImpulse(self):
        return self.angle_per_impulse


    def rotate(self, steps, delay):
        for _ in range(steps):
            self.pulse_line.set_value(1)
            time.sleep(delay)
            self.pulse_line.set_value(0)
            time.sleep(delay)


    def cleanup(self):
        self._sampling_stop.set()
        try:
            self._sampler_thread.join(timeout=1)
        except:
            pass

        self.direction_line.release()
        self.pulse_line.release()

        try:
            self._setpoint_file.close()
        except:
            pass
