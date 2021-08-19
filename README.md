# Equivalence Study 2021
The equivalence study relies on selfplay_parameter_study experiment type files in run_exp/ and run_obs/
Files in those locations for running alternative experiment types (e.g., tournament, selfplay) have been removed.
__USER__ and __USER_EMAIL__ system identifiers have been de-identified. .Rmd file maintains author.

## Visualisation of a behavioural profile as a faceted 3D Surface Map
![3D Surface Map of Q-Learning game outcomes](https://github.com/simoncstanton/equivalence_study/blob/main/docs/exp_id_127288_q-learning-pd-scalar_selfplay_parameter_study.png?raw=true)

## Visualisation of comparison of 2 behavioural profiles as boxplot of distribution of game outcomes with Wilcoxon
![Boxplot equivalence Q-Learning - Wilcoxon](https://github.com/simoncstanton/equivalence_study/blob/main/docs/compare_transforms_qlearning_127288_132060_facet_boxplot_paired_lines.png?raw=true)

## Visualisation of comparison of 2 behavioural profiles as boxplot of distribution of game outcomes
![Boxplot equivalence Q-Learning](https://github.com/simoncstanton/equivalence_study/blob/main/docs/compare_transforms_qlearning_127288_132060_grouped_boxplot.png?raw=trueE)

# agent_model_hpc
Agent Model for R&amp;G topology on HPC
- PBS, and local python env
- Parallelization via PBS jobarray

.gitignore
- exclude /results/ 
  - takes a lot of space and changes
  - to run model, requires (some-maybe all) sub-directories in results/ to exist (see /agent_model_hpc/config/agent_model_hpc_config.json)


Python dependencies
- agent_model/, run_exp/
  - numpy
  - natsorted
- run_obs/ requires* plotly, pandas, matplotlib, seaborn (*mostly)
