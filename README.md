# Equivalence Study 2021
The equivalence study relies on selfplay_parameter_study experiment type files in run_exp/ and run_obs/
Files in those locations for running alternative experiment types (e.g., tournament, selfplay) have been removed.
__USER__ and __USER_EMAIL__ system identifiers have been de-identified. .Rmd file maintains author.

## Visualisation of a behavioural profile as a faceted 3D Surface Map
![3D Surface Map of Q-Learning game outcomes](https://raw.githubusercontent.com/simoncstanton/equivalence_study/6149b5632cd9ed884db6a0294d593aeb9967f71b/docs/exp_id_127288_q-learning-pd-scalar_selfplay_parameter_study.png?token=AUEDDAISHAT23ANNCKQKX43BD3NTM)

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
