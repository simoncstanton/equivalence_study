#!/usr/bin/env python3
# file: obs_compile_exp_timestep_outcomes.py
'''
    obs_compile_exp_timestep_outcomes
    
    usage: python -m obs_compile_exp_timestep_outcomes -j __STR__ -z false -l true
        
        - option -j is __EXP_ID__
        
        - option -z only required if setting to true (default is false). 
            - flips flag to write data as compressed files (json.gz and csv.gz)
            
        - option -l (localhost, ie computer other than PBS/HPC) 
            - only required if setting to true (default is false)
            - used for setting basepath
            
        nominative key
            eo_ts_o   [experiment observation episode outcomes]
        
        
        Activity
        
        - analyses outceoms at timestep level across a set of episodes (minimum == 1) across a set of subjobs (minimum ==1)
            
            - for each subjob
                - for each outcome
                        cc: mutual cooperation
                        cd: cooperate-defect
                        dc: defect-cooperate
                        dd: mutual defection
                        
                - extract per-timestep outcome        
                    - count
                        - for each episode
                        - mean across all episodes in a subjob                   
                    - distribution
                        - for each episode
                        - mean across all episodes in a subjob                    

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
    
    obs_utility().eo_ts_o_set_obs_data_start(obs_data)    
    obs_data_summary = obs_utility().retrieve_obs_data_summary(obs_data)
    
    obs_utility().make_ts_o_job_paths(obs_data, obs_data_summary)
       
    result_set_data = {}
    leaf_dir = hpc_config["exp_data_leaf_dirs"]["cumulative_outcome_history"]
    
    result_set_data = obs_utility().fetch_all_subjobs_result_set_data(obs_data, obs_data_summary, leaf_dir)
    create_obs_data_exp_subjob_dict(obs_data, len(obs_data_summary["obs_exp"]["exp_subjobs_list"]))
    

    '''
        - for each subjob
        
            - for all episodes
                - at each timestep
                    - cc: sum(timestep[t] outome)
                    - cd: 
                    - dc:
                    - dd: 
                    
            obs_{__EXP_ID__}_sj_{__SJ_ID__}_ts_e_total_outcome_count.csv
                
                - data shape

                    4 series: mc, dd, cd, dc
                    x = episode, y = n (where n in range(0-timesteps)
            
                        __value__ = value in exp episode data at timestep
                
                            format (rows in file)
                                cc, cd, dc, dd
                                __value__\ep_0, ... , __value__\ep_n
                                __value__\ep_0, ... , __value__\ep_n
                                __value__\ep_0, ... , __value__\ep_n
                                __value__\ep_0, ... , __value__\ep_n
            
    '''


    

    '''
        ts_o_assemble_terminal_o_count()
        
    '''
    obs_utility().ts_o_assemble_terminal_o_count(result_set_data, obs_data, obs_data_summary)
    

    '''
        ts_o_assemble_o_accum_sum_e_sum()
        
    '''
    obs_utility().ts_o_assemble_o_accum_sum_e_sum(result_set_data, obs_data, obs_data_summary) 
    
    
    '''
        ts_o_assemble_o_accum_sum_e_sum_distribution()
        
    '''    
    obs_utility().ts_o_assemble_o_accum_sum_e_sum_distribution(result_set_data, obs_data, obs_data_summary) 
    

    '''
        ts_o_assemble_o_accum_sum_e_mean()
        
    '''    
    obs_utility().ts_o_assemble_o_accum_sum_e_mean(result_set_data, obs_data, obs_data_summary)   
    

    '''
        ts_o_assemble_o_accum_sum_e_mean_distribution()
        
    '''    
    obs_utility().ts_o_assemble_o_accum_sum_e_mean_distribution(result_set_data, obs_data, obs_data_summary)     
    
    
    
    
    

    
    obs_utility().eo_ts_o_set_obs_data_end(obs_data, obs_data_summary)
    obs_utility().eo_ts_o_write_obs_data_summary(obs_data, obs_data_summary)
    obs_utility().eo_ts_o_write_obs_journal(obs_data, obs_data_summary)
    
    
    


    def integrity_checks():

        '''
            re-iterate over output data to index to exp_summary strategy field and update current obs_data
        '''

        for sj, item in sj_data_ts_e_mean_outcome_distribution.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["strategy"] = obs_data_summary["obs_exp"]["exp_subjobs"][str(sj)]["exp_summary"]["exp_invocation"]["strategy"]




        '''
            integrity checks

                note use of math.isclose()
                    in each case the error is form float addition overflow, so set abs_tol=0.000001
                    which is a greater abs value than the error (so passes), and a smaller value than any of the (tested) values in the data
                    
                [TODO] - eo_id_summary, exp_id, obs_id [chain of provenance] 
        '''
        
        # "rs_length_equals_sj_count"
        
        if len(result_set_data) == len(obs_data_summary["obs_exp"]["exp_subjobs_list"]):
            print(os.path.basename(__file__) + ":: integrity check: subjob_count match : ok")
            obs_data["integrity_checks"]["rs_length_equals_sj_count"] = True  



        # "all_rs_sj_lengths_equal_episode_count"
        
        temp_check = True
        for sj in sj_data_timestep_sum:
            for o in sj_data_timestep_sum[sj]:
            
                if len(sj_data_timestep_sum[sj][o]) != obs_data_summary["obs_exp"]["exp_episodes"]:
                    temp_check = False
        
        if temp_check:
            print(os.path.basename(__file__) + ":: integrity check: episode_count match : ok")
            obs_data["integrity_checks"]["all_rs_sj_lengths_equal_episode_count"] = True        
        


        # "sj_data_per_timestep_distribution_sum_is_unity"
        
        o_sum = 0.0
        temp_check = True
        for sj in sj_data_ts_e_mean_outcome_distribution:
            for i in range(0, obs_data_summary["obs_exp"]["exp_timesteps"]):
            
                o_sum = float(sj_data_ts_e_mean_outcome_distribution[sj]['cc'][i]) + float(sj_data_ts_e_mean_outcome_distribution[sj]['cd'][i]) + float(sj_data_ts_e_mean_outcome_distribution[sj]['dc'][i]) + float(sj_data_ts_e_mean_outcome_distribution[sj]['dd'][i])
                
                if not math.isclose(o_sum, 1, abs_tol=0.000001):
                    temp_check = False
                    print(os.path.basename(__file__) + ":: " + sj_data_ts_e_mean_outcome_distribution[sj]['cc'][i])
                    print(os.path.basename(__file__) + ":: " + sj_data_ts_e_mean_outcome_distribution[sj]['cd'][i])
                    print(os.path.basename(__file__) + ":: " + sj_data_ts_e_mean_outcome_distribution[sj]['dc'][i])
                    print(os.path.basename(__file__) + ":: " + sj_data_ts_e_mean_outcome_distribution[sj]['dd'][i])
                    print()
                    print(os.path.basename(__file__) + ":: error", o_sum, 1)
                
                o_sum = 0
                
        if temp_check:
            print(os.path.basename(__file__) + ":: integrity check: per episode mean terminal sum : ok")
            obs_data["integrity_checks"]["sj_data_per_timestep_distribution_sum_is_unity"] = True 
            
            
    
    
    

    



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