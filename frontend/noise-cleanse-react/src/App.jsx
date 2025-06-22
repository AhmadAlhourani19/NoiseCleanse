import React, { useState, useEffect } from 'react';
import ControlsPanel from './components/ControlsPanel';
import ResultsPanel from './components/ResultsPanel';
import './components/style.css';

function App() {
  const [timePlot, setTimePlot] = useState('');
  const [freqPlot, setFreqPlot] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark-mode' : '';
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app">
      <header className="site-header">
        <div className="header-left">
          <h1>Noise Cleanse</h1>
          <p className="tagline">Clean your audio with one click</p>
        </div>

        <div className="dark-mode-toggle">
          <label className="switch">
            <input
              type="checkbox"
              checked={theme === 'dark'}
              onChange={toggleTheme}
            />
            <span className="slider"></span>
          </label>
          <span className="switch-label">{theme === 'dark' ? '🌙 Dark' : '☀️ Light'}</span>
        </div>
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
