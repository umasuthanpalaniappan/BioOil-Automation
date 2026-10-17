import { useRef, useState } from "react";
import { Tag } from "./ui/Tag";
import { ProductPreview } from "./ProductPreview";
import { scenarios, workflowSteps } from "../data/demoData";
import styles from "./WorkflowTabs.module.css";

export function WorkflowTabs() {
  const [activeIndex, setActiveIndex] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const active = workflowSteps[activeIndex];

  const focusTab = (index: number) => {
    const next = (index + workflowSteps.length) % workflowSteps.length;
    setActiveIndex(next);
    tabRefs.current[next]?.focus();
  };

  const onKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      focusTab(activeIndex + 1);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      focusTab(activeIndex - 1);
    } else if (event.key === "Home") {
      event.preventDefault();
      focusTab(0);
    } else if (event.key === "End") {
      event.preventDefault();
      focusTab(workflowSteps.length - 1);
    }
  };

  return (
    <section id="how-it-works" className={styles.section}>
      <div className="shell">
        <p className="section-label">How it works</p>
        <h2 className={styles.heading}>Three steps, nothing automatic.</h2>

        <div
          role="tablist"
          aria-label="Pyrolysis Advisor workflow"
          className={styles.tabList}
          onKeyDown={onKeyDown}
        >
          {workflowSteps.map((step, index) => (
            <button
              key={step.id}
              ref={(el) => {
                tabRefs.current[index] = el;
              }}
              role="tab"
              id={`tab-${step.id}`}
              aria-selected={index === activeIndex}
              aria-controls={`panel-${step.id}`}
              tabIndex={index === activeIndex ? 0 : -1}
              className={`${styles.tab} ${index === activeIndex ? styles.tabActive : ""}`}
              onClick={() => setActiveIndex(index)}
            >
              <span className={styles.tabNumber}>{step.stepNumber}</span>
              <span className={styles.tabTitle}>{step.title}</span>
            </button>
          ))}
        </div>

        <div
          role="tabpanel"
          id={`panel-${active.id}`}
          aria-labelledby={`tab-${active.id}`}
          className={styles.panel}
        >
          <div className={styles.panelCopy}>
            <Tag tone="accent">{active.statusLabel}</Tag>
            <h3 className={styles.panelTitle}>{active.title}</h3>
            <p className={styles.panelText}>{active.explanation}</p>
            <p className={styles.exampleLabel}>Example data</p>
            <p className={styles.exampleData}>{active.exampleData}</p>
          </div>
          <div className={styles.panelPreview}>
            <ProductPreview scenario={scenarios[0]} approvalState={activeIndex === 2 ? "approved" : "pending"} />
          </div>
        </div>
      </div>
    </section>
  );
}
