export default function RankBadge({ rank }) {
  const styles = {
    1: "bg-yellow-400 text-yellow-900",
    2: "bg-slate-300 text-slate-800",
    3: "bg-amber-600 text-amber-50",
  };
  const cls = styles[rank] || "bg-slate-100 text-slate-600";
  return (
    <span
      className={`inline-flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${cls}`}
    >
      {rank}
    </span>
  );
}
