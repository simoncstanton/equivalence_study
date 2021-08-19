#!/usr/bin/env python3
# file: obs_util.py

import os

import re
from pathlib import Path
from time import process_time_ns, time_ns
from datetime import datetime

import json, gzip, tarfile, io, csv
from natsort import natsorted
from collections import OrderedDict

class Obs_utility:

    def __init__(self):
        self.hpc_config = self.load_hpc_config()
    
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
        
        
      
        
        
        

    def meta_access_exp_result_set(self, obs_data, subjob_id):
        '''
            regardless of the number of subjobs in this experiment, we only open the first (if subjob_id == 0)
            as the data we want here is (*should be*) consistent across all subjobs.
            note, all experiments have a subjob 0.
        '''
        exp_data = self.extract_exp_result_set_summary(obs_data, subjob_id)
        
        obs_data["obs_exp"]["exp_localhost"] = exp_data["exp_invocation"]["localhost"]
        obs_data["obs_exp"]["exp_server"] = exp_data["job_parameters"]["hpc_name"]
        
        obs_data["obs_exp"]["exp_type"] = exp_data["exp_invocation"]["exp_type"]
        obs_data["obs_exp"]["exp_episodes"] = exp_data["exp_invocation"]["episodes"]
        obs_data["obs_exp"]["exp_timesteps"] = exp_data["exp_invocation"]["timesteps"]
        
        obs_data["obs_exp"]["exp_compressed_writes"] = exp_data["exp_invocation"]["compress_writes"]
        
        if obs_data["obs_exp"]["exp_localhost"]:
            obs_data["obs_exp"]["result_set_extension"] = ""


    def extract_exp_result_set_summary(self, obs_data, subjob_id):
        exp_data = {}
        
        path = os.path.join(os.sep.join(self.hpc_config["journal"]['journal_path']), obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["journal"]['journal_sj_summary_path'])
        file = self.hpc_config["journal"]["exp_journal_entry_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + "_" + str(subjob_id) + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as f:
            exp_data = json.load(f)
        
        return exp_data

        
    def set_obs_data_start(self, obs_data):
    
        exp_data_path = [obs_data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"]]
        obs_data["obs_exp"]["exp_data_path"] = list(self.hpc_config["paths"]["experiments"]) + exp_data_path

        obs_data["obs_exp"]["exp_result_set"] = self.glob_exp_parent_dir_result_set(obs_data, os.sep.join(obs_data["obs_exp"]["exp_data_path"]))
        obs_data["obs_exp"]["exp_subjobs_list"] = self.extract_subjob_ids_from_result_set(obs_data["obs_exp"]["exp_result_set"])
        
        self.create_subjob_dicts(obs_data)
        
        obs_data["obs_exp"]["exp_archive_total_size"] = self.get_result_set_subjob_size(obs_data)
        obs_data["obs_exp"]["exp_strategy_list"] = self.get_strategy_list(obs_data)
        obs_data["obs_exp"]["exp_gameform_list"] = self.get_gameform_list(obs_data)
        
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"] + "_" + obs_data["obs_id"]
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        obs_data["obs_exp"]["exp_heartbeat_path"] = list(self.hpc_config["heartbeat"]['heartbeat_path']) + [obs_data["obs_exp"]["exp_parent_id"]]
        obs_data["obs_exp"]["exp_journal_path"] = list(self.hpc_config["journal"]['journal_path']) + [obs_data["obs_exp"]["exp_parent_id"]]
        
    
    def set_obs_data_start_tournament(self, obs_data):
    
        exp_data_path = [obs_data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"]]
        obs_data["obs_exp"]["exp_data_path"] = list(self.hpc_config["paths"]["experiments"]) + exp_data_path

        obs_data["obs_exp"]["exp_result_set"] = self.glob_exp_parent_dir_result_set(obs_data, os.sep.join(obs_data["obs_exp"]["exp_data_path"]))
        obs_data["obs_exp"]["exp_subjobs_list"] = self.extract_subjob_ids_from_result_set(obs_data["obs_exp"]["exp_result_set"])
        
        self.create_subjob_dicts(obs_data)
        
        obs_data["obs_exp"]["exp_archive_total_size"] = self.get_result_set_subjob_size(obs_data)
        obs_data["obs_exp"]["exp_strategy_list"] = self.get_strategy_list_tournament(obs_data)
        #obs_data["obs_exp"]["exp_gameform_list"] = self.get_gameform_list(obs_data)
        
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"] + "_" + obs_data["obs_id"]
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        obs_data["obs_exp"]["exp_heartbeat_path"] = list(self.hpc_config["heartbeat"]['heartbeat_path']) + [obs_data["obs_exp"]["exp_parent_id"]]
        obs_data["obs_exp"]["exp_journal_path"] = list(self.hpc_config["journal"]['journal_path']) + [obs_data["obs_exp"]["exp_parent_id"]]
        
    def glob_exp_parent_dir_result_set(self, obs_data, path):
        result_set = []
        with os.scandir(os.path.join(obs_data["obs_invocation"]["basepath"], path)) as result_set_ls:
            for entry in result_set_ls:
                if entry.is_dir():
                    result_set.append(entry.name)
    
        return natsorted(result_set)


    def extract_subjob_ids_from_result_set(self, result_set):
        subjob_ids = []
        for rs in result_set:
            subjob_ids.append(rs.split('_', 1)[1])
        return natsorted(subjob_ids)


    def create_subjob_dicts(self, obs_data):

        for sj in obs_data["obs_exp"]["exp_subjobs_list"]:
            obs_data["obs_exp"]["exp_subjobs"][sj] = {}
            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_parent_id"] = obs_data["obs_exp"]["exp_parent_id"]
            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_id"] = sj
             
            leaf = obs_data["obs_exp"]["exp_parent_id"] + "_" + sj
            path = list(obs_data["obs_exp"]["exp_data_path"]) + [leaf]

            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_data_path"] = path
            exp_subjob_data_file = obs_data["obs_exp"]["exp_parent_id"] + "_" + sj + obs_data["obs_exp"]["result_set_extension"]
            
            # localhost exp are not in a tarball
            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_data_file"] = ""
            if not obs_data["obs_exp"]["exp_localhost"]:
                obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_data_file"] = exp_subjob_data_file  
            
            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_process_time_ns"] = self.get_process_time_ns(obs_data, sj)
            
            # set to 0 now, update when calculating total size (saves repeated walks)
            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_result_set_size"] = 0
            
            # localhost exp does not output these files, only PBS
            if not obs_data["obs_exp"]["exp_localhost"]:
                obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_pbs_resources_used"] = self.extract_resources_used(obs_data, sj)
               
            obs_data["obs_exp"]["exp_subjobs"][sj]["exp_summary"] = self.extract_exp_result_set_summary(obs_data, sj)



    
    def get_process_time_ns(self, obs_data, sj):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["journal"]['journal_sj_summary_path'])
        file = self.hpc_config["journal"]["exp_journal_entry_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + "_" + sj + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as f:
            exp_data = json.load(f)
        return exp_data["exp_invocation"]["process_end_ns"] - exp_data["exp_invocation"]["process_start_ns"]
        
    
    def extract_resources_used(self, obs_data, sj):
        exp_subjob_pbs_resources_used = {
            "cpupercent"                : "",
            "cput"                      : "",
            "mem"                       : "",
            "ncpus"                     : "",
            "vmem"                      : "",
            "walltime"                  : "",
        }
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["pbs_output_path"]), obs_data["obs_exp"]["exp_parent_id"])
        
        if len(obs_data["obs_exp"]["exp_subjobs_list"]) == 1:
            file = obs_data["obs_exp"]["exp_parent_id"] + "." + obs_data["obs_exp"]["exp_server"] + "." + self.hpc_config["pbs_output_extensions"]["output"]
        else:
            file = obs_data["obs_exp"]["exp_parent_id"] + "[" + sj + "]." + obs_data["obs_exp"]["exp_server"] + "." + self.hpc_config["pbs_output_extensions"]["output"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as f:
            for line in f:
                if 'resources_used' in line:
                    if 'cpupercent' in  line:
                        exp_subjob_pbs_resources_used["cpupercent"] = float(line.split('=')[1].strip())
                    if 'cput' in  line:
                        exp_subjob_pbs_resources_used["cput"] = line.split('=')[1].strip()
                    if 'mem' in  line:
                        exp_subjob_pbs_resources_used["mem"] = line.split('=')[1].strip()
                    if 'ncpus' in  line:
                        exp_subjob_pbs_resources_used["ncpus"] = int(line.split('=')[1].strip())
                    if 'vmem' in  line:
                        exp_subjob_pbs_resources_used["vmem"] = line.split('=')[1].strip()
                    if 'walltime' in  line:
                        exp_subjob_pbs_resources_used["walltime"] = line.split('=')[1].strip()
            
        return exp_subjob_pbs_resources_used    

    
    def get_result_set_subjob_size(self, obs_data):
        total_sj_size = 0
        
        if obs_data["obs_exp"]["exp_localhost"]:
            # localhost means exp result_set is not tar file (pbs_script does the tarring)
            # walk directory tree

            for sj in obs_data["obs_exp"]["exp_subjobs_list"]:
                
                leaf = obs_data["obs_exp"]["exp_parent_id"] + "_" + sj
                path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(list(obs_data["obs_exp"]["exp_data_path"]) + [leaf]))
                
                
                sj_size = sum(f.stat().st_size for f in Path(path).glob('**/*') if f.is_file())
                obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_result_set_size"] = sj_size
                
                total_sj_size += sj_size
                
        else:
            # hpc, so subjob is tar.gz, no need to walk as for localhost
            # but maybe multiple subjobs, so iterate over set of subjobs, get size of each tar.gz and sum
            
            for sj in obs_data["obs_exp"]["exp_subjobs_list"]:

                leaf = obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_data_file"]                
                path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(list(obs_data["obs_exp"]["exp_data_path"]) + [str(obs_data["obs_exp"]["exp_parent_id"] + "_" + sj)] + [leaf]))
                
                sj_size = os.path.getsize(path)
                obs_data["obs_exp"]["exp_subjobs"][sj]["exp_subjob_result_set_size"] = sj_size
                total_sj_size += sj_size
                
        return total_sj_size    
                
            

        
    def get_strategy_list(self, obs_data):
        strategy_list = []
        for sj in obs_data["obs_exp"]["exp_subjobs_list"]:            
            exp_data = self.extract_exp_result_set_summary(obs_data, sj)
            strategy_list.append(exp_data["exp_invocation"]["strategy"])
        
        return ",".join(strategy_list)   
        
    def get_gameform_list(self, obs_data):
        gameform_list = []
        for sj in obs_data["obs_exp"]["exp_subjobs_list"]:            
            exp_data = self.extract_exp_result_set_summary(obs_data, sj)
            gameform = exp_data["exp_invocation"]["gameform"] + ":" + exp_data["exp_invocation"]["reward_type"]
            gameform_list.append(gameform)
        
        return ",".join(set(gameform_list)) 
    
    def get_strategy_list_tournament(self, obs_data):
        strategy_list = []
        #for sj in obs_data["obs_exp"]["exp_subjobs_list"]:            
        exp_data = self.extract_exp_result_set_summary(obs_data, 0)
        strategy_list = exp_data["exp_invocation"]["strategy_list"]
        
        return strategy_list 

        
                   
        
    def make_obs_job_paths(self, obs_data):
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]))
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + ") does not exist.")
            exit(2)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data["obs_exp"]["exp_type"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"])
        self.make_job_path(path)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"])
        self.make_job_path(path)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"])
        self.make_job_path(path)
 
 
    def make_job_path(self, path):
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
                print(os.path.basename(__file__) + ":: created new job_path: " + path)
            except  OSError as e:
                print(os.path.basename(__file__) + ":: The job_path " + path + " already exists. OSError caught: " + e)          

    
    def set_obs_data_end(self, obs_data):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()

    def write_obs_data_summary(self, obs_data):
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]

        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)
    
    def write_obs_journal(self, obs_data):
        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)





    def read_obs_data_summary(self, obs_data):
        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_obs_summary_filename"]

        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as json_file:
            data = json.load(json_file)
        return data


    '''
        data extraction functions
        
            there are 12 cases to deal with
                - localhost
                    - single subjob
                        - single episode
                            - compressed writes
                            - uncompressed writes
                        - multiple episodes
                            - compressed writes
                            - uncompressed writes
                - hpc
                    - single subjob
                        - single episode
                            - compressed writes
                            - uncompressed writes
                        - multiple episodes
                            - compressed writes
                            - uncompressed writes
                    - mulitple subjobs
                        - single episode
                            - compressed writes
                            - uncompressed writes
                        - multiple episodes
                            - compressed writes
                            - uncompressed writes
        
        we have
            - path to the parent directory (in list format)
                so, this
                    results/experiments/symmetric_selfplay/__PBS_PARENT_JOBID_/
                looks like this (for eg)
                    ['results', 'experiments', 'symmetric_selfplay', '001']
                    
        need to
            - determine if exp was run on localhost
                - if yes
                    - then there will only be a single directory - subjob_0
                    - 
                    
                - if not, then
                    - enumerate all directories under this parent (each directory is a subjob)
                        - each directory contains a .tar.gz file
                            - for each tar.gz file 
                                
                                - decompress the file
                                - untar the file
                                - enumerate the files in the directory tree held within the tar
                                    - for each file that matches the relevant pattern (can be anywhere in file path with root as subjob tar
                                        - for each matched file extension (eg, .cvs.gz)
                                            - extract file from tar
                                            - gz.open the file
                                            - csv.read the file into a list
                                            - map the filename and data to a dict to keep relation
                                            
        
    '''

    def fetch_single_compressed_subjobs(self, obs_data, obs_data_summary, sj, leaf_dir):
        result_set_data = []
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(obs_data_summary["obs_exp"]["exp_data_path"]), obs_data_summary["obs_exp"]["exp_result_set"][sj])
        file = obs_data_summary["obs_exp"]["exp_result_set"][sj] + self.hpc_config["exp"]["sj_compressed_file_extension"]
        result_set_data.append(self.access_sj_gz(path, file, leaf_dir, obs_data_summary["obs_exp"]["exp_compressed_writes"], obs_data_summary["obs_exp"]["exp_episodes"]))  
            
        return result_set_data
        
    def fetch_single_uncompressed_subjobs(self, obs_data, obs_data_summary, sj, leaf_dir):
        result_set_data = []
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(obs_data_summary["obs_exp"]["exp_data_path"]), obs_data_summary["obs_exp"]["exp_result_set"][sj])
        result_set_data.append(self.access_sj_set(path, leaf_dir, obs_data_summary["obs_exp"]["exp_compressed_writes"]))
        
        return result_set_data
    
    
    def fetch_all_subjobs_result_set_data(self, obs_data, obs_data_summary, leaf_dir):
        # enter here the first layer of compression - HPC pbs_scripts puts *all* data from subjob into a single tar.gz
        # whereas loclahost is run from CLI, so no 'subjob' compression
        if obs_data_summary["obs_exp"]["exp_localhost"]:
            result_set_data = self.fetch_all_uncompressed_subjobs(obs_data, obs_data_summary, leaf_dir)
            
        else:
            result_set_data = self.fetch_all_compressed_subjobs(obs_data, obs_data_summary, leaf_dir)
        
        return result_set_data
    
    def fetch_all_compressed_subjobs(self, obs_data, obs_data_summary, leaf_dir):
        result_set_data = []
        
        for sj in obs_data_summary["obs_exp"]["exp_subjobs_list"]:
            sj = int(sj)
            path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(obs_data_summary["obs_exp"]["exp_data_path"]), obs_data_summary["obs_exp"]["exp_result_set"][sj])
            file = obs_data_summary["obs_exp"]["exp_result_set"][sj] + self.hpc_config["exp"]["sj_compressed_file_extension"]
            
            result_set_data.append(self.access_sj_gz(path, file, leaf_dir, obs_data_summary["obs_exp"]["exp_compressed_writes"], obs_data_summary["obs_exp"]["exp_episodes"]))  
            
        return result_set_data


    def fetch_all_uncompressed_subjobs(self, obs_data, obs_data_summary, leaf_dir):
        result_set_data = []
        
        for sj in obs_data_summary["obs_exp"]["exp_subjobs_list"]:
            sj = int(sj)
            path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(obs_data_summary["obs_exp"]["exp_data_path"]), obs_data_summary["obs_exp"]["exp_result_set"][sj])
            result_set_data.append(self.access_sj_set(path, leaf_dir, obs_data_summary["obs_exp"]["exp_compressed_writes"]))

        return result_set_data
        
        
    def access_sj_gz(self, path, file, leaf_dir, compressed_writes, episodes):
        '''
            extract experiment result_set_data matching a specific leaf_dir pattern from 
                '.tar.gz' -> '.tar' -> ['.csv'|'.csv.gz'] -> dict(filename:list)
        '''
        result_set_data = {}

        with open(os.path.join(path, file), 'rb') as f:
            result_set_tar = gzip.decompress(f.read())

        if compressed_writes:
            
            found_csv_gz = []
            
            with tarfile.open(fileobj = io.BytesIO(result_set_tar), mode = 'r') as t:
                for file_in_tar in t.getnames():
                    if file_in_tar.lower().endswith(self.hpc_config["exp"]["history_file_compressed_extension"]) and leaf_dir in file_in_tar:   
                        found_csv_gz.append(file_in_tar)
                
                found_csv_gz = natsorted(found_csv_gz)
                
                for file_in_tar in found_csv_gz:
                    csv_gz_file = t.extractfile(file_in_tar)            
                    with gzip.open(csv_gz_file, "rt") as file:

                        temp_list = [i for i in list(csv.reader(file))[0]]

                        if isinstance(temp_list[0], int):
                            temp_list = [int(i) for i in temp_list]
                        else:
                            temp_list = [float(i) for i in temp_list]
                            
                        #result_set_data[entry.name] = temp_list
                        result_set_data[file_in_tar.split('/')[2]] = temp_list #[int(i) for i in list(csv.reader(file))[0]]
                        
                        
                        # above type testing to handle reward_type extension to ordinal transforms
                        # requried because csv.reader reads things in as str type :\   ( i think there is a env option for this?)
                        # previous code below
                        #result_set_data[entry.name] = [int(i) for i in list(csv.reader(file))[0]]
                        
                        #result_set_data[file_in_tar.split('/')[2]] = [int(i) for i in list(csv.reader(file))[0]]
        else:
        
            found_csv = []
            
            with tarfile.open(fileobj = io.BytesIO(result_set_tar), mode = 'r') as t:
                for file_in_tar in t.getnames():
                    if file_in_tar.lower().endswith(self.hpc_config["exp"]["history_file_uncompressed_extension"]) and leaf_dir in file_in_tar: 
                        found_csv.append(file_in_tar)
                
                found_csv = natsorted(found_csv)
                
                for csv_file in found_csv:
                    file = io.TextIOWrapper(t.extractfile(csv_file), encoding="utf-8")

                    temp_list = [i for i in list(csv.reader(file))[0]]
                    if isinstance(temp_list[0], int):
                        temp_list = [int(i) for i in temp_list]
                    else:
                        temp_list = [float(i) for i in temp_list]
                        
                    #result_set_data[entry.name] = temp_list
                    result_set_data[csv_file.split('/')[2]] = temp_list #[int(i) for i in list(csv.reader(file))[0]]
                    
                    
                    # above type testing to handle reward_type extension to ordinal transforms
                    # requried because csv.reader reads things in as str type :\   ( i think there is a env option for this?)
                    # previous code below
                    #result_set_data[entry.name] = [int(i) for i in list(csv.reader(file))[0]]
                            
                    #result_set_data[csv_file.split('/')[2]] = [int(i) for i in list(csv.reader(file))[0]]
                    
        return result_set_data     
        

    def access_sj_set(self, path, leaf_dir, compressed_writes):
        '''
            we know exact path and the subjob is uncompressed
                but leaf directories may contain compressed files (compressed_writes == true)
            
            extract experiment result_set_data matching a specific leaf_dir pattern from 
                ['.csv'|'.csv.gz'] -> dict(filename:list)
        
            ** to natsort the entries, differetn approach here - using OrderedDict - than for access_sj_gz(),
                as there is no comparator defined for nt.entry
                
        '''

        result_set_data = {}

        if compressed_writes:
            
            with os.scandir(os.path.join(path, leaf_dir)) as result_set_ls:  
                for entry in result_set_ls:
                    if entry.is_file():
                        with gzip.open(entry, "rt") as file:
                            temp_list = [i for i in list(csv.reader(file))[0]]
                            if isinstance(temp_list[0], int):
                                temp_list = [int(i) for i in temp_list]
                            else:
                                temp_list = [float(i) for i in temp_list]
                                
                            result_set_data[entry.name] = temp_list
                            
                            # above type testing to handle reward_type extension to ordinal transforms
                            # requried because csv.reader reads things in as str type :\   ( i think there is a env option for this?)
                            # previous code below
                            #result_set_data[entry.name] = [int(i) for i in list(csv.reader(file))[0]]
                
        else:
            
            with os.scandir(os.path.join(path, leaf_dir)) as result_set_ls:
                for entry in result_set_ls:
                    if entry.is_file():
                        with open(entry, newline='') as file:
                            temp_list = [i for i in list(csv.reader(file))[0]]
                            if isinstance(temp_list[0], int):
                                temp_list = [int(i) for i in temp_list]
                            else:
                                temp_list = [float(i) for i in temp_list]
                                
                            result_set_data[entry.name] = temp_list
                            
                            # above type testing to handle reward_type extension to ordinal transforms
                            # requried because csv.reader reads things in as str type :\   ( i think there is a env option for this?)
                            # previous code below
                            #result_set_data[entry.name] = [int(i) for i in list(csv.reader(file))[0]]
           
        return OrderedDict(natsorted(result_set_data.items(), key=lambda t: t[0]))
    
            
        
    '''
        slightly modified for tournament
        
        
    '''
    def fetch_all_subjobs_result_set_data_tournament(self, obs_data, obs_data_summary, leaf_dir, tournament_strategy_count):
        # enter here the first layer of compression - HPC pbs_scripts puts *all* data from subjob into a single tar.gz
        # whereas loclahost is run from CLI, so no 'subjob' compression
        if obs_data_summary["obs_exp"]["exp_localhost"]:
            result_set_data = self.fetch_all_uncompressed_subjobs_tournament(obs_data, obs_data_summary, leaf_dir, tournament_strategy_count)
            
        else:
            result_set_data = self.fetch_all_compressed_subjobs_tournament(obs_data, obs_data_summary, leaf_dir, tournament_strategy_count)
        
        return result_set_data
    
    def fetch_all_compressed_subjobs_tournament(self, obs_data, obs_data_summary, leaf_dir, tournament_strategy_count):
        result_set_data = []
        print("leaf_dir: ", leaf_dir)
        for sj in obs_data_summary["obs_exp"]["exp_subjobs_list"]:
            sj = int(sj)
            path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(obs_data_summary["obs_exp"]["exp_data_path"]), obs_data_summary["obs_exp"]["exp_result_set"][sj])
            #print("path: ", path)
            file = obs_data_summary["obs_exp"]["exp_result_set"][sj] + self.hpc_config["exp"]["sj_compressed_file_extension"]
            #print("file: ", file)
            #if sj == 8:
            result_set_data.append(self.access_sj_gz_tournament(path, file, leaf_dir, obs_data_summary["obs_exp"]["exp_compressed_writes"], obs_data_summary["obs_exp"]["exp_episodes"], tournament_strategy_count))  
            
        return result_set_data
  
    def fetch_all_uncompressed_subjobs_tournament(self, obs_data, obs_data_summary, leaf_dir, tournament_strategy_count):
        result_set_data = []
        
        for sj in obs_data_summary["obs_exp"]["exp_subjobs_list"]:
            sj = int(sj)
            path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(obs_data_summary["obs_exp"]["exp_data_path"]), obs_data_summary["obs_exp"]["exp_result_set"][sj])
            result_set_data.append(self.access_sj_set_tournament(path, leaf_dir, obs_data_summary["obs_exp"]["exp_compressed_writes"], tournament_strategy_count))

        return result_set_data


        
    def access_sj_gz_tournament(self, path, file, leaf_dir, compressed_writes, episodes, tournament_strategy_count):
        '''
            extract experiment result_set_data matching a specific leaf_dir pattern from 
                '.tar.gz' -> '.tar' -> ['.csv'|'.csv.gz'] -> dict(filename:list)
                
            tournament:
                return data matching leaf_dir pattern where path is a single subjob, in tournament this is a single gameform
                - gameform file, eg: 129249\129249_136\129249_136.tar.gz
                    - decompress gives result_set_tar, eg: 129249_136.tar
                    - if compressed writes:
                        - open tarfile and take list of every file within that matches supplied patterns
                            - history_file_compressed_extension
                            - leaf_dir
                        - list recorded in: found_csv_gz
                            - len(found_csv_gz) == tournament_strategy_count * episodes * 4 
                                - (4 == number of outcome distributions [CC, CD, DC, DD])
                        - sort this list
                            - makes good on three requirements:
                                eg: 129249_0/21/history_outcomes_cumulative/exp_129249_0_outcomes_episode_1_cd_cumulative.csv.gz
                                - tournament_trial_id: /21/
                                - file episode id: episode_1
                                - file outcome pattern: cd
                        - iterate over the sorted list:
                            - each entry is a csv.gz file in the tar.gz file (which is effectively a tar file now)
                                - tar extract the csv.gz file as: csv_gz_file
                                - decompress the csv.gz: is now a csv object
                                - use a list comprehension to read each value form the csv object _as an int_ and *append* to a temporary list, trial_array
                            - trial_array has shape: [tournament_strategy_count * episodes * 4][timesteps]
                            
                        - for each trial array:
                            - add to a dict where key is of form: {sj}_{trial}_{ep}_{o}
                                
                                
                            
                            
        '''
        result_set_data = {}
        
        with open(os.path.join(path, file), 'rb') as f:
            result_set_tar = gzip.decompress(f.read())
            
        if compressed_writes:
            
            found_csv_gz = []
            
            with tarfile.open(fileobj = io.BytesIO(result_set_tar), mode = 'r') as t:
            
                for file_in_tar in t.getnames():
                    if file_in_tar.lower().endswith(self.hpc_config["exp"]["history_file_compressed_extension"]) and leaf_dir in file_in_tar:   
                        found_csv_gz.append(file_in_tar)
                
                found_csv_gz = natsorted(found_csv_gz)
                 
                for file_in_tar in found_csv_gz:
                
                    csv_gz_file = t.extractfile(file_in_tar)
                    
                    with gzip.open(csv_gz_file, "rt") as file:

                        sj_label = file_in_tar.split('/')[0]
                        trial_label = file_in_tar.split('/')[1]

                        if leaf_dir == "history_outcomes_cumulative":
                            ep_label = re.search("_episode_(\d*_\w\w)_", file_in_tar.split('/')[3])[1].split('_')[0]
                            o_label = re.search("_episode_(\d*_\w\w)_", file_in_tar.split('/')[3])[1].split('_')[1]
                            entry_label = sj_label + "_" + trial_label + "_" + ep_label + "_" + o_label
                            
                        elif leaf_dir == "history_rewards":
                            ep_label = re.search("_episode_(\d*)", file_in_tar.split('/')[3])[1].split('_')[0]
                            a_label = file_in_tar.split('/')[3].split('_')[6] 
                            entry_label = sj_label + "_" + trial_label + "_" + a_label + "_" + ep_label
                            
                        result_set_data[entry_label] = [int(i) for i in list(csv.reader(file))[0]]
                        
        else:
        
            found_csv = []
            
            with tarfile.open(fileobj = io.BytesIO(result_set_tar), mode = 'r') as t:
                for file_in_tar in t.getnames():
                    if file_in_tar.lower().endswith(self.hpc_config["exp"]["history_file_uncompressed_extension"]) and leaf_dir in file_in_tar: 
                        found_csv.append(file_in_tar)
                
                found_csv = natsorted(found_csv)
                
                for csv_file in found_csv:
                    file = io.TextIOWrapper(t.extractfile(csv_file), encoding="utf-8")                
                    result_set_data[csv_file.split('/')[2]] = [int(i) for i in list(csv.reader(file))[0]]
                    
        return result_set_data     
        

    def access_sj_set_tournament(self, path, leaf_dir, compressed_writes, tournament_trial_count):
        '''
            we know exact path and the subjob is uncompressed
                but leaf directories may contain compressed files (compressed_writes == true)
            
            extract experiment result_set_data matching a specific leaf_dir pattern from 
                ['.csv'|'.csv.gz'] -> dict(filename:list)
        
            ** to natsort the entries, differetn approach here - using OrderedDict - than for access_sj_gz(),
                as there is no comparator defined for nt.entry
                
        '''

        result_set_data = {}

        if compressed_writes:
            
            with os.scandir(os.path.join(path, leaf_dir)) as result_set_ls:  
                for entry in result_set_ls:
                    if entry.is_file():
                        with gzip.open(entry, "rt") as file:
                            result_set_data[entry.name] = [int(i) for i in list(csv.reader(file))[0]]
                
        else:
            
            with os.scandir(os.path.join(path, leaf_dir)) as result_set_ls:
                for entry in result_set_ls:
                    if entry.is_file():
                        with open(entry, newline='') as file:
                            result_set_data[entry.name] = [int(i) for i in list(csv.reader(file))[0]]
           
        return OrderedDict(natsorted(result_set_data.items(), key=lambda t: t[0]))
    
    
    
    

    ''' 
        eo_ep_o functions
            some duplication here - [TODO] re-organise util class (12022021)

    '''

    def eo_ep_o_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["analysis"]["ep_o"]["ep_o"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        
        
    def make_ep_o_job_paths(self, obs_data, obs_data_summary):
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
            
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"], self.hpc_config["analysis"]["ep_o"]["leaf_data"])
        self.make_job_path(path)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ep_o"]["leaf_data"])
        self.make_job_path(path)
        




        
    def eo_ep_o_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        
        obs_data["obs_exp"]["obs_subjob_data_path"] = self.hpc_config["paths"]["observations"] + [obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"]]
        obs_data["obs_exp"]["sj_count"] = len(obs_data_summary["obs_exp"]["exp_subjobs_list"])
    

    def retrieve_obs_data_summary(self, obs_data):
        obs_data_summary = {}
        parent_id = obs_data["obs_exp"]["exp_parent_id"]    
        
        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), parent_id)
        file = self.hpc_config["obs"]["data_file_prefix"] + parent_id + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'r') as f:
            obs_data_summary = json.load(f)
        
        return obs_data_summary
        
        
    def eo_ep_o_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)
   

    def eo_ep_o_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)        
    
    
    def eo_ep_o_write_obs_data(self, obs_data, obs_data_summary, data, sj, file_suffix):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ep_o"]["leaf_data"])
        file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ep_o"]["ep_o"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            write = csv.writer(csv_file)
            for k, v in data.items():
                write.writerow(v)
        
        return [self.hpc_config["analysis"]["ep_o"]["leaf_data"], file]



    '''
        eo_ts_o functions
        
            
        ()
        
        
        
    '''
    
    
    def eo_ts_o_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["analysis"]["ts_o"]["ts_o"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        


    def make_ts_o_job_paths(self, obs_data, obs_data_summary):
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
            
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"], self.hpc_config["analysis"]["ts_o"]["leaf_data"])
        self.make_job_path(path)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ts_o"]["leaf_data"])
        self.make_job_path(path)



    def eo_ts_o_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        
        obs_data["obs_exp"]["obs_subjob_data_path"] = self.hpc_config["paths"]["observations"] + [obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"]]
        obs_data["obs_exp"]["sj_count"] = len(obs_data_summary["obs_exp"]["exp_subjobs_list"])



    def eo_ts_o_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)



    def eo_ts_o_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)


    def eo_ts_o_write_obs_data(self, obs_data, obs_data_summary, data, sj, file_suffix):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ts_o"]["leaf_data"])
        file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ts_o"]["ts_o"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            write = csv.writer(csv_file)
            for k, v in data.items():
                write.writerow(v)
        
        return [self.hpc_config["analysis"]["ts_o"]["leaf_data"], file]    
    
    




    '''
        eo_ep_r functions
        
            
        ()
        
        
        
    '''
    
    
    def eo_ep_r_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["analysis"]["ep_r"]["ep_r"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        


    def make_ep_r_job_paths(self, obs_data, obs_data_summary):
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
            
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"], self.hpc_config["analysis"]["ep_r"]["leaf_data"])
        self.make_job_path(path)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ep_r"]["leaf_data"])
        self.make_job_path(path)



    def eo_ep_r_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        
        obs_data["obs_exp"]["obs_subjob_data_path"] = self.hpc_config["paths"]["observations"] + [obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"]]
        obs_data["obs_exp"]["sj_count"] = len(obs_data_summary["obs_exp"]["exp_subjobs_list"])



    def eo_ep_r_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)



    def eo_ep_r_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)


    # def eo_ep_r_write_obs_data_agent_pair(self, obs_data, obs_data_summary, data, sj, file_suffix):
        
        # path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ep_r"]["leaf_data"])
        # file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ep_r"]["ep_r"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        # with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            # write = csv.writer(csv_file)
            # #for k, v in data.items():
            # write.writerow(data)
        
        # return [self.hpc_config["analysis"]["ep_r"]["leaf_data"], file]    


    def eo_ep_r_write_obs_data(self, obs_data, obs_data_summary, data, sj, file_suffix):
       
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ep_r"]["leaf_data"])
        file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ep_r"]["ep_r"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            write = csv.writer(csv_file)
            write.writerow(data)
        
        return [self.hpc_config["analysis"]["ep_r"]["leaf_data"], file]
    
    
    



    '''
        eo_ts_r functions
        
            
        ()
        
        
        
    '''
    
    
    def eo_ts_r_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["journal_output_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["analysis"]["ts_r"]["ts_r"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        


    def make_ts_r_job_paths(self, obs_data, obs_data_summary):
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"])
        if not os.path.isdir(path):
            print(os.path.basename(__file__) + ":: Error: Observation Directory (" + path + "/) does not exist.")
            exit(2)
            
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"], self.hpc_config["analysis"]["ts_r"]["leaf_data"])
        self.make_job_path(path)
        
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ts_r"]["leaf_data"])
        self.make_job_path(path)



    def eo_ts_r_set_obs_data_end(self, obs_data, obs_data_summary):
        obs_time_end_ns = time_ns()
        
        obs_data["obs_invocation"]["obs_time_end_hr"] = datetime.fromtimestamp(obs_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        obs_data["obs_invocation"]["obs_time_end_ns"] = obs_time_end_ns
        obs_data["obs_invocation"]["process_end_ns"] = process_time_ns()
        
        obs_data["obs_exp"]["obs_subjob_data_path"] = self.hpc_config["paths"]["observations"] + [obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"]]
        obs_data["obs_exp"]["sj_count"] = len(obs_data_summary["obs_exp"]["exp_subjobs_list"])



    def eo_ts_r_write_obs_data_summary(self, obs_data, obs_data_summary):
        
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)



    def eo_ts_r_write_obs_journal(self, obs_data, obs_data_summary):

        path = os.path.join(os.sep.join(self.hpc_config["journal"]["journal_path"]), obs_data_summary["obs_exp"]["exp_parent_id"])
        file = obs_data["journal_output_filename"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w') as json_file:
            json.dump(obs_data, json_file)


    def eo_ts_r_write_obs_data_agent_pair(self, obs_data, obs_data_summary, data, sj, file_suffix):
        #print(data)
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ts_r"]["leaf_data"])
        file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ts_r"]["ts_r"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            write = csv.writer(csv_file)
            for k in data:
                write.writerow(k)
        
        return [self.hpc_config["analysis"]["ts_r"]["leaf_data"], file]    

    # dupe while writing timestep/episode_rewards .. refactor [TODO]
    def eo_ts_r_write_obs_data(self, obs_data, obs_data_summary, data, sj, file_suffix):
       
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ts_r"]["leaf_data"])
        file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ts_r"]["ts_r"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            write = csv.writer(csv_file)
            #for k, v in data.items():
            write.writerow(data)
        
        return [self.hpc_config["analysis"]["ts_r"]["leaf_data"], file]
    
    def eo_ts_r_write_obs_data_items(self, obs_data, obs_data_summary, data, sj, file_suffix):
       
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_data"], self.hpc_config["analysis"]["ts_r"]["leaf_data"])
        file = obs_data["obs_exp"]["obs_data_filename_prefix"] + "_sj_" + sj + self.hpc_config["analysis"]["ts_r"]["ts_r"] + file_suffix + self.hpc_config["obs"]["data_file_extension"]
        
        with open(os.path.join(obs_data["obs_invocation"]["basepath"], path, file), 'w', newline='') as csv_file:
            write = csv.writer(csv_file)
            for k in data:
                write.writerow(k)
        
        return [self.hpc_config["analysis"]["ts_r"]["leaf_data"], file]
    
 
    

    '''
    
        ep_o functions
    
    '''  
    
    
    '''
        per episode terminal count
        
            for each episode, take the final count of each outcome
        
        config tag
            - terminal_e_count
        
        file
            - obs_{__EXP_ID__}_sj_{__SJ_ID__}_ep_o_terminal_e_count.csv
        
        rows = outcomes (cc, cd, dc, dd)
        columns = episode
        
    '''

    def ep_o_assemble_terminal_e_count(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_terminal_count = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_terminal_count:
                    sj_data_terminal_count[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                final_outcome_count = rs_item[-1]
                sj_data_terminal_count[sj][outcome].append(final_outcome_count)
                
        for sj, item in sj_data_terminal_count.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_e_count"] = self.eo_ep_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_o"]["terminal_e_count"])
             
    
    # may not need this for tournament - want e-mean
    def ep_o_assemble_terminal_e_count_tournament(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_terminal_count = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        #print(result_set_data)
        for rs in result_set_data:
            #print(rs)
            for rs_key, rs_item in rs.items():
                #print(rs_key)
                #print(rs_item)
                pass
                # sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                # outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                # if sj not in sj_data_terminal_count:
                    # sj_data_terminal_count[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                # final_outcome_count = rs_item[-1]
                # sj_data_terminal_count[sj][outcome].append(final_outcome_count)
                
        # for sj, item in sj_data_terminal_count.items():
            # obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_e_count"] = self.eo_ep_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_o"]["terminal_e_count"])
             
    
    
    
    '''
        all episodes mean terminal count
        
            for each episode, take the final count of each outcome
        
        config tag
            - terminal_e_count_e_mean
        
        file
            - obs_{__EXP_ID__}_sj_{__SJ_ID__}_ep_o_terminal_e_count_e_mean.csv
        
        rows = outcomes (cc, cd, dc, dd)
        column = episode
        
    '''
    
    
    def ep_o_assemble_terminal_e_count_e_mean(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_count = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_terminal_count_mean = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_terminal_count:
                    sj_data_terminal_count[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_terminal_count_mean:
                    sj_data_terminal_count_mean[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                final_outcome_count = rs_item[-1]
                sj_data_terminal_count[sj][outcome].append(final_outcome_count)
        
        #norm = 1 / obs_data_summary["obs_exp"]["exp_episodes"] 
        for sj in sj_data_terminal_count:
            for outcome in sj_data_terminal_count[sj]:        

                sj_data_terminal_count_mean[sj][outcome] = ["{0:.5f}".format(sum(sj_data_terminal_count[sj][outcome]) / obs_data_summary["obs_exp"]["exp_episodes"])]    
        

        for sj, item in sj_data_terminal_count_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_e_count_e_mean"] = self.eo_ep_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_o"]["terminal_e_count_e_mean"])
            
       
   
    def ep_o_assemble_terminal_e_count_e_mean_tournament(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_count = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_terminal_count_mean = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_terminal_count:
                    sj_data_terminal_count[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_terminal_count_mean:
                    sj_data_terminal_count_mean[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                final_outcome_count = rs_item[-1]
                sj_data_terminal_count[sj][outcome].append(final_outcome_count)
        
        #norm = 1 / obs_data_summary["obs_exp"]["exp_episodes"] 
        for sj in sj_data_terminal_count:
            for outcome in sj_data_terminal_count[sj]:        

                sj_data_terminal_count_mean[sj][outcome] = ["{0:.5f}".format(sum(sj_data_terminal_count[sj][outcome]) / obs_data_summary["obs_exp"]["exp_episodes"])]    
        

        for sj, item in sj_data_terminal_count_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_e_count_e_mean"] = self.eo_ep_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_o"]["terminal_e_count_e_mean"])
            
          


    '''
        per episode terminal distribution
            per episode, take final outcome count, normalise to timesteps

        config tag
            - terminal_e_distribution
        
        file
            - obs_{__EXP_ID__}_sj_{__SJ_ID__}_ep_o_terminal_e_distribution.csv
        
        rows = outcomes (cc, cd, dc, dd)
        columns = episodes       
        
    '''
    
    def ep_o_assemble_terminal_e_distribution(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_distribution = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }

        norm = 1 / obs_data_summary["obs_exp"]["exp_timesteps"]    
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                

                if sj not in sj_data_terminal_distribution:
                    sj_data_terminal_distribution[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                final_outcome_count = rs_item[-1]
                sj_data_terminal_distribution[sj][outcome].append("{0:.5f}".format(float(final_outcome_count * norm)))
                
        for sj, item in sj_data_terminal_distribution.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_e_distribution"] = self.eo_ep_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_o"]["terminal_e_distribution"])



    '''
       all episodes mean terminal distribution 

        obs_{__EXP_ID__}_sj_{__SJ_ID__}_ep_o_mean_terminal_distribution.csv
        
        config tag
            - terminal_e_distribution_e_mean
        
        file
            - obs_{__EXP_ID__}_sj_{__SJ_ID__}_ep_o_terminal_e_distribution_e_mean.csv
        
        rows = outcomes (cc, cd, dc, dd)
        columns = episodes 
        
    '''
    def ep_o_assemble_terminal_distribution_e_mean(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_count = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_terminal_count_mean = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_terminal_distribution_e_mean = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_terminal_count:
                    sj_data_terminal_count[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_terminal_count_mean:
                    sj_data_terminal_count_mean[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_terminal_distribution_e_mean:
                    sj_data_terminal_distribution_e_mean[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                final_outcome_count = rs_item[-1]
                sj_data_terminal_count[sj][outcome].append(final_outcome_count)
        
        
        for sj in sj_data_terminal_count:
            for outcome in sj_data_terminal_count[sj]:        

                sj_data_terminal_count_mean[sj][outcome] = ["{0:.5f}".format(sum(sj_data_terminal_count[sj][outcome]) / obs_data_summary["obs_exp"]["exp_episodes"])]    

        
        for sj in sj_data_terminal_count_mean:
            for outcome in sj_data_terminal_count_mean[sj]:
            
                norm = 1 / obs_data_summary["obs_exp"]["exp_timesteps"]
                sj_data_terminal_distribution_e_mean[sj][outcome] = ["{0:.5f}".format(float(sj_data_terminal_count_mean[sj][outcome][0]) * norm)]
        
 
        for sj, item in sj_data_terminal_distribution_e_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_e_distribution_e_mean"] = self.eo_ep_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_o"]["terminal_e_distribution_e_mean"])
            
        
    '''
    
        ts_o functions
    
    ''' 
    
    
    
    '''
        per episode terminal outcome count, episode sum
            
            each value is sum of outcome across all timesteps in episode
            
        config tag
            - terminal_o_count
        
        file
            - terminal_o_count
            
        - integrity: each column should sum to |timesteps|
        
        rows = outcomes
        columns = episodes
          
    '''
    
    def ts_o_assemble_terminal_o_count(self, result_set_data, obs_data, obs_data_summary):

        sj_data_terminal_o_count = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                
                if sj not in sj_data_terminal_o_count:
                    sj_data_terminal_o_count[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                final_outcome_count = rs_item[-1]            
                sj_data_terminal_o_count[sj][outcome].append(final_outcome_count)
                

        for sj, item in sj_data_terminal_o_count.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_o_count"] = self.eo_ts_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_o"]["terminal_o_count"])
          
        
    
    
    '''
        per timestep accumulating sum of outcome, over all episodes
            
            each value is the accumulated sum of occurences of the outcome across all timesteps in all episodes
            
        config tag
            - o_accum_sum_e_sum
        
        file
            - o_accum_sum_e_sum
            
        - integrity: sum of each column should equal |episodes| * timestep
        
        rows = outcomes
        columns = timesteps
          
    '''
    
    def ts_o_assemble_o_accum_sum_e_sum(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_timestep_accum_sum = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_ts_o_accum_sum_e_sum = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_timestep_accum_sum:
                    sj_data_timestep_accum_sum[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_ts_o_accum_sum_e_sum:
                    sj_data_ts_o_accum_sum_e_sum[str(sj)] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                episode = []
                for i in rs_item:
                    episode.append(i)
                
                sj_data_timestep_accum_sum[sj][outcome].append(episode)  
        
        
        for sj in sj_data_timestep_accum_sum:
            for o in sj_data_timestep_accum_sum[sj]:

                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]

                for ep in sj_data_timestep_accum_sum[sj][o]:

                    for i, v in enumerate(ep):
                        ts_sum[i] += v

                    sj_data_ts_o_accum_sum_e_sum[str(sj)][o] = ts_sum 
        
        for sj, item in sj_data_ts_o_accum_sum_e_sum.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["o_accum_sum_e_sum"] = self.eo_ts_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_o"]["o_accum_sum_e_sum"])
        
    
    
    
    '''
        per timestep, accumulating sum of outcome, sum of all episodes, normalised to potential number of total outcomes (|episodes| x |timesteps|
            
            each value is the accumulated sum of occurences of the outcome across all timesteps in all episodes up to that timestep, normalised
            
        config tag
            - o_accum_sum_e_sum_distribution
        
        file
            - o_accum_sum_e_sum_distribution
            
        - integrity: sum of each column should equal |episodes| * timestep
        
        rows = outcomes
        columns = timesteps
          
    '''
    
    def ts_o_assemble_o_accum_sum_e_sum_distribution(self, result_set_data, obs_data, obs_data_summary): 
    
        sj_data_timestep_accum_sum = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_ts_o_accum_sum_e_sum = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_o_accum_sum_e_sum_distribution = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_timestep_accum_sum:
                    sj_data_timestep_accum_sum[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_ts_o_accum_sum_e_sum:
                    sj_data_ts_o_accum_sum_e_sum[str(sj)] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_o_accum_sum_e_sum_distribution:
                    sj_data_o_accum_sum_e_sum_distribution[str(sj)] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                episode = []
                for i in rs_item:
                    episode.append(i)
                
                sj_data_timestep_accum_sum[sj][outcome].append(episode)  
        
        
        for sj in sj_data_timestep_accum_sum:
            for o in sj_data_timestep_accum_sum[sj]:

                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]

                for ep in sj_data_timestep_accum_sum[sj][o]:

                    for i, v in enumerate(ep):
                        ts_sum[i] += v

                    sj_data_ts_o_accum_sum_e_sum[str(sj)][o] = ts_sum 
                    
        e = 1
        norm = 1 / (obs_data_summary["obs_exp"]["exp_episodes"]  * e)
        
        for t in range(obs_data_summary["obs_exp"]["exp_timesteps"]):   
            for sj in  sj_data_ts_o_accum_sum_e_sum:
                for o, d in sj_data_ts_o_accum_sum_e_sum[sj].items():

                    sj_data_o_accum_sum_e_sum_distribution[sj][o].append( "{0:.5f}".format(d[t] * norm))
                    
            e += 1
            norm = 1 / (obs_data_summary["obs_exp"]["exp_episodes"]  * e)
        
        
        for sj, item in sj_data_o_accum_sum_e_sum_distribution.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["o_accum_sum_e_sum_distribution"] = self.eo_ts_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_o"]["o_accum_sum_e_sum_distribution"])
    
    
    
    
    '''
        per timestep accumulating sum of outcome, mean of all episodes
            
            each value is the accumulated sum of occurences of the outcome across all timesteps in all episodes
            
        config tag
            - o_accum_sum_e_mean
        
        file
            - o_accum_sum_e_mean
            
        - integrity: sum of each column should equal |episodes| * timestep
        
        rows = outcomes
        columns = timesteps
          
    '''
    

    def ts_o_assemble_o_accum_sum_e_mean(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_timestep_accum_sum = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_ts_o_accum_sum_e_mean = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_timestep_accum_sum:
                    sj_data_timestep_accum_sum[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_ts_o_accum_sum_e_mean:
                    sj_data_ts_o_accum_sum_e_mean[str(sj)] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                episode = []
                for i in rs_item:
                    episode.append(i)
                
                sj_data_timestep_accum_sum[sj][outcome].append(episode)  
                
        
        for sj in sj_data_timestep_accum_sum:
            for o in sj_data_timestep_accum_sum[sj]:

                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]
                
                for ep in sj_data_timestep_accum_sum[sj][o]:

                    for i, v in enumerate(ep):
                        ts_sum[i] += v / obs_data_summary["obs_exp"]["exp_episodes"]
   
                    sj_data_ts_o_accum_sum_e_mean[str(sj)][o] = ts_sum 
        
                for i,v in enumerate(sj_data_ts_o_accum_sum_e_mean[str(sj)][o]):
                    sj_data_ts_o_accum_sum_e_mean[str(sj)][o][i] = "{0:.5f}".format(sj_data_ts_o_accum_sum_e_mean[str(sj)][o][i])
                        
        for sj, item in sj_data_ts_o_accum_sum_e_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["o_accum_sum_e_mean"] = self.eo_ts_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_o"]["o_accum_sum_e_mean"])
            
    
    
    
    '''
        per timestep, accumulating sum of outcome, sum of all episodes, normalised to potential number of total outcomes (|episodes| x |timesteps|
            
            each value is the accumulated sum of occurences of the outcome across all timesteps in all episodes up to that timestep, normalised
            
        config tag
            - o_accum_sum_e_sum_distribution
        
        file
            - o_accum_sum_e_sum_distribution
            
        - integrity: sum of each column should equal |episodes| * timestep
        
        rows = outcomes
        columns = timesteps
          
    '''
    
    def ts_o_assemble_o_accum_sum_e_mean_distribution(self, result_set_data, obs_data, obs_data_summary): 
    
        sj_data_timestep_accum_sum = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        sj_data_ts_o_accum_sum_e_mean = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        o_accum_sum_e_mean_distribution = { "0" : {"cc" : [], "cd" : [], "dc" : [], "dd" : []} }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
                
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                outcome = re.search("_episode_(\d*_\w\w)_", rs_key)[1].split('_')[1]
                
                if sj not in sj_data_timestep_accum_sum:
                    sj_data_timestep_accum_sum[sj] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in sj_data_ts_o_accum_sum_e_mean:
                    sj_data_ts_o_accum_sum_e_mean[str(sj)] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                    
                if sj not in o_accum_sum_e_mean_distribution:
                    o_accum_sum_e_mean_distribution[str(sj)] = {"cc" : [], "cd" : [], "dc" : [], "dd" : []}
                
                episode = []
                for i in rs_item:
                    episode.append(i)
                
                sj_data_timestep_accum_sum[sj][outcome].append(episode)  
        
        
        for sj in sj_data_timestep_accum_sum:
            for o in sj_data_timestep_accum_sum[sj]:

                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]

                for ep in sj_data_timestep_accum_sum[sj][o]:

                    for i, v in enumerate(ep):
                        ts_sum[i] += v 

                    sj_data_ts_o_accum_sum_e_mean[str(sj)][o] = ts_sum 
                    
        e = 1
        norm = 1 / ( e * obs_data_summary["obs_exp"]["exp_episodes"])

        for t in range(obs_data_summary["obs_exp"]["exp_timesteps"]):   
            for sj in  sj_data_ts_o_accum_sum_e_mean:
                for o, d in sj_data_ts_o_accum_sum_e_mean[sj].items():

                    o_accum_sum_e_mean_distribution[sj][o].append( "{0:.5f}".format(d[t] * norm))
                    
            e += 1
            norm = 1 / ( e * obs_data_summary["obs_exp"]["exp_episodes"])


        for sj, item in o_accum_sum_e_mean_distribution.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["o_accum_sum_e_mean_distribution"] = self.eo_ts_o_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_o"]["o_accum_sum_e_mean_distribution"])    
    
    
    
    
    
    '''
    
        ep_r functions
    
    '''   
    

    
    '''
        ep_r_assemble_agent_terminal_sum()
        
            sum of reward for agent per episode
        
        config tags
            - terminal_sum_agent_0
            - terminal_sum_agent_1
        
        files
            - terminal_sum_a0
            - terminal_sum_a0
        
        row = episodes
        columns = sum of reward at that episode
        
    '''

    def ep_r_assemble_agent_terminal_sum(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_sum = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')

                if sj not in sj_data_terminal_sum:
                    sj_data_terminal_sum[sj] = {"0" : [], "1" : [] }
                    
                sj_data_terminal_sum[sj][agent].append(sum(rs_item))
                
                
        for sj, agents in sj_data_terminal_sum.items():
            for a in agents:
                obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_sum" + "_agent_" + a] = self.eo_ep_r_write_obs_data(obs_data, obs_data_summary, agents[a], sj, self.hpc_config["analysis"]["ep_r"]["terminal_sum" + "_agent_" + a])
    

    
    
    '''
        ep_r_assemble_terminal_sum_a_mean()
        
            sum of reward per episode per agent, mean of |agents|
        
        config tag
            - terminal_sum_a_mean
        
        file
            - terminal_sum_a_mean
            
        
        row = episodes
        columns = sum of reward, mean of |agents|
        
    '''

    def ep_r_assemble_terminal_sum_a_mean(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_sum = { "0" : {"0" : [], "1" : [] } }
        sj_data_terminal_sum_a_mean = { "0" : [] }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')

                if sj not in sj_data_terminal_sum:
                    sj_data_terminal_sum[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_terminal_sum_a_mean:
                    sj_data_terminal_sum_a_mean[sj] = []
                    
                sj_data_terminal_sum[sj][agent].append(sum(rs_item))
            
        
        for sj in sj_data_terminal_sum:
    
            for e in range(0, obs_data_summary["obs_exp"]["exp_episodes"]):           
                r_sum = 0
                for a in sj_data_terminal_sum[sj].items():
                    r_sum += a[1][e]

                sj_data_terminal_sum_a_mean[sj].append( "{0:.5f}".format(r_sum / len(sj_data_terminal_sum[sj].items())))


        for sj, item in sj_data_terminal_sum_a_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_sum_a_mean"] = self.eo_ep_r_write_obs_data(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ep_r"]["terminal_sum_a_mean"])               

    '''
        ep_r_assemble_terminal_sum_a_mean_e_mean()
        
            sum of reward per episode per agent, mean of |agents|, mean of |episodes|
        
        config tag
            - terminal_sum_a_mean_e_mean
        
        file
            - terminal_sum_a_mean_e_mean
            
        
        row = value
        column = value
        
    '''

    def ep_r_assemble_terminal_sum_a_mean_e_mean(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_sum = { "0" : {"0" : [], "1" : [] } }
        sj_data_terminal_sum_a_mean = { "0" : [] }
        sj_data_terminal_sum_a_mean_e_mean = { "0" : [0] }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')

                if sj not in sj_data_terminal_sum:
                    sj_data_terminal_sum[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_terminal_sum_a_mean:
                    sj_data_terminal_sum_a_mean[sj] = []
                
                if sj not in sj_data_terminal_sum_a_mean_e_mean:
                    sj_data_terminal_sum_a_mean_e_mean[sj] = []
                
                sj_data_terminal_sum[sj][agent].append(sum(rs_item))


        for sj in sj_data_terminal_sum:
    
            for e in range(0, obs_data_summary["obs_exp"]["exp_episodes"]):           
                
                r_sum = 0
                for a in sj_data_terminal_sum[sj].items():
                    r_sum += a[1][e]

                sj_data_terminal_sum_a_mean[sj].append( r_sum / len(sj_data_terminal_sum[sj].items()))


        for sj in sj_data_terminal_sum_a_mean:
            
            for sj in sj_data_terminal_sum_a_mean.items():
                sj_data_terminal_sum_a_mean_e_mean[sj[0]] = "{0:.5f}".format(sum(sj[1]) / obs_data_summary["obs_exp"]["exp_episodes"])


        for sj, item in sj_data_terminal_sum_a_mean_e_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_sum_a_mean_e_mean"] = self.eo_ep_r_write_obs_data(obs_data, obs_data_summary, [sj_data_terminal_sum_a_mean_e_mean[sj]], sj, self.hpc_config["analysis"]["ep_r"]["terminal_sum_a_mean_e_mean"])
            
            
            
            

    '''
        ep_r_assemble_terminal_sum_e_mean()
        
            sum of reward per episode per agent, mean of |episodes|
        
        config tags
            - terminal_sum_e_mean_agent_0
            - terminal_sum_e_mean_agent_1
        
        files
            - terminal_sum_e_mean_a0
            - terminal_sum_e_mean_a1
            
        
        row = agent
        column = mean of agent total reward over all episodes 
        
    '''
    
    def ep_r_assemble_terminal_sum_e_mean(self, result_set_data, obs_data, obs_data_summary):
    
        
        sj_data_terminal_sum = { "0" : {"0" : [], "1" : [] } }
        sj_data_terminal_sum_e_mean = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')

                if sj not in sj_data_terminal_sum:
                    sj_data_terminal_sum[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_terminal_sum_e_mean:
                    sj_data_terminal_sum_e_mean[sj] = {"0" : [], "1" : [] }
                    
                sj_data_terminal_sum[sj][agent].append(sum(rs_item))


        for sj in sj_data_terminal_sum:

            for a in sj_data_terminal_sum[sj].items():
                sj_data_terminal_sum_e_mean[sj][a[0]].append("{0:.5f}".format(sum(a[1]) / obs_data_summary["obs_exp"]["exp_episodes"]))

   
        for sj, agents in sj_data_terminal_sum_e_mean.items():
            for a in agents:
                obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_sum_e_mean" + "_agent_" + a] = self.eo_ep_r_write_obs_data(obs_data, obs_data_summary, agents[a], sj, self.hpc_config["analysis"]["ep_r"]["terminal_sum_e_mean" + "_agent_" + a])    
    
    
    
    
    '''
        ep_r_assemble_terminal_sum_e_mean_a_mean()
        
            sum of reward per episode per agent, mean of {episodes|, mean of |agents|
        
        config tag
            - terminal_sum_e_mean_a_mean

        file
            - terminal_sum_e_mean_a_mean            
        
        row = value
        column = value
        
    '''
    
    def ep_r_assemble_terminal_sum_e_mean_a_mean(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_terminal_sum = { "0" : {"0" : [], "1" : [] } }
        sj_data_terminal_sum_e_mean = { "0" : {"0" : [], "1" : [] } }
        sj_data_a_mean_e_mean = { "0" : [0] }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')

                if sj not in sj_data_terminal_sum:
                    sj_data_terminal_sum[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_terminal_sum_e_mean:
                    sj_data_terminal_sum_e_mean[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_a_mean_e_mean:
                    sj_data_a_mean_e_mean[sj] = [0]
                
                sj_data_terminal_sum[sj][agent].append(sum(rs_item))

  
        for sj in sj_data_terminal_sum:
              
            for a in sj_data_terminal_sum[sj].items():
                sj_data_terminal_sum_e_mean[sj][a[0]].append( sum(a[1]) / obs_data_summary["obs_exp"]["exp_episodes"])
        
       
        for sj, agents in sj_data_terminal_sum_e_mean.items():
            a_mean_e_mean = 0
        
            for a in agents:    
                a_mean_e_mean += agents[a][0]
        
            sj_data_a_mean_e_mean[sj] = "{0:.5f}".format(a_mean_e_mean / len(agents))


        for sj in sj_data_a_mean_e_mean:
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["terminal_sum_e_mean_a_mean"] = self.eo_ep_r_write_obs_data(obs_data, obs_data_summary, [sj_data_a_mean_e_mean[sj]], sj, self.hpc_config["analysis"]["ep_r"]["terminal_sum_e_mean_a_mean"]) 
    
    

    
    '''
    
        ts_r functions
    
    '''
    
    
    
    '''
        ts_r_assemble_acumm_sum()
        
            cumulative sum of reward at each timestep t, for each episode
        
        config tag
            - acumm_sum_agent_0
            - acumm_sum_agent_1
        
        files
            - _acumm_sum_a0
            - _acumm_sum_a1
        
        rows = episodes
        columns = timesteps
        
        
    
    '''    
    
    
    def ts_r_assemble_agent_acumm_sum(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_acumm_sum = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_acumm_sum:
                    sj_data_acumm_sum[sj] = {"0" : [], "1" : [] }
                
                rs_sum = 0 
                episode_accum_sum = []
                
                for i in rs_item:
                    rs_sum += i
                    episode_accum_sum.append(rs_sum)

                sj_data_acumm_sum[sj][agent].append(episode_accum_sum)
                
                
        for sj, agents in sj_data_acumm_sum.items():
            for a in agents:
                obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["acumm_sum" + "_agent_" + a] = self.eo_ts_r_write_obs_data_agent_pair(obs_data, obs_data_summary, agents[a], sj, self.hpc_config["analysis"]["ts_r"]["acumm_sum" + "_agent_" + a])
    
    
    '''
        ts_r_assemble_agent_acumm_sum_e_mean()
        
            cumulative sum of reward at each timestep t, mean of all episodes at each timestep t
        
        config tags **
            - acumm_sum_e_mean_agent_0
            - acumm_sum_e_mean_agent_1
            
        files
            - _acumm_sum_e_mean_a0
            - _acumm_sum_e_mean_a1
        
        row = episode mean
        columns = timesteps
        
        
    
    '''  
    
    def ts_r_assemble_agent_acumm_sum_e_mean(self, result_set_data, obs_data, obs_data_summary):    
        
        
        sj_data_acumm_sum = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_acumm_sum:
                    sj_data_acumm_sum[sj] = {"0" : [], "1" : [] }
                
                rs_sum = 0 
                episode_accum_sum = []
                
                for i in rs_item:
                    rs_sum += i
                    episode_accum_sum.append(rs_sum)

                sj_data_acumm_sum[sj][agent].append(episode_accum_sum)
                
        

        sj_data_acumm_sum_e_mean = { "0" : {"0" : [], "1" : [] } }
    
        for sj in sj_data_acumm_sum:
            for a in sj_data_acumm_sum[sj]:
            
                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]

                for ep in sj_data_acumm_sum[sj][a]:
                    if sj not in sj_data_acumm_sum_e_mean:
                        sj_data_acumm_sum_e_mean[str(sj)] = {"0" : [], "1" : [] }
                    
                    for i, v in enumerate(ep):
                        ts_sum[i] += v
                    
                for i, t in enumerate(ts_sum):
                    ts_sum[i] = "{0:.8f}".format(ts_sum[i] / obs_data_summary["obs_exp"]["exp_episodes"])
            
                sj_data_acumm_sum_e_mean[str(sj)][a].append(ts_sum)
            
        
        for sj, agents in sj_data_acumm_sum_e_mean.items():
            for a in agents:
                obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["acumm_sum_e_mean" + "_agent_" + a] = self.eo_ts_r_write_obs_data_agent_pair(obs_data, obs_data_summary, agents[a], sj, self.hpc_config["analysis"]["ts_r"]["acumm_sum_e_mean" + "_agent_" + a])
        
        
 
    '''
        ts_r_assemble_acumm_sum_e_mean_a_mean()
        
            cumulative sum of reward at each timestep t, mean of all episodes at each timestep t, mean of both agents at each timestep
        
        config tag
            - acumm_sum_e_mean_a_mean
        
        file
            - acumm_sum_e_mean_a_mean
        
        row = episode mean
        columns = timesteps
        
        
        
        [TODO] simplify this function
    
    ''' 
    
    def ts_r_assemble_acumm_sum_e_mean_a_mean(self, result_set_data, obs_data, obs_data_summary):  

        sj_data_acumm_sum = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_acumm_sum:
                    sj_data_acumm_sum[sj] = {"0" : [], "1" : [] }
                
                rs_sum = 0 
                episode_accum_sum = []
                
                for i in rs_item:
                    rs_sum += i
                    episode_accum_sum.append(rs_sum)

                sj_data_acumm_sum[sj][agent].append(episode_accum_sum)
               
        

        sj_data_acumm_sum_e_mean = { "0" : {"0" : [], "1" : [] } }
    
        for sj in sj_data_acumm_sum:
            for a in sj_data_acumm_sum[sj]:
            
                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]

                for ep in sj_data_acumm_sum[sj][a]:
                    if sj not in sj_data_acumm_sum_e_mean:
                        sj_data_acumm_sum_e_mean[str(sj)] = {"0" : [], "1" : [] }
                    
                    for i, v in enumerate(ep):
                        ts_sum[i] += v
                    
                for i, t in enumerate(ts_sum):
                    ts_sum[i] = "{0:.8f}".format(ts_sum[i] / obs_data_summary["obs_exp"]["exp_episodes"])
            
                sj_data_acumm_sum_e_mean[str(sj)][a].append(ts_sum)
            
        
        # take mean of both agents at each timestep
        
        agent_mean_acumm_sum_e_mean = { "0" : [] }

        for sj in sj_data_acumm_sum_e_mean:
        
            if sj not in agent_mean_acumm_sum_e_mean:
                agent_mean_acumm_sum_e_mean[str(sj)] = []
            
            ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]
            
            for a in sj_data_acumm_sum_e_mean[sj]:
           
                for ep in sj_data_acumm_sum_e_mean[sj][a]:
            
                    for i, v in enumerate(ep):
                        ts_sum[i] += float(v)
                           
            for i, t in enumerate(ts_sum):
                ts_sum[i] = "{0:.2f}".format(ts_sum[i] / 2)
                
            agent_mean_acumm_sum_e_mean[str(sj)].append(ts_sum)
        
        
        for sj, item in agent_mean_acumm_sum_e_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["acumm_sum_e_mean_a_mean"] = self.eo_ts_r_write_obs_data(obs_data, obs_data_summary, item[0], sj, self.hpc_config["analysis"]["ts_r"]["acumm_sum_e_mean_a_mean"])
   
   
    '''
        ts_r_assemble_acumm_sum_a_mean()
        
            cumulative sum of reward at each timestep t, mean of both agents at each timestep in each episode
        
        config tag
            - acumm_sum_a_mean
        
        file
            - acumm_sum_a_mean
        
        rows = episodes
        columns = timesteps
        
        
    
    ''' 
    
    def ts_r_assemble_acumm_sum_a_mean(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_acumm_sum = { "0" : {"0" : [], "1" : [] } }
        sj_data_a_mean_acumm_sum = { "0" : [] }
        
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_acumm_sum:
                    sj_data_acumm_sum[sj] = {"0" : [], "1" : [] }
                    
                if sj not in sj_data_a_mean_acumm_sum:
                    sj_data_a_mean_acumm_sum[sj] = []                    

                    
                rs_sum = 0 
                episode_accum_sum = []
                
                for i in rs_item:
                    rs_sum += i
                    episode_accum_sum.append(rs_sum)

                sj_data_acumm_sum[sj][agent].append(episode_accum_sum)
        

        for sj in sj_data_acumm_sum:

            for e in range(0, obs_data_summary["obs_exp"]["exp_episodes"]):
                
                ts_sum = [0] * obs_data_summary["obs_exp"]["exp_timesteps"]
                
                for t in range(0, obs_data_summary["obs_exp"]["exp_timesteps"]):
                    ts_sum[t] = (sj_data_acumm_sum[sj]['0'][e][t] + sj_data_acumm_sum[sj]['1'][e][t]) / 2
                
                sj_data_a_mean_acumm_sum[sj].append(ts_sum)
                

        for sj, item in sj_data_a_mean_acumm_sum.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["acumm_sum_a_mean"] = self.eo_ts_r_write_obs_data_items(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_r"]["acumm_sum_a_mean"])

    
    '''
        ts_r_assemble_agent_timestep_mean()
        
            total reward over episode, divided by |timesteps|, per episode
        
        config tags
            - timestep_mean_agent_0
            - timestep_mean_agent_1
        
        files
            - timestep_mean_agent_0
            - timestep_mean_agent_1
        
        rows = episodes
        column = mean reward over episode
        
        
    
    '''  
    
    def ts_r_assemble_timestep_mean(self, result_set_data, obs_data, obs_data_summary):
    
        sj_data_timestep_mean = { "0" : {"0" : [], "1" : [] } }

        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_timestep_mean:
                    sj_data_timestep_mean[sj] = {"0" : [], "1" : [] }

                episode_series = []
                episode_series.append(sum(rs_item)/obs_data_summary["obs_exp"]["exp_timesteps"])
                 
                sj_data_timestep_mean[sj][agent].append(episode_series)
                
                
        for sj, agents in sj_data_timestep_mean.items():
            for a in agents:
                obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["timestep_mean" + "_agent_" + a] = self.eo_ts_r_write_obs_data_agent_pair(obs_data, obs_data_summary, agents[a], sj, self.hpc_config["analysis"]["ts_r"]["timestep_mean" + "_agent_" + a])  



    '''
        ts_r_assemble_timestep_mean_a_mean()
        
            total reward over episode, divided by |timesteps|, per episode, agent mean
        
        config tag
            - timestep_mean_a_mean
        
        file
            - timestep_mean_a_mean
        
        rows = episodes
        column = mean reward over episode
        
        
    
    '''

    def ts_r_assemble_a_mean_timestep_mean(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_a_mean_timestep_mean = { "0" : [] }
        sj_data_timestep_mean = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_timestep_mean:
                    sj_data_timestep_mean[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_a_mean_timestep_mean:
                    sj_data_a_mean_timestep_mean[sj] = []

                episode_series = []
                episode_series.append(sum(rs_item)/obs_data_summary["obs_exp"]["exp_timesteps"])
                 
                sj_data_timestep_mean[sj][agent].append(episode_series)
                

        for sj in sj_data_timestep_mean:  
            
            ep_sum = [0] * obs_data_summary["obs_exp"]["exp_episodes"]
            
            for e in range(0, obs_data_summary["obs_exp"]["exp_episodes"]):     
                ep_sum[e] =  "{0:.5f}".format((sj_data_timestep_mean[sj]['0'][e][0] + sj_data_timestep_mean[sj]['1'][e][0]) / 2)
                
            sj_data_a_mean_timestep_mean[sj].append(ep_sum)

        
        for sj, item in sj_data_a_mean_timestep_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["timestep_mean_a_mean"] = self.eo_ts_r_write_obs_data_items(obs_data, obs_data_summary, item, sj, self.hpc_config["analysis"]["ts_r"]["timestep_mean_a_mean"])

    
    
  
    ''' 
        ts_r_assemble_timestep_mean_a_mean_e_mean()
        
            total reward over episode, divided by |timesteps|, agent mean, episode mean
        
        config tag
            - timestep_mean_a_mean_e_mean
        
        file
            - timestep_mean_a_mean_e_mean
        
        rows = episode
        column = mean reward over episodes
        
        
    
    '''    
    def ts_r_assemble_timestep_a_mean_mean_e_mean(self, result_set_data, obs_data, obs_data_summary):

        sj_data_a_mean_timestep_mean_e_mean = { "0" : [] }
        sj_data_a_mean_timestep_mean = { "0" : [] }
        sj_data_timestep_mean = { "0" : {"0" : [], "1" : [] } }
        
        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_timestep_mean:
                    sj_data_timestep_mean[sj] = {"0" : [], "1" : [] }
                
                if sj not in sj_data_a_mean_timestep_mean:
                    sj_data_a_mean_timestep_mean[sj] = []

                if sj not in sj_data_a_mean_timestep_mean_e_mean:
                    sj_data_a_mean_timestep_mean_e_mean[sj] = []
                    
                episode_series = []
                episode_series.append(sum(rs_item)/obs_data_summary["obs_exp"]["exp_timesteps"])
                 
                sj_data_timestep_mean[sj][agent].append(episode_series)
                

        for sj in sj_data_timestep_mean:  
            
            ep_sum = [0] * obs_data_summary["obs_exp"]["exp_episodes"]
            
            for e in range(0, obs_data_summary["obs_exp"]["exp_episodes"]):     
                ep_sum[e] =  "{0:.5f}".format((sj_data_timestep_mean[sj]['0'][e][0] + sj_data_timestep_mean[sj]['1'][e][0]) / 2)
                
            sj_data_a_mean_timestep_mean[sj].append(ep_sum)

        
        for sj in sj_data_a_mean_timestep_mean: 
            
            ep_sum = 0
            for e in sj_data_a_mean_timestep_mean[sj]:
                for i, v in enumerate(e):
                    ep_sum += float(v)
            
            sj_data_a_mean_timestep_mean_e_mean[sj].append("{0:.8f}".format(ep_sum / obs_data_summary["obs_exp"]["exp_episodes"]))
                
                
        for sj, item in sj_data_a_mean_timestep_mean_e_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["timestep_mean_a_mean_e_mean"] = self.eo_ts_r_write_obs_data_items(obs_data, obs_data_summary, [item], sj, self.hpc_config["analysis"]["ts_r"]["timestep_mean_a_mean_e_mean"])
 
    
    
    '''
        ts_r_assemble_agent_timestep_mean_e_mean()
            
            total reward over each episode, divided by |timesteps|, mean of episodes
        
        config tags
            - timestep_mean_e_mean_agent_0
            - timestep_mean_e_mean_agent_1
        
        files
            - timestep_mean_e_mean_a0
            - timestep_mean_e_mean_a1
        
        row = episode
        column = mean timestep reward over all episodes
        
    
    '''    
    def ts_r_assemble_agent_timestep_mean_e_mean(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_timestep_mean_e_mean  = { "0" : {"0" : 0, "1" : 0 } }
        sj_data_timestep_mean = { "0" : {"0" : [], "1" : [] } }

        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_timestep_mean:
                    sj_data_timestep_mean[sj] = {"0" : [], "1" : [] }

                episode_series = []
                episode_series.append(sum(rs_item)/obs_data_summary["obs_exp"]["exp_timesteps"])
                 
                sj_data_timestep_mean[sj][agent].append(episode_series)
        
        
        for sj in sj_data_timestep_mean:
            
            if sj not in sj_data_timestep_mean_e_mean:
                sj_data_timestep_mean_e_mean[str(sj)] = {"0" : 0, "1" : 0 }
                        
            for a in sj_data_timestep_mean[sj]:
            
                ep_sum = 0

                for ep in sj_data_timestep_mean[sj][a]:
                    ep_sum += sum(ep)
                    
                ep_sum = ep_sum / obs_data_summary["obs_exp"]["exp_episodes"]
                sj_data_timestep_mean_e_mean[str(sj)][a] = "{0:.8f}".format(ep_sum)

        
        for sj, agents in sj_data_timestep_mean_e_mean.items():
            for a in agents:
                obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["timestep_mean_e_mean" + "_agent_" + a] = self.eo_ts_r_write_obs_data(obs_data, obs_data_summary, [agents[a]], sj, self.hpc_config["analysis"]["ts_r"]["timestep_mean_e_mean" + "_agent_" + a]) 
    
   
 
    '''
        ts_r_assemble_timestep_mean_e_mean_a_mean()
        
            total reward over each episode, divided by |timesteps|, mean of episodes, mean of agents
        
        config tag
            - timestep_mean_e_mean_a_mean
        
        file
            - timestep_mean_e_mean_a_mean
        
        row = episode
        column = mean timestep reward over all episodes over all agents
        
        
        **the output value here should equal the output value of timestep_mean_a_mean_e_mean**
    
    '''    
    
    def ts_r_assemble_timestep_mean_e_mean_a_mean(self, result_set_data, obs_data, obs_data_summary):
        
        sj_data_timestep_mean_e_mean_a_mean = { "0" : [] }
        sj_data_timestep_mean_e_mean  = { "0" : {"0" : 0, "1" : 0 } }
        sj_data_timestep_mean = { "0" : {"0" : [], "1" : [] } }

        for rs in result_set_data:
            for rs_key, rs_item in rs.items():
            
                sj = re.search("^exp_\d*_(\d*)_", rs_key)[1]
              
                agent = re.search("_agent_(\d*)_", rs_key)[1]  #.split('_')
                # episode = re.search("_episode_(\d*)\.", rs_key)[1]  #.split('_')

                if sj not in sj_data_timestep_mean:
                    sj_data_timestep_mean[sj] = {"0" : [], "1" : [] }
                    
                if sj not in sj_data_timestep_mean_e_mean:
                    sj_data_timestep_mean_e_mean[str(sj)] = {"0" : 0, "1" : 0 }
                
                if sj not in sj_data_timestep_mean_e_mean_a_mean:
                    sj_data_timestep_mean_e_mean_a_mean[str(sj)] = []
                    

                episode_series = []
                episode_series.append(sum(rs_item)/obs_data_summary["obs_exp"]["exp_timesteps"])
                 
                sj_data_timestep_mean[sj][agent].append(episode_series)
        
        
        for sj in sj_data_timestep_mean:
                                    
            for a in sj_data_timestep_mean[sj]:
            
                ep_sum = 0

                for ep in sj_data_timestep_mean[sj][a]:
                    ep_sum += sum(ep)
                    
                #ep_sum = ep_sum / obs_data_summary["obs_exp"]["exp_episodes"]
                sj_data_timestep_mean_e_mean[str(sj)][a] = ep_sum / obs_data_summary["obs_exp"]["exp_episodes"] #"{0:.8f}".format(ep_sum)

        
        for sj in sj_data_timestep_mean_e_mean:
    
            ep_sum =  "{0:.8f}".format((sj_data_timestep_mean_e_mean[sj]['0'] + sj_data_timestep_mean_e_mean[sj]['1']) / 2)            
            sj_data_timestep_mean_e_mean_a_mean[sj].append(ep_sum)


        for sj, item in sj_data_timestep_mean_e_mean_a_mean.items():
            obs_data["obs_exp"]["exp_subjobs"][sj]["data_files"]["timestep_mean_e_mean_a_mean"] = self.eo_ts_r_write_obs_data_items(obs_data, obs_data_summary, [item], sj, self.hpc_config["analysis"]["ts_r"]["timestep_mean_e_mean_a_mean"]) 

    
    def eo_gen_e_r_set_obs_data_start(self, obs_data):
        obs_data["eo_id"] = obs_data["obs_exp"]["exp_parent_id"].split('_',1)[0] + "_" + obs_data["obs_id"] 
        obs_data["report_output_filename"] = self.hpc_config["report"]["obs_summary"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["report"]["obs_summary"]["report_suffix"] + self.hpc_config["report"]["obs_summary"]["report_extension"]
        obs_data["obs_exp"]["obs_data_filename_prefix"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"]
        obs_data["journal_obs_summary_filename"] = self.hpc_config["obs"]["data_file_prefix"] + obs_data["obs_exp"]["exp_parent_id"] + self.hpc_config["journal"]["journal_entry_suffix"] + self.hpc_config["journal"]["journal_entry_extension"]
        
        
        
    def write_report(self, obs_data, data, report_pdf):
        path = os.path.join(os.sep.join(self.hpc_config["paths"]["observations"]), data["obs_exp"]["exp_type"], obs_data["obs_exp"]["exp_parent_id"], self.hpc_config["obs"]["leaf_view"])
        file = obs_data["report_output_filename"]   # "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_report" + ".pdf" #obs_data["journal_obs_summary_filename"]
        report_pdf.output(os.path.join(obs_data["obs_invocation"]["basepath"], path, file))
        
        
    