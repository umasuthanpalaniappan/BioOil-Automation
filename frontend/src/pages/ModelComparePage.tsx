import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ErrorBar } from "recharts";
import FeedstockForm from "../components/FeedstockForm";
import { compareModels } from "../api/client";
import { DEFAULT_FEEDSTOCK } from "../types";
import type { FeedstockInput, ModelComparisonResponse } from "../types";

export default function ModelComparePage() {
  const [values, setValues] = useState<FeedstockInput>(DEFAULT_FEEDSTOCK);
  const [result, setResult] = useState<ModelComparisonResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      setResult(await compareModels(values));
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? Object.entries(result.predictions).map(([name, value]) => {
        const ci = result.confidence_intervals[name];
        return {
          name,
          value,
          errorRange: ci ? [value - ci[0], ci[1] - value] : [0, 0],
        };
      })
    : [];

  return (
    <div>
      <div className="card">
        <h2>Model Comparison Sandbox</h2>
        <FeedstockForm values={values} onChange={setValues} />
        <button className="primary" style={{ marginTop: "1rem" }} onClick={run} disabled={loading}>
          {loading ? "Comparing..." : "Compare all models"}
        </button>
      </div>

      {result && (
        <div className="card">
          <h2>Predicted O/C by model</h2>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData} margin={{ top: 20, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#2a3a48" />
              <XAxis dataKey="name" stroke="#9db0bf" />
              <YAxis stroke="#9db0bf" />
              <Tooltip contentStyle={{ background: "#16212c", border: "1px solid #2a3a48" }} />
              <Bar dataKey="value" fill="#4fb8a3">
                <ErrorBar dataKey="errorRange" width={4} strokeWidth={1.5} stroke="#e0a72e" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <table className="data-table">
            <thead><tr><th>Model</th><th>Predicted O/C</th><th>95% CI</th></tr></thead>
            <tbody>
              {Object.entries(result.predictions).map(([name, value]) => {
                const ci = result.confidence_intervals[name];
                return (
                  <tr key={name}>
                    <td>{name}</td>
                    <td>{value.toFixed(3)}</td>
                    <td>{ci ? `${ci[0].toFixed(3)} – ${ci[1].toFixed(3)}` : "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
