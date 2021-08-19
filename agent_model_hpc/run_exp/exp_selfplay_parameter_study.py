#!/usr/bin/env python3
'''
Symmetric Selfplay

usage: python -m run_exp.exp_selfplay_parameter_study -j __STR__ -w __STR__ -s allc -g pd -r scalar -e 10 -t 100 -p na -k true -z false -c false -l true
    
    localhost example: 
        python -m  run_exp.exp_selfplay_parameter_study -j '1111.localhost' -w 'localhost' -s allc  -g pd -r scalar -e 10 -t 100 -p 'na' -k true -z false -c false -l true
    or, 
        python -m  run_exp.exp_selfplay_parameter_study -j '1111.localhost' -w 'localhost' -s actor_critic_1ed  -g pd -r scalar -e 10 -t 100 -p 'alpha=0.1:gamma=0.2' -k true -z false -c false -l true
    
    - option -k only required if setting to true (default is false). 
        - flips flag to write agent and strategy state - can use when running very large jobs and state may enter the gigabyte + range.

    - option -z only required if setting to false (default is true). 
        - flips flag to write data as compressed files (json.gz and csv.gz).
        
    - option -c only required if setting to false (default is true). 
        - flips flag to write a timestep interval update to a central log file: obs_exp/heartbeat/agent_model.heartbeat
        - if true, on a job_array then contention may result, on single job, only one process is running so is (should be) ok.
        - if false, will write per-process hearbeat log to obs_exp/heartbeat/__PBS_PARENT_JOBID__/__PBS_JOBID__.heartbeat
        MODIFIED to writing two heartbeats - due to concurrency issues - update this documentation [TODO]
    
    - option -l (localhost, ie computer other than PBS/HPC) 
        - only required if setting to true (default is false). 
        - flips flag to write directly to experiments directory (localhost), 
            - or to __PBS_SCRATCH_DIR__ (location which is effectively mounted on execution node on PBS/HPC/cluster)
            - which is moved to experiments dir by __PBS_SCRIPT__ after completion, by PBS.
        - setting to true renders -w option redundant.
        - setting to true implie no PBS supplied __PBS_JOBID__
            - use format '__INT__.localhost' where __INT__ is some manually incremented number eg: '001'
        - setting to true writes the experiments directory directly to exp_data["job_parameters"]["job_dir"]
            - otherwise exp_data["job_parameters"]["job_dir"] contains path to -w __PBS_SCRATCH_DIR__
            
            
            
    -   PBS harness script requires parameter_input_2 dimensions.txt file in current working directory. This file is per-line pair of two parameter values where each 
          line is used as input to PBS_SUBJOB with line number as direct match to PBS_ARRAYINDEX.
            - parameter_input_2 dimensions.txt:
                0.0 0.0
                0.0 0.1
                ...
                0.0 0.9
                0.1 0.0
                0.1 0.1
                ...
                1.0 0.9
                1.0 1.0
                
                
'''

import os, sys, getopt
import re

from time import process_time_ns, time_ns
from datetime import datetime

'''
    agent_model_hpc modules
'''
import agent_model.agent as agent
import agent_model.trial as trial

from agent_model.utility import Utility as utility
from run_exp.exp_util import Exp_utility as exp_utility




def main(argv):
    
    exp_data = initialise_exp_data()
    
    parse_input(exp_data, argv)
    exp_utility().set_basepath(exp_data)
    
    exp_utility().set_exp_data_start(exp_data)
    exp_utility().make_exp_job_paths(exp_data)
    
    ''' 
       
    '''
    
    exp_selfplay_parameter_study(exp_data)
    
    ''' 
        
    ''' 
    
    exp_utility().set_exp_data_end(exp_data)
    
    exp_utility().write_exp_data_summary(exp_data)
    exp_utility().write_exp_journal_entry(exp_data)


