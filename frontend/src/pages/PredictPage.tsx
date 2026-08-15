import { useState } from "react";
import FeedstockForm from "../components/FeedstockForm";
import { PhysicsFlagList, DriftFlagList } from "../components/FlagList";
import { predict, explain, exportPdf } from "../api/client";
import { DEFAULT_FEEDSTOCK } from "../types";
import type { FeedstockInput, FullPredictionResponse, ExplainResponse } from "../types";

export default function PredictPage() {
  const [values, setValues] = useState<FeedstockInput>(DEFAULT_FEEDSTOCK);
  const [result, setResult] = useState<FullPredictionResponse | null>(null);
  const [explanation, setExplanation] = useState<ExplainResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runPrediction = async () => {
    setLoading(true);
    setError(null);
    try {
      const [predRes, explainRes] = await Promise.all([
        predict(values),
        explain(values).catch(() => null),
      ]);
      setResult(predRes);
      setExplanation(explainRes);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Prediction failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async () => {
    const blob = await exportPdf(values);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "prediction_report.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="card">
        <h2>Feedstock & Process Conditions</h2>
        <FeedstockForm values={values} onChange={setValues} />
        <div style={{ marginTop: "1rem", display: "flex", gap: "0.6rem" }}>
          <button className="primary" onClick={runPrediction} disabled={loading}>
            {loading ? "Predicting..." : "Predict O/C"}
          </button>
          {result && (
            <button className="secondary" onClick={downloadPdf}>
              Export PDF report
            </button>
          )}
        </div>
        {error && <p style={{ color: "var(--error)" }}>{error}</p>}
      </div>

      {result && (
        <div className="row-flex">
          <div className="card">
            <h2>Predicted O/C ratio</h2>
            <div className="big-number">{result.prediction.toFixed(3)}</div>
            {result.confidence_interval_95 && (
              <p style={{ color: "var(--text-dim)" }}>
                95% CI: {result.confidence_interval_95[0].toFixed(3)} –{" "}
                {result.confidence_interval_95[1].toFixed(3)}
              </p>
            )}
            <p><span className="pill">model: {result.model_used}</span></p>
            {result.secondary && (
              <div style={{ marginTop: "0.75rem" }}>
                <h3 style={{ fontSize: "0.95rem" }}>Secondary properties</h3>
                <p style={{ color: "var(--text-dim)", fontSize: "0.9rem" }}>
                  H/C: {result.secondary["H/C"]?.toFixed(2) ?? "—"} &nbsp;|&nbsp;
                  Calorific value: {result.secondary.Cal_value?.toFixed(2) ?? "—"} MJ/kg &nbsp;|&nbsp;
                  Oil yield: {result.secondary.Oil_yield?.toFixed(1) ?? "—"}%
                </p>
              </div>
            )}
          </div>

          <div className="card">
            <h2>Physics validation</h2>
            <PhysicsFlagList flags={result.physics_flags} />
            <h2 style={{ marginTop: "1rem" }}>Data drift check</h2>
            <DriftFlagList flags={result.drift_flags} />
          </div>
        </div>
      )}

      {explanation && (
        <div className="card">
          <h2>Explainability (SHAP)</h2>
          <p style={{ color: "var(--text-dim)" }}>{explanation.summary}</p>
          <table className="data-table">
            <thead>
              <tr><th>Feature</th><th>Value</th><th>SHAP contribution</th><th>Chemistry interpretation</th></tr>
            </thead>
            <tbody>
              {explanation.top_features.map((f) => (
                <tr key={f.feature}>
                  <td>{f.feature}</td>
                  <td>{f.value}</td>
                  <td style={{ color: f.shap_value > 0 ? "var(--error)" : "var(--accent)" }}>
                    {f.shap_value > 0 ? "+" : ""}{f.shap_value}
                  </td>
                  <td>{f.plain_language}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
