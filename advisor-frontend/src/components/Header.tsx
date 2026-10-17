import { useEffect, useState } from "react";
import { Button } from "./ui/Button";
import styles from "./Header.module.css";

const NAV_LINKS = [
  { href: "#how-it-works", label: "How it works" },
  { href: "#features", label: "Features" },
  { href: "#questions", label: "Questions" },
];

interface HeaderProps {
  onLaunchDemo: () => void;
}

export function Header({ onLaunchDemo }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const handleNavClick = () => setMenuOpen(false);

  return (
    <header className={styles.header}>
      <div className={`${styles.inner} shell`}>
        <a href="#top" className={styles.logo}>
          Pyrolysis<span className={styles.logoAccent}>Advisor</span>
        </a>

        <nav className={styles.nav} aria-label="Primary">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href} className={styles.navLink}>
              {link.label}
            </a>
          ))}
        </nav>

        <div className={styles.ctaWrap}>
          <Button variant="primary" onClick={onLaunchDemo}>
            Run the Advisor
          </Button>
        </div>

        <button
          type="button"
          className={styles.menuButton}
          aria-expanded={menuOpen}
          aria-controls="mobile-nav"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          onClick={() => setMenuOpen((v) => !v)}
        >
          <span className={`${styles.burger} ${menuOpen ? styles.burgerOpen : ""}`} />
        </button>
      </div>

      <div
        id="mobile-nav"
        className={`${styles.mobileNav} ${menuOpen ? styles.mobileNavOpen : ""}`}
        aria-hidden={!menuOpen}
      >
        <nav className={styles.mobileLinks} aria-label="Mobile">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href} className={styles.mobileLink} onClick={handleNavClick}>
              {link.label}
            </a>
          ))}
        </nav>
        <div className={styles.mobileCta}>
          <Button
            variant="primary"
            fullWidth
            onClick={() => {
              setMenuOpen(false);
              onLaunchDemo();
            }}
          >
            Run the Advisor
          </Button>
        </div>
      </div>
    </header>
  );
}
