import { Fragment, useState } from "react";
import RankBadge from "./RankBadge.jsx";
import ScoreBar from "./ScoreBar.jsx";
import SkillPills from "./SkillPills.jsx";

export default function ResultsTable({ results }) {
  const [expanded, setExpanded] = useState(null);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr className="text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <th className="px-4 py-3">Rank</th>
            <th className="px-4 py-3">Resume</th>
            <th className="px-4 py-3">Match score</th>
            <th className="px-4 py-3">Matched skills</th>
            <th className="px-4 py-3">Missing skills</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {results.map((r) => (
            <Fragment key={r.id}>
              <tr className="align-top hover:bg-slate-50">
                <td className="px-4 py-4">
                  <RankBadge rank={r.rank} />
                </td>
                <td className="px-4 py-4 font-medium text-slate-800">
                  {r.filename}
                  <div className="mt-1 text-xs text-slate-400">
                    semantic {r.semantic_score?.toFixed(1)} · skills{" "}
                    {r.skill_score?.toFixed(1)}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <ScoreBar value={r.score} />
                </td>
                <td className="px-4 py-4 max-w-xs">
                  <SkillPills skills={r.matched_skills} tone="green" />
                </td>
                <td className="px-4 py-4 max-w-xs">
                  <SkillPills skills={r.missing_skills} tone="rose" />
                </td>
                <td className="px-4 py-4">
                  <button
                    onClick={() =>
                      setExpanded(expanded === r.id ? null : r.id)
                    }
                    className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                  >
                    {expanded === r.id ? "Hide" : "Why?"}
                  </button>
                </td>
              </tr>
              {expanded === r.id && (
                <tr className="bg-indigo-50/40">
                  <td colSpan={6} className="px-4 py-3 text-sm text-slate-700">
                    <span className="font-semibold text-slate-800">
                      Assessment:{" "}
                    </span>
                    {r.reasoning || "No reasoning available."}
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
