from audioPlayer import AudioPlayer
from plotter import Plotter
from dataAnalyzer import AudioAnalyzer
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time

" config "
isPi = False
USE_ML = True   # True: use ML model to classify, False: use threshold to classify
display = True
SHOW_PERFORMANCE = False
target_runs_per_second = 999

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
FREQUENCY_MAIN = 20000
FREQUENCY_OTHER = 18000 
RoI = 7
window = np.hamming(CHUNK)

# Calculate the target interval between each iteration (in seconds)
target_interval = 1 / target_runs_per_second
start_record_time = time.time()


print("\n\n==========\ninitiallizing...\n==========\n")


print("==========\nloading audio...\n==========\n")
# start playing the single frequency sound
if not isPi:
    player = AudioPlayer()
    player.play_waveform_async(FREQUENCY_MAIN)

    print("==========\naudio loaded\n==========\n") 
else:
    print("==========\naudio skipped\n==========\n")


print("==========\nloading microphone...\n==========\n")
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


print("==========\nloading plotter...\n==========\n")
# create plotter
plotter = Plotter(RATE, CHUNK, (FREQUENCY_OTHER-1000, FREQUENCY_MAIN+1000), (0, 1))
time.sleep(0.2)
print("==========\nplotloaded\n==========\n")


print("==========\nloading analyzer...\n==========\n")
analyzer = None
if not isPi:
    analyzer = AudioAnalyzer(FREQUENCY_MAIN, RATE, CHUNK, RoI, FREQUENCY_OTHER, USE_ML, isPi)
else:
    analyzer = AudioAnalyzer(FREQUENCY_MAIN, RATE, CHUNK, RoI, FREQUENCY_OTHER, USE_ML, isPi)
time.sleep(0.2)
print("==========\nanalyzer loaded\n==========\ n")

def pre_processing(audio_data, window):
    # apply Hamming window to audio data
    audio_data = audio_data * window
    # apply FFT to audio data
    fft_data = np.fft.fft(audio_data, n=CHUNK)
    # compute magnitude spectrum
    mag_data = np.abs(fft_data)[:CHUNK//2]
    return mag_data


print("==========\nstart\n==========\n")

last_time = time.time()
inMovement = False
log = []
label_thres = 0.08

start_record_time = time.time()
c = 0

# start recording and plotting
while True:
    
    # limit the number of runs per second
    start_time = time.time()
    
    # record performance
    c += 1
    if time.time() - start_record_time > 1:
        if SHOW_PERFORMANCE:
            print(c)
        c = 0
        start_record_time = time.time()

    # read audio data from stream
    data = stream.read(CHUNK, exception_on_overflow=False)
    mag_data = pre_processing(np.frombuffer(data, dtype=np.float32), window)
    
    # update plot
    if not isPi and display:
        plotter.draw(mag_data) 
        
    # process data
    analyzer.analyze(mag_data)
    
    # stop the loop if the plot is closed
    if not plt.fignum_exists(plotter.fig.number):
        break  
    
    # limit the number of runs per second
    end_time = time.time()
    elapsed_time = end_time - start_time
    if elapsed_time < target_interval:
        time.sleep(target_interval - elapsed_time)
        
        
# close audio stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()

if not isPi:
    player.close()