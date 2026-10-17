import { FeatureCard } from "./FeatureCard";
import { featureCards } from "../data/demoData";
import styles from "./FeaturesSection.module.css";

export function FeaturesSection() {
  return (
    <section id="features" className={styles.section}>
      <div className="shell">
        <p className="section-label">Principles</p>
        <h2 className={styles.heading}>Built to be trusted, not just impressive.</h2>
        <div className={styles.grid}>
          {featureCards.map((card) => (
            <FeatureCard key={card.index} {...card} />
          ))}
        </div>
      </div>
    </section>
  );
}
