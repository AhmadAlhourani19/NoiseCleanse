import React from 'react';

function AudioUploader({ label, id, accept = '.wav,.mp3', onFileSelect }) {
  const handleChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="form-row">
      <label htmlFor={id}>{label}</label>
      <input
        type="file"
        id={id}
        accept={accept}
        onChange={handleChange}
      />
    </div>
  );
}

export default AudioUploader;