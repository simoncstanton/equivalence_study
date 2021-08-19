#!/usr/bin/env python3
'''

    - generate for every subjob
        a-m, e-m; outcome distributions (4 values)
        a_mean, e-mean; reward  (1 value)
        
        build first
            - y = outcomes["cc"], x = terminal reward
        

'''
import sys, os, getopt
from time import process_time_ns, time_ns
import re
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


from run_obs.view_util import View_utility as view_utility
from agent_model.utility import Utility as utility

def main(argv):
    
    ''' 
        set up for analysis
    
    '''
    hpc_config = view_utility().load_hpc_config()
    
    obs_data = initialise_obs_data()
    parse_input(argv, obs_data)
    view_utility().set_basepath(obs_data)
    
    view_utility().eo_ts_o_view_set_obs_data_start(obs_data)
    print(os.path.basename(__file__) + ":: obs_exp_summary: " + obs_data["journal_obs_summary_filename"])
    
    obs_data_summary = view_utility().retrieve_obs_data_summary(obs_data)
    obs_data["obs_exp"]["obs_subjob_data_path"] = hpc_config["paths"]["observations"] + [obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], hpc_config["obs"]["leaf_data"]]
    obs_data["obs_exp"]["sj_count"] = len(obs_data_summary["obs_exp"]["exp_subjobs_list"])
    
    print(os.path.basename(__file__) + ":: exp_type: " + obs_data_summary["obs_exp"]["exp_type"])
    
    obs_data["exp_type"] = obs_data_summary["obs_exp"]["exp_type"] 
    obs_data["exp_reference"] = obs_data_summary["obs_exp"]["exp_parent_id"]   
    obs_data["path"] = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], "view", "ts_o")
    
    obs_data["strategy"] = obs_data_summary["obs_exp"]["exp_strategy_list"].split(',', 1)[0] 
    obs_data["gameform"] = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":")[0]
    obs_data["reward_type"] = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":")[1]
    obs_data["episodes"] = obs_data_summary["obs_exp"]["exp_episodes"] 
    obs_data["timesteps"] = obs_data_summary["obs_exp"]["exp_timesteps"]
     
    in_path = os.path.join(os.sep.join(obs_data["obs_exp"]["obs_subjob_data_path"]), "ep_r")
    in_path2 = os.path.join(os.sep.join(obs_data["obs_exp"]["obs_subjob_data_path"]), "ep_o")



    
    ''' 
        extract data from required files
        asemble z-data object
            
            - want, eg.
                obs_121999_sj_36_ts_r_acumm_sum_e_mean_a_mean
    
    '''
    sj_data_cc = []
    sj_data_rewards = []
    sj_index = []
    output_suffix = "_ts_outcome_v_reward"
    
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
    
        # want obs_121999_sj_36_ep_r_terminal_sum_e_mean_a_mean.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ep_r_terminal_sum_e_mean_a_mean.csv"  

        sj_data_rewards.append(view_utility().fetch_data(in_path, file, obs_data))
        sj_index.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"])

        
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
    
        # want obs_121999_sj_0_ep_o_terminal_e_distribution_e_mean.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ep_o_terminal_e_distribution_e_mean.csv"  

        sj_data_cc.append(view_utility().fetch_data(in_path2, file, obs_data)[0])
        #sj_index.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"])
        
    '''
        write reward graph, episode mean, agent mean, with lowess
    
    '''
    rewards = []
    cc_outcomes = []
    
    #print(len(sj_data_rewards))
    for i, sj in enumerate(sj_data_rewards): 
        #print(sj_data_rewards[i][0][0])
        rewards.append(sj_data_rewards[i][0][0])
    #print(rewards)
    
    for i, sj in enumerate(sj_data_cc): 
        #print(sj_data_cc[i][0][0])
        cc_outcomes.append(sj_data_cc[i][0])
    #print(cc_outcomes)


    coop_v_reward = {
        'CC': pd.Series(cc_outcomes, index=range(0, obs_data["obs_exp"]["sj_count"])),
        'Reward': pd.Series(rewards, index=range(0, obs_data["obs_exp"]["sj_count"])),
        
    }
    #df = pd.DataFrame(coop_v_reward, columns=sj_index)
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    sns.set(rc={'figure.figsize':(11.7,8.27)})

    sns.scatterplot(x=rewards, y = cc_outcomes, marker="+", color="black")
    
    for i, sj in enumerate(sj_index):
        plt.text(rewards[i]+5, cc_outcomes[i], sj_index[i], horizontalalignment='left', size='small', color='black', weight='normal')
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + ".png"
    plt.savefig(os.path.join(obs_data["path"], file))
    #plt.show()
    
    
    '''
        table of strategies, with cc and reward columns, sorted by cc, then reward
        
    '''
    table_data = []
    
    for i, sj in enumerate(sj_index):
        table_data.append([cc_outcomes[i], rewards[i]])
    
    df_table_data = pd.DataFrame(table_data, columns=['CC', 'Reward'], index=sj_index)
    df_table_data.sort_values(by=['CC', 'Reward'], inplace=True, ascending=False)
    
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Strategy'] + list(df_table_data.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df_table_data.index, df_table_data.CC, df_table_data.Reward],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title="Table") #distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "cc", facet=False, view_title="Parameter Pair by Descending Outcome Frequency "))
    #fig.show()
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_table.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")
    
    
    
    
    
    
    
    
    view_utility().eo_ts_r_view_set_obs_data_end(obs_data, obs_data_summary)
    view_utility().eo_ts_r_view_write_obs_data_summary(obs_data, obs_data_summary)
    view_utility().eo_ts_r_view_write_obs_journal(obs_data, obs_data_summary)










