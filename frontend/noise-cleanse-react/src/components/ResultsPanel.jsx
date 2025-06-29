import React from 'react';

function ResultsPanel() {
  const timestamp = new Date().getTime(); 

  return (
    <div className="results-panel">
      <div className="plot-container">
        <h3>Time Domain</h3>
        <img
          src={`http://localhost:8000/temp_plots/plot_time.png?t=${timestamp}`}
          alt="Time Domain Plot"
          className="plot-image"
        />
      </div>
      <div className="plot-container">
        <h3>Frequency Domain</h3>
        <img
          src={`http://localhost:8000/temp_plots/plot_freq.png?t=${timestamp}`}
          alt="Frequency Domain Plot"
          className="plot-image"
        />
      </div>
    </div>
  );
}

export default ResultsPanel;