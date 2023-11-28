import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# set up audio recording parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 96000
CHUNK = 4096

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
line, = ax.plot([], [])
ax.set_xlim(17000, 21000)
# ax.set_xlim(0, min(RATE/2, 220009))
ax.set_ylim(0,5)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Amplitude')
fig.canvas.draw()

TargetFreq = 20000

# start recording and plotting
while True:
    # read audio data from stream
    data = stream.read(CHUNK)
    audio_data = np.frombuffer(data, dtype=np.float32)

    # apply Hamming window to audio data
    audio_data = audio_data * window

    # apply FFT to audio data
    fft_data = np.fft.fft(audio_data, n=CHUNK)

    # compute magnitude spectrum
    mag_data = np.abs(fft_data)[:CHUNK//2]

    # update plot
    freqs = np.fft.fftfreq(CHUNK, 1/RATE)
    line.set_xdata(freqs[:CHUNK//2])
    line.set_ydata(mag_data)
    fig.canvas.draw()
    fig.canvas.flush_events()
    if not plt.fignum_exists(fig.number):
        break

# close audio stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()
    