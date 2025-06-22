# noise_cleanse/utils.py

import numpy as np
from scipy.signal import resample, spectrogram, istft

def remove_dc(signal: np.ndarray) -> np.ndarray:
    """Remove DC offset from a signal."""
    return signal - np.mean(signal)


def normalize(signal: np.ndarray, peak: float = 1.0) -> np.ndarray:
    """Normalize a signal to a given peak amplitude."""
    max_val = np.max(np.abs(signal)) + 1e-9
    return signal * (peak / max_val)


def apply_fade(signal: np.ndarray, fade_len: int) -> np.ndarray:
    """Apply linear fade-in and fade-out to a signal."""
    if fade_len * 2 >= len(signal):
        raise ValueError("Fade length too large for the signal length.")

    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    signal[:fade_len] *= fade_in
    signal[-fade_len:] *= fade_out
    return signal


def resample_if_needed(signal: np.ndarray, fs_orig: int, fs_target: int) -> np.ndarray:
    """Resample signal to target sampling rate if needed."""
    if fs_orig == fs_target:
        return signal
    ratio = fs_target / fs_orig
    new_length = int(len(signal) * ratio)
    return resample(signal, new_length)


def estimate_snr(signal: np.ndarray, noise_est: float = 1e-4) -> float:
    """Estimate SNR from signal using median-based heuristic."""
    signal_power = np.median(np.abs(signal)**2)
    snr = 10 * np.log10(signal_power / (noise_est * signal_power + 1e-9))
    return snr


def auto_lambda_from_ir(ir: np.ndarray, factor: float = 0.01) -> float:
    """Automatically estimate regularization lambda from IR energy."""
    energy = np.sum(ir**2)
    lambda_val = factor * energy
    print(f"Auto-tuned lambda = {lambda_val:.6f} based on IR energy")
    return lambda_val

def trim_silence(signal: np.ndarray, threshold: float = 0.02) -> np.ndarray:
    """Trim leading/trailing silence."""
    energy = np.abs(signal)
    non_silent = np.where(energy > threshold)[0]
    if non_silent.size == 0:
        return signal
    return signal[non_silent[0]:non_silent[-1]+1]

def smart_spectral_gate(signal: np.ndarray, fs: int, win_size: int = 1024, passes: int = 2) -> np.ndarray:
    print("Applying smart spectral gate...")
    hop = win_size // 2
    window = np.hamming(win_size)

    for _ in range(passes):
        if len(signal) < win_size:
            signal = np.pad(signal, (0, win_size - len(signal)))

        f, t, S = spectrogram(signal, fs, window=window, nperseg=win_size, noverlap=hop, mode='complex')
        mag = np.abs(S)
        phase = np.angle(S)

        noise_floor = np.median(mag, axis=1, keepdims=True)
        threshold = 1.2 * noise_floor

        mask = mag < threshold
        mag[mask] *= 0.2  # reduce noise by 80%

        S_denoised = mag * np.exp(1j * phase)
        _, signal = istft(S_denoised, fs, window=window, nperseg=win_size, noverlap=hop)

    return signal


def adaptive_normalize(signal: np.ndarray, target_rms: float = 0.1) -> np.ndarray:
    """Normalize only non-silent sections using RMS."""
    rms = np.sqrt(np.mean(signal ** 2))
    if rms < 1e-5:
        return signal
    return signal * (target_rms / (rms + 1e-9))
