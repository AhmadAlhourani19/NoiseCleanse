# noise_cleanse/live_deconvolution.py

import numpy as np
import sounddevice as sd
from scipy.signal import lfilter
from scipy.linalg import toeplitz
from scipy.fft import fft, ifft

from . import config
from .utils import auto_lambda_from_ir

# Global state for streaming
_stream = {
    "input": None,
    "output": None,
    "inverse_fir": None,
    "fir_state": None
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


def audio_callback(indata, outdata, frames, time, status):
    """Callback function for real-time deconvolution."""
    if status:
        print(f"Stream status: {status}")

    x = indata[:, 0]
    y, _stream["fir_state"] = lfilter(
        _stream["inverse_fir"], [1.0], x, zi=_stream["fir_state"]
    )
    y *= config.LIVE_GAIN
    outdata[:, 0] = y


def start_live_deconv(ir: np.ndarray, fs: int = config.FS):
    """Start real-time deconvolution with given impulse response."""
    if _stream["input"] is not None:
        stop_live_deconv()

    print("Starting live deconvolution...")

    inv_fir = compute_inverse_fir(ir, config.IMPULSE_LENGTH)
    fir_state = np.zeros(len(inv_fir) - 1)

    _stream["inverse_fir"] = inv_fir
    _stream["fir_state"] = fir_state

    _stream["input"] = sd.Stream(
        samplerate=fs,
        blocksize=config.LIVE_FRAME_SIZE,
        channels=1,
        dtype='float32',
        callback=audio_callback
    )
    _stream["input"].start()
    print("Mic → Deconv → Speaker is live.")


def stop_live_deconv():
    """Stop the real-time deconvolution stream."""
    if _stream["input"] is not None:
        print("Stopping live deconvolution...")
        _stream["input"].stop()
        _stream["input"].close()
        _stream["input"] = None
        _stream["fir_state"] = None
        _stream["inverse_fir"] = None
        print("Live deconvolution stopped.")
    else:
        print("ℹNo live stream to stop.")

