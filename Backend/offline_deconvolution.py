# noise_cleanse/offline_deconvolution.py

import numpy as np
from scipy.signal import butter, filtfilt, spectrogram, istft, find_peaks
from scipy.fft import fft, ifft

from . import config
from .audio_io import save_audio
from .utils import normalize as util_normalize
import soundfile as sf
import os

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


def apply_spectral_gating(signal: np.ndarray, fs: int, passes: int = 2) -> np.ndarray:
    print("Applying spectral gating...")
    win_size = 512
    hop = win_size // 2
    window = np.hamming(win_size)

    for _ in range(passes):
        if len(signal) < win_size:
            signal = np.pad(signal, (0, win_size - len(signal)))
        f, t, S = spectrogram(signal, fs, window=window, nperseg=win_size, noverlap=hop, mode='complex')
        mag = np.abs(S)

        noise_floor = np.median(mag[-50:, :])
        threshold = 1.5 * noise_floor

        mask = mag < threshold
        S[mask] *= 0.1

        _, signal = istft(S, fs, window=window, nperseg=win_size, noverlap=hop)
    return signal


def apply_notch_filters(signal: np.ndarray, fs: int, passes: int = 2) -> np.ndarray:
    print("Applying notch filters...")
    for _ in range(passes):
        N = len(signal)
        spectrum = np.abs(fft(signal, n=N))[:N//2]
        peaks, _ = find_peaks(spectrum, height=config.NOTCH_THRESHOLD * np.max(spectrum))
        for peak in peaks:
            f_center = peak * fs / N
            bw = 100  # notch width
            low = max((f_center - bw/2) / (fs/2), 0.01)
            high = min((f_center + bw/2) / (fs/2), 0.99)
            if low < high:
                b, a = butter(2, [low, high], btype='bandstop')
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


import numpy as np

def offline_deconvolve(signal, ir, fs, gain=1.0):
    print("[Offline Deconvolution] Starting...")
    print(f"  Signal shape: {signal.shape}, IR shape: {ir.shape}, Gain: {gain}")

    if signal is None or len(signal) == 0:
        print("❌ Error: Signal is empty!")
        return np.zeros(44100)

    if ir is None or len(ir) == 0:
        print("❌ Error: IR is empty!")
        return np.zeros(44100)

    # Normalize input
    signal = np.nan_to_num(signal).astype(np.float32)
    ir = np.nan_to_num(ir).astype(np.float32)

    n = len(signal) + len(ir) - 1
    print(f"  Performing FFT of length: {n}")

    SIG = np.fft.fft(signal, n=n)
    IR = np.fft.fft(ir, n=n)

    eps = 1e-8  # avoid division by zero
    recovered = np.fft.ifft(SIG / (IR + eps)).real

    recovered *= gain
    recovered = np.nan_to_num(recovered)

    # Clip to [-1, 1] for WAV saving
    recovered = np.clip(recovered, -1.0, 1.0)

    print(f"  Output shape: {recovered.shape}")
    print(f"  Output min: {recovered.min():.5f}, max: {recovered.max():.5f}, mean: {recovered.mean():.5f}")

    if np.all(recovered == 0):
        print("⚠️ Warning: Output signal is entirely zero.")
    elif np.any(np.isnan(recovered)) or np.any(np.isinf(recovered)):
        print("❌ Error: Output contains NaNs or Infs.")

    return recovered



def save_output_audio(signal: np.ndarray, fs: int, filename: str = "temp_uploads/recovered.wav") -> str:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    sf.write(filename, signal, fs)
    return filename