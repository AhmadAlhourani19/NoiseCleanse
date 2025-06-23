"""
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
"""
import numpy as np
import sounddevice as sd
from scipy.signal import lfilter
from scipy.linalg import toeplitz
from scipy.fft import fft, ifft

from . import config
from .utils import auto_lambda_from_ir

_stream = {
    "input": None,
    "output": None,
    "inverse_fir": None,
    "fir_state": None,
    "noise_profile": None
}

def compute_inverse_fir(ir: np.ndarray, length: int, reg_lambda: float = None) -> np.ndarray:
    """Compute inverse FIR filter using Tikhonov regularization."""
    print("Computing inverse FIR filter...")

    # Automatically tune lambda if not provided
    if reg_lambda is None:
        reg_lambda = auto_lambda_from_ir(ir)

    h = ir.flatten()
    H = toeplitz(h, np.zeros(length))
    d = np.zeros(H.shape[0])
    d[0] = 1  # delta function

    regularized = H.T @ H + reg_lambda * np.eye(length)
    g = np.linalg.solve(regularized, H.T @ d)

    # Normalize inverse filter
    g /= (np.sum(g**2) + 1e-9)
    return g

def measure_noise_profile(duration=1.0, fs=config.FS):
    """Record background noise to create a noise profile."""
    print("Measuring noise profile...")
    recording = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    noise = recording.flatten()
    noise_fft = fft(noise, n=512)
    return np.mean(np.abs(noise_fft))

def spectral_denoise(frame, noise_profile, fs):
    N = 512
    if len(frame) < N:
        frame = np.pad(frame, (0, N - len(frame)))

    X = fft(frame, n=N)
    mag = np.abs(X)
    phase = np.angle(X)

    noise_threshold = 1.5 * noise_profile
    suppression_factor = 0.6 

    mag = np.where(mag < noise_threshold, mag * suppression_factor, mag)

    Y = mag * np.exp(1j * phase)
    cleaned = np.real(ifft(Y))
    return cleaned[:len(frame)]

def audio_callback(indata, outdata, frames, time, status):
    """Callback for real-time deconvolution with energy gating."""
    if status:
        print(f"Stream status: {status}")

    x = indata[:, 0]

    y, _stream["fir_state"] = lfilter(
        _stream["inverse_fir"], [1.0], x, zi=_stream["fir_state"]
    )

    energy = np.mean(y**2)
    threshold = 1e-4  

    if energy < threshold:
        y *= 0.2  

    y *= config.LIVE_GAIN

    outdata[:, 0] = y[:frames]


def start_live_deconv(ir: np.ndarray, fs: int = config.FS,
                      input_device: int = None,
                      output_device: int = None,
                      volume: float = 1.0):

    if _stream["input"] is not None:
        stop_live_deconv()

    print("Input device:", input_device)
    print("Output device:", output_device)

    inv_fir = compute_inverse_fir(ir, config.IMPULSE_LENGTH)
    fir_state = np.zeros(len(inv_fir) - 1)

    _stream["inverse_fir"] = inv_fir
    _stream["fir_state"] = fir_state
    _stream["noise_profile"] = measure_noise_profile()

    def callback(indata, outdata, frames, time, status):
        x = indata[:, 0]
        y, _stream["fir_state"] = lfilter(inv_fir, [1.0], x, zi=_stream["fir_state"])
        y *= min(volume, 1.5)
        outdata[:, 0] = y[:frames]

    try:
        sd.default.device = (input_device, output_device) 
    except Exception as e:
        print("Device selection failed:", e)

    _stream["input"] = sd.Stream(
        samplerate=fs,
        blocksize=config.LIVE_FRAME_SIZE,
        channels=1,
        dtype='float32',
        callback=callback
    )

    _stream["input"].start()
    print("Live deconvolution started.")


def stop_live_deconv():
    """Stop the real-time deconvolution stream."""
    if _stream["input"] is not None:
        print("Stopping live deconvolution...")
        _stream["input"].stop()
        _stream["input"].close()
        _stream["input"] = None
        _stream["fir_state"] = None
        _stream["inverse_fir"] = None
        _stream["noise_profile"] = None
        print("Live deconvolution stopped.")
    else:
        print("ℹNo live stream to stop.")
