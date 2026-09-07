import pandas as pd
import numpy as np

# Located data files
RAW_DIR       = "Raw Data"
SHOOTING_FILE = f"{RAW_DIR}/Shooting.csv"          # Shooting -> included SoT
STANDARD_FILE = f"{RAW_DIR}/Standard Stats.csv"    # Standard -> included Minutes, Age, Position, etc

# Start setting
MIN_MINUTES = 90     # MINIMUM_MINUTES = 90     
MAX_AGE     = 30     # "UNDER 30" = Age < 30

# Data source information
SOURCE_URL = "https://fbref.com/en/comps/1/stats/World-Cup-Stats"   
SOURCE_URL2 = "https://fbref.com/en/comps/1/shooting/World-Cup-Stats"
RETRIEVED  = "2026-08-31"

# Row 0 = source URL, row 1 = category band, row 2 = real column names
shooting = pd.read_csv(SHOOTING_FILE, header=2)
standard = pd.read_csv(STANDARD_FILE, header=2)

# Remove the first row if header is duplicate
shooting = shooting[shooting["Player"] != "Player"]
standard = standard[standard["Player"] != "Player"]

print("Shooting:", shooting.shape)
print("Standard:", standard.shape)
shooting.head(3)

KEY = ["Player", "Squad"]

# 1. Key in each table is unique?
print("Key_Shooting:", shooting.duplicated(subset=KEY).sum())
print("Key_Standard:", standard.duplicated(subset=KEY).sum())

# 2. Is gKey in each table the same?
print("\nSquad sample - Shooting:", repr(shooting["Squad"].iloc[0]))
print("Squad sample - Standard:", repr(standard["Squad"].iloc[0]))

# 3. How many players in Shooting are also in Standard? How many are not?
key_sh = set(zip(shooting["Player"], shooting["Squad"]))
key_st = set(zip(standard["Player"], standard["Squad"]))
print(f"\nKey_Shooting: {len(key_sh)}")
print(f"Key_Standard: {len(key_st)}")
print(f"Key_Shooting & Key_Standard: {len(key_sh & key_st)}")
print(f"Key_Shooting - Key_Standard: {len(key_sh - key_st)}")

if key_sh - key_st:
    print("Sample is not correct:", list(key_sh - key_st)[:5])
    
standard_cols = standard[["Player", "Squad", "MP", "Starts", "Min"]]

df = shooting.merge(standard_cols, on=KEY, how="left", validate="one_to_one")

print(f"Close before merge: {len(shooting)}")
print(f"Close after merge: {len(df)}")
print(f"Equal: {len(shooting) == len(df)}")
print(f"Min missing: {df['Min'].isna().sum()}")

num_cols = ["Age", "Min", "MP", "Starts", "90s", "SoT", "Sh", "Gls"]

for c in num_cols:
    df[c] = pd.to_numeric(
        df[c].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

print(df[num_cols].dtypes)
print("\nThe number of missing values:")
print(df[num_cols].isna().sum())

lech = (df["Min"] - df["90s"] * 90).abs()
print(f"The maximum deviation: {lech.max():.1f} phut")
print(f"The number of rows with deviation > 5 phut: {(lech > 5).sum()}   <-- nen bang 0")

log = []

def step(name, data):
    """Count the number of rows in the data and log the step"""
    log.append({"step": name, "rows": len(data)})
    print(f"{name:.<45} {len(data):>5}")
    return data

print("process\n" + "=" * 52)

d = step("0. Data after merge", df)

# 'FW' players
d = step("1. 'FW' players", d[d["Pos"].str.contains("FW", na=False)])

# Remove DFFW players
d = step("2. Remove DFFW", d[d["Pos"] != "DFFW"])

# Under 30 years old
d = step(f"3. Age < {MAX_AGE}", d[d["Age"] < MAX_AGE])

# Play at least 90 minutes
d = step(f"4. Min >= {MIN_MINUTES}", d[d["Min"] >= MIN_MINUTES])

print("=" * 52)

d = d.copy()

d["group"]  = np.where(d["Pos"] == "FW", "Striker", "Forward-Midfielder")
d["sot90"] = d["SoT"] / (d["Min"] / 90)

# Check the difference between calculated sot90 and FBref's SoT/90
check = (d["sot90"] - pd.to_numeric(d["SoT/90"], errors="coerce")).abs()
print(f"Not match with column SoT/90: max {check.max():.3f}")
print("(difference is small and normal since FBref calculates from 90s and rounds)\n")

print("Group sizes:")
print(d["group"].value_counts())
print(f"\nTotal N = {len(d)}")

cols_giu = ["Player", "Squad", "Pos", "group", "Age",
            "MP", "Starts", "Min", "Sh", "SoT", "sot90"]

population = d[cols_giu].reset_index(drop=True)
population.to_csv("Forward_u30.csv", index=False)

print(f"Save {len(population)} dong vao Forward_u30.csv\n")
pd.DataFrame(log)