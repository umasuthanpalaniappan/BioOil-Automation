import { Tag } from "./ui/Tag";
import { DOMAIN_LIMIT } from "../data/demoData";
import type { Scenario } from "../data/demoData";
import styles from "./ProductPreview.module.css";

interface ProductPreviewProps {
  scenario: Scenario;
  approvalState: "pending" | "approved" | "rejected";
}

export function ProductPreview({ scenario, approvalState }: ProductPreviewProps) {
  const { recommendation, alternative, flagReason, status } = scenario;

  return (
    <div className={styles.panel} aria-label="Pyrolysis Advisor product preview, sample data">
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.dot} aria-hidden="true" />
          <span className={styles.sessionLabel}>pyrolysis-advisor · session</span>
        </div>
        <Tag tone="neutral">SAMPLE DATA</Tag>
      </header>

      <div className={styles.body}>
        <section className={styles.block}>
          <p className={styles.blockLabel}>Current feedstock</p>
          <p className={styles.blockValue}>{scenario.name}</p>
          <p className={styles.blockSub}>{scenario.description}</p>
        </section>

        <section className={styles.block}>
          <p className={styles.blockLabel}>Composition (evidence)</p>
          <dl className={styles.compGrid}>
            <div>
              <dt>C</dt>
              <dd>{scenario.profile.carbonPct}%</dd>
            </div>
            <div>
              <dt>H</dt>
              <dd>{scenario.profile.hydrogenPct}%</dd>
            </div>
            <div>
              <dt>O</dt>
              <dd>{scenario.profile.oxygenPct}%</dd>
            </div>
            <div>
              <dt>N</dt>
              <dd>{scenario.profile.nitrogenPct}%</dd>
            </div>
          </dl>
          <p className={styles.blockSub}>
            Domain distance {scenario.domainDistance.toFixed(2)} (limit {DOMAIN_LIMIT}) —{" "}
            {scenario.domainDistance <= DOMAIN_LIMIT ? "in range" : "out of range"}
          </p>
        </section>

        {status === "confident" && recommendation ? (
          <section className={styles.block}>
            <p className={styles.blockLabel}>Proposed action</p>
            <p className={styles.blockValue}>
              {recommendation.temperatureC}°C · {recommendation.heatingRateCPerMin}°C/min
            </p>
            <div className={styles.statusRow}>
              <Tag tone={approvalState === "approved" ? "accent" : approvalState === "rejected" ? "danger" : "neutral"}>
                {approvalState === "pending" && "Awaiting approval"}
                {approvalState === "approved" && "Approved"}
                {approvalState === "rejected" && "Rejected"}
              </Tag>
            </div>
          </section>
        ) : (
          <section className={styles.block}>
            <p className={styles.blockLabel}>Proposed action</p>
            <div className={styles.flagBox}>
              <Tag tone="danger">Flagged — outside training range</Tag>
              <p className={styles.flagText}>{flagReason}</p>
            </div>
          </section>
        )}

        <section className={styles.beforeAfter}>
          <div className={styles.baCol}>
            <p className={styles.blockLabel}>Across all settings</p>
            <p className={styles.baValue}>
              {scenario.yieldRangeWt[0]}–{scenario.yieldRangeWt[1]} wt%
            </p>
            <p className={styles.baSub}>
              O/C {scenario.ocRange[0]}–{scenario.ocRange[1]}
            </p>
          </div>
          <div className={styles.baArrow} aria-hidden="true">
            →
          </div>
          <div className={styles.baCol}>
            <p className={styles.blockLabel}>Recommended {approvalState !== "approved" && "(proposed)"}</p>
            {recommendation ? (
              <>
                <p className={styles.baValue} style={{ color: approvalState === "approved" ? "var(--accent)" : "var(--text)" }}>
                  {recommendation.predictedYieldWt} wt%
                </p>
                <p className={styles.baSub}>O/C {recommendation.predictedOC}</p>
              </>
            ) : (
              <p className={styles.baValue}>—</p>
            )}
          </div>
        </section>

        {alternative && (
          <section className={styles.block}>
            <p className={styles.blockLabel}>Alternative ({alternative.label})</p>
            <p className={styles.blockSub}>
              {alternative.temperatureC}°C · {alternative.heatingRateCPerMin}°C/min → {alternative.predictedYieldWt} wt%, O/C{" "}
              {alternative.predictedOC}
            </p>
          </section>
        )}

        <p className={styles.limitation}>{scenario.limitation}</p>
      </div>
    </div>
  );
}
