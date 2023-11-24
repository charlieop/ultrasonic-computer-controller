from audioPlayer import AudioPlayer
from plotter import Plotter
from dataAnalyzer import AudioAnalyzer
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time

" constants "
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
frequency = 20000
    # create Hamming window
window = np.hamming(CHUNK)

print("\n\n==========\ninitiallizing...\n==========\n")

# start playing the single frequency sound
player = AudioPlayer()
player.play_waveform_async(frequency)

print("==========\naudio loaded\n==========\n") 

# set up audio recording parameters
p = pyaudio.PyAudio()
# open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
time.sleep(0.5)

print("==========\nmicrophone loaded\n==========\n")

# create plotter
plotter = Plotter(RATE, CHUNK, (frequency-1000, frequency+1000), (0, 20))
time.sleep(0.2)

print("==========\nplotloaded\n==========\n")

analyzer = AudioAnalyzer(frequency, RATE, CHUNK, 9)
time.sleep(0.2)

print("==========\nanalyzer loaded\n==========\n")

def pre_processing(audio_data, window):
    # apply Hamming window to audio data
    audio_data = audio_data * window

    # apply FFT to audio data
    fft_data = np.fft.fft(audio_data, n=CHUNK)

    # compute magnitude spectrum
    mag_data = np.abs(fft_data)[:CHUNK//2]
    
    return mag_data
time.sleep(0.1)

print("==========\nstart\n==========\n")

# start recording and plotting
while True:
    # read audio data from stream
    data = stream.read(CHUNK, exception_on_overflow=False)
    mag_data = pre_processing(np.frombuffer(data, dtype=np.float32), window)
    
    # update plot
    plotter.draw(mag_data)
    
    # process data
    analyzer.analyze(mag_data)
    
    # stop the loop if the plot is closed
    if not plt.fignum_exists(plotter.fig.number):
        break
    
        
# close audio stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()

player.close()