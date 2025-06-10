import React, { useState } from 'react';
import ControlsPanel from './components/ControlsPanel';
import ResultsPanel from './components/ResultsPanel';
import './components/styles.css';

function App() {
  const [timePlot, setTimePlot] = useState('');
  const [freqPlot, setFreqPlot] = useState('');
  const [showResults, setShowResults] = useState(false);

  return (
    <div className="app">
      <header className="site-header">
        <h1>Noise Cleanse</h1>
        <p className="tagline">Clean your audio with one click</p>
      </header>

      <div className={`panels ${showResults ? '' : 'single'}`}>
        <ControlsPanel
          setTimePlot={setTimePlot}
          setFreqPlot={setFreqPlot}
          setShowResults={setShowResults}
        />
        {showResults && (
          <ResultsPanel
            timePlot={timePlot}
            freqPlot={freqPlot}
          />
        )}
      </div>
    </div>
  );
}

export default App;
