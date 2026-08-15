import { useState } from "react";
import FeedstockForm from "../components/FeedstockForm";
import { predict } from "../api/client";
import { DEFAULT_FEEDSTOCK } from "../types";
import type { FeedstockInput } from "../types";

interface ScenarioResult extends FeedstockInput { oc: number; }

export default function ScenarioPage() {
  const [base, setBase] = useState<FeedstockInput>(DEFAULT_FEEDSTOCK);
  const [ptRange, setPtRange] = useState<[number, number]>([400, 700]);
  const [hrRange, setHrRange] = useState<[number, number]>([5, 60]);
  const [ligRange, setLigRange] = useState<[number, number]>([15, 35]);
  const [results, setResults] = useState<ScenarioResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [best, setBest] = useState<ScenarioResult | null>(null);

  const steps = 4;
  const linspace = (a: number, b: number, n: number) =>
    Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1));

  const runScenario = async () => {
    setLoading(true);
    const pts = linspace(ptRange[0], ptRange[1], steps);
    const hrs = linspace(hrRange[0], hrRange[1], steps);
    const ligs = linspace(ligRange[0], ligRange[1], steps);
    const combos: FeedstockInput[] = [];
    for (const pt of pts) for (const hr of hrs) for (const lig of ligs) {
      combos.push({ ...base, PT: pt, HR: hr, Lig: lig });
    }
    const out: ScenarioResult[] = [];
    for (const c of combos) {
      try {
        const res = await predict(c);
        out.push({ ...c, oc: res.prediction });
      } catch { /* skip */ }
    }
    out.sort((a, b) => a.oc - b.oc);
    setResults(out.slice(0, 15));
    setBest(out[0] ?? null);
    setLoading(false);
  };

  return (
    <div>
      <div className="card">
        <h2>Scenario Simulation — minimize bio-oil O/C</h2>
        <p style={{ color: "var(--text-dim)" }}>
          Varies Pyrolysis Temperature, Heating Rate, and Lignin content over
          the ranges below (all other inputs held at the base values below) and
          ranks combinations by predicted O/C — lowest oxygen content first.
        </p>
        <h3 style={{ fontSize: "0.95rem" }}>Base feedstock (held constant except swept fields)</h3>
        <FeedstockForm values={base} onChange={setBase} />
        <div className="row-flex" style={{ marginTop: "1rem" }}>
          <label className="form-field">
            <span>PT range (°C)</span>
            <div style={{ display: "flex", gap: "0.4rem" }}>
              <input type="number" value={ptRange[0]} onChange={(e) => setPtRange([Number(e.target.value), ptRange[1]])} />
              <input type="number" value={ptRange[1]} onChange={(e) => setPtRange([ptRange[0], Number(e.target.value)])} />
            </div>
          </label>
          <label className="form-field">
            <span>HR range (°C/min)</span>
            <div style={{ display: "flex", gap: "0.4rem" }}>
              <input type="number" value={hrRange[0]} onChange={(e) => setHrRange([Number(e.target.value), hrRange[1]])} />
              <input type="number" value={hrRange[1]} onChange={(e) => setHrRange([hrRange[0], Number(e.target.value)])} />
            </div>
          </label>
          <label className="form-field">
            <span>Lignin range (wt%)</span>
            <div style={{ display: "flex", gap: "0.4rem" }}>
              <input type="number" value={ligRange[0]} onChange={(e) => setLigRange([Number(e.target.value), ligRange[1]])} />
              <input type="number" value={ligRange[1]} onChange={(e) => setLigRange([ligRange[0], Number(e.target.value)])} />
            </div>
          </label>
        </div>
        <button className="primary" style={{ marginTop: "1rem" }} onClick={runScenario} disabled={loading}>
          {loading ? "Simulating..." : `Run scenario (${steps ** 3} combinations)`}
        </button>
      </div>

      {best && (
        <div className="card">
          <h2>Best combination found</h2>
          <div className="big-number">{best.oc.toFixed(3)}</div>
          <p style={{ color: "var(--text-dim)" }}>
            PT={best.PT}°C, HR={best.HR}°C/min, Lignin={best.Lig.toFixed(1)}%
          </p>
        </div>
      )}

      {results.length > 0 && (
        <div className="card">
          <h2>Top 15 combinations (lowest predicted O/C)</h2>
          <table className="data-table">
            <thead><tr><th>#</th><th>PT (°C)</th><th>HR (°C/min)</th><th>Lignin (%)</th><th>Predicted O/C</th></tr></thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i}>
                  <td>{i + 1}</td><td>{r.PT}</td><td>{r.HR.toFixed(1)}</td>
                  <td>{r.Lig.toFixed(1)}</td><td>{r.oc.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
