import { useEffect, useState } from "react";
import { createJob, health, rankJob, uploadResumes } from "./api.js";
import ResultsTable from "./components/ResultsTable.jsx";

export default function App() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [llmOn, setLlmOn] = useState(null);

  useEffect(() => {
    health()
      .then((h) => setLlmOn(h.llm_available))
      .catch(() => setLlmOn(false));
  }, []);

  function onFilesChange(e) {
    const picked = Array.from(e.target.files || []);
    // Accumulate across selections and de-duplicate by name+size so users can
    // add files one at a time OR select several at once without losing any.
    setFiles((prev) => {
      const merged = [...prev];
      for (const f of picked) {
        const dup = merged.some(
          (m) => m.name === f.name && m.size === f.size
        );
        if (!dup) merged.push(f);
      }
      return merged;
    });
    // Reset the input so re-selecting the same file still fires onChange.
    e.target.value = "";
  }

  function removeFile(name, size) {
    setFiles((prev) => prev.filter((f) => !(f.name === name && f.size === size)));
  }

  function clearFiles() {
    setFiles([]);
  }

  async function handleRank() {
    setError("");
    if (!description.trim()) {
      setError("Please paste a job description.");
      return;
    }
    if (files.length === 0) {
      setError("Please select at least one resume PDF.");
      return;
    }

    setLoading(true);
    setResults([]);
    try {
      setStatus("Creating job…");
      const job = await createJob(title || "Untitled Job", description);

      setStatus(`Uploading ${files.length} resume(s)…`);
      await uploadResumes(job.id, files);

      setStatus("Ranking resumes (embeddings + FAISS + LLM)…");
      const res = await rankJob(job.id);
      setResults(res.results);
      setStatus(`Done. Ranked ${res.results.length} resume(s).`);
    } catch (err) {
      setError(err.message || "Something went wrong.");
      setStatus("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          AI Resume Ranker
        </h1>
        <p className="mt-1 text-slate-500">
          Upload resumes and a job description. Rank 1 = best match.
        </p>
        <div className="mt-2 text-xs">
          {llmOn === null ? (
            <span className="text-slate-400">Checking backend…</span>
          ) : llmOn ? (
            <span className="rounded-full bg-emerald-100 px-2 py-0.5 font-medium text-emerald-700">
              Ollama LLM connected
            </span>
          ) : (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 font-medium text-amber-700">
              LLM offline — using semantic + skill scoring only
            </span>
          )}
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold text-slate-800">
            1. Job description
          </h2>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Job title (optional)"
            className="mb-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Paste the full job description here…"
            rows={12}
            className="w-full resize-y rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold text-slate-800">
            2. Resumes (PDF)
          </h2>
          <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 px-4 py-10 text-center hover:border-indigo-400 hover:bg-indigo-50/30">
            <input
              type="file"
              accept="application/pdf"
              multiple
              onChange={onFilesChange}
              className="hidden"
            />
            <span className="text-sm font-medium text-slate-600">
              Click to select PDF resumes
            </span>
            <span className="mt-1 text-xs text-slate-400">
              You can select multiple files
            </span>
          </label>

          {files.length > 0 && (
            <div className="mt-4">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {files.length} file{files.length > 1 ? "s" : ""} selected
                </span>
                <button
                  onClick={clearFiles}
                  className="text-xs font-medium text-rose-500 hover:text-rose-700"
                >
                  Clear all
                </button>
              </div>
              <ul className="space-y-1 text-sm text-slate-600">
                {files.map((f) => (
                  <li
                    key={`${f.name}-${f.size}`}
                    className="flex items-center justify-between gap-2 rounded-md bg-slate-50 px-2 py-1"
                  >
                    <span className="flex items-center gap-2 truncate">
                      <span className="text-indigo-500">📄</span>
                      <span className="truncate">{f.name}</span>
                    </span>
                    <button
                      onClick={() => removeFile(f.name, f.size)}
                      className="shrink-0 text-slate-400 hover:text-rose-600"
                      title="Remove"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={handleRank}
            disabled={loading}
            className="mt-5 w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Ranking…" : "Rank resumes"}
          </button>

          {status && <p className="mt-3 text-sm text-slate-500">{status}</p>}
          {error && (
            <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">
              {error}
            </p>
          )}
        </section>
      </div>

      {results.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Ranked results
          </h2>
          <ResultsTable results={results} />
        </section>
      )}
    </div>
  );
}
