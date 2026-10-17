// All figures below are taken directly from the project's honest, grouped-by-biomass
// validation results (see pyrolysis_advisor/results/tables/final_results.json).
// This file feeds the frontend-only demo — nothing here calls a live model.

export interface FeedstockProfile {
  carbonPct: number;
  oxygenPct: number;
  nitrogenPct: number;
}

export type RecommendationStatus = "confident" | "flagged";

export interface Recommendation {
  temperatureC: number;
  heatingRateCPerMin: number;
  predictedYieldWt: number;
  predictedOC: number;
}

export interface AlternativeRecommendation extends Recommendation {
  label: string;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  profile: FeedstockProfile;
  status: RecommendationStatus;
  baselineYieldWt: number;
  baselineOC: number;
  recommendation: Recommendation | null;
  alternative: AlternativeRecommendation | null;
  flagReason: string | null;
  evidence: string[];
  limitation: string;
}

export const scenarios: Scenario[] = [
  {
    id: "pine",
    name: "Pine-like wood",
    description: "Softwood, moderate lignin content — closest to the dataset's training distribution.",
    profile: { carbonPct: 50.5, oxygenPct: 43.2, nitrogenPct: 0.2 },
    status: "confident",
    baselineYieldWt: 38.1,
    baselineOC: 0.081,
    recommendation: { temperatureC: 480, heatingRateCPerMin: 300, predictedYieldWt: 41.8, predictedOC: 0.068 },
    alternative: { label: "Max yield", temperatureC: 570, heatingRateCPerMin: 100, predictedYieldWt: 43.5, predictedOC: 0.097 },
    flagReason: null,
    evidence: [
      "Composition within the training range for C, H, O",
      "Fast pyrolysis regime (HR ≥ 100°C/min) well represented in D3",
      "Tar-selectivity kinetics consistent with known cellulose/lignin behaviour at this temperature",
    ],
    limitation: "Recommendation is a model estimate from literature-compiled data, not a lab measurement for this exact feedstock.",
  },
  {
    id: "rice-husk",
    name: "Rice husk-like",
    description: "High-silica agricultural residue, common in regional biomass studies.",
    profile: { carbonPct: 38.9, oxygenPct: 48.0, nitrogenPct: 0.6 },
    status: "confident",
    baselineYieldWt: 36.4,
    baselineOC: 0.079,
    recommendation: { temperatureC: 510, heatingRateCPerMin: 10, predictedYieldWt: 41.6, predictedOC: 0.062 },
    alternative: { label: "Max yield", temperatureC: 570, heatingRateCPerMin: 100, predictedYieldWt: 44.7, predictedOC: 0.113 },
    flagReason: null,
    evidence: [
      "Composition within the training range for C, H, O",
      "Slow-pyrolysis response curve has multiple nearby D3 examples",
      "O/C trend matches the monotonicity constraint applied at training time",
    ],
    limitation: "Ash/silica content is not an explicit model input — real rice husk pyrolysis may deviate more than the interval shown.",
  },
  {
    id: "microalgae",
    name: "Microalgae-like (N 8.5%)",
    description: "Protein-rich feedstock with nitrogen content well outside typical lignocellulosic biomass.",
    profile: { carbonPct: 46.0, oxygenPct: 28.0, nitrogenPct: 8.5 },
    status: "flagged",
    baselineYieldWt: 33.0,
    baselineOC: 0.095,
    recommendation: null,
    alternative: null,
    flagReason: "Nitrogen content (8.5%) is far above anything in the training data — the applicability check withholds a confident number rather than extrapolate silently.",
    evidence: [
      "Composition falls outside the convex hull of training biomasses",
      "Nearest training neighbours differ by more than 3× on nitrogen content",
      "No physics term in this model currently accounts for protein-derived nitrogen chemistry",
    ],
    limitation: "A usable recommendation needs 1–2 real calibration experiments on this feedstock before the model's output can be trusted.",
  },
  {
    id: "coal",
    name: "Coal-like (C 80%)",
    description: "High-carbon, low-oxygen feedstock — included to test the model's refusal behaviour.",
    profile: { carbonPct: 80.0, oxygenPct: 9.0, nitrogenPct: 1.1 },
    status: "flagged",
    baselineYieldWt: 14.0,
    baselineOC: 0.03,
    recommendation: null,
    alternative: null,
    flagReason: "Carbon content (80%) is outside the biomass composition range the models were trained and validated on.",
    evidence: [
      "Composition is coal-like, not biomass-like — well beyond D1b/D3's range",
      "Pyrolysis chemistry at this composition is governed by different mechanisms than the Broido–Shafizadeh pathway assumed here",
    ],
    limitation: "This feedstock should not be scored by this model at all — shown to illustrate the applicability check, not as a usable output.",
  },
];

