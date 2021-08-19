#!/usr/bin/env python3
'''

    - generate timestep accumulating distribution mean all episodes graph

'''
import sys, os, getopt
from time import process_time_ns, time_ns
import re
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go

from run_obs.view_util import View_utility as view_utility


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
    
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        
        # want this
        #   basepath\results\observations\symmetric_selfplay\001\data\ts_o\obs_001_sj_0_ts_o_o_accum_sum_e_mean_distribution.csv
        path = os.path.join(os.sep.join(obs_data["obs_exp"]["obs_subjob_data_path"]), "ts_o")
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_o" + "_o_accum_sum_e_mean_distribution.csv"

        data = view_utility().fetch_data(path, file, obs_data)
        
        
        # write to
        # basepath\results\observations\exp_type\parent_id\view\ts_o\view_001_sj_0_ts_o_o_accum_sum_e_mean_distribution.html
        path = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], "view", "ts_o")
        file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ts_o_o_accum_sum_e_mean_distribution.html"

        #print(os.path.join(path, file))
        write_graph(data, obs_data_summary, i, os.path.join(path, file))
        

    view_utility().eo_ts_o_view_set_obs_data_end(obs_data, obs_data_summary)
    view_utility().eo_ts_o_view_write_obs_data_summary(obs_data, obs_data_summary)
    view_utility().eo_ts_o_view_write_obs_journal(obs_data, obs_data_summary)




     

def write_graph(data, obs_data_summary, sj_id, path):
    
    strategy = obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["exp_invocation"]["strategy"] 
    gameform = obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["exp_invocation"]["gameform"] 
    episodes = obs_data_summary["obs_exp"]["exp_episodes"]
    timesteps = obs_data_summary["obs_exp"]["exp_timesteps"]
    reward_type = obs_data_summary["obs_exp"]["exp_subjobs"][str(sj_id)]["exp_summary"]["exp_invocation"]["reward_type"]
    exp_type = obs_data_summary["obs_exp"]["exp_type"]
    
    av_sin_tag = "mean"

    
    xaxis_timestep_range = range(1, timesteps+1)
    
    data_traces = {
        'CC': pd.Series(data[0], index = xaxis_timestep_range),
        'CD': pd.Series(data[1], index = xaxis_timestep_range),
        'DC': pd.Series(data[2], index = xaxis_timestep_range),
        'DD': pd.Series(data[3], index = xaxis_timestep_range),
    }

    df = pd.DataFrame(data_traces)
    fig = go.Figure()




    # for each series, remove line if series has no data - stops wrong colour line appearing on visible filled series in plotly
    line_dict = dict(width=1, color='rgb(35, 165, 254, 0.70)')
    if all(i == 0 for i in df["CC"]):
        line_dict = dict(width=0)    
    
    fig.add_trace(go.Scatter(
        x=df["CC"].index, y=df["CC"],
        fillcolor="rgba(35, 165, 254, 0.70)",
        name="CC",
        mode='lines',
        line=line_dict,
        stackgroup='one',
        groupnorm='percent' # sets the normalization for the sum of the stackgroup
    ))

    line_dict = dict(width=1, color='rgba(255, 127, 14, 0.70)')
    if all(i == 0 for i in df["DD"]):
        line_dict = dict(width=0,)
    fig.add_trace(go.Scatter(
        x=df["DD"].index, y=df["DD"],
        fillcolor="rgba(255, 127, 14, 0.70)",
        name="DD",
        mode='lines',
        line=line_dict,
        stackgroup='one'
    ))
    
    line_dict = dict(width=1, color='rgba(196, 0, 250, 0.70)')
    if all(i == 0 for i in df["CD"]):
        line_dict = dict(width=0,)
    fig.add_trace(go.Scatter(
        x=df["CD"].index, y=df["CD"],
        fillcolor="rgba(196, 0, 250, 0.70)",
        name="CD",
        mode='lines',
        line=line_dict,
        stackgroup='one'
    ))
    
    line_dict = dict(width=1, color='rgba(255, 0, 75, 0.70)')
    if all(i == 0 for i in df["DC"]):
        line_dict = dict(width=0,)    
    fig.add_trace(go.Scatter(
        x=df["DC"].index, y=df["DC"],
        fillcolor='rgba(255, 0, 75, 0.70)',
        name="DC",
        mode='lines',
        line=line_dict,
        stackgroup='one'
    ))
    
    _tick = int(timesteps)/10
    fig.update_layout(
        title=view_utility().distribution_graph_title_dict(obs_data_summary, sj_id, gameform, strategy, episodes, reward_type, av_sin_tag, exp_type),
        xaxis_title="timestep",
        yaxis_title="outcome %",
        #legend=distribution_graph_legend_dict(),
        xaxis=dict(
            type='linear',
            range=[1, timesteps],
            tickmode = 'linear',                
            tick0 = _tick,
            dtick = _tick,
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 1)",
            gridwidth=1,
        ),
        yaxis=dict(
            type='linear',
            range=[0, 100],
            ticksuffix='%',
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 1)",
            gridwidth=1,
        ),
    )
    fig.update_yaxes(title_font=dict(size=12), tickfont=dict(size=8))
    fig.update_xaxes(title_font=dict(size=12), tickfont=dict(size=8))
    
    #path = 
    fig.write_html(path, include_plotlyjs="cdn")
    
    #fig.show()
    
    
    
    




















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
    