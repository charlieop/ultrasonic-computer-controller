import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import os


def detectMovementStart(mag_data, targetIndex, radiusOfInterest, rangeOfInterest):
    # return if the speaker is not on
    centeral_intensity = sum(mag_data[targetIndex-1: targetIndex+2])
    if centeral_intensity < 5:
        print("speaker is off" + str(centeral_intensity))
        return False
    
    # return if the frequency change is caused by noise (present in all frequency)
    noiseThreshold = 0.5
    if np.average(mag_data[targetIndex-40:targetIndex-10]) > noiseThreshold or np.average(mag_data[targetIndex+10:targetIndex+40]) > noiseThreshold:
        print("noise detected" + str(centeral_intensity))
        return False
    
    # detect if there is a movement
    movementThreshold = 0.4
    if ( np.average(rangeOfInterest[0: radiusOfInterest - 4]) > movementThreshold or np.average(rangeOfInterest[radiusOfInterest + 5: 2 * radiusOfInterest + 1]) > movementThreshold):
        # print("movement detected" + str(centeral_intensity))
        return True
    

# set up audio recording parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024 # in this setup, the computer can run for 38 loops per second


# create PyAudio object
p = pyaudio.PyAudio()

# open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# create Hamming window
window = np.hamming(CHUNK)

# plot settings
plt.ion()  # turn on interactive mode
fig, ax = plt.subplots()
dots = ax.scatter([], [], s=1, c='black')
ax.set_xlim(18000, 21000)
ax.set_ylim(0, 20)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Amplitude')
fig.canvas.draw()

TargetFreq = 20000
targetIndex = int(TargetFreq / (RATE / CHUNK))
radiusOfInterest = 15

movementData = np.array([])

i = 0
lastMovementRecordTime = time.time()

# Define the desired minimum number of runs per second
target_runs_per_second = 20

# Calculate the target interval between each iteration (in seconds)
target_interval = 1 / target_runs_per_second

start_record_time = time.time()
c = 0

# start recording and plotting
while True:
    
    start_time = time.time()
    
    # # record how many loops per second
    # c += 1
    # if time.time() - start_record_time > 1:
    #     print(c)
    #     c = 0
    #     start_record_time = time.time()
    
    # read audio data from stream
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.float32)

    # apply Hamming window to audio data
    audio_data = audio_data * window

    # apply FFT to audio data
    fft_data = np.fft.fft(audio_data, n=CHUNK)

    # compute magnitude spectrum
    mag_data = np.abs(fft_data)[:CHUNK//2]
    
    # update plot
    freqs = np.fft.fftfreq(CHUNK, 1/RATE)
    dots.set_offsets(np.column_stack((freqs[:CHUNK//2], mag_data)))
    fig.canvas.draw()
    fig.canvas.flush_events()
    dots.remove()  # remove the old scatter plot
    dots = ax.scatter(freqs[:CHUNK//2], mag_data, s=1, c='black')  # plot the new scatter plot
    if not plt.fignum_exists(fig.number):
        break
    
    # data processing part
    rangeOfInterest = mag_data[targetIndex-radiusOfInterest:targetIndex+radiusOfInterest+1]
    
    if(time.time() - lastMovementRecordTime > 1):
        if (movementData.size > 0):
            print("movement recorded")
            # print(movementData.shape)
            
            # create a new file and save the data into it, the path is : datas/movement_data_i.npy
            directory = 'datas'
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, "movement_data_" + str(i) + ".npy")
            if not os.path.exists(file_path):
                open(file_path, 'w').close()
            np.save("datas/movement_data_" + str(i) + ".npy", movementData)
            print("movement_data_" + str(i) + ".npy saved")
            
            movementData = np.array([])
        if detectMovementStart(mag_data, targetIndex, radiusOfInterest, rangeOfInterest):
            print("movement detected", i)
            i += 1
            lastMovementRecordTime = time.time()
            movementData = np.append(movementData, rangeOfInterest)
    else:
        movementData = np.append(movementData, rangeOfInterest)
        
    end_time = time.time()
    elapsed_time = end_time - start_time

    if elapsed_time < target_interval:
        time.sleep(target_interval - elapsed_time)
        
        
# close audio stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()
