import type { ConstraintFlag, DriftFlag } from "../types";

export function PhysicsFlagList({ flags }: { flags: ConstraintFlag[] }) {
  if (!flags.length) return <p className="flag-list-empty">No physics constraint violations detected.</p>;
  return (
    <div>
      {flags.map((f, i) => (
        <div key={i} className={`flag ${f.severity}`}>
          <strong>{f.field}:</strong> {f.message}
        </div>
      ))}
    </div>
  );
}

export function DriftFlagList({ flags }: { flags: DriftFlag[] }) {
  if (!flags.length) return <p className="flag-list-empty">All inputs within training data range.</p>;
  return (
    <div>
      {flags.map((f, i) => (
        <div key={i} className="flag">
          <strong>{f.field}={f.value}:</strong> {f.message}
        </div>
      ))}
    </div>
  );
}
