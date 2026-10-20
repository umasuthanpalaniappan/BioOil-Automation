import { Button } from "./ui/Button";
import { ProductPreview } from "./ProductPreview";
import { scenarios } from "../data/demoData";
import styles from "./Hero.module.css";

interface HeroProps {
  onLaunchDemo: () => void;
}

const metadata = [
  { label: "Status", value: "Research prototype" },
  { label: "O/C accuracy", value: "R² 0.90 (80/20 test)" },
  { label: "Models", value: "GPR + XGBoost hybrid" },
];

export function Hero({ onLaunchDemo }: HeroProps) {
  return (
    <section id="top" className={styles.hero}>
      <div className={`shell ${styles.grid}`}>
        <div className={styles.copy}>
          <p className="eyebrow">Physics-informed ML · literature-benchmarked</p>
          <h1 className={styles.headline}>
            Know the temperature
            <br />
            that actually works
            <br />
            for your biomass.
          </h1>
          <p className={styles.subhead}>
            Pyrolysis Advisor recommends a pyrolysis temperature and heating rate for higher bio-oil
            yield and lower oxygen content — trained on literature data, constrained by known
            chemistry, and benchmarked against published results.
          </p>
          <div className={styles.actions}>
            <Button variant="primary" onClick={onLaunchDemo}>
              Run the Advisor
            </Button>
            <a href="#how-it-works" className={styles.secondaryLink}>
              See how it's validated →
            </a>
          </div>
          <dl className={styles.metaRow}>
            {metadata.map((item) => (
              <div key={item.label} className={styles.metaItem}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className={styles.previewWrap}>
          <ProductPreview scenario={scenarios[0]} approvalState="pending" />
        </div>
      </div>
    </section>
  );
}
