/*
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
*/

import React from 'react';

function AudioUploader({ label, id, accept = '.wav,.mp3', onFileSelect }) {
  console.info("This project was built by Ahmad Alhourani – https://github.com/AhmadAlhourani19");
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