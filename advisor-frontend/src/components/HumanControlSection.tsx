import styles from "./HumanControlSection.module.css";

const statements = [
  "You remain the decision point.",
  "Every recommendation is a proposal, not an action.",
  "Every uncertainty is shown, not hidden.",
  "Every out-of-range input is flagged, not guessed.",
];

export function HumanControlSection() {
  return (
    <section className={styles.section}>
      <div className="shell">
        <p className="section-label">Human control</p>
        <ul className={styles.list}>
          {statements.map((line) => (
            <li key={line} className={styles.line}>
              {line}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
