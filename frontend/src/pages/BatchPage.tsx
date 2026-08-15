import { useState } from "react";
import { batchPredict, batchPredictDownloadUrl } from "../api/client";

interface BatchRow {
  row_index: number;
  prediction?: number | null;
  error?: string | null;
  physics_flags: { field: string; message: string; severity: string }[];
  drift_flags: { field: string; message: string }[];
}

interface BatchResponse {
  n_rows: number;
  n_succeeded: number;
  n_failed: number;
  results: BatchRow[];
  summary: { mean_prediction: number | null; min_prediction: number | null; max_prediction: number | null };
}

export default function BatchPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<BatchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await batchPredict(file));
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Batch prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  const download = async () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(batchPredictDownloadUrl(), { method: "POST", body: form });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "batch_predictions.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="card">
        <h2>Batch Processing</h2>
        <p style={{ color: "var(--text-dim)" }}>
          Upload a CSV or Excel file with columns: Cel, Hem, Lig, VM, Ash, FC,
          C%, H%, O%, N%, Size, HR, PT (Temp optional). Each row gets a
          predicted O/C plus physics and drift flags.
        </p>
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <div style={{ marginTop: "1rem", display: "flex", gap: "0.6rem" }}>
          <button className="primary" onClick={run} disabled={!file || loading}>
            {loading ? "Processing..." : "Run batch prediction"}
          </button>
          {result && (
            <button className="secondary" onClick={download}>
              Download results CSV
            </button>
          )}
        </div>
        {error && <p style={{ color: "var(--error)" }}>{error}</p>}
      </div>

      {result && (
        <div className="card">
          <h2>Summary</h2>
          <p>
            {result.n_succeeded}/{result.n_rows} rows succeeded &nbsp;|&nbsp;
            mean O/C: {result.summary.mean_prediction ?? "—"} &nbsp;|&nbsp;
            range: {result.summary.min_prediction ?? "—"} – {result.summary.max_prediction ?? "—"}
          </p>
          <table className="data-table">
            <thead><tr><th>Row</th><th>Predicted O/C</th><th>Flags</th></tr></thead>
            <tbody>
              {result.results.map((r) => (
                <tr key={r.row_index}>
                  <td>{r.row_index}</td>
                  <td>{r.error ? <span style={{ color: "var(--error)" }}>{r.error}</span> : r.prediction}</td>
                  <td>{r.physics_flags.length + r.drift_flags.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
