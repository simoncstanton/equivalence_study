#!/usr/bin/env python3
# file: obs_compile_exp_timestep_rewards.py
'''
    obs_compile_exp_timestep_rewards

    usage: python -m obs_compile_exp_timestep_rewards -j __STR__ -z false -l true
        
        - option -j is __EXP_ID__
        
        - option -z only required if setting to true (default is false). 
            - flips flag to write data as compressed files (json.gz and csv.gz)
            
        - option -l (localhost, ie computer other than PBS/HPC) 
            - only required if setting to true (default is false)
            - used for setting basepath
            
        nominative key
            eo_ts_r   [experiment observation episode rewards]       
        
        Activity
        
        - analyses rewards across a set of episodes (minimum == 1) across a set of subjobs (minimum ==1) for both agents
            
            - for each subjob
                
                - extract episode reward data
                
                    - for each agent
                        - terminal sum per episode 
                            (agent_0_terminal_sum, agent_1_terminal_sum)
                        - terminal mean of sum across all episodes in a subjob for each agent
                            (agent_0_e_mean_terminal_sum, agent_1_e_mean_terminal_sum)
                        
                    - mean across both agents
                        - terminal sum per episode
                            (a_mean_terminal_sum)
                        - terminal mean of sum across all episodes in a subjob
                            (a_mean_e_mean_terminal_sum)
                         

        - perform integrity checks
        
        
'''



import sys, os, getopt

from time import process_time_ns, time_ns
from datetime import datetime

import re
import math
from natsort import natsorted

from run_obs.obs_util import Obs_utility as obs_utility

def main(argv):
    
    hpc_config = obs_utility().load_hpc_config()
    
    obs_data = initialise_obs_data()
    parse_input(argv, obs_data)
    obs_utility().set_basepath(obs_data)
    
    obs_utility().eo_ts_r_set_obs_data_start(obs_data)    
    obs_data_summary = obs_utility().retrieve_obs_data_summary(obs_data)
    
    obs_utility().make_ts_r_job_paths(obs_data, obs_data_summary)
       
    result_set_data = {}
    leaf_dir = hpc_config["exp_data_leaf_dirs"]["reward_history"]
    
    result_set_data = obs_utility().fetch_all_subjobs_result_set_data(obs_data, obs_data_summary, leaf_dir)
    create_obs_data_exp_subjob_dict(obs_data, len(obs_data_summary["obs_exp"]["exp_subjobs_list"]))
    
    
    '''
        ts_r_assemble_agent_acumm_sum()
        
    '''
    obs_utility().ts_r_assemble_agent_acumm_sum(result_set_data, obs_data, obs_data_summary)
    
    
    '''
        ts_r_assemble_agent_acumm_sum_e_mean()
        
    '''
    obs_utility().ts_r_assemble_agent_acumm_sum_e_mean(result_set_data, obs_data, obs_data_summary)


    '''
        ts_r_assemble_agent_mean_acumm_sum_e_mean()
    
    '''     
    obs_utility().ts_r_assemble_acumm_sum_e_mean_a_mean(result_set_data, obs_data, obs_data_summary)

    
    '''
        ts_r_assemble_acumm_sum_a_mean()
    
    '''    
    obs_utility().ts_r_assemble_acumm_sum_a_mean(result_set_data, obs_data, obs_data_summary)

    
    '''
        ts_r_assemble_timestep_mean()
    
    '''
    obs_utility().ts_r_assemble_timestep_mean(result_set_data, obs_data, obs_data_summary)

    
    '''
        ts_r_assemble_a_mean_timestep_mean()

    '''   
    obs_utility().ts_r_assemble_a_mean_timestep_mean(result_set_data, obs_data, obs_data_summary)

    
    '''
        ts_r_assemble_timestep_a_mean_mean_e_mean()
    
    '''
    obs_utility().ts_r_assemble_timestep_a_mean_mean_e_mean(result_set_data, obs_data, obs_data_summary)

    
    '''
        ts_r_assemble_agent_timestep_mean_e_mean()
    
    '''    
    obs_utility().ts_r_assemble_agent_timestep_mean_e_mean(result_set_data, obs_data, obs_data_summary)
    
    '''
        ts_r_assemble_timestep_mean_e_mean_a_mean()
    
    '''      
    obs_utility().ts_r_assemble_timestep_mean_e_mean_a_mean(result_set_data, obs_data, obs_data_summary)
    
    
    
    obs_utility().eo_ts_r_set_obs_data_end(obs_data, obs_data_summary)
    obs_utility().eo_ts_r_write_obs_data_summary(obs_data, obs_data_summary)
    obs_utility().eo_ts_r_write_obs_journal(obs_data, obs_data_summary)
    









