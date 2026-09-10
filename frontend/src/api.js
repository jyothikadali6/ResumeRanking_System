// Thin API client.
// - Dev: VITE_API_URL is unset, so BASE = "/api" and the Vite proxy forwards
//   to http://localhost:8000 (see vite.config.js).
// - Prod (Vercel): set VITE_API_URL to the backend origin, e.g.
//   https://resume-ranker-api.onrender.com  -> BASE becomes ".../api".
const API_ROOT = import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "";
const BASE = `${API_ROOT}/api`;

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function health() {
  return handle(await fetch(`${BASE}/health`));
}

export async function createJob(title, description) {
  return handle(
    await fetch(`${BASE}/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description }),
    })
  );
}

export async function uploadResumes(jobId, files) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  return handle(
    await fetch(`${BASE}/jobs/${jobId}/resumes`, {
      method: "POST",
      body: form,
    })
  );
}

export async function rankJob(jobId) {
  return handle(await fetch(`${BASE}/jobs/${jobId}/rank`, { method: "POST" }));
}
