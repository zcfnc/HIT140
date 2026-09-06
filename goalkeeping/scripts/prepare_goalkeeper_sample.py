"""Step 2: Select one eligible goalkeeper per team for analysis."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MERGED_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_merged.csv"
OUTPUT_FILE = PROJECT_ROOT / "data_clean" / "goalkeeper_analysis_sample.csv"

TARGET_GROUPS = ["Knockout", "Group Stage Eliminated"]


goalkeeper_merged_df = pd.read_csv(MERGED_FILE)

study_frame_df = goalkeeper_merged_df.loc[
    goalkeeper_merged_df["progression_group"].isin(TARGET_GROUPS)
].copy()

eligible_goalkeepers_df = study_frame_df.loc[
    study_frame_df["save_pct"].notna() & (study_frame_df["minutes"] >= 90)
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

group_counts = analysis_df["progression_group"].value_counts()
checks = {
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

if any(checks[key] != value for key, value in expected_checks.items()):
    raise ValueError("Final sample validation failed. Review the source data and locked rules.")

analysis_df.to_csv(OUTPUT_FILE, index=False)

print(pd.Series(checks).to_string())
