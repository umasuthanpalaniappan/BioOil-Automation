import { Tag } from "./ui/Tag";
import styles from "./Footer.module.css";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={`shell ${styles.inner}`}>
        <div className={styles.left}>
          <p className={styles.name}>Pyrolysis Advisor</p>
          <p className={styles.tagline}>
            Physics-informed bio-oil pyrolysis recommendations, benchmarked against the literature.
          </p>
          <div className={styles.tags}>
            <Tag tone="neutral">Research prototype</Tag>
            <Tag tone="neutral">Frontend demo only</Tag>
          </div>
        </div>

        <div className={styles.right}>
          <a
            className={styles.link}
            href="https://github.com/umasuthanpalaniappan/BioOil-Automation"
            target="_blank"
            rel="noreferrer"
          >
            GitHub repository
          </a>
          <a className={styles.link} href="#top">
            Back to top
          </a>
          <p className={styles.copyright}>© {year} Pyrolysis Advisor. All results shown are sample data.</p>
        </div>
      </div>
    </footer>
  );
}
