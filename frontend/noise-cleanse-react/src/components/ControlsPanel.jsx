import React, { useState } from 'react';
import AudioUploader from './AudioUploader';
import SelectDevices from './SelectDevices';
import {
  startRecording,
  stopRecording,
  offlineDeconvolve,
  fetchOfflinePlots,
  startLive,
  stopLive,
  recordFullImpulseResponse,
} from '../api/noiseCleanseAPI';

function ControlsPanel({ setTimePlot, setFreqPlot, setShowResults }) {
  const [signalFile, setSignalFile] = useState(null);
  const [irFile, setIrFile] = useState(null);
  const [recording, setRecording] = useState(false);
  const [liveRunning, setLiveRunning] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [inputDevice, setInputDevice] = useState('');
  const [outputDevice, setOutputDevice] = useState('');
  const [volume, setVolume] = useState(1.0);

  const handleDeviceChange = (field, value) => {
    if (field === 'inputDevice') setInputDevice(value);
    else if (field === 'outputDevice') setOutputDevice(value);
    else if (field === 'volume') setVolume(value);
  };

  const handleRecord = async () => {
    try {
      if (!recording) {
        await startRecording();
        setRecording(true);
        setFeedback('Recording… click again to stop.');
      } else {
        const res = await stopRecording();
        setRecording(false);
        setSignalFile(null);
        setFeedback('Recording saved.');
        const recordedBlob = await fetch(res.file).then(r => r.blob());
        const recordedFile = new File([recordedBlob], 'recorded.wav', { type: 'audio/wav' });
        setSignalFile(recordedFile);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleOfflineDeconv = async () => {
    if (!signalFile) {
      setFeedback('Please provide a signal file.');
      return;
    }
    try {
      setFeedback('Running offline deconvolution…');
      const res = await offlineDeconvolve(signalFile, irFile);
      const plots = await fetchOfflinePlots();
      setTimePlot(plots.time_plot);
      setFreqPlot(plots.freq_plot);
      setShowResults(true);
      setFeedback('Offline deconvolution complete!');
    } catch (err) {
      console.error(err);
      setFeedback('Offline deconvolution failed.');
    }
  };

  const handleLiveToggle = async () => {
    try {
      if (!liveRunning) {
        if (!irFile) {
          setFeedback('Please select an IR file first.');
          return;
        }
        const res = await startLive(irFile, Number(inputDevice), Number(outputDevice), volume);
        if (res.status === 'live started') {
          setLiveRunning(true);
          setFeedback('Live deconvolution is running.');
        } else {
          setFeedback(res.reason || 'Failed to start live deconvolution.');
        }
      } else {
        await stopLive();
        setLiveRunning(false);
        setFeedback('Live deconvolution stopped.');
      }
    } catch (err) {
      console.error(err);
      setFeedback('Live deconvolution error.');
    }
  };

  const handleRecordFullIR = async () => {
    try {
      alert("Recording impulse response. Please stay quiet during playback...");
      const result = await recordFullImpulseResponse();
      alert(result.status || "Impulse response recorded!");
    } catch (error) {
      console.error("Recording IR failed:", error);
      alert("Failed to record impulse response.");
    }
  };

  return (
    <section className="panel controls-panel">
      <h2>Controls</h2>

      <div className="form-row drop-area" id="dropArea" onClick={() => document.getElementById("signalFile").click()}>
        <label htmlFor="signalFile">Signal</label>
        <div className="drop-message">Drag & Drop audio here<br />or click to upload</div>
        <AudioUploader label="" id="signalFile" onFileSelect={setSignalFile} />
      </div>

      <div className="form-row drop-area" id="irDropArea" onClick={() => document.getElementById("irFile").click()}>
        <label htmlFor="irFile">Impulse Response</label>
        <div className="drop-message">Drag & Drop IR here<br />or click to upload</div>
        <AudioUploader label="" id="irFile" onFileSelect={setIrFile} />
      </div>
      <div className="buttons-row">
        <button className="btn-record" onClick={handleRecord}>{recording ? '⏹ Stop' : '● Record'}</button>
        <button
          className="btn-save"
          onClick={async () => {
            try {
              const res = await fetch("http://localhost:8000/output/speech_recorded.wav");
              const blob = await res.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "speech_recorded.wav";
              document.body.appendChild(a);
              a.click();
              a.remove();
              setFeedback("Speech recording saved.");
            } catch (err) {
              console.error(err);
              setFeedback("Failed to save speech recording.");
            }
          }}
        >
          💾 Save Speech
        </button>
      </div>
      <div className="buttons-row">
        <button className="btn-deconv" onClick={handleOfflineDeconv}>⚙️ Deconvolve</button>
        <button
          className="btn-save"
          onClick={async () => {
            try {
              const res = await fetch("http://localhost:8000/output/recovered_output.wav");
              const blob = await res.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "recovered_output.wav";
              document.body.appendChild(a);
              a.click();
              a.remove();
              setFeedback("Recovered output saved.");
            } catch (err) {
              console.error(err);
              setFeedback("Failed to save recovered output.");
            }
          }}
        >
          💾 Save
        </button>
      </div>
      <div className="buttons-row">
        <button className="btn-play" onClick={() => {
          const audio = new Audio("http://localhost:8000/output/recovered_output.wav");
          audio.play().catch(err => {
            console.error("Playback error:", err);
            alert("Failed to play audio.");
          });
        }}>▶️ Play</button>
        <button className="btn-view" onClick={() => setShowResults(prev => !prev)}>📊 View Graphs</button>
      </div>
      <div className="buttons-row">
        <button className="btn btn-ir" onClick={handleRecordFullIR}>
          🎤 Record Impulse Response
        </button>
         <button
          className="btn-save"
          onClick={async () => {
            try {
              const res = await fetch("http://localhost:8000/output/impulse_response.wav");
              const blob = await res.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "impulse_response.wav";
              document.body.appendChild(a);
              a.click();
              a.remove();
              setFeedback("Impulse response saved.");
            } catch (err) {
              console.error(err);
              setFeedback("Failed to save impulse response.");
            }
          }}
        >
          💾 Save IR
        </button>
        <button className="btn-live" onClick={handleLiveToggle}>
          {liveRunning ? '⏹ Stop Live Deconvolution' : '🔴 Start Live Deconvolution'}
        </button>
      </div>
      <SelectDevices
        inputDevice={inputDevice}
        outputDevice={outputDevice}
        volume={volume}
        onChange={handleDeviceChange}
      />
      <div className="feedback">{feedback}</div>
    </section>
  );
}

export default ControlsPanel;