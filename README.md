# Equivalence Study 2021
The equivalence study relies on selfplay_parameter_study experiment type files in run_exp/ and run_obs/
Files in those locations for running alternative experiment types (e.g., tournament, selfplay) have been removed.
__USER__ and __USER_EMAIL__ system identifiers have been de-identified. .Rmd file maintains author.

# agent_model_hpc
Agent Model for R&amp;G topology on HPC
- PBS, and local python env
- Parallelization via PBS jobarray
- Paths and notification handles are environment and user specific (remember to clean forks)

.gitignore
- exclude R scripts and R-data output dirs. 
  - TODO: include individual .rmd files per-experiment type here.
- exclude /results/ 
  - takes a lot of space and changes
  - to run model, requires (some-maybe all) sub-directories in results/ to exist (see /agent_model_hpc/config/agent_model_hpc_config.json)
- exclude /notes/
  - mostly scratch files

Python dependencies
- agent_model/, run_exp/
  - numpy
  - natsorted
- run_obs/ requires* plotly, pandas, matplotlib, seaborn (*mostly)
