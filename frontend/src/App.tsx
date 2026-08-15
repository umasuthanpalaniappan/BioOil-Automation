import { useState } from "react";
import PredictPage from "./pages/PredictPage";
import DashboardPage from "./pages/DashboardPage";
import ScenarioPage from "./pages/ScenarioPage";
import ModelComparePage from "./pages/ModelComparePage";
import BatchPage from "./pages/BatchPage";

const TABS = [
  { key: "predict", label: "Predict", component: PredictPage },
  { key: "dashboard", label: "Dashboard", component: DashboardPage },
  { key: "scenario", label: "Scenario Simulation", component: ScenarioPage },
  { key: "compare", label: "Model Comparison", component: ModelComparePage },
  { key: "batch", label: "Batch Processing", component: BatchPage },
] as const;

function App() {
  const [tab, setTab] = useState<(typeof TABS)[number]["key"]>("predict");
  const Active = TABS.find((t) => t.key === tab)!.component;

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Bio-Oil Pyrolysis Deoxygenation</h1>
        <p>
          Predicting and optimizing pyrolysis conditions to minimize bio-oil oxygen
          content (O/C ratio) — Biomass → Pyrolysis → Crude bio-oil.
        </p>
      </header>
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={tab === t.key ? "active" : ""}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <main className="app-main">
        <Active />
      </main>
    </div>
  );
}

export default App;
