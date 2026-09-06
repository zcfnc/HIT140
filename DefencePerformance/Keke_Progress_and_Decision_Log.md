# Keke – Progress and Decision Log

## 2 September 2026 – Data acquisition

- Downloaded and retained the original FIFA team statistics workbook.
- Downloaded and retained the FBref Scores & Fixtures export.
- Recorded both source URLs in the final workbook and Notebook.

## 2 September 2026 – Data wrangling

- Repaired the alternating statistics/team-name structure in the copied FIFA table.
- Removed blank separator rows from the FBref export.
- Standardised country-code labels and the Bosnia and Herzegovina team name.
- Parsed score fields without counting penalty-shootout tallies as match goals.
- Reshaped 104 matches into 208 team–match records.
- Confirmed that FIFA and FBref both produced 308 tournament goals conceded.

## 2 September 2026 – HD review and analytic refinement

- Identified that an all-tournament outcome would include matches played after qualification.
- Restricted the primary outcome to 72 group-stage matches / 144 team–match records.
- Derived group-stage goals conceded per match, clean-sheet rate and goal difference per match.
- Kept the pre-specified two-sided comparison between later progression groups.

## 2 September 2026 – Statistical analysis

- Calculated group descriptive statistics and confidence intervals.
- Checked IQR outliers, Q–Q plots, Shapiro–Wilk normality and Levene variance equality.
- Used Welch's two-sample t-test because group variances differed.
- Reported mean difference, 95% confidence interval, t-statistic, degrees of freedom and p-value.
- Added Hedges' g, a bootstrap confidence interval and a permutation sensitivity test.

## 2 September 2026 – Quality review

- Confirmed all 48 teams had three group-stage matches and complete primary outcomes.
- Confirmed the Notebook reproduces the final Excel dataset.
- Executed every code cell successfully.
- Visually reviewed all three exported figures.
- Documented limitations and restricted the conclusion to association rather than causation.

## Team update to post

I have completed the HD-focused revision of the Team Defence Performance analysis. I changed the primary outcome to group-stage goals conceded per match so that later knockout matches do not contaminate the pre-qualification comparison. The workflow now documents two-source wrangling, 208 team–match records, sampling, assumptions, Welch's t-test, confidence intervals, effect size and robustness checks. The cleaned workbook, Notebook, figures, README and decision log are ready in the DefencePerformance folder. Please review the revised question and let me know if any integration changes are needed for the final presentation.

## Ongoing review record

Add a dated entry here whenever a teammate reviews the analysis, a decision changes, or presentation content is updated. Include the reviewer, issue raised, decision and action taken.
