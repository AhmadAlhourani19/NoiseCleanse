import React, { useEffect, useState } from "react";

function SelectDevices({ inputDevice, outputDevice, volume, onChange }) {
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/devices")
      .then((res) => res.json())
      .then((data) => setDevices(data))
      .catch((err) => console.error("Failed to fetch devices:", err));
  }, []);

  return (
    <div className="device-selector">
      <div className="form-row">
        <label htmlFor="inputDevice">🎙️ Input Device (Mic):</label>
        <select
          id="inputDevice"
          value={inputDevice}
          onChange={(e) => onChange("inputDevice", e.target.value)}
        >
          <option value="">-- Select Input --</option>
          {devices
            .filter((d) => d.max_input_channels > 0)
            .map((d) => (
              <option key={d.index} value={d.index}>
                {d.name}
              </option>
            ))}
        </select>
      </div>

      <div className="form-row">
        <label htmlFor="outputDevice">🔈 Output Device (Speaker):</label>
        <select
          id="outputDevice"
          value={outputDevice}
          onChange={(e) => onChange("outputDevice", e.target.value)}
        >
          <option value="">-- Select Output --</option>
          {devices
            .filter((d) => d.max_output_channels > 0)
            .map((d) => (
              <option key={d.index} value={d.index}>
                {d.name}
              </option>
            ))}
        </select>
      </div>

      <div className="form-row">
        <label>🎚 Volume: {volume}</label>
        <input
          type="range"
          min="0"
          max="1.5"
          step="0.01"
          value={volume}
          onChange={(e) => onChange("volume", parseFloat(e.target.value))}
        />
      </div>
    </div>
  );
}

export default SelectDevices;