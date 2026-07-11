interface Finding {
  severity: string;
}

interface FindingsChartProps {
  findings: Finding[];
}

const SEVERITY_CONFIG: Record<string, { color: string; bg: string; label: string; order: number }> = {
  CRITICAL: { color: '#ef4444', bg: 'bg-red-500/20',    label: 'Critical', order: 0 },
  HIGH:     { color: '#f97316', bg: 'bg-orange-500/20', label: 'High',     order: 1 },
  MEDIUM:   { color: '#eab308', bg: 'bg-yellow-500/20', label: 'Medium',   order: 2 },
  LOW:      { color: '#3b82f6', bg: 'bg-blue-500/20',   label: 'Low',      order: 3 },
};

function DonutChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  if (total === 0) return null;

  const radius = 54;
  const stroke = 16;
  const circumference = 2 * Math.PI * radius;
  const cx = 70;
  const cy = 70;

  let offset = 0;
  const slices = data
    .filter(d => d.value > 0)
    .map(d => {
      const pct = d.value / total;
      const dash = pct * circumference;
      const gap = circumference - dash;
      const slice = { ...d, dash, gap, offset };
      offset += dash;
      return slice;
    });

  return (
    <svg viewBox="0 0 140 140" className="w-full h-full drop-shadow-lg">
      {/* Background ring */}
      <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#27272a" strokeWidth={stroke} />
      {slices.map((s, i) => (
        <circle
          key={i}
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={s.color}
          strokeWidth={stroke}
          strokeDasharray={`${s.dash} ${s.gap}`}
          strokeDashoffset={-s.offset + circumference * 0.25}
          strokeLinecap="round"
          className="transition-all duration-700"
          style={{ filter: `drop-shadow(0 0 6px ${s.color}66)` }}
        />
      ))}
      {/* Center text */}
      <text x={cx} y={cy - 6} textAnchor="middle" fill="white" fontSize="22" fontWeight="bold">
        {total}
      </text>
      <text x={cx} y={cy + 12} textAnchor="middle" fill="#a1a1aa" fontSize="9" letterSpacing="1">
        ISSUES
      </text>
    </svg>
  );
}

export default function FindingsChart({ findings }: FindingsChartProps) {
  const counts: Record<string, number> = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  findings.forEach(f => {
    const key = f.severity?.toUpperCase();
    if (key && key in counts) counts[key]++;
    else if (key) counts[key] = (counts[key] ?? 0) + 1;
  });

  const chartData = Object.entries(SEVERITY_CONFIG)
    .sort((a, b) => a[1].order - b[1].order)
    .map(([key, cfg]) => ({ label: cfg.label, value: counts[key] ?? 0, color: cfg.color }));

  return (
    <div className="bg-[#111113] border border-zinc-800 rounded-2xl p-6 shadow-xl hover:border-purple-500/30 transition-colors">
      <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-5">
        Severity Breakdown
      </h3>
      <div className="flex items-center gap-6">
        {/* Donut */}
        <div className="w-32 h-32 flex-shrink-0">
          <DonutChart data={chartData} />
        </div>

        {/* Legend */}
        <div className="flex flex-col gap-3 flex-1">
          {chartData.map(d => (
            <div key={d.label} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: d.color, boxShadow: `0 0 6px ${d.color}88` }}
                />
                <span className="text-sm text-zinc-400">{d.label}</span>
              </div>
              <span
                className="text-sm font-bold tabular-nums"
                style={{ color: d.value > 0 ? d.color : '#52525b' }}
              >
                {d.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
