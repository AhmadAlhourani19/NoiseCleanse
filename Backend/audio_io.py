"""
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
"""

import os
import numpy as np
import sounddevice as sd
from scipy.io import wavfile


def record_audio(filename: str, duration: float, fs: int = 44100):
    """Record audio from the default input device and save as WAV."""
    print(f"Recording for {duration} seconds at {fs} Hz...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    recording = np.squeeze(recording)
    recording = recording / np.max(np.abs(recording) + 1e-9)
    wavfile.write(filename, fs, recording)
    print(f"Recording saved to {filename}")
    return recording


def play_audio(filename: str):
    """Play a WAV file through the default output device."""
    fs, data = wavfile.read(filename)
    if data.dtype != np.float32:
        data = data.astype(np.float32) / np.max(np.abs(data))
    print(f"Playing {filename}...")
    sd.play(data, samplerate=fs)
    sd.wait()


def save_audio(filename: str, signal: np.ndarray, fs: int):
    """Save a numpy array as a WAV file."""
    signal = signal / (np.max(np.abs(signal)) + 1e-9)
    signal = np.squeeze(signal).astype(np.float32)
    wavfile.write(filename, fs, signal)
    print(f"Saved audio to {filename}")


def load_audio(filename: str, target_fs: int = None):
    """Load a WAV file and optionally resample it."""
    fs, data = wavfile.read(filename)
    data = np.squeeze(data).astype(np.float32)
    if np.max(np.abs(data)) > 0:
        data /= np.max(np.abs(data))
    if target_fs is not None and fs != target_fs:
        from scipy.signal import resample
        num_samples = int(len(data) * target_fs / fs)
        data = resample(data, num_samples)
        fs = target_fs
    print(f"Loaded {filename} at {fs} Hz")
    return data, fs
