"""Step 5: Run a two-sided Welch t-test for Save%."""

from pathlib import Path

import pandas as pd
from scipy import stats
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_analysis_sample.csv"
GROUP_ORDER = ["Knockout", "Group Stage Eliminated"]
ALPHA = 0.05

analysis_df = pd.read_csv(INPUT_FILE)

knockout_save_pct = analysis_df.loc[
    analysis_df["progression_group"] == "Knockout", "save_pct"
]
eliminated_save_pct = analysis_df.loc[
    analysis_df["progression_group"] == "Group Stage Eliminated", "save_pct"
]

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

print(pd.to_numeric(test_summary.drop("decision")).round(4).to_string())
print(f"decision={decision}")
