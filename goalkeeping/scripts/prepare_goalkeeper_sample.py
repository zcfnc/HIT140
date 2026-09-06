"""Step 2: Create and validate the locked goalkeeper analysis sample."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MERGED_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_merged.csv"
OUTPUT_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_analysis_sample.csv"

TARGET_GROUPS = ["Knockout", "Group Stage Eliminated"]


# Define candidate inclusion-rule summaries.
def rule_summary(dataframe, name, condition):
    rule_df = dataframe.loc[condition].copy()
    group_counts = rule_df["progression_group"].value_counts()
    team_counts = rule_df.groupby("team").size()

    return {
        "rule": name,
        "n": len(rule_df),
        "knockout_n": group_counts.get("Knockout", 0),
        "eliminated_n": group_counts.get("Group Stage Eliminated", 0),
        "excluded_n": len(dataframe) - len(rule_df),
        "teams_with_multiple_goalkeepers": (team_counts > 1).sum(),
    }


# Restrict the source data to the two planned progression groups.
goalkeeper_merged_df = pd.read_csv(MERGED_FILE)

study_frame_df = goalkeeper_merged_df.loc[
    goalkeeper_merged_df["progression_group"].isin(TARGET_GROUPS)
].copy()

# Compare the candidate inclusion rules.
valid_save_pct = study_frame_df["save_pct"].notna()

rule_summary_df = pd.DataFrame(
    [
        rule_summary(study_frame_df, "A: valid save_pct", valid_save_pct),
        rule_summary(
            study_frame_df,
            "B: valid save_pct and minutes >= 90",
            valid_save_pct & (study_frame_df["minutes"] >= 90),
        ),
        rule_summary(
            study_frame_df,
            "C: valid save_pct and shots faced >= 5",
            valid_save_pct & (study_frame_df["shots_on_target_faced"] >= 5),
        ),
        rule_summary(
            study_frame_df,
            "D: valid save_pct and match or start >= 1",
            valid_save_pct
            & ((study_frame_df["matches"] >= 1) | (study_frame_df["starts"] >= 1)),
        ),
    ]
)

# Apply the locked rule and select one highest-minute goalkeeper per team.
eligible_goalkeepers_df = study_frame_df.loc[
    valid_save_pct & (study_frame_df["minutes"] >= 90)
].copy()

analysis_df = (
    eligible_goalkeepers_df
    .sort_values(
        ["team", "minutes", "starts", "matches", "player"],
        ascending=[True, False, False, False, True],
    )
    .drop_duplicates(subset="team", keep="first")
    .copy()
)

# Validate and save the final 48-goalkeeper sample.
group_counts = analysis_df["progression_group"].value_counts()
final_checks = {
    "sample_size": len(analysis_df),
    "knockout_n": group_counts.get("Knockout", 0),
    "eliminated_n": group_counts.get("Group Stage Eliminated", 0),
    "duplicate_teams": analysis_df["team"].duplicated().sum(),
    "missing_save_pct": analysis_df["save_pct"].isna().sum(),
    "minimum_minutes": analysis_df["minutes"].min(),
}

expected_checks = {
    "sample_size": 48,
    "knockout_n": 32,
    "eliminated_n": 16,
    "duplicate_teams": 0,
    "missing_save_pct": 0,
}

if any(final_checks[key] != value for key, value in expected_checks.items()):
    raise ValueError("Final sample validation failed. Review the source data and locked rules.")

analysis_df.to_csv(OUTPUT_FILE, index=False)

print(rule_summary_df.to_string(index=False))
print(pd.Series(final_checks).to_string())
