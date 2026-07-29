import numpy as np
import sounddevice as sd

class SoundStimulator:
    def __init__(self, frequence=5000, duration=0.5):
        # Paramètres
        self.frequence = frequence  # Fréquence en Hz
        self.duree = duration  # Durée en secondes
        self.sampling_rate = 44100  # Taux d'échantillonnage

        # Génération du signal
        self.temps = np.linspace(0, self.duree, int(self.sampling_rate * self.duree), endpoint=False)
        self.signal = 0.5 * np.sin(2 * np.pi * self.frequence * self.temps)  # Signal sinusoïdal

    def playTheMusic(self):

        # Émission du son
        sd.play(self.signal, samplerate=self.sampling_rate)
        # sd.wait()  # Attendre la fin du son

