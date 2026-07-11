import { useState } from 'react';

interface Finding {
  resource_id: string;
  resource_type: string;
  issue: string;
  severity: string;
  estimated_monthly_savings_usd: number;
  fix_recommendation: string;
}

interface FindingsDashboardProps {
  findings: Finding[];
  summary: {
    total_resources_scanned: number;
    total_issues_found: number;
    total_estimated_monthly_savings_usd: number;
  };
}

const SEVERITY_STYLES: Record<string, { badge: string; row: string; label: string; order: number }> = {
  CRITICAL: { badge: 'bg-red-500/20 text-red-400 border border-red-500/30',     row: 'hover:bg-red-500/5',    label: 'Critical', order: 0 },
  HIGH:     { badge: 'bg-orange-500/20 text-orange-400 border border-orange-500/30', row: 'hover:bg-orange-500/5', label: 'High',     order: 1 },
  MEDIUM:   { badge: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30', row: 'hover:bg-yellow-500/5', label: 'Medium',   order: 2 },
  LOW:      { badge: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',   row: 'hover:bg-blue-500/5',   label: 'Low',      order: 3 },
};

function getSeverityStyle(severity: string) {
  return SEVERITY_STYLES[severity?.toUpperCase()] ?? SEVERITY_STYLES['LOW'];
}

type SortKey = 'severity' | 'savings' | 'resource_type';
type FilterKey = 'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export default function FindingsDashboard({ findings, summary }: FindingsDashboardProps) {
  const [expanded, setExpanded] = useState<number | null>(null);
  const [filter, setFilter] = useState<FilterKey>('ALL');
  const [sort, setSort] = useState<SortKey>('severity');

  const filtered = findings
    .filter(f => filter === 'ALL' || f.severity?.toUpperCase() === filter)
    .sort((a, b) => {
      if (sort === 'severity') {
        const aOrder = getSeverityStyle(a.severity).order;
        const bOrder = getSeverityStyle(b.severity).order;
        return aOrder - bOrder;
      }
      if (sort === 'savings') return b.estimated_monthly_savings_usd - a.estimated_monthly_savings_usd;
      if (sort === 'resource_type') return a.resource_type.localeCompare(b.resource_type);
      return 0;
    });

  const filterOptions: FilterKey[] = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

  const countFor = (key: FilterKey) =>
    key === 'ALL' ? findings.length : findings.filter(f => f.severity?.toUpperCase() === key).length;

  const exportToCSV = () => {
    const headers = ['Resource ID', 'Resource Type', 'Severity', 'Issue', 'Monthly Savings (USD)', 'Fix Recommendation'];
    const rows = findings.map(f => [
      f.resource_id,
      f.resource_type,
      f.severity,
      `"${f.issue.replace(/"/g, '""')}"`,
      f.estimated_monthly_savings_usd,
      `"${f.fix_recommendation.replace(/"/g, '""')}"`
    ]);
    
    const csvContent = "data:text/csv;charset=utf-8," 
      + headers.join(",") + "\n" 
      + rows.map(e => e.join(",")).join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `finops_report_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Summary stat cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#111113] border border-zinc-800 rounded-xl p-4 hover:border-purple-500/30 transition-colors">
          <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Resources Scanned</p>
          <p className="text-3xl font-bold text-zinc-100 mt-1">{summary.total_resources_scanned}</p>
        </div>
        <div className="bg-[#111113] border border-zinc-800 rounded-xl p-4 hover:border-red-500/30 transition-colors">
          <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Issues Found</p>
          <p className="text-3xl font-bold text-red-400 mt-1">{summary.total_issues_found}</p>
        </div>
        <div className="bg-[#111113] border border-zinc-800 rounded-xl p-4 hover:border-green-500/30 transition-colors">
          <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Monthly Savings</p>
          <p className="text-3xl font-bold text-green-400 mt-1">
            ${summary.total_estimated_monthly_savings_usd?.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Findings table */}
      <div className="bg-[#111113] border border-zinc-800 rounded-2xl shadow-xl overflow-hidden">
        {/* Table header bar */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800/80 gap-3 flex-wrap">
          <div className="flex items-center gap-4">
            <div>
              <h3 className="text-base font-semibold text-zinc-100">Findings</h3>
              <p className="text-xs text-zinc-500 mt-0.5">{filtered.length} of {findings.length} shown</p>
            </div>
            <button
              onClick={exportToCSV}
              className="hidden sm:flex items-center gap-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium py-1.5 px-3 rounded-lg transition-all"
              title="Export all findings to CSV"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              Export CSV
            </button>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Severity filter pills */}
            <div className="flex gap-1.5 flex-wrap">
              {filterOptions.map(opt => {
                const count = countFor(opt);
                const isActive = filter === opt;
                const style = opt !== 'ALL' ? getSeverityStyle(opt) : null;
                return (
                  <button
                    key={opt}
                    id={`filter-${opt.toLowerCase()}`}
                    onClick={() => setFilter(opt)}
                    className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                      isActive
                        ? style ? style.badge : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                        : 'bg-zinc-800/50 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300'
                    }`}
                  >
                    {opt === 'ALL' ? 'All' : SEVERITY_STYLES[opt].label} ({count})
                  </button>
                );
              })}
            </div>

            {/* Sort */}
            <select
              id="sort-findings"
              value={sort}
              onChange={e => setSort(e.target.value as SortKey)}
              className="text-xs bg-zinc-800/70 border border-zinc-700 rounded-lg px-3 py-1.5 text-zinc-300 focus:outline-none focus:border-purple-500 transition-colors"
            >
              <option value="severity">Sort: Severity</option>
              <option value="savings">Sort: Savings</option>
              <option value="resource_type">Sort: Resource Type</option>
            </select>
          </div>
        </div>

        {/* Rows */}
        <div className="divide-y divide-zinc-800/50">
          {filtered.length === 0 && (
            <div className="py-12 text-center text-zinc-500 text-sm">
              No findings match the current filter.
            </div>
          )}
          {filtered.map((f, i) => {
            const style = getSeverityStyle(f.severity);
            const isOpen = expanded === i;
            return (
              <div key={i} className={`transition-colors ${style.row}`}>
                {/* Row summary */}
                <button
                  id={`finding-row-${i}`}
                  onClick={() => setExpanded(isOpen ? null : i)}
                  className="w-full flex items-center gap-4 px-5 py-4 text-left group"
                >
                  {/* Severity badge */}
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-md flex-shrink-0 ${style.badge}`}>
                    {style.label}
                  </span>

                  {/* Resource info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-zinc-200 truncate">{f.issue}</p>
                    <p className="text-xs text-zinc-500 mt-0.5 truncate">
                      {f.resource_type} · <span className="font-mono">{f.resource_id}</span>
                    </p>
                  </div>

                  {/* Savings */}
                  {f.estimated_monthly_savings_usd > 0 && (
                    <span className="text-sm font-semibold text-green-400 flex-shrink-0">
                      ${f.estimated_monthly_savings_usd.toFixed(2)}/mo
                    </span>
                  )}

                  {/* Expand chevron */}
                  <svg
                    className={`w-4 h-4 text-zinc-600 group-hover:text-zinc-400 flex-shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Expanded fix recommendation */}
                {isOpen && (
                  <div className="px-5 pb-5 pt-1 animate-fadeIn">
                    <div className="bg-[#09090B] border border-zinc-700/50 rounded-xl p-4">
                      <p className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2">
                        Fix Recommendation
                      </p>
                      <p className="text-sm text-zinc-300 leading-relaxed">{f.fix_recommendation}</p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
