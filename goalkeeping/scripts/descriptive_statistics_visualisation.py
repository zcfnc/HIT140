"""Step 3: Summarise Save% and create a boxplot."""

from pathlib import Path

import matplotlib

# Use a non-interactive backend so the chart can be saved from a script.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_analysis_sample.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_PLOT = OUTPUT_DIR / "save_pct_boxplot.png"

GROUP_ORDER = ["Knockout", "Group Stage Eliminated"]
analysis_df = pd.read_csv(INPUT_FILE)

summary = (
    analysis_df.groupby("progression_group", sort=False)["save_pct"]
    .agg(n="count", mean="mean", median="median", sd="std", minimum="min", maximum="max")
    .reindex(GROUP_ORDER)
)

quartiles = (
    analysis_df.groupby("progression_group", sort=False)["save_pct"]
    .quantile([0.25, 0.75])
    .unstack()
    .rename(columns={0.25: "q1", 0.75: "q3"})
    .reindex(GROUP_ORDER)
)
results_table = summary.join(quartiles)
results_table["iqr"] = results_table["q3"] - results_table["q1"]
results_table = results_table[["n", "mean", "median", "sd", "minimum", "maximum", "q1", "q3", "iqr"]]

OUTPUT_DIR.mkdir(exist_ok=True)
plot_data = [
    analysis_df.loc[analysis_df["progression_group"] == group, "save_pct"]
    for group in GROUP_ORDER
]

fig, ax = plt.subplots(figsize=(8, 6))
boxplot = ax.boxplot(
    plot_data,
    tick_labels=["Knockout", "Group Stage\nEliminated"],
    patch_artist=True,
    medianprops={"color": "black", "linewidth": 2},
    whiskerprops={"color": "#4A4A4A"},
    capprops={"color": "#4A4A4A"},
    flierprops={"marker": "o", "markerfacecolor": "#B22222", "markeredgecolor": "#B22222", "markersize": 5},
)
for patch, colour in zip(boxplot["boxes"], ["#4C78A8", "#F58518"]):
    patch.set_facecolor(colour)
    patch.set_alpha(0.75)

ax.set_title("Distribution of Goalkeeper Save Percentage by Team Progression")
ax.set_xlabel("Team Progression Group")
ax.set_ylabel("Save Percentage (%)")
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.35)
fig.tight_layout()
fig.savefig(OUTPUT_PLOT, dpi=300, bbox_inches="tight")
plt.close(fig)

print(results_table.round(2).to_string())
