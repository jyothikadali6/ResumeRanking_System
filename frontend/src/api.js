// Thin API client. Uses the Vite dev proxy (/api -> http://localhost:8000).
const BASE = "/api";

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
