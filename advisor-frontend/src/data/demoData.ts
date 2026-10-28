// Scenario values below come from pyrolysis_advisor/results/tables/final_results.json
// ("examples") and the input compositions in pyrolysis_advisor/src/07_final_advisor.py.
// This file feeds the frontend-only demo — nothing here calls a live model.

export interface FeedstockProfile {
  carbonPct: number;
  hydrogenPct: number;
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
  domainDistance: number;
  yieldRangeWt: [number, number];
  ocRange: [number, number];
  recommendation: Recommendation | null;
  alternative: AlternativeRecommendation | null;
  flagReason: string | null;
  limitation: string;
}

export const DOMAIN_LIMIT = 0.41;

export const scenarios: Scenario[] = [
  {
    id: "pine",
    name: "Pine-like wood",
    description: "Typical softwood composition, close to the biomasses the models were trained on.",
    profile: { carbonPct: 50.0, hydrogenPct: 6.1, oxygenPct: 43.5, nitrogenPct: 0.2 },
    status: "confident",
    domainDistance: 0.15,
    yieldRangeWt: [35.0, 43.5],
    ocRange: [0.058, 0.12],
    recommendation: { temperatureC: 480, heatingRateCPerMin: 300, predictedYieldWt: 41.8, predictedOC: 0.068 },
    alternative: { label: "Max yield", temperatureC: 570, heatingRateCPerMin: 100, predictedYieldWt: 43.5, predictedOC: 0.097 },
    flagReason: null,
    limitation: "Model estimate from literature-compiled data (80% interval ±12.6 wt% for a new biomass), not a lab measurement.",
  },
  {
    id: "rice-husk",
    name: "Rice husk-like",
    description: "Oxygen-rich agricultural residue, still inside the training composition range.",
    profile: { carbonPct: 41.5, hydrogenPct: 5.6, oxygenPct: 51.5, nitrogenPct: 0.6 },
    status: "confident",
    domainDistance: 0.25,
    yieldRangeWt: [36.2, 44.7],
    ocRange: [0.059, 0.156],
    recommendation: { temperatureC: 510, heatingRateCPerMin: 10, predictedYieldWt: 41.6, predictedOC: 0.062 },
    alternative: { label: "Max yield", temperatureC: 570, heatingRateCPerMin: 100, predictedYieldWt: 44.7, predictedOC: 0.113 },
    flagReason: null,
    limitation: "Model estimate from literature-compiled data (80% interval ±12.6 wt% for a new biomass), not a lab measurement.",
  },
  {
    id: "microalgae",
    name: "Microalgae-like (N 8.5%)",
    description: "Protein-rich feedstock with far more nitrogen than lignocellulosic biomass.",
    profile: { carbonPct: 52.0, hydrogenPct: 7.5, oxygenPct: 31.0, nitrogenPct: 8.5 },
    status: "flagged",
    domainDistance: 0.52,
    yieldRangeWt: [35.9, 44.5],
    ocRange: [0.092, 0.147],
    recommendation: null,
    alternative: null,
    flagReason: "Composition distance 0.52 exceeds the applicability limit of 0.41, so the Advisor withholds a confident recommendation instead of extrapolating.",
    limitation: "Run 1–2 real calibration experiments on this feedstock before trusting any model output.",
  },
  {
    id: "coal",
    name: "Coal-like (C 80%)",
    description: "High-carbon, low-oxygen feedstock — included to test the model's refusal behaviour.",
    profile: { carbonPct: 80.0, hydrogenPct: 4.5, oxygenPct: 14.0, nitrogenPct: 1.5 },
    status: "flagged",
    domainDistance: 1.2,
    yieldRangeWt: [36.1, 44.7],
    ocRange: [0.092, 0.138],
    recommendation: null,
    alternative: null,
    flagReason: "Composition distance 1.20 is nearly 3× the applicability limit of 0.41 — this is not biomass the models know.",
    limitation: "Shown only to demonstrate the applicability check; this feedstock should not be scored by this model.",
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
    exampleData: "C 50.0% · H 6.1% · O 43.5% · N 0.2% → distance 0.15 (limit 0.41)",
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
      "Predictions come with an uncertainty interval and show which physics constraints shaped the result. For a brand-new feedstock, one or two real experiments sharpen the estimate.",
    statusLabel: "VERIFIED",
    exampleData: "Avg. yield error ~8 wt% with 0 experiments → 5.3 wt% with 1 → 4.2 wt% with 2",
  },
];

export const featureCards = [
  {
    index: "01",
    label: "ACCURACY",
    title: "Matches the published benchmark",
    body:
      "On the standard 80/20 test used in the literature, our O/C model reaches R² 0.90, close to the 0.93 reported by Zhang et al. (2022). A second, stricter test on brand-new biomasses is reported too, so you know when to calibrate.",
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
      "O/C is constrained to fall monotonically with temperature; tar share comes from Chan et al. Arrhenius wood kinetics. Predicted O/C can never rise with temperature, even on unfamiliar biomass.",
  },
];

export const faqItems = [
  {
    question: "Is this connected to a real reactor or lab instrument?",
    answer:
      "No. This page is a frontend-only demo running entirely in your browser on fixed sample data computed offline from the project's trained models. No device, reactor, or live backend is being read or controlled.",
  },
  {
    question: "How accurate are the predictions?",
    answer:
      "On the standard 80/20 test, the best O/C model reaches R² 0.90 and the final Advisor models about 0.61 for both O/C and yield (averaged over 10 random splits). On a stricter test with completely new biomasses, scores drop (O/C R² ≈ 0.27), so for a new feedstock run 1–2 calibration experiments. Treat outputs as a starting point, not a lab result.",
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