export const caseStudyVerification = [
  { biomass: "Biomass 11 (C 49%, O 34%)", realOptimum: "450°C", modelOptimum: "450°C", match: true, errorNoExp: "6.6 wt%", errorOneExp: "13.0 wt%" },
  { biomass: "Biomass 108 (C 50%, O 45%)", realOptimum: "550°C", modelOptimum: "550°C", match: true, errorNoExp: "5.6 wt%", errorOneExp: "1.7 wt%" },
  { biomass: "Biomass 99 (C 45%, O 47%)", realOptimum: "500°C", modelOptimum: "600°C", match: false, errorNoExp: "6.0 wt%", errorOneExp: "1.9 wt%" },
];

export const workflowSteps = [
  {
    id: "describe",
    stepNumber: "01",
    title: "Describe your feedstock",
    explanation:
      "Enter elemental composition (C, H, O, N) or pick a feedstock profile close to yours. The model checks whether your biomass falls inside the range it was actually trained on.",
    statusLabel: "INPUT",
    exampleData: "C 50.5% · H 6.1% · O 43.2% · N 0.2%",
  },
  {
    id: "review",
    stepNumber: "02",
    title: "Review and approve the recommendation",
    explanation:
      "The Advisor proposes a temperature and heating rate on a yield/O₂ Pareto front. Nothing is applied automatically — you compare the trade-off and choose, or reject it outright.",
    statusLabel: "AWAITING APPROVAL",
    exampleData: "480°C, 300°C/min → 41.8 wt% yield, O/C 0.068",
  },
  {
    id: "verify",
    stepNumber: "03",
    title: "Verify the predicted outcome",
    explanation:
      "Predictions come with an honest uncertainty interval from grouped-by-biomass validation — not an optimistic random-split number — plus which physics constraints shaped the result.",
    statusLabel: "VERIFIED",
    exampleData: "±12.6 wt% (0 experiments) → ±5.3 wt% (1 calibration experiment)",
  },
];

export const featureCards = [
  {
    index: "01",
    label: "VALIDATION",
    title: "Honest numbers, not optimistic ones",
    body:
      "Every reported accuracy is measured on biomasses the model never saw during training, not on a random row split that leaks the same biomass into both sets. Random-split R² of 0.63 becomes 0.23 under this test — that number is what's shown.",
  },
  {
    index: "02",
    label: "CONTROL",
    title: "You choose the trade-off",
    body:
      "The Advisor never picks for you. It lays out the yield/oxygen Pareto front and lets you approve, reject, or ask for the maximum-yield alternative — the last 1–2 wt% of yield can cost 40% more oxygen.",
  },
  {
    index: "03",
    label: "PHYSICS",
    title: "Constrained by known chemistry",
    body:
      "O/C is constrained to fall monotonically with temperature; tar selectivity follows Broido–Shafizadeh kinetics. The model can't output a result that violates known pyrolysis behaviour, even on unfamiliar biomass.",
  },
];

export const faqItems = [
  {
    question: "Is this connected to a real reactor or lab instrument?",
    answer:
      "No. This page is a frontend-only demo running entirely in your browser on fixed sample data computed offline from the project's trained models. No device, reactor, or live backend is being read or controlled.",
  },
  {
    question: "How accurate are these recommendations really?",
    answer:
      "Honestly validated on biomasses excluded from training, O/C reaches R² ≈ 0.26 (log scale) and yield shape R² ≈ 0.12 — a real but modest improvement over guessing the dataset average, not the 0.9+ numbers a random split would report. Treat outputs as a starting point, not a lab result.",
  },
  {
    question: "What happens if my biomass isn't like anything in the training data?",
    answer:
      "The applicability check flags it instead of guessing silently — see the microalgae and coal scenarios in the demo above. In that case the model recommends running 1–2 real calibration experiments, which measurably improve its accuracy for that biomass.",
  },
  {
    question: "Can I run this on my own feedstock data?",
    answer:
      "Not from this page — it has no backend. The trained models, full training code and validation methodology are in the project repository linked below; the supporting FastAPI service in the same repo exposes a /predict endpoint for that purpose.",
  },
];
