#!/usr/bin/env python3
'''

    orderset - a collection of first statistics and reports on an experiment
    
    runs all operations in each
        - obs_compile_exp_summary
        - obs_compile_exp_episode_outcomes
        - obs_compile_exp_episode_rewards
        - obs_compile_exp_timestep_outcomes
        - obs_compile_exp_timestep_rewards
        - obs_generate_exp_report
        
'''
import sys

from run_obs.orderset_components import obs_compile_exp_summary as exp_summary

from run_obs.orderset_components import obs_compile_exp_episode_outcomes as ep_outcomes
from run_obs.orderset_components import obs_compile_exp_episode_rewards as ep_rewards
from run_obs.orderset_components import obs_compile_exp_timestep_outcomes as ts_outcomes
from run_obs.orderset_components import obs_compile_exp_timestep_rewards as ts_rewards
from run_obs.orderset_components import obs_generate_exp_report as pdf


def main(argv):
    
    exp_summary.main(argv[1:])
    
    ep_outcomes.main(argv[1:])
    ep_rewards.main(argv[1:])
    ts_outcomes.main(argv[1:])
    ts_rewards.main(argv[1:])
    
    pdf.main(argv[1:])







if __name__ == '__main__':
    main(sys.argv)  