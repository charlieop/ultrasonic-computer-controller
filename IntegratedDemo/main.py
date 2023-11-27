from audioPlayer import AudioPlayer
from plotter import Plotter
from dataAnalyzer import AudioAnalyzer
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import os

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
player.play_waveform_async( frequency)

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
plotter = Plotter(RATE, CHUNK, (17000, frequency+1000), (0, 1))
time.sleep(0.2)

print("==========\nplotloaded\n==========\n")

analyzer = AudioAnalyzer(frequency, RATE, CHUNK, 10)
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

# testing
targetIndexOf18k = int(18000 / RATE * CHUNK)
radiusOfInterestof18k = 12
thresholdOf18k = 0.01
targetIndexOf20k = int(20000 / RATE * CHUNK)
radiusOfInterestof20k = 12
left_log = np.array([])
right_log = np.array([])
left_log_20k = np.array([])
right_log_20k = np.array([])

log18k = []
log20k = []

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
    
    
    rangeOfInterestof20k = mag_data[targetIndexOf20k- radiusOfInterestof20k : targetIndexOf20k + radiusOfInterestof20k+1]
    left = np.average(rangeOfInterestof20k[0: radiusOfInterestof20k-2])
    right = np.average(rangeOfInterestof20k[radiusOfInterestof20k+3: -1])
    left_log_20k = np.append(left_log_20k, left)
    right_log_20k = np.append(right_log_20k, right)

    log20k.append(rangeOfInterestof20k)
    
    rangeOfInterestof18k = mag_data[targetIndexOf18k- radiusOfInterestof18k : targetIndexOf18k + radiusOfInterestof18k+1]
    right = np.average(rangeOfInterestof18k[0: radiusOfInterestof18k-2])
    left = np.average(rangeOfInterestof18k[radiusOfInterestof18k+3: -1])
    left_log = np.append(left_log, left)
    right_log = np.append(right_log, right)
    
    log18k.append(rangeOfInterestof18k)

    # stop the loop if the plot is closed
    if not plt.fignum_exists(plotter.fig.number):
        break
    
        
# close audio stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()

directory = 'datas'
if not os.path.exists(directory):
    os.makedirs(directory)
file_path = os.path.join(directory, "left.npy")
if not os.path.exists(file_path):
    open(file_path, 'w').close()
np.save("datas/left.npy", left_log)
print("left.npy saved")
file_path = os.path.join(directory, "right.npy")
if not os.path.exists(file_path):
    open(file_path, 'w').close()
np.save("datas/right.npy", right_log)
print("right.npy saved")
file_path = os.path.join(directory, "left_20k.npy")
if not os.path.exists(file_path):
    open(file_path, 'w').close()
np.save("datas/left_20k.npy", left_log_20k)
print("left.npy saved")
file_path = os.path.join(directory, "right_20k.npy")
if not os.path.exists(file_path):
    open(file_path, 'w').close()
np.save("datas/right_20k.npy", right_log_20k)
print("right.npy saved")

log18k = np.array(log18k)
file_path = os.path.join(directory, "log18k.npy")
if not os.path.exists(file_path):
    open(file_path, 'w').close()
np.save("datas/log18k.npy", log18k)
print(f"log18k.npy saved. shape: {log18k.shape}")

log20k = np.array(log20k)
file_path = os.path.join(directory, "log20k.npy")
if not os.path.exists(file_path):
    open(file_path, 'w').close()
np.save("datas/log20k.npy", log20k)
print(f"log20k.npy saved. shape: {log20k.shape}")

player.close()