def exp_selfplay_parameter_study(exp_data):
    
    matrix = utility().retrieve_matrix(exp_data["exp_invocation"]["gameform"], exp_data["exp_invocation"]["reward_type"])
    
    '''
        assemble the parameters for each agent's strategy
            - is same for both agents (symmetric)
            - agent context is same gameform for both agents
            - first,
                - load default strategy parameter values (memory_depth, alpha, gamma etc)
                - then,
                - override default parameter values via reading input parameters
            
    '''
    
    strategy_parameters = exp_utility().load_selfplay_parameter_study_strategy_parameters(exp_data, matrix)
    

    ''' 
        - temporary episode and timestep local variables for easy reading. 
            - the values (stored in exp_data) are considered immutable for the course of the experiment
        
    '''
    
    timesteps = exp_data["exp_invocation"]["timesteps"]
    episodes = exp_data["exp_invocation"]["episodes"]

       
    ''' 
        -------------------------------------------------------
        start all episodes
        
    '''
    exp_utility().heartbeat_start(exp_data)
    
    for e in range(episodes):
        
        print(os.path.basename(__file__) + ":: episode: ", e)
        
        '''
            - episode and timestep collections
            
        '''
        
        single_episode_outcomes_cumulative  = {"cc": [], "cd": [], "dc": [], "dd": []}
        single_episode_outcomes_timestep_map   = {"cc": [0] * timesteps, "cd": [0] * timesteps, "dc": [0] * timesteps, "dd": [0] * timesteps}
        
        
        '''
            instantiate agents
                - Re-instantiate agents at each episode start to effectively clear agent and strategy state.
                    ok for 'static' experiments, ie episodes must have exact same agent/strategy profile,
                    otherwise, can instantiate outside the episode loop, and handle state deliberately (which will be useful in later experiments)
                    
                - agents dynamically load strategy class with default values from strategy_config["default_strategy_parameters"] dictionary
                - symmetric mode so strategy and parameters are same for both agents
                - note that strategy superclass may have default parameter options - these are written to exp_data on conclusion of experiment
                
        '''
        
        agent_0 = agent.Agent(0, exp_data["exp_invocation"]["strategy"], strategy_parameters)
        agent_1 = agent.Agent(1, exp_data["exp_invocation"]["strategy"], strategy_parameters)
        
        '''
            - update exp_data summary with strategy options             [***]
                - can only do this after agents are instantiated, 
                    - cleaner to do it at the end than in the episode loop but need it set to get for filenames (written at each end of an episode) [TODO]
                    - ensures strategy superclass defaults are captured
            
        '''
    
        if not exp_data["agent_parameters"]["agent_0"]["strategy"]:
            exp_utility().set_exp_data_symmetric_agent_parameters(exp_data, [agent_0, agent_1])
        ''' 
            ---------------------------
            start single trial (1 episode)
            
                - update final timestep rewards in final_step() for both agent (in Trial.trial) 
                    This is normally done at start of each timestep in Trial.trial ( _trial.step() ), 
                    but after final timestep we do not enter _trial.step again in the timestep loop.
                
                - single_episode_outcomes_timestep_map can update by direclty mapping into the outcome 
                - single_episode_outcomes_cumulative updates all four possible outcomes with running cumulative totals,
                    so calls a helper function to abstract four lines out of this section of code.
                
                heartbeat
                    - update heartbeat write (occurs every order_of_magnitude(timesteps) - 1 timesteps)
        '''
        
        _trial = trial.Trial((agent_0, agent_1), matrix)
        
        previous_step = []
        for t in range(timesteps):
            actions = _trial.step(t, previous_step)
            previous_step = actions
 
            single_episode_outcomes_timestep_map[exp_utility().map_actions_to_semantic_outcome(actions)][t] = 1
            exp_utility().append_timestep_outcome_to_single_episode_outcomes_cumulative(single_episode_outcomes_cumulative, _trial)
            exp_utility().heartbeat(exp_data, e, t)
        
        _trial.final_step(t, previous_step)
        
        
        '''
            ^^ end single trial/episode
            ---------------------------
            then, 
            
            - update episode collections
                - per agent: total episode reward
                
            - write single episode collections
                - write agent action, reward history, strategy_state, agent_state
                - write single episode outcomes (cumulative and count)
        '''
                
        exp_utility().write_agent_history_single_episode(exp_data, [agent_0, agent_1], e)
        
        exp_utility().write_single_episode_outcomes_cumulative(exp_data, e, single_episode_outcomes_cumulative)
        exp_utility().write_single_episode_outcomes_timestep_map(exp_data, e, single_episode_outcomes_timestep_map)


    '''
        ^^ end all episodes
        ---------------------------
        then,
        
        
    '''
        
    exp_utility().heartbeat_end(exp_data) 
   
   

