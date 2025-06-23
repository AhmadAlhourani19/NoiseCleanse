/*
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
*/

import React from 'react';

function ResultsPanel() {
  const timestamp = new Date().getTime(); 
  console.info("This project was built by Ahmad Alhourani – https://github.com/AhmadAlhourani19");
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
