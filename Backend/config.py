# noise_cleanse/config.py

import os

# === Sampling & Sweep ===
FS = 44100  # Sampling rate (Hz)
SWEEP_DURATION = 10  # Sweep duration in seconds
FREQ_START = 20      # Sweep start frequency (Hz)
FREQ_END = 20000     # Sweep end frequency (Hz)

# === IR Parameters ===
IR_FADE_SECONDS = 0.05     # Fade-in/out duration for sweep
IR_HIGH_PASS = 150         # High-pass filter cutoff for IR (Hz)
IR_LOW_PASS = 6000         # Low-pass filter cutoff for IR (Hz)
IMPULSE_LENGTH = 256       # Target length for FIR impulse response

# === Offline Deconvolution ===
OFFLINE_LAMBDA = 5.0       # Default spectral division bias (Tikhonov)
AUTO_LAMBDA_FACTOR = 0.01  # Scaling factor for auto-tuned lambda
NOTCH_THRESHOLD = 0.2      # Fraction of peak to consider for notching
NUM_NOTCH_PASSES = 2       # How many passes of notch filtering

# === MMSE Parameters ===
DEFAULT_NOISE_FLOOR = 1e-4  # Relative noise level used in MMSE filter

# === Live Deconvolution ===
LIVE_FRAME_SIZE = 1024
LIVE_INV_LAMBDA = 1e-3      # Default Tikhonov lambda for FIR inversion
LIVE_GAIN = 4.0             # Output gain multiplier

# In Backend/config.py
REG_LAMBDA = 0.01

# === Paths ===
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
SWEEP_FILE = os.path.join(OUTPUT_DIR, 'sine_sweep.wav')
RESPONSE_FILE = os.path.join(OUTPUT_DIR, 'room_recorded.wav')
IR_FILE = os.path.join(OUTPUT_DIR, 'impulse_response.wav')
SPEECH_FILE = os.path.join(OUTPUT_DIR, 'speech_recorded.wav')
RECOVERED_FILE = os.path.join(OUTPUT_DIR, 'recovered_output.wav')

# === Plotting ===
PLOT_DPI = 100

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)