// src/api/noiseCleanseAPI.js

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const buildUrl = (path) => `${BASE_URL}${path}`;

async function postForm(path, formData) {
  const response = await fetch(buildUrl(path), {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const msg = await response.text();
    throw new Error(`Request failed (${response.status}): ${msg}`);
  }
  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

async function postJson(path, payload = {}) {
  const response = await fetch(buildUrl(path), {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const msg = await response.text();
    throw new Error(`Request failed (${response.status}): ${msg}`);
  }
  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

async function getJson(path) {
  const response = await fetch(buildUrl(path));
  if (!response.ok) {
    throw new Error(`GET ${path} failed: ${response.status}`);
  }
  return response.json();
}

// -----------------------------
// IR related
// -----------------------------
export async function prepareIR(irFile) {
  const form = new FormData();
  form.append("ir", irFile);
  return postForm("/api/prepare-ir", form);
}

export async function recordFullIROffline() {
  return postJson("/api/ir/full/offline");
}

export async function recordFullIRLive() {
  return postJson("/api/ir/full/live");
}

// -----------------------------
// Deconvolution (Offline)
// -----------------------------
export async function offlineDeconvolve(signalFile, irFile) {
  const form = new FormData();
  form.append("signal", signalFile);
  form.append("ir", irFile);
  return postForm("/api/deconvolve", form);
}

export async function fetchOfflinePlots() {
  return getJson("/api/plot/offline");
}

// -----------------------------
// Live Deconvolution
// -----------------------------
export async function startLive(irFile) {
  const form = new FormData();
  form.append("ir", irFile);
  return postForm("/api/live/load-ir", form);
}

export async function stopLive() {
  return postJson("/api/live/stop");
}

export async function liveStatus() {
  return getJson("/api/live/status");
}

// -----------------------------
// Recording
// -----------------------------
export async function startRecording() {
  return postJson("/api/record/start");
}

export async function stopRecording() {
  return postJson("/api/record/stop");
}

// -----------------------------
// Utility / Dev
// -----------------------------
export async function resetBackend() {
  return postJson("/api/reset");
}

export async function recordFullImpulseResponse() {
  const response = await fetch("http://localhost:8000/api/ir/full/offline", {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to record impulse response");
  }
  return await response.json();
}
