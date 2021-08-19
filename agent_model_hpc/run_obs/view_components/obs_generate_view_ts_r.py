#!/usr/bin/env python3
'''

    - generate timestep reward scatter plot, mean of episodes
        

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
    obs_data["path"] = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], "view", "ts_r")
    
    obs_data["strategy"] = obs_data_summary["obs_exp"]["exp_strategy_list"].split(',', 1)[0] 
    obs_data["gameform"] = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":")[0]
    obs_data["reward_type"] = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":")[1]
    obs_data["episodes"] = obs_data_summary["obs_exp"]["exp_episodes"] 
    obs_data["timesteps"] = obs_data_summary["obs_exp"]["exp_timesteps"]
     
    in_path = os.path.join(os.sep.join(obs_data["obs_exp"]["obs_subjob_data_path"]), "ts_r")
    #obs_data["output_suffix"] = "_ts_r_a_mean_reward_per_timestep"


    
    ''' 
        extract data from required files
        asemble z-data object
            
            - want, eg.
                obs_121999_sj_36_ts_r_acumm_sum_e_mean_a_mean
    
    '''
    data = []
    sj_data = []
    sj_index = []
    output_suffix = "_ts_r_e_mean_a_mean"
    
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
    
        # want obs_121999_sj_36_ts_r_acumm_sum_e_mean_a_mean.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_r_acumm_sum_e_mean_a_mean.csv"  

        sj_data.append(view_utility().fetch_data(in_path, file, obs_data))
        sj_index.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"])
        
       
    '''
        write reward graph, episode mean, agent mean, with lowess
    
    '''
    
    for i, sj in enumerate(sj_data):

        for j, k in enumerate(sj_data[i]):
            s_out = [0]* obs_data["timesteps"]
            
            for p, v in enumerate(k):
                s_out[p] = v/(p+1)

            data.append(s_out)

        write_reward_graph(obs_data, obs_data_summary, data[i], sj_index[i], i, output_suffix)
    
    
    
    
    '''
        write reward graph, episode mean, both agents
    
    '''
    data_a0 = []
    sj_data_a0 = []
    sj_index_a0 = []
    output_suffix = "_ts_r_e_mean_a0_a1_traces"
    
    for i in range(0, obs_data["obs_exp"]["sj_count"]):

        # want obs_121999_sj_0_ts_r_acumm_sum_e_mean_a0.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_r_acumm_sum_e_mean_a0.csv"  

        sj_data_a0.append(view_utility().fetch_data(in_path, file, obs_data))
        sj_index_a0.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"])

    for i, sj in enumerate(sj_data_a0):

        for j, k in enumerate(sj_data_a0[i]):
            s_out = [0] * obs_data["timesteps"]
            
            for p, v in enumerate(k):
                s_out[p] = v/(p+1)

            data_a0.append(s_out)
    
    data_a1 = []
    sj_data_a1 = []
    sj_index_a1 = []

    for i in range(0, obs_data["obs_exp"]["sj_count"]):

        # want obs_121999_sj_0_ts_r_acumm_sum_e_mean_a1.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_r_acumm_sum_e_mean_a1.csv"  

        sj_data_a1.append(view_utility().fetch_data(in_path, file, obs_data))
        sj_index_a1.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"]) 
        
    for i, sj in enumerate(sj_data_a1):

        for j, k in enumerate(sj_data_a1[i]):
            s_out = [0]* obs_data["timesteps"]
            
            for p, v in enumerate(k):
                s_out[p] = v/(p+1)

            data_a1.append(s_out)
    
    
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        write_reward_graph_e_mean_a0_a1(obs_data, obs_data_summary, data_a0[i], data_a1[i], data[i], sj_index_a1[i], i, output_suffix)    
    
    
    
    
    '''
        write reward graph of all episodes per agent
        
        - want  
            sj -> a[] -> e[]
            strategy -> agent -> episode series
    
    '''    
    
    sj_data_all_series = []
    a0_data_all_series = []*obs_data["obs_exp"]["sj_count"]
    sj_index_all_series = []
    data_out = []

    output_suffix = "_ts_r_e_series_a0"

    for i in range(0, obs_data["obs_exp"]["sj_count"]):

        # want obs_121999_sj_0_ts_r_acumm_sum_a0.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_r_acumm_sum_a0.csv"  

        sj_data_all_series.append(view_utility().fetch_data(in_path, file, obs_data))
        
        sj_index_all_series.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"]) 
        
    for i, sj in enumerate(sj_data_all_series):
        
        one_set_e = []
        for k, e in enumerate(sj_data_all_series[i]):
        
            s_out = [0]* obs_data["timesteps"]
            for j, v in enumerate(e):
                s_out[j] = e[j] / (j+1)
            
            one_set_e.append(s_out)
        
        a0_data_all_series.append(one_set_e)   
                
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        a_id = "Zero"
        write_reward_graph_all_episode_series(obs_data, obs_data_summary, a0_data_all_series[i], sj_index_all_series[i], i, output_suffix, a_id)
    
    
    
    
    
    
    
    sj_data_all_series = []
    a0_data_all_series = [] * obs_data["obs_exp"]["sj_count"]
    sj_index_all_series = []
    data_out = []

    output_suffix = "_ts_r_e_series_a1"

    for i in range(0, obs_data["obs_exp"]["sj_count"]):

        # want obs_121999_sj_0_ts_r_acumm_sum_a0.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_r_acumm_sum_a1.csv"  

        sj_data_all_series.append(view_utility().fetch_data(in_path, file, obs_data))
        
        sj_index_all_series.append(obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["strategy"]) 
        
    for i, sj in enumerate(sj_data_all_series):
        
        one_set_e = []
        for k, e in enumerate(sj_data_all_series[i]):
        
            s_out = [0]* obs_data["timesteps"]
            for j, v in enumerate(e):
                s_out[j] = e[j] / (j+1)
            
            one_set_e.append(s_out)
        
        a0_data_all_series.append(one_set_e)   
                
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        a_id = "One"
        write_reward_graph_all_episode_series(obs_data, obs_data_summary, a0_data_all_series[i], sj_index_all_series[i], i, output_suffix, a_id)    
    
    
    
    
    
    
    
    
    
    view_utility().eo_ts_r_view_set_obs_data_end(obs_data, obs_data_summary)
    view_utility().eo_ts_r_view_write_obs_data_summary(obs_data, obs_data_summary)
    view_utility().eo_ts_r_view_write_obs_journal(obs_data, obs_data_summary)







def write_reward_graph_all_episode_series(obs_data, obs_data_summary, data_a, strategy, sj_id, output_suffix, a_id):

    trendline_type = "" #"lowess"
    trendlines_part = "" #"[" + trendline_type.upper() + " trendline] "
    av_sin_tag = "Agent " + a_id + ": all episodes."
    
    #alt_title = "Average Reward Sum by timestep"
    
    data = {}
    xaxis_timestep_range = range(1, obs_data["timesteps"]+1)
    for i, e in enumerate(data_a):
        data.update({ "episode " + str(i) : pd.Series(data_a[i], index=xaxis_timestep_range) })
        
    df = pd.DataFrame(data)
    
    fig = px.scatter(df) 

    y_max = view_utility().scale_y_max(obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["exp_invocation"]["reward_type"])    
    
    fig.update_yaxes(title_text='reward', title_font=dict(size=12), range=[0, y_max], tickfont=dict(size=8))
    fig.update_xaxes(title_text='timestep', title_font=dict(size=12), range=[1, obs_data["timesteps"]], tickfont=dict(size=8))


    for i in range(0, len(data_a)):
        fig.data[i].update(marker_size=2)   # marker_color="#00f"

    
    fig.update_layout(
        title = reward_graph_title_dict_e_series(obs_data, obs_data_summary, trendlines_part, av_sin_tag, strategy, sj_id),
        #legend=graph_legend_dict_e_series()
    )
    fig.update_layout(showlegend=False)
    
    #fig.show()
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + "_sj_" + str(sj_id) + output_suffix + ".html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")


def reward_graph_title_dict_e_series(obs_data, obs_data_summary, trendlines_part, av_sin_tag, strategy, sj_id):
    
    agent_strategy_parameters = get_agent_strategy_parameters(obs_data_summary, obs_data, sj_id)
    strategy_display_names = utility().strategy_display_names()
    gf_display_name = utility().retrieve_matrix_displayname(obs_data["gameform"])
    

    #av_sin_tag = " " + av_sin_tag.capitalize()
    episode_tag = "(" + str(obs_data["episodes"]) +  " episodes)"

        
    return {
        'text' : "<span style='font-size:12px;font-weight:bold;'>Selfplay: " + strategy_display_names[strategy] + "</span>" \
            + "<span style='font-size:12px;'> " + av_sin_tag + " Reward per-timestep " + episode_tag + " " \
            + "<span style='font-size:8px;'>" + trendlines_part  + " " \
            + "<span style='font-size:8px;'> [Exp_ID: " + obs_data["exp_reference"] + "] " \
            + "[Gameform: " + gf_display_name + ", " + obs_data["reward_type"].capitalize() + "] </span>" \
            
            + "<br>" + agent_strategy_parameters + "</span>",
        'y':0.975,
        'x':0.055,
        'xanchor': 'left',
        'yanchor': 'top',
    }
    
    
def graph_legend_dict_e_series():
    return dict(title='', font=dict(size=10), bgcolor='rgb(229, 236, 246)', itemsizing='constant')     





def write_reward_graph_e_mean_a0_a1(obs_data, obs_data_summary, data_0, data_1, data_mean, strategy, sj_id, output_suffix):
        
    trendline_type = "lowess"
    trendlines_part = "[" + trendline_type.upper() + " trendline] "
    av_sin_tag = "episode-mean"
    
    #s1 = pd.Series(data_0, index=range(0, obs_data["timesteps"]), name='s1')
    #s2 = pd.Series(data_1, index=range(0, obs_data["timesteps"]), name='s2')
    
    #df = pd.concat([s1, s2], axis=1)
    xaxis_timestep_range = range(1, obs_data["timesteps"]+1)
    data = {
        'Agent One': pd.Series(data_0, index=xaxis_timestep_range),
        'Agent Two': pd.Series(data_1, index=xaxis_timestep_range),
        "Agent-Mean"    : pd.Series(data_mean, index=xaxis_timestep_range),
    }
    df = pd.DataFrame(data)
    
    fig = px.scatter(df, trendline=trendline_type) 
    #fig.add_scatter(data_1)
    
    y_max = view_utility().scale_y_max(obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["exp_invocation"]["reward_type"])     
    
    fig.update_yaxes(title_text=av_sin_tag + ' reward', title_font=dict(size=12), range=[0, y_max], tickfont=dict(size=8))
    fig.update_xaxes(title_text='timestep', title_font=dict(size=12), range=[1, obs_data["timesteps"]], tickfont=dict(size=8))

    # set width of trend lines
    fig.data[1].update(line_width=0.5, line_color='#00f')
    fig.data[3].update(line_width=0.5, line_color='#f00')
    fig.data[5].update(line_width=0.5, line_color='#0f0')

    # set size of point data
    fig.data[0].update(marker_size=2)
    fig.data[2].update(marker_size=2)
    fig.data[4].update(marker_size=2)
    
    fig.update_layout(
        title = reward_graph_title_dict(obs_data, obs_data_summary, trendlines_part, av_sin_tag, strategy, sj_id),
        legend=graph_legend_dict()
    )
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + "_sj_" + str(sj_id) + output_suffix + ".html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")
    

    
def write_reward_graph(obs_data, obs_data_summary, data, strategy, sj_id, output_suffix):
    trendline_type = "lowess"
    trendlines_part = "[" + trendline_type.upper() + " trendlines] "
    av_sin_tag = "Agent-mean, Episode-mean."

    xaxis_timestep_range = range(1, obs_data["timesteps"]+1)
    dataframe = {
        'Agent Mean': pd.Series(data, index=xaxis_timestep_range),
    }
    
    df = pd.DataFrame(dataframe)
    fig = px.scatter(df, trendline=trendline_type) 

    y_max = view_utility().scale_y_max(obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["exp_invocation"]["reward_type"])   
    
    fig.update_yaxes(title_text=av_sin_tag + ' reward', title_font=dict(size=12), range=[0, y_max], tickfont=dict(size=8))
    fig.update_xaxes(title_text='timestep', title_font=dict(size=12), range=[1, obs_data["timesteps"]], tickfont=dict(size=8))  #, tickformat=',d' # integer axis labels, but adds LHS full height block

    # set width of trend lines
    fig.data[1].update(line_width=0.5, line_color='#f00')
    #fig.data[3].update(line_width=1)

    # set size of point data
    fig.data[0].update(marker_size=2)
    #fig.data[2].update(marker_size=2)
    
    fig.update_layout(
        title = reward_graph_title_dict(obs_data, obs_data_summary, trendlines_part, av_sin_tag, strategy, sj_id),
        legend=graph_legend_dict()
    )
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + "_sj_" + str(sj_id) + output_suffix + ".html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")
    



def reward_graph_title_dict(obs_data, obs_data_summary, trendlines_part, av_sin_tag, strategy, sj_id):
    
    agent_strategy_parameters = get_agent_strategy_parameters(obs_data_summary, obs_data, sj_id)
    strategy_display_names = utility().strategy_display_names()
    gf_display_name = utility().retrieve_matrix_displayname(obs_data["gameform"])
    
    # if av_sin_tag == "mean":
        # av_sin_tag = " " + av_sin_tag.capitalize()
        # episode_tag = "(over " + str(obs_data["episodes"]) +  " episodes)"
    # else:
        # episode_tag = "(episode " + str(obs_data["episodes"]) + ")"

    if av_sin_tag == "mean":
        av_sin_tag = " " + av_sin_tag.capitalize()
        episode_tag = "(over " + str(obs_data["episodes"]) +  " episodes)"
    elif av_sin_tag == "Agent-mean, Episode-mean.":
        av_sin_tag = " " + av_sin_tag.capitalize()
        episode_tag = "(over " + str(obs_data["episodes"]) +  " episodes)"
    elif av_sin_tag == "episode-mean":
        av_sin_tag = " " + av_sin_tag.capitalize()
        episode_tag = "(over " + str(obs_data["episodes"]) +  " episodes)"
    else:
        episode_tag = "(episode " + str(obs_data["episodes"]) + ")"
        
    return {
        'text' : "<span style='font-size:12px;font-weight:bold;'>Selfplay: " + strategy_display_names[strategy] + "</span>" \
            + "<span style='font-size:12px;'> " + av_sin_tag.capitalize() + " Reward per-timestep " + episode_tag + " " \
            + "<span style='font-size:8px;'>" + trendlines_part  + " " \
            + "<span style='font-size:8px;'> [Exp_ID: " + obs_data["exp_reference"] + "] " \
            + "[Gameform: " + gf_display_name + ", " + obs_data["reward_type"].capitalize() + "] </span>" \
            
            + "<br>" + agent_strategy_parameters + "</span>",
        'y':0.975,
        'x':0.055,
        'xanchor': 'left',
        'yanchor': 'top',
    }

 
def graph_legend_dict():
    return dict(title='', font=dict(size=10), bgcolor='rgb(229, 236, 246)', itemsizing='constant', yanchor="bottom", y=1.015, xanchor="right", x=1, orientation="h")   

def get_agent_strategy_parameters(obs_data_summary, obs_data, sj_id):
    parameter_string = ""
    for a in obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["agent_parameters"]:
        parameter_string += "[<span style='font-weight:bold;'>" + a + "</span>:"
        for k, v in obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["agent_parameters"][a]["strategy_parameters"].items():
            if k not in obs_data["hidden_parameters"]:
                parameter_string += " " + k + ":" + str(v)
        parameter_string += "] "
        
    return parameter_string




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
    