import { Button } from "./ui/Button";
import styles from "./FinalCTA.module.css";

interface FinalCTAProps {
  onLaunchDemo: () => void;
}

export function FinalCTA({ onLaunchDemo }: FinalCTAProps) {
  return (
    <section className={styles.section}>
      <div className="shell">
        <div className={styles.box}>
          <h2 className={styles.heading}>See the trade-off on a sample feedstock.</h2>
          <p className={styles.sub}>
            Pick a sample biomass, review the Advisor's recommendation, and decide whether to approve
            it — all running locally in your browser on pre-computed results from the project's
            trained models.
          </p>
          <div className={styles.actions}>
            <Button variant="primary" onClick={onLaunchDemo}>
              Run the Advisor
            </Button>
            <Button
              variant="secondary"
              href="https://github.com/umasuthanpalaniappan/BioOil-Automation"
              target="_blank"
              rel="noreferrer"
            >
              View the project on GitHub
            </Button>
          </div>
          <p className={styles.note}>
            This page is a frontend-only demo on fixed sample data — no reactor, device or live model
            is connected.
          </p>
        </div>
      </div>
    </section>
  );
}
