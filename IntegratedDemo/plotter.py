import numpy as np
import matplotlib.pyplot as plt
import threading

class Plotter:
    def __init__(self, rate, chunk, xlim, ylim):
        self.RATE = rate
        self.CHUNK = chunk
        self.fig, self.ax = plt.subplots()
        self.dots = self.ax.scatter([], [], s=1, c='black')
        self.ax.set_xlim(xlim[0], xlim[1])
        self.ax.set_ylim(ylim[0], ylim[1])
        self.ax.set_xlabel('Frequency (Hz)')
        self.ax.set_ylabel('Amplitude')
        self.freqs = np.fft.fftfreq(self.CHUNK, 1 / self.RATE)
        plt.ion()
        plt.show()
        self.fig.canvas.draw()
        self.lock = threading.Lock()

    def draw(self, mag_data):
        with self.lock:
            self.dots.set_offsets(np.column_stack((self.freqs[:self.CHUNK // 2], mag_data)))
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
