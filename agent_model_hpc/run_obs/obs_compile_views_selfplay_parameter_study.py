#!/usr/bin/env python3
'''
    obs_compile_views_selfplay_parameter_study

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

from run_obs.view_components import obs_generate_view_ep_o_parameter_study as ep_outcomes




def main(argv):
    
    

    ep_outcomes.main(argv[1:])
    







if __name__ == '__main__':
    main(sys.argv)  