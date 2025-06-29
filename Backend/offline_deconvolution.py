"""
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
"""

import numpy as np
from scipy.signal import butter, filtfilt, spectrogram, istft, find_peaks, iirnotch
from scipy.fft import fft, ifft
import soundfile as sf
import os

from . import config
from .audio_io import save_audio
from .utils import normalize as util_normalize
from .utils import trim_silence, adaptive_normalize, smart_spectral_gate


def spectral_division(recorded: np.ndarray, ir: np.ndarray, fs: int, lambda_reg: float) -> np.ndarray:
    print("Performing Tikhonov spectral division...")
    N = max(len(recorded), len(ir))
    X = fft(recorded, n=N)
    H = fft(ir, n=N)

    phase_X = np.angle(X)
    mag_X = np.abs(X)
    mag_H = np.abs(H)

    mag_Y = mag_X / (mag_H + lambda_reg)
    Y = mag_Y * np.exp(1j * phase_X)
    y = np.real(ifft(Y))
    return y


def mmse_deconvolve(recorded: np.ndarray, ir: np.ndarray, fs: int, noise_floor: float = 1e-4) -> np.ndarray:
    print("Performing MMSE deconvolution")
    N = max(len(recorded), len(ir))
    X = fft(recorded, n=N)
    H = fft(ir, n=N)

    H_conj = np.conj(H)
    H_power = np.abs(H)**2
    signal_power = np.median(np.abs(X)**2)
    noise_power = noise_floor * signal_power

    MMSE_filter = H_conj / (H_power + noise_power)
    S_hat = MMSE_filter * X
    recovered = np.real(ifft(S_hat))
    return recovered


def apply_notch_filters(signal: np.ndarray, fs: int, passes: int = 2) -> np.ndarray:
    print("Applying only fixed notch filters at 50 and 100 Hz...")
    for freq in [50, 100]:
        b, a = iirnotch(freq / (fs / 2), Q=60)
        signal = filtfilt(b, a, signal)
    return signal


def apply_filters(signal: np.ndarray, fs: int) -> np.ndarray:
    print("Applying band-pass filtering...")
    b_hp, a_hp = butter(2, config.IR_HIGH_PASS / (fs / 2), btype='high')
    signal = filtfilt(b_hp, a_hp, signal)

    if config.IR_LOW_PASS < fs / 2:
        b_lp, a_lp = butter(2, config.IR_LOW_PASS / (fs / 2), btype='low')
        signal = filtfilt(b_lp, a_lp, signal)

    return signal


def normalize(signal: np.ndarray, peak: float = 0.999) -> np.ndarray:
    return util_normalize(signal, peak)

def apply_static_notch_filters(signal: np.ndarray, fs: int) -> np.ndarray:
    print("Applying static notch filters at 60Hz and harmonics...")
    notch_freqs = [60, 120, 180, 240]  
    for freq in notch_freqs:
        low = (freq - 1) / (fs / 2)
        high = (freq + 1) / (fs / 2)
        b, a = butter(2, [low, high], btype='bandstop')
        signal = filtfilt(b, a, signal)
    return signal

def refined_spectral_gate(signal: np.ndarray, fs: int) -> np.ndarray:
    print("Applying refined spectral gating...")
    win_size = 512
    hop = win_size // 2
    window = np.hanning(win_size)

    f, t, S = spectrogram(signal, fs, window=window, nperseg=win_size, noverlap=hop, mode='magnitude')
    noise_floor = np.median(S, axis=1, keepdims=True)
    mask = S < (1.5 * noise_floor)

    S_masked = S * (~mask)
    phase = np.angle(fft(signal, n=win_size))[:len(S_masked)]
    S_complex = S_masked * np.exp(1j * phase[:, np.newaxis])
    _, signal_out = istft(S_complex, fs, window=window, nperseg=win_size, noverlap=hop)

    return signal_out


def offline_deconvolve(signal: np.ndarray, ir: np.ndarray, fs: int, gain=1.0) -> np.ndarray:
    print("[Offline Deconvolution] Starting...")

    if signal is None or len(signal) == 0 or ir is None or len(ir) == 0:
        print("Invalid input signal or IR.")
        return np.zeros(44100)

    n = len(signal) + len(ir) - 1
    SIG = np.fft.fft(signal, n=n)
    IR = np.fft.fft(ir, n=n)
    eps = 1e-8
    recovered = np.fft.ifft(SIG / (IR + eps)).real
    recovered = np.nan_to_num(recovered)
    recovered *= gain

    recovered = apply_static_notch_filters(recovered, fs)

    b_hp, a_hp = butter(2, 80 / (fs / 2), btype='high')
    recovered = filtfilt(b_hp, a_hp, recovered)

    if fs / 2 > 15000:
        b_lp, a_lp = butter(2, 15000 / (fs / 2), btype='low')
        recovered = filtfilt(b_lp, a_lp, recovered)

    max_val = np.max(np.abs(recovered)) + 1e-9
    recovered = recovered / max_val
    recovered = np.clip(recovered, -1.0, 1.0)

    recovered = smart_spectral_gate(recovered, fs)

    print(f"Output stats: min={recovered.min():.4f}, max={recovered.max():.4f}, mean={recovered.mean():.4f}")
    return recovered

def save_output_audio(signal: np.ndarray, fs: int, filename: str = "temp_uploads/recovered.wav") -> str:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    sf.write(filename, signal, fs)
    return filename