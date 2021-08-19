#!/usr/bin/env python3
# file: view_util.py

import os

import re
from pathlib import Path
from time import process_time_ns, time_ns
from datetime import datetime

import json, gzip, tarfile, io, csv
from natsort import natsorted
from collections import OrderedDict

from agent_model.utility import Utility as utility

class View_utility:

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

    def set_basepath(self, obs_data):

        obs_data["obs_invocation"]["home"] = str(Path.home())
        print(os.path.basename(__file__) + ":: setting home to " + obs_data["obs_invocation"]["home"])

        if obs_data["obs_invocation"]["localhost"]:
            localhost = os.sep.join(self.hpc_config["paths"]["basepath_localhost"])
            obs_data["obs_invocation"]["basepath"] = os.path.join(obs_data["obs_invocation"]["home"], localhost)
            
        else:
            hpc = os.sep.join(self.hpc_config["paths"]["basepath_hpc"])
            obs_data["obs_invocation"]["basepath"] = os.path.join(obs_data["obs_invocation"]["home"], hpc)
            
        print(os.path.basename(__file__) + ":: setting basepath to " + obs_data["obs_invocation"]["basepath"])
        
    

    def scale_y_max(self, reward_type):
        y_max = 1
        if reward_type == 'scalar':
            y_max = 5
        elif reward_type == 'ordinal':
            y_max = 4
        return y_max
        
    '''
        ts_o graph functions
    
    '''
    def eo_ts_o_view_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["view"]["ts_o"]["mean_episode_distribution"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        #obs_data["view_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["view"]["view_suffix"] + self.hpc_config["view"]["view_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        obs_data["journal_obs_summary_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        
    def eo_ts_o_view_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        

        
    
    def retrieve_obs_data_summary(self, obs_data):
        obs_data_summary = {}
        parent_id = obs_data["obs_exp"]["exp_parent_id"]    
        
        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), parent_id)
        file = self.hpc_config["obs"]["data_file_prefix"] + parent_id + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as f:
            obs_data_summary = json.load(f)
        
        return obs_data_summary

    def eo_ts_o_view_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)
   

    def eo_ts_o_view_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)  





    '''
        ep_o graph functions
    
    '''
    def eo_ep_o_view_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["view"]["ep_o"]["default"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        #obs_data["view_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["view"]["view_suffix"] + self.hpc_config["view"]["view_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        obs_data["journal_obs_summary_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        
    def eo_ep_o_view_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        

        
    
    

    def eo_ep_o_view_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)
   

    def eo_ep_o_view_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)  





    '''
        ts_r graph functions
    
    '''
    def eo_ts_r_view_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["view"]["ts_r"]["default"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        #obs_data["view_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["view"]["view_suffix"] + self.hpc_config["view"]["view_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        obs_data["journal_obs_summary_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        
    def eo_ts_r_view_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        

        
    
    

    def eo_ts_r_view_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)
   

    def eo_ts_r_view_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)  
            
            
            



    
    def fetch_data(self, path, file, obs_data):
        data = []
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            for row in csv_reader:
                data.append(row)
        return data



    def distribution_graph_title_dict(self, obs_data_summary, sj_id, gameform, strategy, episodes, reward_type, av_sin_tag, exp_type):
        exp_reference = obs_data_summary["obs_exp"]["exp_parent_id"]
        trial_agent_strategy_parameters = self.get_trial_agent_strategy_parameters(obs_data_summary, sj_id)
        
        strategy_display_names = utility().strategy_display_names()
        gf_display_name = utility().retrieve_matrix_displayname(gameform)
    
    
        if av_sin_tag == "mean":
            av_sin_tag = " " + av_sin_tag.capitalize()
            episode_tag = "(over " + str(episodes) + " episodes)"
        else:
            av_sin_tag = ""
            episode_tag = "(episode " + str(episodes+1) + ")"
        return {
            'text' : "<span style='font-size:12px;font-weight:bold;'>" + exp_type + ": " + strategy_display_names[strategy] + "</span>" \
                + "<span style='font-size:12px;'>" + av_sin_tag + " Distribution of Outcomes per-timestep " + episode_tag + "</span> " \
                + "<br><span style='font-size:8px;'>[Exp_ID: " + exp_reference + "] " \
                + "[Gameform: " + gf_display_name + ", " + reward_type.capitalize() + "] </span>" \
                + "<br><span style='font-size:8px;'>" + trial_agent_strategy_parameters + "</span>",
            'y':0.975,
            'x':0.055,
            'xanchor': 'left',
            'yanchor': 'top',
        }
        
        
    def get_trial_agent_strategy_parameters(self, obs_data_summary, sj_id):
        parameter_string = ""
        for a in obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["agent_parameters"]:
            parameter_string += "[<span style='font-weight:bold;'>" + a + "</span>:"
            for k, v in obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["agent_parameters"][a]["strategy_parameters"].items():
                #print(k, v)
                #if k not in obs_data_summary["hidden_parameters"]:
                #parameter_string += " " + k + ":" + str(v)
                if k not in ["gameform_matrix", "has_state", "notes"]:   # "memory_depth"
                    parameter_string += " " + k + ":" + str(v)
            parameter_string += "] "
            
        return parameter_string        