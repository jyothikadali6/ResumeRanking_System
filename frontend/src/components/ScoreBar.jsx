export default function ScoreBar({ value }) {
  const pct = Math.max(0, Math.min(100, value ?? 0));
  const color =
    pct >= 70 ? "bg-emerald-500" : pct >= 45 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-12 text-right text-sm font-semibold tabular-nums">
        {pct.toFixed(1)}
      </span>
    </div>
  );
}
