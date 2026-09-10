export default function SkillPills({ skills, tone = "green" }) {
  if (!skills || skills.length === 0) {
    return <span className="text-xs text-slate-400">—</span>;
  }
  const toneClasses =
    tone === "green"
      ? "bg-emerald-100 text-emerald-700"
      : "bg-rose-100 text-rose-700";
  return (
    <div className="flex flex-wrap gap-1">
      {skills.map((s) => (
        <span
          key={s}
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${toneClasses}`}
        >
          {s}
        </span>
      ))}
    </div>
  );
}
