import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, filtfilt, wiener
from scipy.fft import fft, ifft
from scipy.io import wavfile

from . import config
from .audio_io import save_audio

def generate_sweep(fs: int, duration: float, f1: float, f2: float) -> np.ndarray:
    print("Generating sweep...")
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    sweep = np.sin(2 * np.pi * f1 * (duration / np.log(f2 / f1)) * 
                   (np.exp(t * np.log(f2 / f1) / duration) - 1))

    fade_len = int(config.IR_FADE_SECONDS * fs)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    sweep[:fade_len] *= fade_in
    sweep[-fade_len:] *= fade_out

    sweep /= np.max(np.abs(sweep) + 1e-9)
    save_audio(config.SWEEP_FILE, sweep, fs)
    return sweep

def high_pass_filter(signal, fs, cutoff=60):
    b, a = butter(2, cutoff / (fs / 2), btype='high')
    return filtfilt(b, a, signal)

def spectral_gate(signal, threshold=0.02):
    return np.where(np.abs(signal) < threshold, 0, signal)

def extract_ir(recorded: np.ndarray, sweep: np.ndarray, fs: int) -> np.ndarray:
    print("Extracting impulse response via deconvolution...")
    N = len(recorded) + len(sweep) - 1
    R = fft(recorded, N)
    S = fft(sweep, N)
    IR = np.real(ifft(R / (S + 1e-9)))

    peak_idx = np.argmax(np.abs(IR))
    end_idx = min(len(IR), peak_idx + int(0.5 * fs))
    ir = IR[peak_idx:end_idx]

    fade_len = int(config.IR_FADE_SECONDS * fs)
    fade = np.linspace(1, 0, fade_len)
    if len(ir) >= fade_len:
        ir[-fade_len:] *= fade

    ir = ir / (np.max(np.abs(ir)) + 1e-9)
    save_audio(config.IR_FILE, ir, fs)

    return ir

def preprocess_ir(ir: np.ndarray, fs: int, target_len: int = config.IMPULSE_LENGTH) -> np.ndarray:
    print("Preprocessing impulse response...")
    ir = ir - np.mean(ir)

    b_hp, a_hp = butter(1, 20 / (fs / 2), btype='high')
    ir = filtfilt(b_hp, a_hp, ir)

    env = np.abs(ir)
    peak_idx = np.argmax(env)
    thresh = 0.05 * env[peak_idx]
    post = env[peak_idx:] < thresh
    end_idx = peak_idx + np.argmax(post) if np.any(post) else len(ir)
    ir = ir[peak_idx:end_idx]

    if len(ir) < target_len:
        ir = np.pad(ir, (0, target_len - len(ir)), mode='constant')
    else:
        ir = ir[:target_len]

    ir = ir / (np.max(np.abs(ir)) + 1e-9)

    return ir

def postprocess_audio(output: np.ndarray, fs: int) -> np.ndarray:
    print("Applying postprocessing filters...")
    output = high_pass_filter(output, fs)
    output = spectral_gate(output, threshold=0.02)
    output = wiener(output, mysize=29)
    output = output / (np.max(np.abs(output)) + 1e-9)

    return output

def run_full_ir(duration=config.SWEEP_DURATION, fs=config.FS, output_path=config.IR_FILE):
    print("Playing sweep and recording response...")
    sweep = generate_sweep(fs, duration, config.FREQ_START, config.FREQ_END)
    recording = sd.playrec(sweep, samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    recorded = recording.flatten()
    ir = extract_ir(recorded, sweep, fs)
    print("IR recorded and extracted.")
    sf.write(output_path, ir, fs)

    return output_path