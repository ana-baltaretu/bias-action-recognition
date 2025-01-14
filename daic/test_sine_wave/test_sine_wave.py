import numpy as np
import matplotlib.pyplot as plt

def plot_sine_wave():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Sine Wave')
    plt.title('Plot of Sine Wave')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.savefig('sine_wave.png')
    plt.show()

if __name__ == '__main__':
    plot_sine_wave()