import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Question: Is there a difference in Shots on Target per 90 between Strikers and Forward-Midfielders?
# H0: mu_striker = mu_fwmf  (No difference)
# Ha: mu_striker != mu_fwmf (There is a difference)
# Two-tailed test, alpha = 0.05

ALPHA = 0.05
SEED = 42

# Stratified random sampling with PROPORTIONAL ALLOCATION (n = 80 total).
N_STRIKER = 48
N_FWMF = 32

# Load the dataset
df = pd.read_csv("Forward_u30.csv").dropna(subset=["sot90"])

striker_pop = df[df["group"] == "Striker"]["sot90"]
fwmf_pop = df[df["group"] == "Forward-Midfielder"]["sot90"]

# POPULATION vs SAMPLE
# The population is finite and small, so the sampling fraction must be reported.
print("--- POPULATION AND SAMPLING ---")
print(f"Population N (Striker)          : {len(striker_pop)}")
print(f"Population N (Forward-Midfielder): {len(fwmf_pop)}")

# Proportional allocation is used because:
#   It preserves the 63:43 structure of the population.
#   It balances the sampling fractions across the two strata (76% vs 74%),
#   instead of 63% vs 93% under equal allocation.
#   Because the group variances are unequal (S = 0.707 vs 0.566), the optimal
#   split for comparing two means is n1/n2 = S1/S2 = 1.25, i.e. about 44/36.
# random_state ensures the sample is reproducible.
striker = striker_pop.sample(n=N_STRIKER, random_state=SEED).values
fwmf = fwmf_pop.sample(n=N_FWMF, random_state=SEED).values

print(f"\nSample n (Striker)              : {N_STRIKER}")
print(f"Sample n (Forward-Midfielder)   : {N_FWMF}")
print(f"Sampling fraction (Striker)     : {N_STRIKER / len(striker_pop):.1%}")
print(f"Sampling fraction (Fwd-Mid)     : {N_FWMF / len(fwmf_pop):.1%}")
print("NOTE: high sampling fractions -> see limitations (finite population).")

# Measures of Central Tendency & Dispersion
def compute_descriptive_stats(data, name):
    n = len(data)
    mean_val = np.mean(data)
    median_val = np.median(data)
    s_squared = np.var(data, ddof=1)
    s = np.std(data, ddof=1)
    data_range = np.max(data) - np.min(data)

    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25

    return {
        "Group": name, "n": n,
        "Mean": mean_val, "Median": median_val,
        "Variance": s_squared, "Std Dev": s,
        "Range": data_range, "IQR": iqr
    }

print("\n--- MEASURES OF CENTRAL TENDENCY & DISPERSION ---")
desc_df = pd.DataFrame([
    compute_descriptive_stats(striker, "Striker"),
    compute_descriptive_stats(fwmf, "Forward-Midfielder")
])
print(desc_df.to_string(index=False))

# ASSUMPTION CHECKS
# 1. Independence: one row per player, satisfied by design. Random sampling: satisfied by the stratified draw above.
#    Normality: Shapiro-Wilk on each group. Equal variances: Levene's test -> decides Student vs Welch.
print("\n--- ASSUMPTION CHECKS ---")

for data, name in [(striker, "Striker"), (fwmf, "Forward-Midfielder")]:
    W, p_shapiro = stats.shapiro(data)
    verdict = "not normal" if p_shapiro < ALPHA else "consistent with normal"
    print(f"Shapiro-Wilk {name:15s}: W = {W:.4f}, p = {p_shapiro:.4f}  ({verdict})")

levene_stat, p_levene = stats.levene(striker, fwmf, center="median")
equal_var = p_levene >= ALPHA
print(f"\nLevene's test: statistic = {levene_stat:.4f}, p = {p_levene:.4f}")
print(f"-> variances are {'equal' if equal_var else 'unequal'}, "
      f"so {'Student' if equal_var else 'Welch'}'s t-test is appropriate.")

# Two-Sample t-Test
n1, n2 = len(striker), len(fwmf)
mean1, mean2 = np.mean(striker), np.mean(fwmf)
s1, s2 = np.std(striker, ddof=1), np.std(fwmf, ddof=1)

# Welch standard error: variances are NOT pooled
se_diff = np.sqrt((s1**2 / n1) + (s2**2 / n2))
t_star = (mean1 - mean2) / se_diff

# Welch-Satterthwaite degrees of freedom
df_welch = (s1**2 / n1 + s2**2 / n2) ** 2 / (
    (s1**2 / n1) ** 2 / (n1 - 1) + (s2**2 / n2) ** 2 / (n2 - 1)
)

p_value = stats.t.sf(np.abs(t_star), df_welch) * 2

print("\n--- TWO-SAMPLE t-TEST RESULTS (Welch) ---")
print(f"t-statistic (t*): {t_star:.4f}")
print(f"Degrees of freedom (df): {df_welch:.2f}")
print(f"p-value: {p_value:.4f}")

# Cross-check the manual calculation against scipy
t_scipy, p_scipy = stats.ttest_ind(striker, fwmf, equal_var=False)
print(f"Cross-check (scipy): t = {t_scipy:.4f}, p = {p_scipy:.4f}")

