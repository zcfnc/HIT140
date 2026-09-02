"""Step 4: Estimate a Welch-style 95% CI for the locked mean Save% difference."""

from pathlib import Path

import pandas as pd
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_analysis_sample.csv"
GROUP_ORDER = ["Knockout", "Group Stage Eliminated"]

# Read and validate the locked final sample.
analysis_df = pd.read_csv(INPUT_FILE)

if set(analysis_df["progression_group"].dropna()) != set(GROUP_ORDER):
    raise ValueError("The final sample must contain exactly the two planned groups.")
if analysis_df["save_pct"].isna().any():
    raise ValueError("The final sample must not contain missing save_pct values.")

# Create the two independent Save% groups.
knockout_save_pct = analysis_df.loc[
    analysis_df["progression_group"] == "Knockout", "save_pct"
]
eliminated_save_pct = analysis_df.loc[
    analysis_df["progression_group"] == "Group Stage Eliminated", "save_pct"
]

# Estimate the unequal-variance mean difference and its 95% CI.
knockout_stats = DescrStatsW(knockout_save_pct, ddof=1)
eliminated_stats = DescrStatsW(eliminated_save_pct, ddof=1)
comparison = CompareMeans(knockout_stats, eliminated_stats)

mean_knockout = knockout_save_pct.mean()
mean_eliminated = eliminated_save_pct.mean()
mean_difference = mean_knockout - mean_eliminated
standard_error = comparison.std_meandiff_separatevar
welch_df = comparison.dof_satt()
ci_lower, ci_upper = comparison.tconfint_diff(
    alpha=0.05,
    alternative="two-sided",
    usevar="unequal",
)

# Store group summaries and CI results for reporting.
group_results = pd.DataFrame(
    {
        "n": [knockout_save_pct.count(), eliminated_save_pct.count()],
        "mean_save_pct": [mean_knockout, mean_eliminated],
        "sample_sd": [knockout_save_pct.std(ddof=1), eliminated_save_pct.std(ddof=1)],
    },
    index=GROUP_ORDER,
)

ci_results = pd.Series(
    {
        "mean_difference_knockout_minus_eliminated": mean_difference,
        "standard_error": standard_error,
        "welch_satterthwaite_df_for_ci": welch_df,
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
    }
)

print(group_results.round(2).to_string())
print(ci_results.round(2).to_string())
