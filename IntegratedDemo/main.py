from audioPlayer import AudioPlayer
from plotter import Plotter
from dataAnalyzer import AudioAnalyzer
from dirClassifier import DirClassifier
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import os

" constants "
isPi = False
display = True
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
FREQUENCY_MAIN = 20000
FREQUENCY_OTHER = 18000 
USE_ML = True   # True: use ML model to classify, False: use threshold to classify
RoI = 7
# create Hamming window
window = np.hamming(CHUNK)
# Define the desired minimum number of runs per second
target_runs_per_second = 999

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
    analyzer = AudioAnalyzer(FREQUENCY_MAIN, RATE, CHUNK, RoI, FREQUENCY_OTHER, USE_ML)
else:
    analyzer = AudioAnalyzer(FREQUENCY_MAIN, RATE, CHUNK, RoI)
time.sleep(0.2)
print("==========\nanalyzer loaded\n==========\n")


predictor = DirClassifier()
time.sleep(0.2)
print("==========\nmodel loaded\n==========\n")


def pre_processing(audio_data, window):
    # apply Hamming window to audio data
    audio_data = audio_data * window
    # apply FFT to audio data
    fft_data = np.fft.fft(audio_data, n=CHUNK)
    # compute magnitude spectrum
    mag_data = np.abs(fft_data)[:CHUNK//2]
    return mag_data


# testing
targetIndexOf18k = int(18000 / RATE * CHUNK)
radiusOfInterestof18k = 7
targetIndexOf20k = int(20000 / RATE * CHUNK)
radiusOfInterestof20k = 7

# left_log = np.array([])
# right_log = np.array([])
# left_log_20k = np.array([])
# right_log_20k = np.array([])
# log18k = []
# log20k = []

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
        
    '''
    rangeOfInterestof20k = mag_data[targetIndexOf20k- radiusOfInterestof20k : targetIndexOf20k + radiusOfInterestof20k+1]
    left_avg_20k = np.clip(np.average(rangeOfInterestof20k[0: radiusOfInterestof20k-2]), -0.5, 0.5)
    right_avg_20k = np.clip(np.average(rangeOfInterestof20k[radiusOfInterestof20k+3: -1]), -0.5, 0.5)
    
    rangeOfInterestof18k = mag_data[targetIndexOf18k- radiusOfInterestof18k : targetIndexOf18k + radiusOfInterestof18k+1]
    left_avg_18k = np.clip(np.average(rangeOfInterestof18k[0: radiusOfInterestof18k-2]), -0.5, 0.5)
    right_avg_18k = np.clip(np.average(rangeOfInterestof18k[radiusOfInterestof18k+3: -1]), -0.5, 0.5)
    
    diff18k = (right_avg_18k - left_avg_18k)
    diff20k = (right_avg_20k - left_avg_20k)
    diff20k_18k = (diff18k - diff20k)

    if (np.abs(diff18k) > label_thres) | (np.abs(diff20k) > label_thres) | (np.abs(diff20k_18k) > label_thres):
        if not inMovement:
            print("==========movement========")
            inMovement = True
        res = predictor.get_class(diff18k, diff20k, diff20k_18k)
        log.append(res[0])
        last_time = time.time()
    elif time.time() - last_time > 0.5 and inMovement:
        print("\n")
        down1 = False
        up1 = False
        down2 = False
        up2 = False
        for i in range(len(log)):
            if log[i] == "down":
                down1 = True
            if down1 and log[i] == "up":
                up1 = True
            if up1 and log[i] == "down":
                down2 = True
            if down2 and log[i] == "up":
                up2 = True
        if down1 and up1 and down2 and up2:
            print("double tap")
        elif down1 and up1:
            print("single tap")
        else:
            print(f"value: {log}\nmax: {max(log, key=log.count)}" )
        log = []
        inMovement = False
    '''
    
    # left_log_20k = np.append(left_log_20k, left_avg_20k)
    # right_log_20k = np.append(right_log_20k, right_avg_20k)
    # log20k.append(rangeOfInterestof20k)
    # left_log = np.append(left_log, left_avg_18k)
    # right_log = np.append(right_log, right_avg_18k)
    # log18k.append(rangeOfInterestof18k)
    
    
# close audio stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()

# directory = 'datas'
# if not os.path.exists(directory):
#     os.makedirs(directory)
# file_path = os.path.join(directory, "left.npy")
# if not os.path.exists(file_path):
#     open(file_path, 'w').close()
# np.save("datas/left.npy", left_log)
# print("left.npy saved")
# file_path = os.path.join(directory, "right.npy")
# if not os.path.exists(file_path):
#     open(file_path, 'w').close()
# np.save("datas/right.npy", right_log)
# print("right.npy saved")
# file_path = os.path.join(directory, "left_20k.npy")
# if not os.path.exists(file_path):
#     open(file_path, 'w').close()
# np.save("datas/left_20k.npy", left_log_20k)
# print("left.npy saved")
# file_path = os.path.join(directory, "right_20k.npy")
# if not os.path.exists(file_path):
#     open(file_path, 'w').close()
# np.save("datas/right_20k.npy", right_log_20k)
# print("right.npy saved")

# log18k = np.array(log18k)
# file_path = os.path.join(directory, "log18k.npy")
# if not os.path.exists(file_path):
#     open(file_path, 'w').close()
# np.save("datas/log18k.npy", log18k)
# print(f"log18k.npy saved. shape: {log18k.shape}")

# log20k = np.array(log20k)
# file_path = os.path.join(directory, "log20k.npy")
# if not os.path.exists(file_path):
#     open(file_path, 'w').close()
# np.save("datas/log20k.npy", log20k)
# print(f"log20k.npy saved. shape: {log20k.shape}")

player.close()