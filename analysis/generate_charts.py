import argparse
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str((Path(__file__).parent / ".matplotlib").resolve()))

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_RESULT_FILES = {
    "Claude Opus 4.1": "claude-opus-4-1-20250805_210925_few3.md",
    "Gemini 2.5 Pro": "gemini-2.5-pro_210925_few3.md",
    "GPT-5 Few-shot": "gpt-5-2025-08-07_230925_few3.md",
    "GPT-5 Mini": "gpt-5-mini-2025-08-07_290925_few3.md",
    "Llama 3.1 8B": "llama3.1-8b_290925_few3.md",
}


def parse_md_table(path: Path) -> pd.DataFrame:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    table_lines = [line for line in lines if line.startswith("|")]
    if len(table_lines) < 3:
        raise ValueError(f"No markdown table found in {path}")

    headers = [cell.strip() for cell in table_lines[0].split("|")[1:-1]]
    rows = []
    for line in table_lines[2:]:
        cells = [cell.strip().replace("**", "") for cell in line.split("|")[1:-1]]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))

    df = pd.DataFrame(rows)
    numeric_cols = [
        "Input",
        "Output",
        "Cost",
        "Tests",
        "Syntax",
        "Consistent",
        "Previous",
        "Valid",
        "%",
        "Complete",
        "Wrong",
        "Misses",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def totals_for_model(model: str, path: Path) -> dict:
    df = parse_md_table(path)
    totals = df[df["Requirement"].str.fullmatch(r"Totals", case=False, na=False)]
    if totals.empty:
        totals = df[df["Requirement"].str.contains(r"\bTotals\b", case=False, na=False)]
    if totals.empty:
        raise ValueError(f"No totals row found in {path}")

    row = totals.iloc[-1].to_dict()
    row["Model"] = model
    row["Source"] = str(path)
    return row


def annotate_bars(ax, suffix="%"):
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


def save_performance_chart(df: pd.DataFrame, output_path: Path):
    metrics = ["Syntax (%)", "Consistent (%)", "Valid (%)"]
    ax = df.set_index("Model")[metrics].plot(kind="bar", figsize=(11, 6), width=0.78)
    ax.set_title("Alloy4Fun Instance Generation Performance")
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("")
    ax.set_ylim(0, 108)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3)
    ax.tick_params(axis="x", rotation=20)
    annotate_bars(ax)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_missed_chart(df: pd.DataFrame, output_path: Path):
    df_plot = df.dropna(subset=["Missed (%)"])
    ax = df_plot.set_index("Model")[["Missed (%)"]].plot(
        kind="bar", figsize=(9, 5), width=0.65, color="#c44e52", legend=False
    )
    ax.set_title("Erroneous Specifications Missed")
    ax.set_ylabel("Missed (%) - lower is better")
    ax.set_xlabel("")
    ax.set_ylim(0, 108)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.tick_params(axis="x", rotation=20)
    annotate_bars(ax)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_cost_chart(df: pd.DataFrame, output_path: Path):
    ax = df.set_index("Model")[["Cost"]].plot(
        kind="bar", figsize=(9, 5), width=0.65, color="#4c72b0", legend=False
    )
    ax.set_title("Estimated Execution Cost")
    ax.set_ylabel("Cost")
    ax.set_xlabel("")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.tick_params(axis="x", rotation=20)
    annotate_bars(ax, suffix="")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def build_summary(results_dir: Path) -> pd.DataFrame:
    rows = []
    for model, filename in DEFAULT_RESULT_FILES.items():
        path = results_dir / filename
        if path.exists():
            rows.append(totals_for_model(model, path))

    if not rows:
        raise ValueError(f"No known result markdown files found in {results_dir}")

    df = pd.DataFrame(rows)
    df["Syntax (%)"] = (df["Syntax"] / df["Tests"]) * 100
    df["Consistent (%)"] = (df["Consistent"] / df["Tests"]) * 100
    df["Valid (%)"] = (df["Valid"] / df["Tests"]) * 100
    df["Missed (%)"] = (df["Misses"] / df["Wrong"]) * 100

    columns = [
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
    return df[columns].sort_values("Model").reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Generate project charts from analysis markdown results.")
    parser.add_argument("--results-dir", default="analysis/results", help="Directory with analysis .md files")
    parser.add_argument("--output-dir", default="docs/images/generated", help="Directory to save charts")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

    summary = build_summary(results_dir)
    summary_path = output_dir / "summary.csv"
    summary.to_csv(summary_path, index=False)

    save_performance_chart(summary, output_dir / "alloy_performance.png")
    save_missed_chart(summary, output_dir / "missed_specifications.png")
    save_cost_chart(summary, output_dir / "execution_cost.png")

    print(f"Summary saved to {summary_path}")
    print(f"Charts saved to {output_dir}")
    print(summary.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
