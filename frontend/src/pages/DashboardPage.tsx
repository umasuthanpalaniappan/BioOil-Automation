import { useEffect, useState } from "react";
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Legend, LineChart, Line,
} from "recharts";
import FeedstockForm from "../components/FeedstockForm";
import { api, predict } from "../api/client";
import { DEFAULT_FEEDSTOCK } from "../types";
import type { FeedstockInput } from "../types";

interface Diagnostics { target: string; best_model: string; y_test: number[]; y_pred: number[]; }

export default function DashboardPage() {
  const [diag, setDiag] = useState<Diagnostics | null>(null);
  const [ptSweep, setPtSweep] = useState<{ pt: number; oc: number }[]>([]);
  const [baseFeedstock, setBaseFeedstock] = useState<FeedstockInput>(DEFAULT_FEEDSTOCK);
  const [loadingSweep, setLoadingSweep] = useState(false);

  useEffect(() => {
    api.get("/diagnostics/O_C").then((r) => setDiag(r.data)).catch(() => setDiag(null));
  }, []);

  const runSweep = async (feedstock: FeedstockInput) => {
    setLoadingSweep(true);
    const points: { pt: number; oc: number }[] = [];
    for (let pt = 300; pt <= 800; pt += 50) {
      try {
        const res = await predict({ ...feedstock, PT: pt });
        points.push({ pt, oc: res.prediction });
      } catch {
        /* skip failed point */
      }
    }
    setPtSweep(points);
    setLoadingSweep(false);
  };

  const scatterData = diag ? diag.y_test.map((y, i) => ({ actual: y, predicted: diag.y_pred[i] })) : [];
  const residualData = diag
    ? diag.y_test.map((y, i) => ({ actual: y, residual: diag.y_pred[i] - y }))
    : [];

  return (
    <div>
      <div className="card">
        <h2>Predicted vs Actual (held-out test set, {diag?.best_model ?? "—"})</h2>
        {diag ? (
          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#2a3a48" />
              <XAxis type="number" dataKey="actual" name="Actual O/C" stroke="#9db0bf" />
              <YAxis type="number" dataKey="predicted" name="Predicted O/C" stroke="#9db0bf" />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={{ background: "#16212c", border: "1px solid #2a3a48" }} />
              <Scatter data={scatterData} fill="#4fb8a3" />
            </ScatterChart>
          </ResponsiveContainer>
        ) : <p className="flag-list-empty">Diagnostics unavailable — train models first.</p>}
      </div>

      <div className="card">
        <h2>Residuals (predicted − actual)</h2>
        {diag && (
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#2a3a48" />
              <XAxis type="number" dataKey="actual" name="Actual O/C" stroke="#9db0bf" />
              <YAxis type="number" dataKey="residual" name="Residual" stroke="#9db0bf" />
              <Tooltip contentStyle={{ background: "#16212c", border: "1px solid #2a3a48" }} />
              <Scatter data={residualData} fill="#e0a72e" />
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card">
        <h2>Live sensitivity: Pyrolysis Temperature vs predicted O/C</h2>
        <p style={{ color: "var(--text-dim)", fontSize: "0.85rem" }}>
          Sweeps PT from 300–800°C holding all other inputs below constant.
        </p>
        <FeedstockForm values={baseFeedstock} onChange={setBaseFeedstock} />
        <button className="secondary" style={{ marginTop: "0.75rem" }} onClick={() => runSweep(baseFeedstock)} disabled={loadingSweep}>
          {loadingSweep ? "Sweeping..." : "Run sensitivity sweep"}
        </button>
        {ptSweep.length > 0 && (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={ptSweep} margin={{ top: 20, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#2a3a48" />
              <XAxis dataKey="pt" stroke="#9db0bf" label={{ value: "PT (°C)", position: "insideBottom", offset: -5 }} />
              <YAxis stroke="#9db0bf" label={{ value: "Predicted O/C", angle: -90, position: "insideLeft" }} />
              <Tooltip contentStyle={{ background: "#16212c", border: "1px solid #2a3a48" }} />
              <Legend />
              <Line type="monotone" dataKey="oc" stroke="#4fb8a3" name="Predicted O/C" dot />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
