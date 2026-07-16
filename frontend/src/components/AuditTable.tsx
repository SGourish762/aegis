import { useEffect, useState } from "react";
import { getAuditRecord, listAudit } from "../api";
import type { AuditRecordDetail, AuditRecordOut } from "../types";

const PAGE_SIZE = 10;

export default function AuditTable({ refreshKey }: { refreshKey: number }) {
  const [items, setItems] = useState<AuditRecordOut[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [kind, setKind] = useState("");
  const [verdict, setVerdict] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<AuditRecordDetail | null>(null);

  useEffect(() => {
    listAudit({ kind, verdict, limit: PAGE_SIZE, offset })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, [kind, verdict, offset, refreshKey]);

  async function openDetail(id: number) {
    try {
      setSelected(await getAuditRecord(id));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <section className="card">
      <h2>Audit log</h2>
      <div className="filters">
        <select
          value={kind}
          onChange={(e) => {
            setOffset(0);
            setKind(e.target.value);
          }}
        >
          <option value="">All kinds</option>
          <option value="screen">screen</option>
          <option value="agent_run">agent_run</option>
        </select>
        <select
          value={verdict}
          onChange={(e) => {
            setOffset(0);
            setVerdict(e.target.value);
          }}
        >
          <option value="">All verdicts</option>
          <option value="allow">allow</option>
          <option value="flag">flag</option>
          <option value="block">block</option>
          <option value="deny">deny</option>
          <option value="mixed">mixed</option>
        </select>
      </div>

      {error && <p className="error">{error}</p>}

      <table className="audit-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Kind</th>
            <th>Verdict</th>
            <th>Summary</th>
            <th>Categories</th>
          </tr>
        </thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.id} onClick={() => openDetail(r.id)} className="clickable">
              <td>{new Date(r.created_at).toLocaleString()}</td>
              <td>{r.kind}</td>
              <td>{r.verdict}</td>
              <td className="summary-cell">{r.input_summary}</td>
              <td>{r.categories.join(", ")}</td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={5} className="muted">
                No audit records yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="pagination">
        <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>
          Prev
        </button>
        <span>
          {total === 0 ? 0 : offset + 1}-{Math.min(offset + PAGE_SIZE, total)} of {total}
        </span>
        <button disabled={offset + PAGE_SIZE >= total} onClick={() => setOffset(offset + PAGE_SIZE)}>
          Next
        </button>
      </div>

      {selected && (
        <div className="modal-backdrop" onClick={() => setSelected(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                Record #{selected.id} — {selected.kind}
              </h3>
              <button onClick={() => setSelected(null)}>×</button>
            </div>
            <pre className="detail-json">{JSON.stringify(selected.detail, null, 2)}</pre>
          </div>
        </div>
      )}
    </section>
  );
}
