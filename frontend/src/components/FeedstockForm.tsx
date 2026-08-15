import type { FeedstockInput } from "../types";

interface FieldSpec {
  key: keyof FeedstockInput;
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
}

const FIELDS: FieldSpec[] = [
  { key: "Cel", label: "Cellulose", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "Hem", label: "Hemicellulose", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "Lig", label: "Lignin", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "VM", label: "Volatile Matter", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "Ash", label: "Ash", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "FC", label: "Fixed Carbon", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "C%", label: "Carbon (ultimate)", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "H%", label: "Hydrogen (ultimate)", unit: "wt%", min: 0, max: 30, step: 0.1 },
  { key: "O%", label: "Oxygen (ultimate)", unit: "wt%", min: 0, max: 100, step: 0.1 },
  { key: "N%", label: "Nitrogen (ultimate)", unit: "wt%", min: 0, max: 30, step: 0.1 },
  { key: "Size", label: "Particle Size", unit: "mm", min: 0.01, max: 50, step: 0.01 },
  { key: "HR", label: "Heating Rate", unit: "°C/min", min: 0.1, max: 1000, step: 0.1 },
  { key: "PT", label: "Pyrolysis Temperature", unit: "°C", min: 100, max: 1200, step: 1 },
  { key: "Temp", label: "Secondary Temp Param", unit: "°C", min: 0, max: 1000, step: 1 },
];

interface Props {
  values: FeedstockInput;
  onChange: (values: FeedstockInput) => void;
}

export default function FeedstockForm({ values, onChange }: Props) {
  const update = (key: keyof FeedstockInput, val: string) => {
    onChange({ ...values, [key]: val === "" ? undefined : Number(val) });
  };

  return (
    <div className="form-grid">
      {FIELDS.map((f) => (
        <label key={f.key} className="form-field">
          <span>
            {f.label} <em>({f.unit})</em>
          </span>
          <input
            type="number"
            value={values[f.key] ?? ""}
            min={f.min}
            max={f.max}
            step={f.step}
            onChange={(e) => update(f.key, e.target.value)}
          />
        </label>
      ))}
    </div>
  );
}
