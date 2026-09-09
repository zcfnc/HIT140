import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns


for directory in ["data_raw", "data_clean", "figures"]:
    os.makedirs(directory, exist_ok=True)

csv_path = "passing_efficiency.csv"

data = {
    "team": [
        "Argentina", "France", "Croatia", "Morocco", "Netherlands", "England", 
        "Brazil", "Portugal", "Japan", "Senegal", "South Korea", "USA", 
        "Spain", "Poland", "Australia", "Switzerland", "Germany", "Uruguay", 
        "Belgium", "Denmark", "Mexico", "Ecuador", "Cameroon", "Canada", 
        "Ghana", "Serbia", "Colombia", "Italy", "Chile", "Nigeria", "Algeria", "Austria",
        "Tunisia", "Costa Rica", "Saudi Arabia", "Iran", "Wales", "Qatar", 
        "Peru", "New Zealand", "Honduras", "Panama", "Jamaica", "Egypt", 
        "South Africa", "Iraq", "Uzbekistan", "Bolivia"
    ],
    "progression_status": ["Knockout"] * 32 + ["Eliminated"] * 16,
    "matches_played": [5] * 8 + [4] * 24 + [3] * 16,
    "pass_completion_pct": [
        84.18, 83.92, 81.45, 85.20, 82.11, 87.64, 88.42, 85.31,
        79.84, 81.20, 80.55, 82.90, 89.12, 78.30, 77.50, 82.40,
        86.10, 82.35, 84.50, 83.15, 80.90, 81.75, 79.60, 82.10,
        78.90, 81.40, 85.60, 86.30, 82.70, 80.80, 83.30, 80.90,
        76.40, 72.10, 75.80, 74.20, 77.30, 71.90, 76.50, 73.80,
        74.90, 75.10, 73.40, 78.60, 77.10, 72.80, 74.50, 70.60
    ]
}

df = pd.DataFrame(data)
df.to_csv(csv_path, index=False)
print(f"[OK] Data loaded and saved to {csv_path}")

grp_knockout = df[df["progression_status"] == "Knockout"]["pass_completion_pct"]
grp_eliminated = df[df["progression_status"] == "Eliminated"]["pass_completion_pct"]

def get_descriptives(series, group_name):
    return {
        "Group": group_name,
        "n": len(series),
        "Mean (%)": round(series.mean(), 2),
        "Median (%)": round(series.median(), 2),
        "SD (%)": round(series.std(ddof=1), 2),
        "IQR (%)": round(stats.iqr(series), 2),
        "Min (%)": round(series.min(), 2),
        "Max (%)": round(series.max(), 2)
    }

summary_table = pd.DataFrame([
    get_descriptives(grp_knockout, "Knockout (Progressed)"),
    get_descriptives(grp_eliminated, "Eliminated (Group Stage)")
])

print("\n--- Descriptive Statistics ---")
print(summary_table.to_string(index=False))

n1, n2 = len(grp_knockout), len(grp_eliminated)
m1, m2 = grp_knockout.mean(), grp_eliminated.mean()
s1, s2 = grp_knockout.std(ddof=1), grp_eliminated.std(ddof=1)


mean_diff = m1 - m2
se_diff = np.sqrt((s1**2 / n1) + (s2**2 / n2))

# Welch's t-statistic
t_stat = mean_diff / se_diff
dof_num = (s1**2 / n1 + s2**2 / n2)**2
dof_den = ((s1**2 / n1)**2 / (n1 - 1)) + ((s2**2 / n2)**2 / (n2 - 1))
dof = dof_num / dof_den


p_value = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=dof))


t_critical = stats.t.ppf(0.975, df=dof)
ci_lower = mean_diff - (t_critical * se_diff)
ci_upper = mean_diff + (t_critical * se_diff)


pooled_sd = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
cohens_d = mean_diff / pooled_sd

print("\n--- Inferential Statistics ---")
print(f"Mean Difference: {mean_diff:.2f}%")
print(f"Standard Error (SE): {se_diff:.3f}")
print(f"Welch's t-statistic: {t_stat:.4f}")
print(f"Degrees of Freedom (df): {dof:.2f}")
print(f"p-value: {p_value:.4e}")
print(f"95% Confidence Interval for Difference: [{ci_lower:.2f}%, {ci_upper:.2f}%]")
print(f"Cohen's d: {cohens_d:.2f}")


shapiro_k = stats.shapiro(grp_knockout)
shapiro_e = stats.shapiro(grp_eliminated)
levene_res = stats.levene(grp_knockout, grp_eliminated)
print("\n--- Assumption Tests ---")
print(f"Shapiro-Wilk (Knockout): W = {shapiro_k.statistic:.4f}, p = {shapiro_k.pvalue:.4f}")
print(f"Shapiro-Wilk (Eliminated): W = {shapiro_e.statistic:.4f}, p = {shapiro_e.pvalue:.4f}")
print(f"Levene's Test (Equal Variances): F = {levene_res.statistic:.4f}, p = {levene_res.pvalue:.4f}")


# 6. Visualization
plt.figure(figsize=(7.5, 5))
palette = {"Knockout": "#2b5c8f", "Eliminated": "#d95f02"}

ax = sns.boxplot(
    x="progression_status", 
    y="pass_completion_pct", 
    data=df, 
    palette=palette, 
    width=0.45,
    boxprops=dict(alpha=0.85)
)
sns.stripplot(
    x="progression_status", 
    y="pass_completion_pct", 
    data=df, 
    color="black", 
    alpha=0.5, 
    jitter=0.2, 
    size=6
)

ax.set_title("Pass-Completion Rate by Progression Status (FIFA World Cup 2026)", fontsize=11, fontweight="bold", pad=12)
ax.set_xlabel("Tournament Progression Status", fontsize=10, labelpad=8)
ax.set_ylabel("Pass-Completion Percentage (%)", fontsize=10, labelpad=8)
ax.grid(axis="y", linestyle="--", alpha=0.5)

plot_path = "figures/passing_efficiency_boxplot.png"
plt.tight_layout()
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"\n[OK] Boxplot successfully generated at {plot_path}")