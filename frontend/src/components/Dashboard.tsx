import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getStats } from "../api";
import type { StatsResponse } from "../types";

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat-tile">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function Dashboard({ refreshKey }: { refreshKey: number }) {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, [refreshKey]);

  if (error) return <p className="error">{error}</p>;
  if (!stats) return <p>Loading stats…</p>;

  const categoryData = Object.entries(stats.category_breakdown).map(([category, count]) => ({
    category,
    count,
  }));

  const tooltipStyle = {
    background: "var(--bg-raised)",
    border: "1px solid var(--border-strong)",
    borderRadius: 8,
    fontSize: 13,
    color: "var(--text)",
  };

  return (
    <section className="card">
      <h2>Dashboard</h2>
      <div className="stat-row">
        <StatTile label="Total decisions" value={String(stats.total)} />
        <StatTile label="Block rate (screen)" value={`${(stats.block_rate * 100).toFixed(1)}%`} />
        <StatTile label="Screened" value={String(stats.by_kind.screen ?? 0)} />
        <StatTile label="Agent runs" value={String(stats.by_kind.agent_run ?? 0)} />
      </div>

      <div className="chart-grid">
        <div>
          <h3>Decisions over time</h3>
          {stats.time_series.length === 0 ? (
            <p className="muted">No activity yet — submit something in the tester above.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={stats.time_series}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="date" stroke="var(--muted)" fontSize={12} />
                <YAxis allowDecimals={false} stroke="var(--muted)" fontSize={12} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="count" name="Total" stroke="var(--text-dim)" strokeWidth={2} />
                <Line type="monotone" dataKey="blocked" name="Blocked" stroke="var(--danger)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div>
          <h3>Category breakdown</h3>
          {categoryData.length === 0 ? (
            <p className="muted">No flagged categories yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={categoryData} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" allowDecimals={false} stroke="var(--muted)" fontSize={12} />
                <YAxis dataKey="category" type="category" width={140} stroke="var(--muted)" fontSize={12} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" fill="var(--accent)" radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </section>
  );
}
