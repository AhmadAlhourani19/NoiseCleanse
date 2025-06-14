import React, { useState } from 'react';
import AudioUploader from './AudioUploader';
import {
  startRecording,
  stopRecording,
  offlineDeconvolve,
  fetchOfflinePlots,
  startLive,
  stopLive,
  recordFullImpulseResponse 
} from '../api/noiseCleanseAPI';

function ControlsPanel({ setTimePlot, setFreqPlot, setShowResults }) {
  const [signalFile, setSignalFile] = useState(null);
  const [irFile, setIrFile] = useState(null);
  const [recording, setRecording] = useState(false);
  const [liveRunning, setLiveRunning] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [recoveredPath, setRecoveredPath] = useState('');

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
        setFeedback('Recording saved. Ready to upload or deconvolve.');
        const recordedBlob = await fetch(res.file).then((r) => r.blob());
        const recordedFile = new File([recordedBlob], 'recorded.wav', { type: 'audio/wav' });
        setSignalFile(recordedFile);
      }
    } catch (err) {
      console.error(err);
      setFeedback('Recording error.');
    }
  };

  const handleUpload = () => {
    if (!signalFile && !irFile) {
      setFeedback('Select at least one file to upload.');
      return;
    }
    setFeedback('Files selected — ready for deconvolution.');
  };

  const handleOfflineDeconv = async () => {
    if (!signalFile) {
      setFeedback('Please provide a signal file.');
      return;
    }
    try {
      setFeedback('Running offline deconvolution…');
      const res = await offlineDeconvolve(signalFile, irFile);
      setRecoveredPath(res.output_file);
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
        setFeedback('Starting live deconvolution…');
        const res = await startLive(irFile);
        if (res.status === 'live started') {
          setLiveRunning(true);
          setFeedback('Live deconvolution is running.');
        } else {
          setFeedback(res.reason || 'Failed to start live deconvolution.');
        }
      } else {
        setFeedback('Stopping live deconvolution…');
        await stopLive();
        setLiveRunning(false);
        setFeedback('Live deconvolution stopped.');
      }
    } catch (err) {
      console.error(err);
      setFeedback('Live deconvolution error.');
    }
  };

const handlePlay = () => {
  const audio = document.createElement('audio');
  audio.src = "http://localhost:8000/output/recovered_output.wav";
  audio.play().catch((err) => {
    console.error('Playback failed:', err);
    alert('Playback failed.');
  });
};

  const handleSave = () => {
    if (!recoveredPath) {
      setFeedback('Nothing to save yet.');
      return;
    }
    const link = document.createElement('a');
    link.href = recoveredPath;
    link.download = 'recovered_output.wav';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setFeedback('Download started.');
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

      <AudioUploader label="Signal" id="signalFile" onFileSelect={setSignalFile} />
      <AudioUploader label="Impulse Response" id="irFile" onFileSelect={setIrFile} />

      {/*dropdown for preset IRs (placeholder, coming in later) */}
      <div className="form-row">
        <label htmlFor="irSelect">Select IR</label>
        <select id="irSelect" defaultValue="">
          <option value="">— choose preset —</option>
          <option value="hall">Hall</option>
          <option value="room">Room</option>
        </select>
      </div>

      {/* Row 1: Record & Upload */}
      <div className="buttons-row">
        <button className="btn-record" onClick={handleRecord}>
          {recording ? '⏹ Stop' : '● Record'}
        </button>
        <button className="btn-upload" onClick={handleUpload}>⬆️ Upload</button>
      </div>

      {/* Row 2: Offline + Live Deconvolution */}
      <div className="buttons-row">
        <button className="btn-deconv" onClick={handleOfflineDeconv}>⚙️ Offline Deconvolution</button>
        <button className="btn-live" onClick={handleLiveToggle}>
          {liveRunning ? '⏹ Stop Live Deconvolution' : '🔴 Start Live Deconvolution'}
        </button>
        <button className="btn btn-ir" onClick={handleRecordFullIR}>
          Record Impulse Response
        </button>
      </div>

      {/* Row 3: Save & Play */}
      <div className="buttons-row">
        <button className="btn-save" onClick={handleSave}>💾 Save</button>
        <button className="btn-play" onClick={handlePlay}>▶️ Play</button>
      </div>

      {/* Row 4: View Graphs */}
      <div className="buttons-row">
        <button className="btn-view" onClick={() => setShowResults((prev) => !prev)}>
          📊 View Graphs
        </button>
      </div>

      <div className="feedback">{feedback}</div>
    </section>
  );
}

export default ControlsPanel;