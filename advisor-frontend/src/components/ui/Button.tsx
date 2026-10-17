import { forwardRef } from "react";
import type { ButtonHTMLAttributes, AnchorHTMLAttributes } from "react";
import styles from "./Button.module.css";

type Variant = "primary" | "secondary" | "ghost";

interface CommonProps {
  variant?: Variant;
  fullWidth?: boolean;
}

type ButtonAsButton = CommonProps &
  ButtonHTMLAttributes<HTMLButtonElement> & { href?: undefined };

type ButtonAsAnchor = CommonProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & { href: string };

type ButtonProps = ButtonAsButton | ButtonAsAnchor;

export const Button = forwardRef<HTMLButtonElement | HTMLAnchorElement, ButtonProps>(
  ({ variant = "primary", fullWidth = false, className, ...rest }, ref) => {
    const classes = [styles.btn, styles[variant], fullWidth ? styles.fullWidth : "", className]
      .filter(Boolean)
      .join(" ");

    if ("href" in rest && rest.href !== undefined) {
      const { href, ...anchorRest } = rest as AnchorHTMLAttributes<HTMLAnchorElement>;
      return (
        <a ref={ref as React.Ref<HTMLAnchorElement>} href={href} className={classes} {...anchorRest} />
      );
    }

    const buttonRest = rest as ButtonHTMLAttributes<HTMLButtonElement>;
    return <button ref={ref as React.Ref<HTMLButtonElement>} className={classes} {...buttonRest} />;
  },
);

Button.displayName = "Button";
