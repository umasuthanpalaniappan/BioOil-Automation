"""Exploratory data analysis for the bio-oil pyrolysis dataset.

Produces:
- ml/reports/eda_summary.md   (missingness, descriptive stats, correlation notes)
- ml/reports/figures/*.png    (distributions, correlation heatmap, scatter plots)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from data_loader import FEATURE_COLS, TARGET_COLS, load_raw

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
FIG_DIR = REPORTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def missingness_table(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    miss = df.isna().sum().sort_values(ascending=False)
    return pd.DataFrame({
        "missing": miss,
        "missing_pct": (miss / n * 100).round(1),
        "n_available": n - miss,
    })


def plot_missingness(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(df.isna(), cbar=False, yticklabels=False, ax=ax, cmap="Reds")
    ax.set_title("Missing value pattern (data sheet, 320 rows)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "missingness_heatmap.png", dpi=150)
    plt.close(fig)


def plot_target_distribution(df: pd.DataFrame, col: str = "O/C"):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    sns.histplot(df[col].dropna(), kde=True, ax=axes[0], color="#2b6cb0")
    axes[0].set_title(f"{col} distribution (n={df[col].notna().sum()})")
    sns.boxplot(x=df[col].dropna(), ax=axes[1], color="#63b3ed")
    axes[1].set_title(f"{col} boxplot")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{col.replace('/', '_')}_distribution.png", dpi=150)
    plt.close(fig)


def plot_correlation_heatmap(df: pd.DataFrame):
    num_df = df[FEATURE_COLS + TARGET_COLS]
    corr = num_df.corr(method="pearson")
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax,
                annot_kws={"size": 7})
    ax.set_title("Pearson correlation: features vs targets")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "correlation_heatmap.png", dpi=150)
    plt.close(fig)
    return corr


def plot_key_relationships(df: pd.DataFrame):
    pairs = [("PT", "O/C"), ("HR", "O/C"), ("Lig", "O/C"), ("O%", "O/C")]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for ax, (x, y) in zip(axes.flat, pairs):
        sub = df[[x, y]].dropna()
        sns.regplot(data=sub, x=x, y=y, ax=ax, scatter_kws={"alpha": 0.5, "s": 20},
                    line_kws={"color": "red"})
        ax.set_title(f"{y} vs {x}  (n={len(sub)})")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "key_relationships.png", dpi=150)
    plt.close(fig)


def main():
    df = load_raw()
    miss = missingness_table(df)
    plot_missingness(df)
    plot_target_distribution(df, "O/C")
    corr = plot_correlation_heatmap(df)
    plot_key_relationships(df)

    oc = df["O/C"].dropna()
    desc = df[FEATURE_COLS + TARGET_COLS].describe().T

    lines = []
    lines.append("# EDA Summary — Bio-Oil Pyrolysis Dataset\n")
    lines.append(f"Raw shape: {df.shape[0]} rows x {df.shape[1]} columns "
                  f"(after dropping empty `Gas_yield`/`Char_yield` columns).\n")

    lines.append("## Missingness by column\n")
    lines.append(miss.to_markdown())
    lines.append("")

    lines.append("## Primary target: O/C\n")
    lines.append(f"- Non-null count: {oc.count()} / {len(df)} rows "
                  f"({oc.count()/len(df)*100:.1f}%)")
    lines.append(f"- Mean: {oc.mean():.3f}, Median: {oc.median():.3f}, "
                  f"Std: {oc.std():.3f}")
    lines.append(f"- Min: {oc.min():.3f}, Max: {oc.max():.3f}")
    q1, q3 = oc.quantile(0.25), oc.quantile(0.75)
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    n_outliers = (oc > upper_fence).sum()
    lines.append(f"- IQR upper fence: {upper_fence:.3f} — {n_outliers} value(s) above it "
                  f"(max={oc.max():.2f}); see preprocessing report for the decision on "
                  f"whether these are kept.")
    lines.append("")

    lines.append("## Descriptive statistics (available rows per column)\n")
    lines.append(desc.round(2).to_markdown())
    lines.append("")

    lines.append("## Correlation with O/C (Pearson, pairwise-complete)\n")
    oc_corr = corr["O/C"].drop("O/C").sort_values(key=lambda s: s.abs(), ascending=False)
    lines.append(oc_corr.round(3).to_markdown())
    lines.append("")
    lines.append(
        "Cross-check note: the source workbook's `Table 3` sheet reports its own "
        "pairwise Pearson coefficients (different variable naming: HTT=PT, "
        "FR=O/C-related ratio, etc.) computed over a possibly different row subset. "
        "Directional agreement (e.g. PT and O/C negatively associated) was used as a "
        "sanity check rather than an exact numeric match, since the row sets and exact "
        "target definitions are not guaranteed identical.\n"
    )

    lines.append("## Figures\n")
    lines.append("- `figures/missingness_heatmap.png`")
    lines.append("- `figures/O_C_distribution.png`")
    lines.append("- `figures/correlation_heatmap.png`")
    lines.append("- `figures/key_relationships.png`")

    (REPORTS_DIR / "eda_summary.md").write_text("\n".join(lines))
    print("EDA summary written to", REPORTS_DIR / "eda_summary.md")


if __name__ == "__main__":
    main()
