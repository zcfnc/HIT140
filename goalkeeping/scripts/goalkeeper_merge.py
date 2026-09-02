"""Clean goalkeeper and progression data, then validate a many-to-one merge."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_CLEAN = PROJECT_ROOT / "data_clean"

GOALKEEPER_FILE = DATA_RAW / "Goalkeeper_raw.xlsx"
PROGRESSION_FILE = DATA_RAW / "Team_Progression_raw.xlsx"
OUTPUT_FILE = DATA_CLEAN / "goalkeeper_merged.csv"


# The first four Excel rows are blank rows or webpage-export headings.
goalkeeper_raw_df = pd.read_excel(GOALKEEPER_FILE, skiprows=4)

goalkeeper_clean_df = goalkeeper_raw_df[
    ["Player", "Squad", "MP", "Starts", "Min", "SoTA", "Saves", "Save%"]
].copy()

goalkeeper_clean_df = goalkeeper_clean_df.rename(
    columns={
        "Player": "player",
        "Squad": "team",
        "MP": "matches",
        "Starts": "starts",
        "Min": "minutes",
        "SoTA": "shots_on_target_faced",
        "Saves": "saves",
        "Save%": "save_pct",
    }
)

goalkeeper_clean_df["player"] = (
    goalkeeper_clean_df["player"].astype("string").str.strip()
)

# The goalkeeper source has a country-code prefix, for example "jo Jordan".
goalkeeper_clean_df["team"] = (
    goalkeeper_clean_df["team"]
    .astype("string")
    .str.strip()
    .str.split(" ", n=1)
    .str[1]
    .str.strip()
)

numeric_columns = [
    "minutes",
    "matches",
    "starts",
    "shots_on_target_faced",
    "saves",
    "save_pct",
]

for column in numeric_columns:
    goalkeeper_clean_df[column] = pd.to_numeric(
        goalkeeper_clean_df[column], errors="coerce"
    )


# Clean and retain only progression variables needed for this project.
progression_raw_df = pd.read_excel(PROGRESSION_FILE)

progression_clean_df = progression_raw_df[
    ["team", "progressed_to_knockout", "progression_group", "final_stage"]
].copy()

progression_clean_df["team"] = (
    progression_clean_df["team"].astype("string").str.strip()
)


# These mappings are based on the observed differences between the two sources.
team_name_mapping = {
    "Bosnia–Herz": "Bosnia and Herzegovina",
    "Congo DR": "DR Congo",
    "IR Iran": "Iran",
}

goalkeeper_clean_df["team"] = goalkeeper_clean_df["team"].replace(
    team_name_mapping
)


# Check the one-record-per-team requirement before merging.
duplicate_progression_teams = progression_clean_df[
    progression_clean_df["team"].duplicated(keep=False)
]

if not duplicate_progression_teams.empty:
    print("Duplicate teams found in progression data:")
    print(duplicate_progression_teams.sort_values("team"))
    raise SystemExit("Fix duplicate progression teams before merging.")


# Compare unique team names before the merge.
goalkeeper_teams = set(goalkeeper_clean_df["team"].dropna().unique())
progression_teams = set(progression_clean_df["team"].dropna().unique())

print("Goalkeeper teams not found in progression data:")
print(sorted(goalkeeper_teams - progression_teams))

print("\nProgression teams not found in goalkeeper data:")
print(sorted(progression_teams - goalkeeper_teams))


# A team can have many goalkeepers, but only one progression record.
goalkeeper_merged_df = pd.merge(
    goalkeeper_clean_df,
    progression_clean_df,
    on="team",
    how="left",
    validate="many_to_one",
    indicator=True,
)


# Validate that every goalkeeper was matched; do not remove unmatched rows.
print("\nMerge results:")
print(goalkeeper_merged_df["_merge"].value_counts())

left_only_rows = goalkeeper_merged_df[
    goalkeeper_merged_df["_merge"] == "left_only"
]

if not left_only_rows.empty:
    print("\nUnmatched goalkeeper records requiring investigation:")
    print(
        left_only_rows[
            ["player", "team", "matches", "minutes", "_merge"]
        ].sort_values(["team", "player"])
    )
    raise SystemExit("Do not continue until all left_only records are investigated.")


goalkeeper_merged_df = goalkeeper_merged_df.drop(columns="_merge")

DATA_CLEAN.mkdir(exist_ok=True)
goalkeeper_merged_df.to_csv(OUTPUT_FILE, index=False)

print("\nMerge validation successful.")
print("Merged dataframe shape:", goalkeeper_merged_df.shape)
print("Saved merged dataset to:", OUTPUT_FILE)
