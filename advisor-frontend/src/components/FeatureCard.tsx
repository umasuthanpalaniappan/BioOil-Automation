import styles from "./FeatureCard.module.css";

interface FeatureCardProps {
  index: string;
  label: string;
  title: string;
  body: string;
}

export function FeatureCard({ index, label, title, body }: FeatureCardProps) {
  return (
    <article className={styles.card}>
      <div className={styles.top}>
        <span className={styles.index}>{index}</span>
        <span className={styles.marker} aria-hidden="true" />
      </div>
      <p className={styles.label}>{label}</p>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.body}>{body}</p>
    </article>
  );
}
