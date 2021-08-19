#!/usr/bin/env python3
'''
    obs_compile_views_selfplay

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

from run_obs.view_components import obs_generate_view_ts_o as ts_outcomes
from run_obs.view_components import obs_generate_view_ts_r as ts_rewards
from run_obs.view_components import obs_generate_view_ep_r_table_rewards as ep_rewards
from run_obs.view_components import obs_generate_view_ep_o_table_outcomes as ep_outcomes
from run_obs.view_components import obs_generate_view_ts_outcome_v_reward as outcome_v_reward


def main(argv):
    
    
    ts_outcomes.main(argv[1:])
    ts_rewards.main(argv[1:])
    ep_rewards.main(argv[1:])
    ep_outcomes.main(argv[1:])
    outcome_v_reward.main(argv[1:])







if __name__ == '__main__':
    main(sys.argv)  