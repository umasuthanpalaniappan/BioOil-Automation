import styles from "./Tag.module.css";

interface TagProps {
  children: React.ReactNode;
  tone?: "neutral" | "accent" | "danger";
}

export function Tag({ children, tone = "neutral" }: TagProps) {
  return <span className={`${styles.tag} ${styles[tone]}`}>{children}</span>;
}
