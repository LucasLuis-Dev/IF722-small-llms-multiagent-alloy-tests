import os
import argparse
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str((Path(__file__).parent / ".matplotlib").resolve()))

import matplotlib.pyplot as plt
import pandas as pd

from generate_charts import totals_for_model


def annotate(ax, suffix="%"):
    for patch in ax.patches:
        height = patch.get_height()
        if pd.isna(height):
            continue
        ax.annotate(
            f"{height:.1f}{suffix}",
            (patch.get_x() + patch.get_width() / 2, height),
            ha="center",
            va="bottom",
            fontsize=8,
            xytext=(0, 4),
            textcoords="offset points",
        )


def build_summary(result_files: dict[str, Path]) -> pd.DataFrame:
    rows = []
    for model, path in result_files.items():
        rows.append(totals_for_model(model, path))

    df = pd.DataFrame(rows)
    df["Syntax (%)"] = (df["Syntax"] / df["Tests"]) * 100
    df["Consistent (%)"] = (df["Consistent"] / df["Tests"]) * 100
    df["Valid (%)"] = (df["Valid"] / df["Tests"]) * 100
    df["Missed (%)"] = (df["Misses"] / df["Wrong"]) * 100
    return df[
        [
            "Model",
            "Tests",
            "Syntax",
            "Consistent",
            "Valid",
            "Wrong",
            "Misses",
            "Cost",
            "Syntax (%)",
            "Consistent (%)",
            "Valid (%)",
            "Missed (%)",
            "Source",
        ]
    ]


def main():
    parser = argparse.ArgumentParser(description="Generate context comparison charts.")
    parser.add_argument("--raw-md", default="data/raw/experiment_raw.md")
    parser.add_argument("--processed-md", default="data/processed/experiment_processed.md")
    parser.add_argument("--output-dir", default="docs/images/generated/context")
    args = parser.parse_args()

    result_files = {
        "GPT-5 Baseline": Path("analysis/results/gpt-5-2025-08-07_230925_few3.md"),
        "Gemini Raw": Path(args.raw_md),
        "Gemini Processed + Context": Path(args.processed_md),
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

    summary = build_summary(result_files)
    summary.to_csv(output_dir / "context_summary.csv", index=False)

    metrics = ["Syntax (%)", "Consistent (%)", "Valid (%)"]
    ax = summary.set_index("Model")[metrics].plot(kind="bar", figsize=(10, 6), width=0.72)
    ax.set_title("Pipeline Performance With Self-Reflection Context")
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("")
    ax.set_ylim(0, 108)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    ax.tick_params(axis="x", rotation=15)
    annotate(ax)
    plt.tight_layout()
    plt.savefig(output_dir / "context_performance.png", dpi=180)
    plt.close()

    ax = summary.set_index("Model")[["Missed (%)"]].plot(
        kind="bar", figsize=(9, 5), width=0.58, color="#c44e52", legend=False
    )
    ax.set_title("Erroneous Specifications Missed")
    ax.set_ylabel("Missed (%) - lower is better")
    ax.set_xlabel("")
    ax.set_ylim(0, 108)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.tick_params(axis="x", rotation=15)
    annotate(ax)
    plt.tight_layout()
    plt.savefig(output_dir / "context_missed_specifications.png", dpi=180)
    plt.close()

    print(f"Context charts saved to {output_dir}")
    print(summary.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