def parse_input(exp_data, argv):

    try:
        options, args = getopt.getopt(argv, "hj:w:s:g:r:e:t:p:k:z:c:l:", ["pbs_jobstr", "pbs_scratch_dir", "strategy", "gameform", "reward_type", "episodes", "timesteps", "parameter_string", "write_state", "compress_writes", "write_2_heartbeats", "localhost"])
        print(os.path.basename(__file__) + ":: args", options)
    except getopt.GetoptError:
        print(os.path.basename(__file__) + ":: error in input, try -h for help")
        sys.exit(2)
        
    for opt, arg in options:
    
        if opt == '-h':
            print("usage: " + os.path.basename(__file__) + " \r\n \
            -j <pbs_jobstr [__JOBSTR__]> | \r\n \
            -w <pbs_scratch_dir [__PATH__]> | \r\n \
            -s <strategy [tft|allc|qlearning|...|fictitiousplay]> | \r\n \
            -f <family [axelrod, crandall, bandit, rlmethods, all]>] \r\n \
            -g <gameform [pd|staghunt|...|chicken|g{nnn}|all_topology ]> \r\n \
            -r <reward_type [scalar|ordinal|ordinal_transform ]> \r\n \
            -e <episodes> \r\n \
            -t <timesteps> \r\n \
            -p <parameter_string ['{file}.agent_properties'|'na']> \r\n \
            -k <write_state> boolean (default is false)\r\n \
            -z <compress_writes> boolean (default is true) \r\n \
            -c <write_2_heartbeats> boolean (default is true) \r\n \
            -l <localhost> boolean (default is false) \r\n \
            - minimal: (-s) {strategy} -g {gameform} -e {n} -t {n} -p {file_name} \r\n \
            - required: -m {options} -s {strategy} -g {gameform} -e {n} -t {n} -p {} \r\n \
        ")
        
        elif opt in ('-j', '--pbs_jobstr'):
            exp_data["job_parameters"]["pbs_jobstr"] = arg
            
        elif opt in ('-w', '--pbs_scratch_dir'):
            exp_data["job_parameters"]["pbs_scratch_dir"] = arg
            
        elif opt in ('-s', '--strategy'):
            exp_data["exp_invocation"]["strategy"] = arg
            
        elif opt in ('-g', '--gameform'):
            exp_data["exp_invocation"]["gameform"] = arg
            
        elif opt in ('-r', '--reward_type'):
            exp_data["exp_invocation"]["reward_type"] = arg
            
        elif opt in ('-e', '--episodes'):
            exp_data["exp_invocation"]["episodes"] = int(arg)
            
        elif opt in ('-t', '--timesteps'):
            exp_data["exp_invocation"]["timesteps"] = int(arg)
            
        elif opt in ('-p', '--parameter_string'):
            exp_data["exp_invocation"]["parameter_string"] = arg
        
        elif opt in ('-k', '--write_state'):
            if arg == 'true':
                exp_data["exp_invocation"]["write_state"] = True
            
        elif opt in ('-z', '--compress_writes'):
            if arg == 'false':
                exp_data["exp_invocation"]["compress_writes"] = False

        elif opt in ('-c', '--write_2_heartbeats'):
            if arg == 'false':
                exp_data["exp_invocation"]["write_2_heartbeats"] = False 

        elif opt in ('-l', '--localhost'):
            if arg == 'true':
                exp_data["exp_invocation"]["localhost"] = True                 
             
    
    if not options:
        print(os.path.basename(__file__) + ":: error in input: no options supplied, try -h for help")
    else:
        exp_data["exp_invocation"]["exp_args"] = options
        
    if exp_data["job_parameters"]["pbs_jobstr"] == "":
        print(os.path.basename(__file__) + ":: error in input: pbs_jobstr is required, use -j __STR__ or try -h for help")
        sys.exit(2)
        
    if exp_data["job_parameters"]["pbs_scratch_dir"] == "" and not exp_data["exp_invocation"]["localhost"]:
        print(os.path.basename(__file__) + ":: error in input: pbs_scratch_dir is required, use -w __STR__ or try -h for help")
        sys.exit(2) 
          
    if exp_data["exp_invocation"]["strategy"] == "" and exp_data["exp_invocation"]["family"] == "":
        print(os.path.basename(__file__) + ":: error in input: strategy or family required, use -s __STR__ or try -h for help")
        sys.exit(2)
        
    if exp_data["exp_invocation"]["gameform"] == "":
        print(os.path.basename(__file__) + ":: error in input: gameform is required, use -g __STR__ or try -h for help")
        sys.exit(2)
        
    if exp_data["exp_invocation"]["reward_type"] == "":
        print(os.path.basename(__file__) + ":: error in input: reward_type is required, use -r __STR__ or try -h for help")
        sys.exit(2)
        
    if exp_data["exp_invocation"]["episodes"] == 0 or exp_data["exp_invocation"]["episodes"] == '':
        print(os.path.basename(__file__) + ":: error in input - requires episodes, use -e __INT__ or try -h for help")
        sys.exit(2)
        
    if exp_data["exp_invocation"]["timesteps"] == 0 or exp_data["exp_invocation"]["timesteps"] == '':
        print(os.path.basename(__file__) + ":: error in input - requires timesteps, use -t __INT__ or try -h for help")
        sys.exit(2)
        
    if exp_data["exp_invocation"]["parameter_string"] == "" :
        print(os.path.basename(__file__) + ":: error in input: parameter_string is required, use -p __STR__ or try -h for help")
        sys.exit(2)
    
    
