#!/usr/bin/env python3
'''
    obs_generate_view_ep_o_table_outcomes
    
    - for symmetric_selfplay to rank across subjob set, for an outcome
    - where the exp is a set of subjobs where the signifying object can be ranked by ep_o terminal episode distribution episode mean
     gives:
        - strategy
        - cc, cd, dc, dd

'''
import sys, os, getopt
from time import process_time_ns, time_ns
import re
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from run_obs.view_util import View_utility as view_utility
from agent_model.utility import Utility as utility

def main(argv):
    
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
    
    column_names = ["Strategy", "CC", "CD", "DC", "DD"]

    data = []
    df_index = []
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        
        # want this
        #   basepath\results\observations\symmetric_selfplay\001\data\ts_o\obs_001_sj_0_ts_o_o_accum_sum_e_mean_distribution.csv
        path = os.path.join(os.sep.join(obs_data["obs_exp"]["obs_subjob_data_path"]), "ep_o")
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ep_o" + "_terminal_e_distribution_e_mean.csv"
        #s_outcomes = { obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"] : []}
        s_out = [] 
        
        sj_data = view_utility().fetch_data(path, file, obs_data)
        #print(sj_data[1][0])
        s_out.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"])
        for j in range(0, 4):
            #print(i)
            #data[obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"]].append(sj_data[j][0])
            #s_outcomes[obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"]].append(sj_data[j][0])
            s_out.append(sj_data[j][0])
        df_index.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"])
            #print(s_outcomes)
        #data[obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"]] = s_out
        
        data.append(s_out)

    #print(data)
    
    
    
    df = pd.DataFrame(data, index=df_index, columns=column_names)
    #print(df)
    df.sort_values(by=['CC'], inplace=True, ascending=False)
        # write to
        # basepath\results\observations\exp_type\parent_id\view\ts_o\view_001_sj_0_ts_o_o_accum_sum_e_mean_distribution.html
    path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], "view", "ep_o")
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + "_ep_o_table_outcomes.csv"
    filename = os.path.join(path, file)
        #print(os.path.join(path, file))
        #write_graph(data, obs_data_summary, i, os.path.join(path, file))
  
    df.to_csv(filename, encoding='utf-8', index=False)
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.Strategy, df.CC, df.CD, df.DC, df.DD],
                   fill_color='lavender',
                   align='left'))
    ])
    
    
    gameform, reward_type = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":") 
    episodes = obs_data_summary["obs_exp"]["exp_episodes"]
    timesteps = obs_data_summary["obs_exp"]["exp_timesteps"]

    exp_type = obs_data_summary["obs_exp"]["exp_type"]
    
    fig.update_layout(title=distribution_graph_title_dict(obs_data_summary, gameform, episodes, reward_type, exp_type))
    #fig.show()   
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + "_ep_o_table_outcomes.html"
    filename = os.path.join(path, file)
    fig.write_html(filename, include_plotlyjs="cdn")
    
    
    view_utility().eo_ts_o_view_set_obs_data_end(obs_data, obs_data_summary)
    view_utility().eo_ts_o_view_write_obs_data_summary(obs_data, obs_data_summary)
    view_utility().eo_ts_o_view_write_obs_journal(obs_data, obs_data_summary)



def distribution_graph_title_dict(obs_data_summary, gameform, episodes, reward_type, exp_type):
    exp_reference = obs_data_summary["obs_exp"]["exp_parent_id"]
    trial_agent_strategy_parameters = "" #self.get_trial_agent_strategy_parameters(obs_data_summary, sj_id)
    
    strategy_display_names = utility().strategy_display_names()
    gf_display_name = utility().retrieve_matrix_displayname(gameform)


    # if av_sin_tag == "mean":
        # av_sin_tag = " " + av_sin_tag.capitalize()
    timesteps = obs_data_summary["obs_exp"]["exp_timesteps"]
    episode_tag = "(over " + str(episodes) + " episodes of " + str(timesteps) + " timesteps)"
    # else:
        # av_sin_tag = ""
        # episode_tag = "(episode " + str(episodes+1) + ")"
    return {
        'text' : "<span style='font-size:12px;font-weight:bold;'>" + exp_type + " </span>" \
            + "<span style='font-size:12px;'>Episode-mean distribution of outcomes " + episode_tag + "</span> " \
            + "<br><span style='font-size:8px;'>[Exp_ID: " + exp_reference + "] " \
            + "[Gameform: " + gf_display_name + ", " + reward_type.capitalize() + "] </span>" ,
        'y':0.975,
        'x':0.055,
        'xanchor': 'left',
        'yanchor': 'top',
    }
     




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
    