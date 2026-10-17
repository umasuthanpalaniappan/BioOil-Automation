import { useState } from "react";
import { faqItems } from "../data/demoData";
import styles from "./FAQ.module.css";

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggle = (index: number) => {
    setOpenIndex((current) => (current === index ? null : index));
  };

  return (
    <section id="questions" className={styles.section}>
      <div className="shell">
        <p className="section-label">Questions</p>
        <h2 className={styles.heading}>Answered honestly, limitations included.</h2>

        <div className={styles.list}>
          {faqItems.map((item, index) => {
            const isOpen = openIndex === index;
            const panelId = `faq-panel-${index}`;
            const buttonId = `faq-button-${index}`;
            return (
              <div key={item.question} className={styles.item}>
                <h3 className={styles.itemHeading}>
                  <button
                    type="button"
                    id={buttonId}
                    className={styles.trigger}
                    aria-expanded={isOpen}
                    aria-controls={panelId}
                    onClick={() => toggle(index)}
                  >
                    <span>{item.question}</span>
                    <span className={`${styles.icon} ${isOpen ? styles.iconOpen : ""}`} aria-hidden="true" />
                  </button>
                </h3>
                <div
                  id={panelId}
                  role="region"
                  aria-labelledby={buttonId}
                  className={`${styles.panel} ${isOpen ? styles.panelOpen : ""}`}
                >
                  <p className={styles.answer}>{item.answer}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
