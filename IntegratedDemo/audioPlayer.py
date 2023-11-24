import pyaudio
import numpy as np
import threading

class AudioPlayer:
    def __init__(self):
        # Set up audio parameters
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.DURATION = 6000.0

        # Create PyAudio object
        self.p = pyaudio.PyAudio()
        self.stream = None

    def generate_sine_wave(self, frequency):
        # Create sine wave
        samples = np.arange(int(self.DURATION * self.RATE))
        waveform = np.sin(2 * np.pi * frequency * samples / self.RATE)
        return waveform

    def play_waveform(self, waveform):
        # Create audio stream
        self.stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             output=True)

        # Play audio stream
        self.stream.write(waveform.astype(np.float32).tobytes())
        
    def play_waveform_async(self, frequency):
        waveform = self.generate_sine_wave(frequency)
        # Create a new thread to play the waveform asynchronously
        thread = threading.Thread(target=self.play_waveform, args=(waveform,))
        thread.start()
        
    def stop(self):
        # Stop audio stream
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def close(self):
        # Terminate PyAudio object
        self.stop()
        self.p.terminate()


'''
# Usage example
player = AudioPlayer()
frequency = 20000
player.play_waveform_async(frequency)

import time
time.sleep(2)
print("top")
player.stop()

player.close()
'''