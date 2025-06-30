
# NoiseCleanse

NoiseCleanse is a cross-platform desktop application built with Electron, React, and FastAPI, designed to remove background noise from audio recordings. The project includes:

* **FastAPI backend** for processing audio
* **React frontend** powered by Vite for user interaction
* **Electron wrapper** to package everything into a standalone desktop app

## Features

* Real-time noise reduction using FastAPI endpoints
* Live preview of cleaned audio in the React interface
* Desktop packaging for Windows, macOS, and Linux via Electron

---

## Prerequisites

Make sure you have the following installed on your system:

* **Python 3.9+**
* **Node.js 16+** and **npm**
* **Git**
* (Optional) **PyInstaller** for creating standalone executables

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/AhmadAlhourani19/NoiseCleanse.git
   cd NoiseCleanse
   ```
2. **Install backend dependencies**

3. **Install frontend dependencies**

   ```bash
   cd frontend/noise-cleanse-react
   npm install
   cd ../..  # back to project root
   ```

---

## Running the Backend

To start the FastAPI backend locally:

```bash
uvicorn run_backend:app --host 127.0.0.1 --port 8000

## Creating a Stand-Alone Backend Executable

If you need a single-file Windows executable (no console window):

```bash
pyinstaller run_backend.py --onefile --noconsole
```

The resulting `run_backend.exe` will be placed in the `dist/` directory.

---

## Frontend (React)

### Development

```bash
cd frontend/noise-cleanse-react
npm run dev
```

This starts the Vite dev server with hot module replacement at `http://localhost:3000`.

### Production Build

```bash
npm run build
```

Builds optimized static files into `frontend/noise-cleanse-react/dist/`.

---

## Electron App

From the project root, run:

```bash
npm install    # ensure all dependencies are up to date
npm run build  # (optional) build React assets
npm run dist   # package into a distributable .exe or installer
```

* `npm run build` here compiles your React frontend.
* `npm run dist` uses Electron Builder (or your configured packager) to create the desktop application.


## Author

This portfolio project was entirely built by **Ahmad Alhourani**.

* GitHub: [AhmadAlhourani19](https://github.com/AhmadAlhourani19)
* LinkedIn: [ahmad-alhourani-9555a72b6](https://www.linkedin.com/in/ahmad-alhourani-9555a72b6/)

Enjoy! Feel free to open issues or reach out if you have any questions.
