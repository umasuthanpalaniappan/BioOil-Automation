import { useEffect, useRef, useState } from "react";
import { Button } from "./ui/Button";
import { Tag } from "./ui/Tag";
import { ProductPreview } from "./ProductPreview";
import { scenarios } from "../data/demoData";
import type { Scenario } from "../data/demoData";
import styles from "./DemoModal.module.css";

type Stage = "select" | "analyzing" | "review" | "result";
type Decision = "approved" | "rejected" | null;

interface DemoModalProps {
  onClose: () => void;
  triggerRef: React.RefObject<HTMLElement | null>;
}

export function DemoModal({ onClose, triggerRef }: DemoModalProps) {
  const [stage, setStage] = useState<Stage>("select");
  const [selected, setSelected] = useState<Scenario | null>(null);
  const [decision, setDecision] = useState<Decision>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const titleId = "demo-modal-title";

  useEffect(() => {
    closeButtonRef.current?.focus();
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
      triggerRef.current?.focus();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (stage !== "analyzing") return;
    const timer = window.setTimeout(() => setStage("review"), 900);
    return () => window.clearTimeout(timer);
  }, [stage]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
        return;
      }
      if (event.key !== "Tab" || !dialogRef.current) return;

      const focusable = dialogRef.current.querySelectorAll<HTMLElement>(
        'button, a[href], input, [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleBackdropClick = (event: React.MouseEvent) => {
    if (event.target === event.currentTarget) onClose();
  };

  const startDemo = (scenario: Scenario) => {
    setSelected(scenario);
    setDecision(null);
    setStage("analyzing");
  };

  const handleDecision = (value: Decision) => {
    setDecision(value);
    setStage("result");
  };

  const reset = () => {
    setStage("select");
    setSelected(null);
    setDecision(null);
  };

  return (
    <div className={styles.backdrop} onMouseDown={handleBackdropClick}>
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={styles.dialog}
      >
        <header className={styles.header}>
          <div>
            <p className={styles.kicker}>Pyrolysis Advisor demo</p>
            <h2 id={titleId} className={styles.title}>
              {stage === "select" && "Choose a sample feedstock"}
              {stage === "analyzing" && "Checking applicability…"}
              {stage === "review" && "Review the recommendation"}
              {stage === "result" && "Result"}
            </h2>
          </div>
          <button
            ref={closeButtonRef}
            type="button"
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close demo"
          >
            ×
          </button>
        </header>

        <div className={styles.body}>
          {stage === "select" && (
            <div className={styles.scenarioGrid}>
              {scenarios.map((scenario) => (
                <button
                  key={scenario.id}
                  type="button"
                  className={styles.scenarioCard}
                  onClick={() => startDemo(scenario)}
                >
                  <div className={styles.scenarioTop}>
                    <span className={styles.scenarioName}>{scenario.name}</span>
                    <Tag tone={scenario.status === "flagged" ? "danger" : "accent"}>
                      {scenario.status === "flagged" ? "Likely flagged" : "In range"}
                    </Tag>
                  </div>
                  <p className={styles.scenarioDesc}>{scenario.description}</p>
                </button>
              ))}
            </div>
          )}

          {stage === "analyzing" && selected && (
            <div className={styles.analyzing} role="status" aria-live="polite">
              <span className={styles.spinner} aria-hidden="true" />
              <p>Comparing {selected.name} against the training distribution…</p>
            </div>
          )}

          {stage === "review" && selected && (
            <div className={styles.reviewLayout}>
              <ProductPreview scenario={selected} approvalState="pending" />
              <div className={styles.reviewActions}>
                {selected.status === "confident" ? (
                  <>
                    <p className={styles.reviewPrompt}>
                      Approve this recommendation, or reject it and keep current conditions.
                    </p>
                    <div className={styles.actionRow}>
                      <Button variant="primary" onClick={() => handleDecision("approved")}>
                        Approve recommendation
                      </Button>
                      <Button variant="secondary" onClick={() => handleDecision("rejected")}>
                        Reject
                      </Button>
                    </div>
                  </>
                ) : (
                  <>
                    <p className={styles.reviewPrompt}>
                      No confident recommendation is available for this feedstock — see the flagged
                      reason in the panel. You can acknowledge this and return to try another sample.
                    </p>
                    <div className={styles.actionRow}>
                      <Button variant="secondary" onClick={() => handleDecision("rejected")}>
                        Acknowledge
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {stage === "result" && selected && (
            <div className={styles.reviewLayout}>
              <ProductPreview
                scenario={selected}
                approvalState={decision === "approved" ? "approved" : "rejected"}
              />
              <div className={styles.reviewActions}>
                {selected.status === "flagged" ? (
                  <p className={styles.resultText}>
                    No action was taken. {selected.name} needs real calibration data before this
                    model can make a confident recommendation.
                  </p>
                ) : decision === "approved" ? (
                  <p className={styles.resultText}>
                    Recommendation applied in this demo session only. Projected yield moved from{" "}
                    {selected.baselineYieldWt} wt% to {selected.recommendation?.predictedYieldWt} wt% —
                    a model estimate, not a measurement. A successful recommendation here does not
                    confirm real-world performance without an actual pyrolysis run.
                  </p>
                ) : (
                  <p className={styles.resultText}>
                    Recommendation rejected. No change was made — the feedstock stays at its baseline
                    conditions ({selected.baselineYieldWt} wt%, O/C {selected.baselineOC}).
                  </p>
                )}
                <div className={styles.actionRow}>
                  <Button variant="secondary" onClick={reset}>
                    Try another feedstock
                  </Button>
                  <Button variant="ghost" onClick={onClose}>
                    Close
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