def initialise_exp_data():    
    
    exp_time_start_ns = time_ns()
    
    return {
        "exp_id"                    : "",
        "journal_output_filename"   : "",
        "job_parameters"            : {
            "pbs_jobstr"            : "",
            "pbs_jobid"             : "",
            "pbs_parent_jobid"      : "",
            "pbs_sub_jobid"         : 0,
            "pbs_scratch_dir"       : "",
            "hpc_name"              : "",
            "data_filename_prefix"  : "",
            "job_dir"               : "",
            "job_args"              : "",
            "heartbeat_path"        : "",
            "journal_path"          : "",
            "heartbeat_interval"    : 0
        },
        "exp_invocation"          : {
            "filename"              : __file__,
            "exp_args"              : "",
            "exp_time_start_hr"     : datetime.fromtimestamp(exp_time_start_ns / 1E9).strftime("%d%m%Y-%H%M%S"),
            "exp_time_end_hr"       : "",
            "exp_time_start_ns"     : str(exp_time_start_ns),
            "exp_time_end_ns"       : "",
            "process_start_ns"      : process_time_ns(),
            "process_end_ns"        : 0,
            "exp_type"              : re.search(r"exp_([A-Za-z_\s]*)", os.path.basename(__file__))[1],
            "strategy"              : "",
            "gameform"              : "",
            "reward_type"           : "",
            "episodes"              : 0,
            "timesteps"             : 0,
            "parameter_string"      : "",
            "write_state"           : False,
            "compress_writes"       : True,
            "write_2_heartbeats"    : True,
            "localhost"             : False,
            "home"				    : "",
            "basepath"				: "",
        },
        "agent_parameters"          : {
            "agent_0"             : { 
                "strategy"          : "",
                "strategy_parameters" : "",
            },
            "agent_1"             : {
                "strategy"          : "",
                "strategy_parameters" : "",
            },
        },
    }

    
if __name__ == '__main__':
    main(sys.argv[1:]) 