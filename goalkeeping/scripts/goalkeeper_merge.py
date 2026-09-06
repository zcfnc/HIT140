"""Step 1: Clean goalkeeper data and merge team progression data."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_CLEAN = PROJECT_ROOT / "data_clean"

GOALKEEPER_FILE = DATA_RAW / "Goalkeeper_raw.xlsx"
PROGRESSION_FILE = DATA_RAW / "Team_Progression_raw.xlsx"
OUTPUT_FILE = DATA_CLEAN / "goalkeeper_merged.csv"

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

progression_raw_df = pd.read_excel(PROGRESSION_FILE)

progression_clean_df = progression_raw_df[
    ["team", "progressed_to_knockout", "progression_group", "final_stage"]
].copy()

progression_clean_df["team"] = (
    progression_clean_df["team"].astype("string").str.strip()
)

team_name_mapping = {
    "Bosnia–Herz": "Bosnia and Herzegovina",
    "Congo DR": "DR Congo",
    "IR Iran": "Iran",
}

goalkeeper_clean_df["team"] = goalkeeper_clean_df["team"].replace(
    team_name_mapping
)

if progression_clean_df["team"].duplicated().any():
    raise SystemExit("Fix duplicate progression teams before merging.")

goalkeeper_merged_df = pd.merge(
    goalkeeper_clean_df,
    progression_clean_df,
    on="team",
    how="left",
    validate="many_to_one",
    indicator=True,
)

if (goalkeeper_merged_df["_merge"] == "left_only").any():
    raise SystemExit("Do not continue until all left_only records are investigated.")

goalkeeper_merged_df = goalkeeper_merged_df.drop(columns="_merge")

DATA_CLEAN.mkdir(exist_ok=True)
goalkeeper_merged_df.to_csv(OUTPUT_FILE, index=False)
