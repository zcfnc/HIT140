# Keke – Team Defence Performance

## Analytic question

During the group stage, was mean goals conceded per match different between teams that subsequently reached the knockout stage and teams eliminated in the group stage?

The primary outcome uses group-stage matches only. This preserves temporal order and avoids adding post-qualification matches to the defensive outcome.

## Folder contents

- `Keke_Defence_Performance_Analysis.ipynb` – complete reproducible analysis.
- `DATA/defence.xlsx` – original FIFA team-statistics download.
- `DATA/fbref_world_cup_2026_scores_fixtures_raw.txt` – original FBref fixture export.
- `DATA/keke_defence_final_dataset.xlsx` – validated final team-level dataset and audit sheets.
- `outputs/Figure_1_Group_Stage_Defence_Boxplot.png` – presentation-ready group comparison.
- `outputs/Figure_2_Team_Level_Defence.png` – team-level distribution figure.
- `outputs/Figure_3_Normality_QQ_Plots.png` – assumption diagnostic.
- `Keke_Progress_and_Decision_Log.md` – progress, decisions, checks and contribution record.
- `requirements.txt` – tested Python package versions.

## How to reproduce

1. Open `Keke_Defence_Performance_Analysis.ipynb` from this folder.
2. Select a Python environment containing the packages in `requirements.txt`.
3. Run all cells from top to bottom.
4. Confirm that the cross-source and final-workbook validation prints `PASS`.
5. Confirm that the three figures are written to the `outputs` folder.

## Main result

The knockout group conceded 1.052 group-stage goals per match on average, compared with 2.375 for teams eliminated in the group stage. The estimated difference was -1.323 goals per match, with a 95% Welch confidence interval of [-1.936, -0.710]. Welch's two-sample t-test gave t = -4.487, df = 20.893 and p = 0.0002. Hedges' g was -1.577. Bootstrap and permutation sensitivity checks supported the same conclusion.

The result shows an association within this tournament; it does not establish causation.

## HD rubric alignment

- Non-trivial, timing-aware analytic question.
- Useful derived variables created from match-level data.
- Two-source acquisition, cleaning, reshaping and validation.
- Explicit eligibility and sampling method.
- Descriptive statistics and confidence intervals.
- Welch two-sample t-test with assumptions and limitations.
- Effect size, bootstrap interval and permutation sensitivity check.
- High-resolution figures and a presentation-ready narrative.
- Maintained contribution and decision documentation.

## Team evidence still required

To demonstrate the Collaboration and Documentation criterion, commit these files to the team GitHub/shared workspace with clear messages, keep the decision log current, and post concise progress updates in Teams. The repository and Teams history provide evidence that cannot be created by the analysis files alone.
