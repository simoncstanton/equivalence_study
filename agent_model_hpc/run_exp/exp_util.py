import os, sys
from pathlib import Path

from datetime import datetime
from time import process_time_ns, time_ns

import re
import math   
import json, csv, gzip
            
class Exp_utility:

    def __init__(self):
        self.hpc_config = self.load_hpc_config()
        self.strategy_config = self.load_strategy_config()
   
   # move next set of three functions to common obs exp util [TODO]
    def load_strategy_config(self): 
        with open('config/strategy_config.json') as f:
            return json.load(f)
   
    def load_hpc_config(self):
        with open('config/agent_model_hpc_config.json') as f:
            return json.load(f)    

    def load_tournament_strategy_set(self, filename):
        with open('pbs_scripts/parameter_input_files/' + filename) as f:
            return json.load(f) 



    def set_basepath(self, exp_data):

        exp_data["exp_invocation"]["home"] = str(Path.home())
        print(os.path.basename(__file__) + ":: setting home to " + exp_data["exp_invocation"]["home"])

        if exp_data["exp_invocation"]["localhost"]:
            localhost = os.sep.join(self.hpc_config["paths"]["basepath_localhost"])
            exp_data["exp_invocation"]["basepath"] = os.path.join(exp_data["exp_invocation"]["home"], localhost)
            
        else:
            hpc = os.sep.join(self.hpc_config["paths"]["basepath_hpc"])
            exp_data["exp_invocation"]["basepath"] = os.path.join(exp_data["exp_invocation"]["home"], hpc)
            
        print(os.path.basename(__file__) + ":: setting basepath to " + exp_data["exp_invocation"]["basepath"])   




    def set_exp_data_start(self, exp_data):
    
        exp_data["job_parameters"]["job_args"] = str(list(map(''.join, sys.argv[1:])))
        exp_data["job_parameters"]["pbs_jobid"], exp_data["job_parameters"]['hpc_name'] = exp_data["job_parameters"]['pbs_jobstr'].split('.', 1)
        
        if '[' in exp_data["job_parameters"]['pbs_jobid']:
            exp_data["job_parameters"]["pbs_parent_jobid"] = exp_data["job_parameters"]['pbs_jobid'].split('[', 1)[0]
            exp_data["job_parameters"]["pbs_sub_jobid"] = re.search(r"\[([0-9\s]*)\]", exp_data["job_parameters"]['pbs_jobid'])[1]
        else:
            exp_data["job_parameters"]["pbs_parent_jobid"] = exp_data["job_parameters"]['pbs_jobid']
         
        exp_data["exp_id"] = exp_data["job_parameters"]['pbs_parent_jobid'] + "_" + str(exp_data["job_parameters"]["pbs_sub_jobid"])
        
        
        '''
            create job_dir 
                - this is either 
                    - temporary __PBS_SCRATCH_DIR__/{__PBS_PARENT_JOBID__}_{__PBS_SUBJOB__}/ 
                        - (after execution, is moved from scratch volume to home results directory by enclosing __PBS_SCRIPT__)
                    - permanent results directory if running from localhost
            
            the path -'job_dir' is only used in execution here (this file), so we want the absolute path for ease of filehandling/directory creation.
                - on hpc this is commonly '/scratch/__USER__', but on localhost it may be a full Windows path ...
                - after this step (in obs_*) we use a relative path stored as a list [eg, exp_subjob_data_file], and add the executing files basepath for writes, as required
                    this keeps the summary json from each step (exp, obs_summary, obs_ep_o_d, etc) platform agnostic
        '''
        
        if exp_data["exp_invocation"]["localhost"]:
        
            exp_path = os.sep.join([exp_data["exp_invocation"]["exp_type"], exp_data["job_parameters"]["pbs_parent_jobid"], exp_data["exp_id"]])
            exp_data["job_parameters"]['job_dir'] = os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["experiments"]), exp_path)

        else:
        
            scratch_path = os.sep.join(exp_data["job_parameters"]['pbs_scratch_dir'].split('/'))
            exp_data["job_parameters"]['job_dir'] = os.path.join(scratch_path, exp_data["exp_id"])
        
        print(os.path.basename(__file__) + ":: set jobdir to ", exp_data["job_parameters"]['job_dir']) 
        
        exp_data["job_parameters"]["data_filename_prefix"] = self.hpc_config["exp"]["data_file_prefix"] + exp_data["exp_id"]
        # set to 2 powers less, so 1000 timesteps will write only on t ==0, t == 1000
        exp_data["job_parameters"]["heartbeat_interval"] = math.pow(10, int(math.log10(exp_data["exp_invocation"]["timesteps"])) - 1)
        exp_data["journal_output_filename"] = exp_data["job_parameters"]['data_filename_prefix'] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]


    def set_exp_data_end(self, exp_data):
        exp_time_end_ns = time_ns()
        
        exp_data["exp_invocation"]["exp_time_end_hr"] = datetime.fromtimestamp(exp_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        exp_data["exp_invocation"]["exp_time_end_ns"] = str(exp_time_end_ns)
        exp_data["exp_invocation"]["process_end_ns"] = process_time_ns()
         
            
        
    def make_exp_job_paths(self, exp_data):
        
        '''
            on hpc, this directory *has* to be made by the pbs_script calling the agent_model experiment, 
                so that the shell can move compressed data files from __PBS_SCRATCH_DIR__/ to ~/kunanyi/results/experiments/__PBS_PARENT_JOBID__/{__PBS_PARENT_JOBID__}_{__PBS_SUBJOB__}/
                If this job_path does not exist, then exit.
            
            on localhost, we can create it here, from the assigned value in exp_data["job_parameters"]['job_dir']
                see set_exp_data_start():
                    creates directory such as:  
                        ~/kunanyi/results/experiments/__EXP_TYPE__/__PBS_PARENT_JOBID__/{__PBS_PARENT_JOBID__}_{__PBS_JOBID__}/
                    or, 
                        ~/kunanyi/results/experiments/symmetric_self_play/001/001_0/
                If this job_path does not exist, then we can make it..
        '''
        
        if exp_data["exp_invocation"]["localhost"]:
            self.make_job_path(exp_data["job_parameters"]['job_dir'])

        else:            
            if not os.path.isdir(exp_data["job_parameters"]['job_dir']):
                print(os.path.basename(__file__) + ":: Error: Results (Job) Directory (" + exp_data["job_parameters"]['job_dir'] + ") does not exist.")
                sys.exit(2)
            
        '''
            for both hpc and localhost context, these directories store the some summary data.
                - journal entry is same as summary file written to job dir
                    - writing it separately as the job dir is compressed and tarred so is not easily accessible from the command line during later episodes, 
                        or after execution - if you just want to check the summry can view the journal entry
                - heartbeat is also a copy of the heartbeat stored in job dir, for same reasons as above.
                - for both  heartbeat and journal, need to create a __PBS_PARENT_JOBID__ dir to collect them all.
                - would like to have dir for ER and OU files, but not possible to prescribe to PBS a job id dependent directory,
                    as the PBS directives are parsed in the shell script before the __PBS_JOBID__ is available.
        '''

        '''
            hpc context is not threadsafe when running a PBS Jobarray, so try to catch the case where another instance creates the same parent directory 
                before the current instance can (after checking that it does not exist); especially likely when hpc is under extreme load ...
                self.make_job_path() catches OSError in this case
        '''

        '''
            do not make secondary heartbeat path if on HPC
        '''

        if exp_data["exp_invocation"]["localhost"]:
            exp_data["job_parameters"]["heartbeat_path"] = list(self.hpc_config["heartbeat"]['heartbeat_path']) + [exp_data["job_parameters"]["pbs_parent_jobid"]]        
            self.make_job_path(os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(exp_data["job_parameters"]["heartbeat_path"])))
        
        exp_data["job_parameters"]["journal_path"] = list(self.hpc_config["journal"]['journal_path']) + [exp_data["job_parameters"]["pbs_parent_jobid"]] + [self.hpc_config["journal"]["journal_sj_summary_path"]]
        self.make_job_path(os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(exp_data["job_parameters"]["journal_path"])))
        
        '''
            for tournaments, there is an additional layer of indirection in the folder structure.
                - so for all other exp modes, make episode paths as usual
                - for tournaments do nothing here
                - we make the indirected folder (tournament_trial_id) within the subjob folder, and then build the relevant episode paths within the tournament_trial_id folder,
                    which is all done from the exp_tournament main loop
        '''
        if not exp_data["exp_invocation"]["exp_type"] == "tournament":
            self.make_job_episode_paths(exp_data)
        
        
    def make_tournament_trial_folder(self, exp_data, tournament_trial_id):
        tournament_trial_path = os.path.join(exp_data["job_parameters"]['job_dir'], str(tournament_trial_id))
        self.make_job_path(tournament_trial_path)
        self.make_job_episode_paths_tournament(exp_data, tournament_trial_path)

    def make_job_episode_paths_tournament(self, exp_data, tournament_trial_path):    
        '''
            for both hpc and localhost context, these directories store the data from the experiment, and 
            are the same for experiment types: symmetric selfplay, asymmetric_selfpay, selfplay_parameter_study; 
                potentially also for round-robin and tournament [TODO] [confirm]
        '''

        
        reward_history_path = os.path.join(tournament_trial_path, self.hpc_config["exp_data_leaf_dirs"]["reward_history"])
        self.make_job_path(reward_history_path)

        
        cumulative_outcome_history_path = os.path.join(tournament_trial_path, self.hpc_config["exp_data_leaf_dirs"]["cumulative_outcome_history"])
        self.make_job_path(cumulative_outcome_history_path)


        
    def make_job_episode_paths(self, exp_data):    
        '''
            for both hpc and localhost context, these directories store the data from the experiment, and 
            are the same for experiment types: symmetric selfplay, asymmetric_selfpay, selfplay_parameter_study; 
                potentially also for round-robin and tournament [TODO] [confirm]
        '''
        action_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["action_history"])
        self.make_job_path(action_history_path)
        
        reward_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["reward_history"])
        self.make_job_path(reward_history_path)

        map_outcome_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["map_outcome_history"])
        self.make_job_path(map_outcome_history_path)
        
        cumulative_outcome_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["cumulative_outcome_history"])
        self.make_job_path(cumulative_outcome_history_path)

        agent_internal_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["agent_internal_state"])
        self.make_job_path(agent_internal_state_path)

        strategy_internal_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["strategy_internal_state"])
        self.make_job_path(strategy_internal_state_path)
        
        
    def make_job_path(self, path):
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
                print(os.path.basename(__file__) + ":: created new job_path: " + path)
            except  OSError as e:
                print(os.path.basename(__file__) + ":: The job_path " + path + " already exists. OSError caught: " + e)
                

    '''
        assemble strategy_parameter set for symmetric selfplay
            update agent_parameters with input parameters
                - parameters string contains strategy parameter names and values, supplied via -p __PARAMETER_STRING__ in form: "alpha=$i:gamma=$j", 
                    where $i and $j are floats in range(0,1)
                - the values in parameter string overrides the default parameter values for both agents/strategies (symmetric selfplay)
                - if parameters are passed in as input, but are not applicable to the strategy, then ignore those parameters
        
    '''
    
    def load_symmetric_strategy_parameters(self, exp_data, matrix):
        
        strategy_parameters = {"gameform_matrix": matrix}
        
        applicable_parameters = {}
        
        if exp_data["exp_invocation"]["strategy"] in self.strategy_config["default_strategy_parameters"]:    
            strategy_parameters.update(self.strategy_config["default_strategy_parameters"][exp_data["exp_invocation"]["strategy"]])

        if ':' in exp_data["exp_invocation"]["parameter_string"]:
            input_parameters = dict(parameter_pair.split("=") for parameter_pair in exp_data["exp_invocation"]["parameter_string"].split(":"))
            for k, v in input_parameters.items():
                if k in self.strategy_config["default_strategy_parameters"][exp_data["exp_invocation"]["strategy"]].keys():
                    applicable_parameters[k] = float(v)
            strategy_parameters.update(applicable_parameters)
            
        return strategy_parameters
    
    '''
        is same load sequence as for symmetric_selfplay. duplicated atm as that might change down the track, also, might not - in which case can remove [TODO]
    '''
    def load_selfplay_parameter_study_strategy_parameters(self, exp_data, matrix):
        
        strategy_parameters = {"gameform_matrix": matrix}
        
        applicable_parameters = {}
        
        if exp_data["exp_invocation"]["strategy"] in self.strategy_config["default_strategy_parameters"]:    
            strategy_parameters.update(self.strategy_config["default_strategy_parameters"][exp_data["exp_invocation"]["strategy"]])
        print(exp_data["exp_invocation"]["parameter_string"])
        
        if exp_data["exp_invocation"]["parameter_string"]:
            input_parameters = dict(parameter_pair.split("=") for parameter_pair in exp_data["exp_invocation"]["parameter_string"].split(":"))
            print(f"Job args input parameters: { input_parameters }")
            for k, v in input_parameters.items():
                if k in self.strategy_config["default_strategy_parameters"][exp_data["exp_invocation"]["strategy"]].keys():
                    applicable_parameters[k] = float(v)
            strategy_parameters.update(applicable_parameters)
        print(f"Assembled default strategy parameters and input job parameters are {strategy_parameters}")
        return strategy_parameters
    

    
    def set_exp_data_symmetric_agent_parameters(self, exp_data, agents): 
        exp_data["agent_parameters"]["agent_0"]["strategy"] = exp_data["exp_invocation"]["strategy"]
        exp_data["agent_parameters"]["agent_1"]["strategy"] = exp_data["exp_invocation"]["strategy"]
        
        # write strategy.options - not strategy_parameters - so as to include strategy superclass defaults
        exp_data["agent_parameters"]["agent_0"]["strategy_parameters"] = agents[0].strategy.options
        exp_data["agent_parameters"]["agent_1"]["strategy_parameters"] = agents[1].strategy.options
        
        
        
        
        
         
    def load_tournament_strategy_parameters(self, exp_data, strategy, matrix):
    
        strategy_parameters = {"gameform_matrix": matrix}
        
        applicable_parameters = {}
        
        if strategy in self.strategy_config["default_strategy_parameters"]:    
            strategy_parameters.update(self.strategy_config["default_strategy_parameters"][strategy])
        #print(exp_data["exp_invocation"]["parameter_string"])
        
        # if exp_data["exp_invocation"]["parameter_string"]:
            # input_parameters = dict(parameter_pair.split("=") for parameter_pair in exp_data["exp_invocation"]["parameter_string"].split(":"))
            # print(f"Job args input parameters: { input_parameters }")
            # for k, v in input_parameters.items():
                # if k in self.strategy_config["default_strategy_parameters"][exp_data["exp_invocation"]["strategy"]].keys():
                    # applicable_parameters[k] = float(v)
            # strategy_parameters.update(applicable_parameters)
        
        #print(f"{os.path.basename(__file__)}:: Assembled default strategy parameters for {strategy}: {strategy_parameters}")
        
        return strategy_parameters        



    
    '''
        write state / history
            - compressed, or not, dependent on exp parameter: exp_data["exp_invocation"]["compress_writes"]
        
    '''
    
    def write_agent_history_single_episode(self, exp_data, agents,  e):
        for a in agents:
            self.write_agent_episode_history(exp_data, e, "agent_" + str(a.agent_id), "action_history", a.action_history)
            self.write_agent_episode_history(exp_data, e, "agent_" + str(a.agent_id), "reward_history", a.reward_history)
            
            if a.agent_has_state() and exp_data["exp_invocation"]["write_state"]:
                self.write_agent_state(exp_data, a, e)
                
            if a.strategy.strategy_has_state() and exp_data["exp_invocation"]["write_state"]:
                self.write_strategy_state(exp_data, a, e)
    
    def write_agent_reward_history_single_episode_tournament(self, exp_data, agents, e, tournament_trial_id):
        for a in agents:
            self.write_agent_episode_history_tournament(exp_data, e, "agent_" + str(a.agent_id), "reward_history", a.reward_history, tournament_trial_id)
            
                
    def write_agent_episode_history(self, exp_data, episode, agent_id, history_type, data):
        history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"][history_type])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + history_type + "_" + agent_id + "_" + "episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".csv.gz"
            self.write_compressed_csv(data, os.path.join(history_path, file))
        else:
            file = file + ".csv"
            self.write_csv(data, os.path.join(history_path, file))

    def write_agent_episode_history_tournament(self, exp_data, episode, agent_id, history_type, data, tournament_trial_id):
        history_path = os.path.join(exp_data["job_parameters"]['job_dir'], str(tournament_trial_id), self.hpc_config["exp_data_leaf_dirs"][history_type])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + history_type + "_" + agent_id + "_" + "episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".csv.gz"
            self.write_compressed_csv(data, os.path.join(history_path, file))
        else:
            file = file + ".csv"
            self.write_csv(data, os.path.join(history_path, file))
   
    def write_agent_state(self, exp_data, agent, episode):
        agent_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["agent_internal_state"]) 
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + self.hpc_config["exp_data_leaf_dirs"]["agent_internal_state"] + "_agent_" + str(agent.agent_id) + "_episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(agent_state_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(agent_state_path, file))


    def write_strategy_state(self, exp_data, agent, episode):
        strategy_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["strategy_internal_state"]) 
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + self.hpc_config["exp_data_leaf_dirs"]["strategy_internal_state"] + "_" + \
                exp_data["agent_parameters"]['agent_0']['strategy'] + "_agent_" + str(agent.agent_id) + "_episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(agent.state_history, os.path.join(strategy_state_path, file))
        else:
            file = file + ".json"
            self.write_json(agent.state_history, os.path.join(strategy_state_path, file)) 
        
            
    def write_single_episode_outcomes_cumulative(self, exp_data, episode, single_episode_outcomes_cumulative):
        o_d_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["cumulative_outcome_history"])
        
        for o, d in single_episode_outcomes_cumulative.items():
            file = exp_data["job_parameters"]['data_filename_prefix'] + "_outcomes_" + "episode_" + str(episode+1) + "_" + o + "_cumulative"
            
            if exp_data["exp_invocation"]["compress_writes"]:
                file = file + ".csv.gz"
                self.write_compressed_csv(single_episode_outcomes_cumulative[o], os.path.join(o_d_path, file))
            else:
                file = file + ".csv"
                self.write_csv(single_episode_outcomes_cumulative[o], os.path.join(o_d_path, file))       

    def write_single_episode_outcomes_cumulative_tournament(self, exp_data, episode, single_episode_outcomes_cumulative, tournament_trial_id):
        o_d_path = os.path.join(exp_data["job_parameters"]['job_dir'], str(tournament_trial_id), self.hpc_config["exp_data_leaf_dirs"]["cumulative_outcome_history"])
        
        for o, d in single_episode_outcomes_cumulative.items():
            file = exp_data["job_parameters"]['data_filename_prefix'] + "_outcomes_" + "episode_" + str(episode+1) + "_" + o + "_cumulative"
            
            if exp_data["exp_invocation"]["compress_writes"]:
                file = file + ".csv.gz"
                self.write_compressed_csv(single_episode_outcomes_cumulative[o], os.path.join(o_d_path, file))
            else:
                file = file + ".csv"
                self.write_csv(single_episode_outcomes_cumulative[o], os.path.join(o_d_path, file)) 
                
    def write_single_episode_outcomes_timestep_map(self, exp_data, episode, single_episode_outcomes_timestep_map):
        o_t_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.hpc_config["exp_data_leaf_dirs"]["map_outcome_history"])
        
        for o, d in single_episode_outcomes_timestep_map.items():
            file = exp_data["job_parameters"]['data_filename_prefix'] + "_outcomes_" + "episode_" + str(episode+1) + "_" + o + "_map"
            
            if exp_data["exp_invocation"]["compress_writes"]:
                file = file + ".csv.gz"
                self.write_compressed_csv(single_episode_outcomes_timestep_map[o], os.path.join(o_t_path, file))
            else:
                file = file + ".csv"
                self.write_csv(single_episode_outcomes_timestep_map[o], os.path.join(o_t_path, file))


    def write_exp_data_summary(self, exp_data):        
        path = exp_data["job_parameters"]['job_dir']
        file = exp_data["journal_output_filename"]
        
        with open(os.path.join(path, file), 'w') as json_file:
            json.dump(exp_data, json_file)


    def write_exp_journal_entry(self, exp_data):    
        
        if exp_data["exp_invocation"]["localhost"]:
            path = os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(self.hpc_config["journal"]["journal_path"]), exp_data["job_parameters"]["pbs_parent_jobid"], self.hpc_config["journal"]["journal_sj_summary_path"])
        else:
            # obs_exp/journal
            path = os.path.join(exp_data["job_parameters"]["pbs_scratch_dir"], os.sep.join(self.hpc_config["journal"]["journal_scratch_path"]))
            #path = os.path.join(exp_data["job_parameters"]["pbs_scratch_dir"], os.sep.join(self.hpc_config["journal"]["journal_scratch_path"]), exp_data["job_parameters"]["pbs_parent_jobid"])
           
        file = exp_data["journal_output_filename"]
        
        with open(os.path.join(path, file), 'w') as json_file:
            json.dump(exp_data, json_file)
            
            
    def write_compressed_json(self, data, path):
        with gzip.open(path, 'w') as json_file_gz:
            json_file_gz.write(json.dumps(data).encode('utf-8'))

    def write_json(self, data, path):
        with open(path, 'w') as json_file:
            json.dump(data, json_file)
        
    def write_compressed_csv(self, data, path):
        with gzip.open(path, 'wt', ) as csv_file_gz:
            write = csv.writer(csv_file_gz)
            write.writerow(data)

    def write_csv(self, data, path):
        with open(path, 'wt', newline='') as csv_file:
            write = csv.writer(csv_file)
            write.writerow(data)
    

    '''
        heartbeat
    
    '''
    def heartbeat_start(self, exp_data):
        exp_process_time = process_time_ns()
        exp_time_now_ns = time_ns()
        exp_time_now_readable = datetime.fromtimestamp(exp_time_now_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        
        heartbeat_msg = os.path.basename(__file__) + ":: heartbeat_start: " + exp_time_now_readable + " " + str(exp_time_now_ns) + " " + \
                        exp_data["exp_id"]  + " " +  str(exp_data["exp_invocation"]["episodes"]) + " "  +  str(exp_data["exp_invocation"]["timesteps"]) + " " + str(exp_process_time) + "\n"
        
        self.heartbeat_write(exp_data, heartbeat_msg)
    
    def heartbeat(self, exp_data, e, t):
        if t % exp_data["job_parameters"]["heartbeat_interval"] == 0:
            exp_process_time = process_time_ns()
            exp_time_now_ns = time_ns()
            exp_time_now_readable = datetime.fromtimestamp(exp_time_now_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        
            heartbeat_msg = os.path.basename(__file__) + ":: heartbeat: " + exp_time_now_readable + " " + str(exp_time_now_ns) + " " + \
                            exp_data["exp_id"]  + " " +  str(e) + " " +  str(t) + " " + str(exp_process_time) + "\n"
            
            self.heartbeat_write(exp_data, heartbeat_msg)

    def heartbeat_end(self, exp_data):
        exp_process_time = process_time_ns()
        exp_time_now_ns = time_ns()
        exp_time_now_readable = datetime.fromtimestamp(exp_time_now_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        
        heartbeat_msg = os.path.basename(__file__) + ":: heartbeat_end: " + exp_time_now_readable + " " + str(exp_time_now_ns) + " " + \
                        exp_data["exp_id"]  + " " +  str(exp_data["exp_invocation"]["episodes"]) + " " +  str(exp_data["exp_invocation"]["timesteps"]) + " " + str(exp_process_time) + "\n"
        
        self.heartbeat_write(exp_data, heartbeat_msg)

    def heartbeat_write(self, exp_data, heartbeat_msg): 
        '''
            write (append) heartbeat_msg to job directory
            
            then, also, if exp_data["exp_invocation"]["write_2_heartbeats"]     
                    write (append) heartbeat_msg to heartbeat directory
                if not localhost, write to SCRATCH
        '''
        file = self.hpc_config["heartbeat"]["exp_heartbeat_prefix"] + exp_data["exp_id"] + self.hpc_config["heartbeat"]["heartbeat_extension"]
        path = os.path.join(exp_data["job_parameters"]["job_dir"], file)        
        
        self.write_heartbeat(path, heartbeat_msg) 
        
        if exp_data["exp_invocation"]["write_2_heartbeats"]:
            if exp_data["exp_invocation"]["localhost"]:
                path = os.path.join(os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(exp_data["job_parameters"]["heartbeat_path"])), file)
            else:
                path = os.path.join(os.path.join(exp_data["job_parameters"]["pbs_scratch_dir"], os.sep.join(self.hpc_config["heartbeat"]["heartbeat_scratch_path"])), file)
                #path = os.path.join(os.path.join(exp_data["job_parameters"]["pbs_scratch_dir"], os.sep.join(self.hpc_config["heartbeat"]["heartbeat_scratch_path"]), exp_data["job_parameters"]["pbs_parent_jobid"]), file)
                
            self.write_heartbeat(path, heartbeat_msg)


    '''
        heartbeat tournament
    
    '''
    def heartbeat_start_tournament(self, exp_data, tournament_trial_id):
        exp_process_time = process_time_ns()
        exp_time_now_ns = time_ns()
        exp_time_now_readable = datetime.fromtimestamp(exp_time_now_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        
        heartbeat_msg = os.path.basename(__file__) + ":: heartbeat_start: " + exp_time_now_readable + " " + str(exp_time_now_ns) + " " + \
                        exp_data["exp_id"] + "_" + str(tournament_trial_id) + " " + str(exp_data["exp_invocation"]["episodes"]) + " "  +  str(exp_data["exp_invocation"]["timesteps"]) + " " + str(exp_process_time) + "\n"
        
        self.heartbeat_write_tournament(exp_data, heartbeat_msg, tournament_trial_id)
    
    def heartbeat_tournament(self, exp_data, e, t, tournament_trial_id):
        if t % exp_data["job_parameters"]["heartbeat_interval"] == 0:
            exp_process_time = process_time_ns()
            exp_time_now_ns = time_ns()
            exp_time_now_readable = datetime.fromtimestamp(exp_time_now_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        
            heartbeat_msg = os.path.basename(__file__) + ":: heartbeat: " + exp_time_now_readable + " " + str(exp_time_now_ns) + " " + \
                            exp_data["exp_id"]  + "_" + str(tournament_trial_id) + " " +  str(e) + " " +  str(t) + " " + str(exp_process_time) + "\n"
            
            self.heartbeat_write_tournament(exp_data, heartbeat_msg, tournament_trial_id)

    def heartbeat_end_tournament(self, exp_data, tournament_trial_id):
        exp_process_time = process_time_ns()
        exp_time_now_ns = time_ns()
        exp_time_now_readable = datetime.fromtimestamp(exp_time_now_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        
        heartbeat_msg = os.path.basename(__file__) + ":: heartbeat_end: " + exp_time_now_readable + " " + str(exp_time_now_ns) + " " + \
                        exp_data["exp_id"]  + "_" + str(tournament_trial_id) + " " +  str(exp_data["exp_invocation"]["episodes"]) + " " +  str(exp_data["exp_invocation"]["timesteps"]) + " " + str(exp_process_time) + "\n"
        
        self.heartbeat_write_tournament(exp_data, heartbeat_msg, tournament_trial_id)

    def heartbeat_write_tournament(self, exp_data, heartbeat_msg, tournament_trial_id): 
        '''
            write (append) heartbeat_msg to job directory
            
            then, also, if exp_data["exp_invocation"]["write_2_heartbeats"]     
                    write (append) heartbeat_msg to heartbeat directory
                if not localhost, write to SCRATCH
        '''
        file = self.hpc_config["heartbeat"]["exp_heartbeat_prefix"] + exp_data["exp_id"] + self.hpc_config["heartbeat"]["heartbeat_extension"]
        path = os.path.join(exp_data["job_parameters"]["job_dir"], file)        
        
        self.write_heartbeat(path, heartbeat_msg) 
        
        if exp_data["exp_invocation"]["write_2_heartbeats"]:
            if exp_data["exp_invocation"]["localhost"]:
                path = os.path.join(os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(exp_data["job_parameters"]["heartbeat_path"])), file)
            else:
                path = os.path.join(os.path.join(exp_data["job_parameters"]["pbs_scratch_dir"], os.sep.join(self.hpc_config["heartbeat"]["heartbeat_scratch_path"])), file)
                #path = os.path.join(os.path.join(exp_data["job_parameters"]["pbs_scratch_dir"], os.sep.join(self.hpc_config["heartbeat"]["heartbeat_scratch_path"]), exp_data["job_parameters"]["pbs_parent_jobid"]), file)
                
            self.write_heartbeat(path, heartbeat_msg)


    '''
        write heartbeat
    
    '''

    def write_heartbeat(self, path, heartbeat_msg):
        with open(path, 'a', buffering = 1) as heartbeat:
            heartbeat.write(heartbeat_msg)
            heartbeat.flush()
            os.fsync(heartbeat.fileno()) 

    
    
    '''
        ungrouped helper functions
    
    '''
    def append_timestep_outcome_to_single_episode_outcomes_cumulative(self, single_episode_outcomes_cumulative, trial):
        single_episode_outcomes_cumulative["cc"].append(trial.get_CC())
        single_episode_outcomes_cumulative["cd"].append(trial.get_CD())
        single_episode_outcomes_cumulative["dc"].append(trial.get_DC())
        single_episode_outcomes_cumulative["dd"].append(trial.get_DD())
        
      
    # move to gameforms {TODO]
    def map_actions_to_semantic_outcome(self, actions):
        mapped_matrix = [[["cc"],["cd"]],[["dc"],["dd"]]]
        return mapped_matrix[actions[0]][actions[1]][0]