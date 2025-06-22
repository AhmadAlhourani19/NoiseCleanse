from fastapi import FastAPI, UploadFile, File, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import uuid
from pathlib import Path
import soundfile as sf
import numpy as np
import sounddevice as sd
from typing import Optional
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from .impulse_response import run_full_ir

from Backend import config, impulse_response, offline_deconvolution, live_deconvolution, plotting

UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/temp_plots", StaticFiles(directory="temp_plots"), name="plots")


recorder = None
last_uploaded_signal = None
last_uploaded_ir = None

@app.post("/api/record/start")
def start_recording():
    global recorder
    if recorder is not None:
        return {"status": "error", "message": "Recording already in progress."}
    duration_seconds = 10
    fs = config.FS
    print("🎙️ Starting recording...")
    recorder = sd.rec(int(duration_seconds * fs), samplerate=fs, channels=1)
    return {"status": "recording started"}

@app.post("/api/record/stop")
def stop_recording():
    global recorder, last_uploaded_signal
    if recorder is None:
        return {"status": "error", "message": "No recording in progress."}

    print("⏹️ Stopping recording...")
    sd.wait()
    recorded_data = recorder
    recorder = None

    print(f"🎤 Recorded shape: {recorded_data.shape}, dtype: {recorded_data.dtype}, size: {recorded_data.size}")

    if recorded_data.size < 10:
        return {"status": "error", "message": "Recording too short or failed."}

    output_path = Path("output") / "speech_recorded.wav"
    print(f"💾 Saving to: {output_path}")
    sf.write(output_path, recorded_data, config.FS)
    last_uploaded_signal = output_path

    return {
        "status": "recorded",
        "file": str(output_path)
    }

@app.post("/api/ir/full/offline")
def run_full_ir_offline():
    try:
        output_path = impulse_response.run_full_ir()
        return {"status": "IR recorded", "output": str(output_path)}
    except Exception as e:
        print(f"IR recording failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to record impulse response.")

@app.post("/api/ir/full/live")
def run_full_ir_live():
    path = impulse_response.run_full_ir()
    ir_data, _ = sf.read(path)
    pre_ir = impulse_response.preprocess_ir(ir_data, config.FS)
    live_deconvolution.start_live_deconv(pre_ir)
    return {"status": "Impulse Response captured and live deconvolution started", "ir_file": str(path)}



# ---------------------------------------------------------------------------
#  OFFLINE  DECONVOLUTION  ENDPOINT  (plays back correctly now)
# ---------------------------------------------------------------------------
from typing import Optional
from uuid import uuid4
...

@app.post("/api/deconvolve")
async def deconvolve(
    signal: Optional[UploadFile] = File(None),
    ir:     UploadFile | None    = File(None),
    gain:   float                = Query(default=1.0)
):
    """
    Runs offline deconvolution.
    If `signal` is omitted, falls back to the WAV recorded via /api/record/stop.
    Always saves the recovered audio to output/recovered_output.wav and returns
    a RELATIVE URL that the front-end can play directly.
    """
    global last_uploaded_signal

    # -------- Locate signal WAV --------
    if signal is None:
        if last_uploaded_signal is None:
            raise HTTPException(400, "No signal uploaded or recorded.")
        signal_path = last_uploaded_signal
    else:
        signal_path = UPLOAD_DIR / f"signal_{uuid4().hex}.wav"
        with signal_path.open("wb") as f:
            shutil.copyfileobj(signal.file, f)
        last_uploaded_signal = signal_path

    sig_data, _ = sf.read(signal_path)

    # -------- Locate / preprocess IR --------
    if ir is not None:
        ir_path = UPLOAD_DIR / f"ir_{uuid4().hex}.wav"
        with ir_path.open("wb") as f:
            shutil.copyfileobj(ir.file, f)
        ir_data, _ = sf.read(ir_path)
        ir_pre = impulse_response.preprocess_ir(ir_data, config.FS)
    elif preprocessed_ir is not None:
        ir_pre = preprocessed_ir
    else:
        raise HTTPException(400, "No IR provided or preloaded.")

    # -------- Deconvolve + SAVE --------
    recovered = offline_deconvolution.offline_deconvolve(sig_data, ir_pre, config.FS, gain=gain)

    output_path = Path(config.RECOVERED_FILE)        # e.g. .../output/recovered_output.wav
    offline_deconvolution.save_output_audio(recovered, config.FS, output_path)

    # Return RELATIVE path so the browser can fetch it
    relative_url = f"/output/{output_path.name}"
    return {"status": "done", "output_file": relative_url}

@app.post("/api/record/stop")
def stop_recording():
    global recorder
    if recorder is None:
        return {"status": "error", "message": "No recording in progress."}

    sd.wait()
    recorded_data = recorder
    recorder = None

    if recorded_data.size < 10:
        return {"status": "error", "message": "Recording too short or failed."}

    output_path = Path("output") / "speech_recorded.wav"
    sf.write(output_path, recorded_data, config.FS)
    
    global last_uploaded_signal
    last_uploaded_signal = output_path

    return {
        "status": "recorded",
        "file": "output/speech_recorded.wav"
    }

@app.get("/api/plot/offline")
async def plot_offline():
    sig, fs = sf.read(config.RECOVERED_FILE)
    time_path = plotting.plot_time(sig, fs, "Recovered Signal (Time Domain)", filename="plot_time.png")
    freq_path = plotting.plot_freq(sig, fs, "Recovered Signal (Frequency Domain)", filename="plot_freq.png")
    return {
        "status": "plot generated",
        "time_plot": time_path,
        "freq_plot": freq_path
    }

@app.post("/api/live/load-ir")
async def load_ir_for_live(
    request: Request,
    ir: UploadFile = File(...)
):
    input_device = request.query_params.get("input_device")
    output_device = request.query_params.get("output_device")
    volume = request.query_params.get("volume", 1.0)

    # Convert to int or None
    input_device = int(input_device) if input_device and input_device.isdigit() else None
    output_device = int(output_device) if output_device and output_device.isdigit() else None
    volume = float(volume)

    ir_path = UPLOAD_DIR / f"live_ir_{uuid.uuid4().hex}.wav"
    with ir_path.open("wb") as f:
        shutil.copyfileobj(ir.file, f)
    data, fs = sf.read(ir_path)
    ir_pre = impulse_response.preprocess_ir(data, fs)
    try:
        live_deconvolution.start_live_deconv(ir_pre, fs, input_device, output_device, volume)
        return {"status": "live started"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}


@app.post("/api/live/start")
async def start_live():
    if live_deconvolution._stream["inverse_fir"] is not None:
        return {"status": "already running or IR loaded"}
    return {"status": "IR not loaded, please upload via /live/load-ir first"}

@app.post("/api/live/stop")
async def stop_live():
    try:
        live_deconvolution.stop_live_deconv()
        return {"status": "stopped"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

@app.get("/api/live/status")
async def live_status():
    return {"running": live_deconvolution._stream["input"] is not None}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/clear-temp")
async def clear_temp():
    for f in UPLOAD_DIR.glob("*"):
        f.unlink()
    return {"status": "temp files cleared"}

@app.get("/api/devices")
def list_audio_devices():
    import sounddevice as sd
    devices = sd.query_devices()
    return [
        {
            "index": i,
            "name": d["name"],
            "max_input_channels": d["max_input_channels"],
            "max_output_channels": d["max_output_channels"]
        }
        for i, d in enumerate(devices)
    ]
