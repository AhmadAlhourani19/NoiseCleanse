"""
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PLOT_DIR = Path("temp_plots")
PLOT_DIR.mkdir(exist_ok=True)

def plot_time(signal: np.ndarray, fs: int, title: str = "Time Domain", filename: str = "plot_time.png") -> str:
    plt.figure(figsize=(10, 3))
    t = np.arange(len(signal)) / fs
    plt.plot(t, signal)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    out_path = PLOT_DIR / filename
    plt.savefig(out_path)
    plt.close()
    return str(out_path)

def plot_freq(signal: np.ndarray, fs: int, title: str = "Frequency Domain", filename: str = "plot_freq.png") -> str:
    plt.figure(figsize=(10, 3))
    N = len(signal)
    f = np.fft.rfftfreq(N, d=1/fs)
    spectrum = np.abs(np.fft.rfft(signal))
    plt.plot(f, spectrum)
    plt.title(title)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.tight_layout()
    out_path = PLOT_DIR / filename
    plt.savefig(out_path)
    plt.close()
    return str(out_path)
