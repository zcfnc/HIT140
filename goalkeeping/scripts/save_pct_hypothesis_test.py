"""Step 5: Check assumptions and run the locked Welch two-sample Save% t-test."""

from pathlib import Path

import matplotlib

# Use a non-interactive backend so diagnostic plots can be saved from a script.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_analysis_sample.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
ASSUMPTION_PLOT = OUTPUT_DIR / "save_pct_assumption_checks.png"

GROUP_ORDER = ["Knockout", "Group Stage Eliminated"]
ALPHA = 0.05


def iqr_outliers(values: pd.Series) -> pd.DataFrame:
    q1, q3 = values.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    outliers = values[(values < lower_fence) | (values > upper_fence)]
    return pd.DataFrame(
        {
            "q1": [q1],
            "q3": [q3],
            "iqr": [iqr],
            "lower_fence": [lower_fence],
            "upper_fence": [upper_fence],
            "outlier_count": [len(outliers)],
            "outlier_save_pct": [outliers.tolist()],
        }
    )

# Read and validate the locked final sample.
analysis_df = pd.read_csv(INPUT_FILE)

if set(analysis_df["progression_group"].dropna()) != set(GROUP_ORDER):
    raise ValueError("The final sample must contain exactly the two planned groups.")
if analysis_df["save_pct"].isna().any():
    raise ValueError("The final sample contains missing Save% values.")
if analysis_df["team"].duplicated().any():
    raise ValueError("The final sample must have one goalkeeper per team.")

# Create independent Save% groups and descriptive diagnostics.
knockout_save_pct = analysis_df.loc[
    analysis_df["progression_group"] == "Knockout", "save_pct"
]
eliminated_save_pct = analysis_df.loc[
    analysis_df["progression_group"] == "Group Stage Eliminated", "save_pct"
]

group_summary = (
    analysis_df.groupby("progression_group")["save_pct"]
    .agg(n="count", mean="mean", sample_sd="std", sample_variance="var")
    .reindex(GROUP_ORDER)
)

# Check potential outliers and variance.
outlier_summary = pd.concat(
    [
        iqr_outliers(knockout_save_pct).assign(progression_group="Knockout"),
        iqr_outliers(eliminated_save_pct).assign(
            progression_group="Group Stage Eliminated"
        ),
    ],
    ignore_index=True,
).set_index("progression_group")

levene_statistic, levene_p_value = stats.levene(
    knockout_save_pct, eliminated_save_pct, center="median"
)

# Save boxplot, histograms, and Q-Q plots for assumption checks.
OUTPUT_DIR.mkdir(exist_ok=True)
fig, axes = plt.subplots(2, 3, figsize=(14, 8))

axes[0, 0].boxplot(
    [knockout_save_pct, eliminated_save_pct],
    tick_labels=["Knockout", "Group Stage\nEliminated"],
    patch_artist=True,
    boxprops={"facecolor": "#9ECAE1"},
    medianprops={"color": "black", "linewidth": 2},
)
axes[0, 0].set_title("Boxplot")
axes[0, 0].set_ylabel("Save Percentage (%)")
axes[0, 0].set_ylim(0, 100)

for axis, values, label, colour in [
    (axes[0, 1], knockout_save_pct, "Knockout", "#4C78A8"),
    (axes[0, 2], eliminated_save_pct, "Group Stage Eliminated", "#F58518"),
]:
    axis.hist(values, bins=7, color=colour, edgecolor="white")
    axis.set_title(f"Histogram: {label}")
    axis.set_xlabel("Save Percentage (%)")
    axis.set_ylabel("Count")
    axis.set_xlim(0, 100)

for axis, values, label in [
    (axes[1, 1], knockout_save_pct, "Knockout"),
    (axes[1, 2], eliminated_save_pct, "Group Stage Eliminated"),
]:
    stats.probplot(values, dist="norm", plot=axis)
    axis.set_title(f"Q-Q Plot: {label}")
    axis.set_xlabel("Theoretical Quantiles")
    axis.set_ylabel("Ordered Save%")

axes[1, 0].axis("off")
axes[1, 0].text(
    0,
    0.85,
    "Design check\n\nOne eligible goalkeeper per team\nNo duplicate teams\nIndependent groups by team progression",
    fontsize=12,
    va="top",
)
fig.suptitle("Save% Assumption Diagnostics", fontsize=16)
fig.tight_layout()
fig.savefig(ASSUMPTION_PLOT, dpi=300, bbox_inches="tight")
plt.close(fig)

# Run the pre-specified two-sided Welch t-test.
test_result = stats.ttest_ind(
    knockout_save_pct,
    eliminated_save_pct,
    equal_var=False,
    alternative="two-sided",
)

comparison = CompareMeans(
    DescrStatsW(knockout_save_pct, ddof=1),
    DescrStatsW(eliminated_save_pct, ddof=1),
)
welch_df = comparison.dof_satt()
mean_difference = knockout_save_pct.mean() - eliminated_save_pct.mean()
decision = "Reject H0" if test_result.pvalue < ALPHA else "Fail to reject H0"

test_summary = pd.Series(
    {
        "mean_difference_knockout_minus_eliminated": mean_difference,
        "t_statistic": test_result.statistic,
        "welch_satterthwaite_df": welch_df,
        "p_value": test_result.pvalue,
        "alpha": ALPHA,
        "decision": decision,
    }
)

print(group_summary.round(2).to_string())
print(outlier_summary.round(2).to_string())
print(f"Levene statistic={levene_statistic:.3f}, p-value={levene_p_value:.3f}")
print(pd.to_numeric(test_summary.drop("decision")).round(4).to_string())
print(f"decision={decision}")
