# Equivalence Study 2021
------------------------
Code and supplementary material for the paper **Representation-Induced Algorithmic Bias**
Accepted to AJCAI21 as a regular paper (ajcai2021.net).
Was delayed by several months (covid) so 2021 conference is being held in Febraury 2022.



[Edit 01/02/2022]
Added pre-print of paper, supplementary material, poster, and video presentation to docs/
Conference is tmrw so expect the proceedings to be published sometime soon. Will update with official link when that happens.
- previous version of R&G model had three typos (games g431, g256, g141) where one digit in each matrix was wrong. this part of the model was not being used in this study so this work is not affected. Correction has been made to the file.

[Edit 04/10/2021]
- Created new release with modified line in one algorithm as per edit below
- Added _RepresentationInducedAlgorithmicBias-Supplementary-Material-A.pdf_


[Edit 28/09/2021]
- Paper was submitted and accepted and is approaching camera-ready. 
More detail will be posted here as _RepresentationInducedAlgorithmicBias-Supplementary-Material-A.pdf_. 
- Will add a new release to this repository as I found a typo/error in a variable name (s/self.prev_state/self.state/) in one algorithm's action-selection mechanism. It doesn't appear to change the algorithm's behaviour in respect of the hypothesis presented in the paper (non-variance) since it (the algorithm) is processing as before, but from one step back in time. This is debateable sure, as is the literature maybe. Regardless, the low number of possible states in these game environments makes for long cycles. The affected algorithm still displays a ~similar level of variance across the four gameform representations as before. The experiments have been re-run, tables updated, and _the conclusions reached in the paper remain_. 
- Edited the appropriate file in the release codebase and committed the change 01/02/2022

[Edit 20/08/2021 and older]
This codebase is for a paper on behavioural equivalence in learning algorithms (submitted, will update details if accepted)

## Overview
The equivalence study relies on selfplay_parameter_study experiment type files in run_exp/ and run_obs/.
Files in those locations for running alternative experiment types (e.g., tournament, selfplay) have been removed.
__USER__ and __USER_EMAIL__ system identifiers have been de-identified. .Rmd file maintains author.

### Visualisation of a behavioural profile as a faceted 3D Surface Map
![3D Surface Map of Q-Learning game outcomes](https://github.com/simoncstanton/equivalence_study/blob/main/docs/exp_id_127288_q-learning-pd-scalar_selfplay_parameter_study.png?raw=true)

### Visualisation of comparison of 2 behavioural profiles as boxplot of distribution of game outcomes with Wilcoxon
![Boxplot equivalence Q-Learning - Wilcoxon](https://github.com/simoncstanton/equivalence_study/blob/main/docs/compare_transforms_qlearning_127288_132060_facet_boxplot_paired_lines.png?raw=true)

### Visualisation of comparison of 2 behavioural profiles as boxplot of distribution of game outcomes
![Boxplot equivalence Q-Learning](https://github.com/simoncstanton/equivalence_study/blob/main/docs/compare_transforms_qlearning_127288_132060_grouped_boxplot.png?raw=trueE)

## agent_model_hpc
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
- run_obs/ 
  - requires natsort
  - individual files may require plotly, pandas, matplotlib, seaborn