# Effect size
# Cohen's d does not depend on sample size
# Question: "is the difference large enough to matter on the pitch?"
pooled_sd = np.sqrt((s1**2 + s2**2) / 2)
cohens_d = (mean1 - mean2) / pooled_sd
size = "small" if abs(cohens_d) < 0.5 else "medium" if abs(cohens_d) < 0.8 else "large"
print(f"\nCohen's d: {cohens_d:.4f} ({size} effect)")

# 95% Confidence Intervals
# The t distribution is used (NOT z) because sigma is unknown and
# is estimated from the sample.
def compute_ci(mean, s, n, conf=0.95):
    t_crit = stats.t.ppf((1 + conf) / 2, n - 1)
    margin_of_error = t_crit * (s / np.sqrt(n))
    return mean - margin_of_error, mean + margin_of_error

ci_striker = compute_ci(mean1, s1, n1)
ci_fwmf = compute_ci(mean2, s2, n2)

print("\n--- 95% CONFIDENCE INTERVALS ---")
print(f"Striker:            [{ci_striker[0]:.4f}, {ci_striker[1]:.4f}]")
print(f"Forward-Midfielder: [{ci_fwmf[0]:.4f}, {ci_fwmf[1]:.4f}]")

# CI for the DIFFERENCE of means (uses Welch df)
diff = mean1 - mean2
moe_diff = stats.t.ppf(1 - ALPHA / 2, df_welch) * se_diff
print(f"Difference:         [{diff - moe_diff:.4f}, {diff + moe_diff:.4f}]")
print("(if this interval excludes 0, H0 is rejected at alpha = 0.05)")

# Visualisation
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

axes[0].boxplot([striker, fwmf], tick_labels=["Striker", "Forward-Midfielder"],
                showmeans=True)
axes[0].set_title("Shots on target per 90 by role")
axes[0].set_ylabel("Shots on target per 90 minutes")

axes[1].hist(striker, bins=12, alpha=0.55, label=f"Striker (n={n1})")
axes[1].hist(fwmf, bins=12, alpha=0.55, label=f"Forward-Midfielder (n={n2})")
axes[1].set_title("Distribution by role")
axes[1].set_xlabel("Shots on target per 90 minutes")
axes[1].set_ylabel("Number of players")
axes[1].legend()

plt.tight_layout()
plt.savefig("attacking_threat_comparison.png", dpi=150, bbox_inches="tight")
plt.show()

# SENSITIVITY CHECK
# The population is small (N = 106), so the result may depend on which players happen to be drawn. Two things are varied here to test how stable it is:
#   (a) the allocation rule (proportional 48/32 vs equal 40/40)
#   (b) the random seed
# ALL results are reported, not just the most favourable one.
def run_test(n_a, n_b, seed):
    a = striker_pop.sample(n=n_a, random_state=seed).values
    b = fwmf_pop.sample(n=n_b, random_state=seed).values
    sa, sb = np.std(a, ddof=1), np.std(b, ddof=1)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    d = (np.mean(a) - np.mean(b)) / np.sqrt((sa**2 + sb**2) / 2)
    se = np.sqrt(sa**2 / n_a + sb**2 / n_b)
    return {"Allocation": f"{n_a}/{n_b}", "Seed": seed,
            "SE(diff)": se, "t": t, "p": p, "Cohen's d": d}

print("\n--- SENSITIVITY CHECK ---")
rows = [run_test(N_STRIKER, N_FWMF, SEED), run_test(40, 40, SEED)]
for s in [1, 7, 99, 2026]:
    rows.append(run_test(N_STRIKER, N_FWMF, s))

sens = pd.DataFrame(rows)
print(sens.to_string(index=False,
      formatters={"SE(diff)": "{:.5f}".format, "t": "{:.3f}".format,
                  "p": "{:.4f}".format, "Cohen's d": "{:.3f}".format}))
print(f"\np ranges from {sens['p'].min():.4f} to {sens['p'].max():.4f}, "
      f"while SE(diff) barely moves "
      f"({sens['SE(diff)'].min():.5f}-{sens['SE(diff)'].max():.5f}).")
print("-> The instability comes from sampling noise in a small finite population,")
print("   NOT from a difference in efficiency between the allocation rules.")
d_col = sens["Cohen's d"]
print(f"Cohen's d stays in the {d_col.min():.2f}-{d_col.max():.2f} range "
      "(small-to-medium) throughout.")

# Conclusion
print("\n--- CONCLUSION ---")
if p_value <= ALPHA:
    print(f"p-value <= {ALPHA}. Sufficient statistical evidence to reject H0.")
    print("Conclusion: there is a difference in SoT90 between Strikers and Forward-Midfielders.")
else:
    print(f"p-value > {ALPHA}. Insufficient statistical evidence to reject H0.")
    print("Conclusion: cannot conclude that there is a difference in SoT90 between the two groups.")
print(f"Effect size (Cohen's d) = {cohens_d:.3f} ({size}).")