def parse_input(argv, obs_data):

    try:
        options, args = getopt.getopt(argv, "hj:z:l:", ["exp_id", "compress_writes", "localhost"])
        print(os.path.basename(__file__) + ":: args", options)
    except getopt.GetoptError:
        print(os.path.basename(__file__) + ":: error in input, try -h for help")
        sys.exit(2)
        
    for opt, arg in options:
        if opt == '-h':
            print("usage: " + os.path.basename(__file__) + " \r\n \
            -j <eo_id [__EO_ID__]> | \r\n \
            -z <compress_writes> boolean (default is true) \r\n \
            -l <localhost> boolean (default is false) \r\n \
        ")
        
        elif opt in ('-j', '--pbs_jobstr'):
            obs_data["obs_exp"]["exp_parent_id"] = arg
            
        elif opt in ('-z', '--compress_writes'):
            if arg == 'true':
                obs_data["obs_invocation"]["compress_writes"] = True
        
        elif opt in ('-l', '--localhost'):
            if arg == 'true':
                obs_data["obs_invocation"]["localhost"] = True
                
             
    if obs_data["obs_exp"]["exp_parent_id"] == "":
        print(os.path.basename(__file__) + ":: error in input: exp_parent_id is required, use -j __STR__ or try -h for help")
        sys.exit(2)
        
    if not options:
        print(os.path.basename(__file__) + ":: error in input: no options supplied, try -h for help")
        
    else:
        obs_data["obs_invocation"]["obs_args"] = options


def create_obs_data_exp_subjob_dict(obs_data, sj_count):
    for sj in range(0, sj_count):
        obs_data["obs_exp"]["exp_subjobs"][str(sj)] = {
            "strategy"      : "",
            "data_files"    : {},
        }
        
def initialise_obs_data():    

    obs_time_start_ns = time_ns()
    
    return {
        "obs_id"                    : str(time_ns()),
        "eo_id"                     :   "",
        "journal_output_filename"   : "",
        "obs_exp"   : {
            "exp_parent_id"             : "",
            "obs_data_filename_prefix"  : "",
            "sj_count"                  : 0,
            "obs_subjob_data_path"      : "",
            "exp_subjobs"  : {
                "0"                     : {
                    "strategy"      : "",
                    "data_files"    : [],
                }
            }
        },
        "obs_invocation"        : {
            "filename"              : __file__,
            "obs_args"              : "",
            "obs_type"              : re.search(r"obs_([A-Za-z_\s]*)", os.path.basename(__file__))[1],
            "obs_time_start_hr"     : datetime.fromtimestamp(obs_time_start_ns / 1E9).strftime("%d%m%Y-%H%M%S"),
            "obs_time_end_hr"       : "",
            "obs_time_start_ns"     : obs_time_start_ns,
            "obs_time_end_ns"       : 0,
            "process_start_ns"      : process_time_ns(),
            "process_end_ns"        : 0,
            "compress_writes"       : False,
            "localhost"             : False,
            "home"				    : "",
            "basepath"				: "",
        },
        "integrity_checks"      : {
            "rs_length_equals_sj_count"                                 : False,
            "all_rs_sj_lengths_equal_episode_count"                     : False,
            "sj_data_per_timestep_distribution_sum_is_unity"            : False,
        }
        
    }

    
        
if __name__ == '__main__':
    main(sys.argv[1:])        