def parse_input(argv, obs_data):

    try:
        options, args = getopt.getopt(argv, "hj:l:", ["exp_id", "localhost"])
        print(os.path.basename(__file__) + ":: args", options)
    except getopt.GetoptError:
        print(os.path.basename(__file__) + ":: error in input, try -h for help")
        sys.exit(2)
        
    for opt, arg in options:
        if opt == '-h':
            print("usage: " + os.path.basename(__file__) + " \r\n \
            -j <eo_id [__EO_ID__]> | \r\n \
            -l <localhost> boolean (default is false) \r\n \
        ")
        
        elif opt in ('-j', '--pbs_jobstr'):
            obs_data["obs_exp"]["exp_parent_id"] = arg
        
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


def initialise_obs_data():    

    obs_time_start_ns = time_ns()
    
    return {
        "obs_id"                        : str(time_ns()),
        "eo_id"                         :   "",
        "journal_output_filename"       : "",
        "journal_obs_summary_filename"  : "",
        "path_to_writes"                : "",
        "output_suffix"                 : "",
        "hidden_parameters"             : ["gameform_matrix", "has_state", "notes", "temperature"],      # default parameters to elide from title block in graphs
        "outcome_labels"                : {"cc" : "Mutual Cooperation", "dd" : "Mutual Defection", "cd" : "Cooperate-Defect", "dc" : "Defect-Cooperate"},
        "strategy"                      : "", 
        "gameform"                      : "", 
        "outcome_label"                 : "", 
        "episodes"                      : "", 
        "timesteps"                     : "", 
        "reward_type"                   : "", 
        "exp_type"                      : "", 
        "exp_reference"                 : "",
        "obs_exp"   : {
            "exp_parent_id"             : "",
            "obs_data_filename_prefix"  : "",
            "sj_count"                  : 0,

        },
        "exp_subjobs"  : {
            "0"                     : {
                "data_files"    : [],
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
            "localhost"             : False,
            "home"				    : "",
            "basepath"				: "",
        },

        
    }







if __name__ == '__main__':
    main(sys.argv[1:]) 
    