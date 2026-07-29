import gpiod
import time
import threading

class Wheel_Encoder:
    def __init__(self, phase_a_PIN=23, phase_b_PIN=22, phase_z_PIN=24, resolution=1024):
        """
        Initializes the Wheel_Encoder object with GPIO pins and resolution.

        :param phase_a_PIN: GPIO pin number for phase A
        :param phase_b_PIN: GPIO pin number for phase B
        :param phase_z_PIN: GPIO pin number for phase Z
        :param resolution: Number of encoder pulses per full rotation
        """
        self.phase_a_PIN = phase_a_PIN
        self.phase_b_PIN = phase_b_PIN
        self.phase_z_PIN = phase_z_PIN
        self.position = 0
        self.direction = "motionless"
        self.resolution = resolution
        self.angle_per_impulse = 180 / self.resolution

        # Initialize additional attributes
        self.last_position = 0
        self.last_time = time.time()
        self.speed = 0

        # Initialize GPIO chip and lines
        self.chip = gpiod.Chip("gpiochip4")
        self.phase_a_line = self.chip.get_line(self.phase_a_PIN)
        self.phase_b_line = self.chip.get_line(self.phase_b_PIN)
        self.phase_z_line = self.chip.get_line(self.phase_z_PIN)

        # Request GPIO lines
        self.phase_a_line.request(consumer="StepsMotor Encoder", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        self.phase_b_line.request(consumer="StepsMotor Encoder", type=gpiod.LINE_REQ_DIR_IN)
        self.phase_z_line.request(consumer="StepsMotor Encoder", type=gpiod.LINE_REQ_DIR_IN)

        # Start the event monitoring thread
        self.event_thread = threading.Thread(target=self.monitor_events)
        self.event_thread.daemon = True
        self.event_thread.start()

    def encoder_callback(self, channel):
        """
        Callback function for handling encoder pulses and calculating direction.

        :param channel: The GPIO line that triggered the callback
        """
        phase_a = self.phase_a_line.get_value()
        phase_b = self.phase_b_line.get_value()
        phase_z = self.phase_z_line.get_value()

        if phase_a == phase_b:
            self.position += 1
            self.direction = "counterclockwise"
        else:
            self.position -= 1
            self.direction = "clockwise"

        self.calculate_speed()

    def calculate_speed(self):
        """
        Calculates the current speed of the encoder based on position and time.
        """
        current_time = time.time()
        delta_position = self.position - self.last_position
        delta_time = current_time - self.last_time

        if delta_time > 0:
            self.speed = (delta_position / delta_time) * self.angle_per_impulse

        # Update last_position and last_time
        self.last_position = self.position
        self.last_time = current_time

    def get_speed(self):
        """
        Returns the current speed of the encoder.

        :return: The speed of the encoder
        """
        return self.speed

    def monitor_events(self):
        """
        Monitors GPIO events and invokes the encoder callback.
        """
        while True:
            event = self.phase_a_line.event_wait(sec=1)
            if event:
                event = self.phase_a_line.event_read()
                self.encoder_callback(self.phase_a_line)

    def get_position(self):
        """
        Returns the current position of the encoder.

        :return: The position of the encoder
        """
        return self.position

    def get_direction(self):
        """
        Returns the current direction of rotation.

        :return: The direction of rotation
        """
        return self.direction

    def cleanup(self):
        """
        Releases GPIO lines.
        """
        self.phase_a_line.release()
        self.phase_b_line.release()
        self.phase_z_line.release()

    def get_anglePerImpulse(self):
        """
        Returns the angle covered per encoder pulse.

        :return: Angle per pulse
        """
        return self.angle_per_impulse
