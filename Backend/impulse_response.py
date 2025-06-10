# noise_cleanse/impulse_response.py

import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, filtfilt
from scipy.fft import fft, ifft
from scipy.io import wavfile

from . import config
from .audio_io import save_audio

def generate_sweep(fs: int, duration: float, f1: float, f2: float) -> np.ndarray:
    """Generate a logarithmic sine sweep and apply fade in/out."""
    print("Generating sweep...")
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    sweep = np.sin(2 * np.pi * f1 * (duration / np.log(f2 / f1)) * 
                   (np.exp(t * np.log(f2 / f1) / duration) - 1))

    # Fade-in/out
    fade_len = int(config.IR_FADE_SECONDS * fs)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    sweep[:fade_len] *= fade_in
    sweep[-fade_len:] *= fade_out

    sweep /= np.max(np.abs(sweep) + 1e-9)
    save_audio(config.SWEEP_FILE, sweep, fs)
    return sweep


def extract_ir(recorded: np.ndarray, sweep: np.ndarray, fs: int) -> np.ndarray:
    """Extract impulse response from recorded response and sweep."""
    print("Extracting impulse response via deconvolution...")
    N = len(recorded) + len(sweep) - 1
    R = fft(recorded, N)
    S = fft(sweep, N)
    IR = np.real(ifft(R / (S + 1e-9)))

    # Trim after peak
    peak_idx = np.argmax(np.abs(IR))
    end_idx = min(len(IR), peak_idx + int(0.5 * fs))  # up to 0.5 sec
    ir = IR[peak_idx:end_idx]

    # Apply fade-out
    fade_len = int(config.IR_FADE_SECONDS * fs)
    fade = np.linspace(1, 0, fade_len)
    if len(ir) >= fade_len:
        ir[-fade_len:] *= fade

    ir = ir / (np.max(np.abs(ir)) + 1e-9)
    save_audio(config.IR_FILE, ir, fs)
    return ir


def preprocess_ir(ir: np.ndarray, fs: int, target_len: int = config.IMPULSE_LENGTH) -> np.ndarray:
    """Clean and trim IR: remove DC, HPF, trim tail, pad/cut, normalize."""
    print("Preprocessing impulse response...")

    # Remove DC offset
    ir = ir - np.mean(ir)

    # High-pass filter (20 Hz default)
    b_hp, a_hp = butter(1, 20 / (fs / 2), btype='high')
    ir = filtfilt(b_hp, a_hp, ir)

    # Trim tail after peak to when energy drops
    env = np.abs(ir)
    peak_idx = np.argmax(env)
    thresh = 0.05 * env[peak_idx]
    post = env[peak_idx:] < thresh
    end_idx = peak_idx + np.argmax(post) if np.any(post) else len(ir)
    ir = ir[peak_idx:end_idx]

    # Pad or trim to target length
    if len(ir) < target_len:
        ir = np.pad(ir, (0, target_len - len(ir)), mode='constant')
    else:
        ir = ir[:target_len]

    # Normalize
    ir = ir / (np.max(np.abs(ir)) + 1e-9)

    return ir

def run_full_ir(duration=config.SWEEP_DURATION, fs=config.FS, output_path=config.IR_FILE):
    """Play sine sweep and record it to generate impulse response."""
    print("▶ Playing sweep and recording response...")

    sweep = generate_sweep(fs, duration, config.FREQ_START, config.FREQ_END)
    recording = sd.playrec(sweep, samplerate=fs, channels=1, dtype='float32')
    sd.wait()

    recorded = recording.flatten()
    ir = extract_ir(recorded, sweep, fs)

    print("✅ IR recorded and extracted.")
    sf.write(output_path, ir, fs)
    return output_path