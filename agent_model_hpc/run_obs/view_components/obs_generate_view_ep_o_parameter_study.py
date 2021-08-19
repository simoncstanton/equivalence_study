#!/usr/bin/env python3
'''

    - generate episode terminal outcome distribution, episode-mean, for surface view of each outcome
        - parameterised by input parameter values - each pair is a subjob
        z_data
        

'''
import sys, os, getopt
from time import process_time_ns, time_ns
import re
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    
    view_utility().eo_ep_o_view_set_obs_data_start(obs_data)
    print(os.path.basename(__file__) + ":: obs_exp_summary: " + obs_data["journal_obs_summary_filename"])
    
    obs_data_summary = view_utility().retrieve_obs_data_summary(obs_data)
    obs_data["obs_exp"]["obs_subjob_data_path"] = hpc_config["paths"]["observations"] + [obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], hpc_config["obs"]["leaf_data"]]
    obs_data["obs_exp"]["sj_count"] = len(obs_data_summary["obs_exp"]["exp_subjobs_list"])
    
    print(os.path.basename(__file__) + ":: exp_type: " + obs_data_summary["obs_exp"]["exp_type"])
    

    obs_data["strategy"] = obs_data_summary["obs_exp"]["exp_strategy_list"].split(',', 1)[0] 
    obs_data["gameform"] = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":")[0]

    obs_data["episodes"] = obs_data_summary["obs_exp"]["exp_episodes"] 
    obs_data["timesteps"] = obs_data_summary["obs_exp"]["exp_timesteps"]
    obs_data["reward_type"] = obs_data_summary["obs_exp"]["exp_gameform_list"].split(":")[1] 
    obs_data["exp_type"] = obs_data_summary["obs_exp"]["exp_type"] 
    obs_data["exp_reference"] = obs_data_summary["obs_exp"]["exp_parent_id"]
        
        
    
    obs_data["path"] = os.path.join(obs_data["obs_invocation"]["basepath"], os.sep.join(hpc_config["paths"]["observations"]), obs_data_summary["obs_exp"]["exp_type"], obs_data_summary["obs_exp"]["exp_parent_id"], "view", "ep_o")
    
    
    ''' 
        extract data from required files
        asemble z-data object
        
    
    '''
    
    sj_data = []
    outcome_distributions = ["cc", "cd", "dc", "dd"]
    
    in_path = os.path.join(os.sep.join(obs_data["obs_exp"]["obs_subjob_data_path"]), "ep_o")
    output_suffix = "_ep_o_table_parameter_study"
    
    x_values = []
    y_values = []
    
    # ouch. needs to be retrofitted to compiling the obs_data_summary [TODO]
    x_parameter_set = [] #['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
    y_parameter_set = [] #['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
    
    
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        s_out = []
        
        # want obs_124375_sj_0_ep_o_terminal_e_distribution_e_mean.csv for all sj
        file = "obs_" + obs_data["obs_exp"]["exp_parent_id"] + "_sj_" + str(i) + "_ep_o_terminal_e_distribution_e_mean.csv"  

        sj_data.append(view_utility().fetch_data(in_path, file, obs_data))

        
        parameter_string = obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["exp_invocation"]["parameter_string"]
        x_value, y_value = parameter_string.split(':')
        
        x_label, x_value = x_value.split('=')
        y_label, y_value = y_value.split('=')
        
        x_parameter_set.append(x_value)
        y_parameter_set.append(y_value)
        
        x_value = float(x_value)
        y_value = float(y_value)
        
        if x_value not in x_values:
            x_values.append(x_value)
        if y_value not in y_values:
            y_values.append(y_value)
        
            
        if x_label not in obs_data["hidden_parameters"]:
            obs_data["hidden_parameters"].append(x_label)
        if y_label not in obs_data["hidden_parameters"]:
            obs_data["hidden_parameters"].append(y_label)            
            
        x_values.sort()
        y_values.sort()
        
    
    x_parameter_set = list(set(x_parameter_set))
    y_parameter_set = list(set(y_parameter_set))
    x_parameter_set.sort()
    y_parameter_set.sort()
    
    z_data_cardinality = len(x_values) * len(y_values)

    z_data = {k:[[0] * len(y_values) for i in range(len(x_values))] for k in outcome_distributions}
    
    # Note it does not matter which agent we index into here, as we are looking at outceoms, not rewards.
    for i in range(0, obs_data["obs_exp"]["sj_count"]):
        x = obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["agent_parameters"]["agent_0"]["strategy_parameters"][x_label]
        y = obs_data_summary["obs_exp"]["exp_subjobs"][str(i)]["exp_summary"]["agent_parameters"]["agent_0"]["strategy_parameters"][y_label]
        
        z_data["cc"][y_values.index(y)][x_values.index(x)] = sj_data[i][0][0]
        z_data["cd"][y_values.index(y)][x_values.index(x)] = sj_data[i][1][0]
        z_data["dc"][y_values.index(y)][x_values.index(x)] = sj_data[i][2][0]
        z_data["dd"][y_values.index(y)][x_values.index(x)] = sj_data[i][3][0]
        # z_data["cc"][x_values.index(x)][y_values.index(y)] = sj_data[i][0][0]
        # z_data["cd"][x_values.index(x)][y_values.index(y)] = sj_data[i][1][0]
        # z_data["dc"][x_values.index(x)][y_values.index(y)] = sj_data[i][2][0]
        # z_data["dd"][x_values.index(x)][y_values.index(y)] = sj_data[i][3][0]    
    
    #print(z_data["cc"])
    
    '''
        create dataframe of four series indexed by combined label
        
    '''
    cc_data_series = {}
    labels = []
    parameter_pair = x_label + " " + y_label
    print(parameter_pair)
    
    for i, z in enumerate(x_parameter_set):
        for j, w in enumerate(y_parameter_set):
            label = str(z + "x" + w)
            labels.append(label)
            cc_data_series[label] = z_data["cc"][j][i]
    
    cc_df_series = pd.DataFrame(cc_data_series.items(), columns=[parameter_pair, 'CC'], index=labels)

    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_cc_series.csv"
    cc_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    # Sorted
    cc_df_series.sort_values(by=['CC'], inplace=True, ascending=False)
    #print(cc_df_series)

    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_cc_series_sorted.csv"
    cc_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)


    cd_data_series = {}
    labels = []
    for i, z in enumerate(x_parameter_set):
        for j, w in enumerate(y_parameter_set):
            label = str(z + "x" + w)
            labels.append(label)
            cd_data_series[label] = z_data["cd"][j][i]
    
    cd_df_series = pd.DataFrame(cd_data_series.items(), columns=[parameter_pair, 'CD'], index=labels)

    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_cd_series.csv"
    cd_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    # Sorted
    cd_df_series.sort_values(by=['CD'], inplace=True, ascending=False)
    #print(cd_df_series)
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_cd_series_sorted.csv"
    cd_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    
    dc_data_series = {}
    labels = []
    for i, z in enumerate(x_parameter_set):
        for j, w in enumerate(y_parameter_set):
            label = str(z + "x" + w)
            labels.append(label)
            dc_data_series[label] = z_data["dc"][j][i]
    
    dc_df_series = pd.DataFrame(dc_data_series.items(), columns=[parameter_pair, 'DC'], index=labels)

    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_dc_series.csv"
    dc_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    # Sorted
    dc_df_series.sort_values(by=['DC'], inplace=True, ascending=False)
    #print(dc_df_series)
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_dc_series_sorted.csv"
    dc_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    
    dd_data_series = {}
    labels = []
    for i, z in enumerate(x_parameter_set):
        for j, w in enumerate(y_parameter_set):
            label = str(z + "x" + w)
            labels.append(label)
            dd_data_series[label] = z_data["dd"][j][i]
    
    dd_df_series = pd.DataFrame(dd_data_series.items(), columns=[parameter_pair, 'DD'], index=labels)

    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_dd_series.csv"
    dd_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    # Sorted
    dd_df_series.sort_values(by=['DD'], inplace=True, ascending=False)
    #print(dd_df_series)

    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_dd_series_sorted.csv"
    dd_df_series.to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    
    
    
    
    
    
    
    
    
    
    ''' 
        save z_data to output location as four dataframes
    
    '''

    df_outcomes = {}
    # df_outcomes["cc"] = pd.DataFrame(z_data["cc"], columns=y_values, index=x_values)
    # df_outcomes["cd"] = pd.DataFrame(z_data["cd"], columns=y_values, index=x_values)
    # df_outcomes["dc"] = pd.DataFrame(z_data["dc"], columns=y_values, index=x_values)
    # df_outcomes["dd"] = pd.DataFrame(z_data["dd"], columns=y_values, index=x_values)
    df_outcomes["cc"] = pd.DataFrame(z_data["cc"], columns=x_values, index=y_values)
    df_outcomes["cd"] = pd.DataFrame(z_data["cd"], columns=x_values, index=y_values)
    df_outcomes["dc"] = pd.DataFrame(z_data["dc"], columns=x_values, index=y_values)
    df_outcomes["dd"] = pd.DataFrame(z_data["dd"], columns=x_values, index=y_values)

    for s in outcome_distributions:
        
        file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_" + s + ".csv"
        df_outcomes[s].to_csv(os.path.join(obs_data["path"], file), encoding='utf-8', index=True)
    


    ''' 
        build four plotly surface graphs
    
    '''
    write_parameter_study_outcome_distribution_graph(obs_data, obs_data_summary, x_label, y_label, z_data, x_values, y_values, outcome_distributions)


    ''' 
        build plotly facet surface graph

    '''
    write_facet_graph_surface_map(obs_data, obs_data_summary, z_data, x_values, y_values, x_label, y_label)



    '''
        write tables sorted by x,y parameter pair outcome frequency descending
        
    '''

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(cc_df_series.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[cc_df_series[parameter_pair], cc_df_series.CC],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "cc", facet=False, view_title="Parameter Pair by Descending Outcome Frequency "))
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_cc_series_table.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")

    '''
        write title text, while we have it
        
    '''
    title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "cc", facet=False, view_title="Parameter Pair by Descending Outcome Frequency ")
    file = "title_text_cc_series_table.html"
    with open(os.path.join(obs_data["path"], file), "w") as f:
        f.write(str(title_text['text']))


    fig = go.Figure(data=[go.Table(
        header=dict(values=list(cd_df_series.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[cd_df_series[parameter_pair], cd_df_series.CD],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "cd", facet=False, view_title="Parameter Pair by Descending Outcome Frequency "))
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_cd_series_table.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")

    '''
        write title text, while we have it
        
    '''
    title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "cd", facet=False, view_title="Parameter Pair by Descending Outcome Frequency ")
    file = "title_text_cd_series_table.html"
    with open(os.path.join(obs_data["path"], file), "w") as f:
        f.write(str(title_text['text']))


    fig = go.Figure(data=[go.Table(
        header=dict(values=list(dc_df_series.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[dc_df_series[parameter_pair], dc_df_series.DC],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "dc", facet=False, view_title="Parameter Pair by Descending Outcome Frequency "))
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_dc_series_table.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")

    '''
        write title text, while we have it
        
    '''
    title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "dc", facet=False, view_title="Parameter Pair by Descending Outcome Frequency ")
    file = "title_text_dc_series_table.html"
    with open(os.path.join(obs_data["path"], file), "w") as f:
        f.write(str(title_text['text']))
        
        
        

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(dd_df_series.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[dd_df_series[parameter_pair], dd_df_series.DD],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "dd", facet=False, view_title="Parameter Pair by Descending Outcome Frequency "))
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_dd_series_table.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")

    '''
        write title text, while we have it
        
    '''
    title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "dd", facet=False, view_title="Parameter Pair by Descending Outcome Frequency ")
    file = "title_text_dd_series_table.html"
    with open(os.path.join(obs_data["path"], file), "w") as f:
        f.write(str(title_text['text']))
        
        
        

    '''
        write table of top ten x,y parameter pairs by outcome frequency descending for all outcomes as facets
        parameter_pair, value
        
        
    '''
    cc_df_series_10 = cc_df_series[:10]
    cd_df_series_10 = cd_df_series[:10]
    dc_df_series_10 = dc_df_series[:10]
    dd_df_series_10 = dd_df_series[:10]
    
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'table'}, {'type': 'table'}], [{'type': 'table'}, {'type': 'table'}]],
        
    )

    fig.add_trace(go.Table(
        header=dict(values=list(cc_df_series_10.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[cc_df_series_10[parameter_pair], cc_df_series_10.CC],
                   fill_color='lavender',
                   align='left'),
        ), row=1, col=1
    )
    fig.add_trace(go.Table(
        header=dict(values=list(cd_df_series_10.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[cd_df_series_10[parameter_pair], cd_df_series_10.CD],
                   fill_color='lavender',
                   align='left'),
        ), row=1, col=2
    )
    fig.add_trace(go.Table(
        header=dict(values=list(dc_df_series_10.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[dc_df_series_10[parameter_pair], dc_df_series_10.DC],
                   fill_color='lavender',
                   align='left'),
        ), row=2, col=1
        
    )
    fig.add_trace(go.Table(
        header=dict(values=list(dd_df_series_10.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[dd_df_series_10[parameter_pair], dd_df_series_10.DD],
                   fill_color='lavender',
                   align='left'),
        ), row=2, col=2
        
    )
    
    fig.update_layout(title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "", facet=True, view_title="Top 10 parameter pairs"))
    
    file = "view_" + obs_data_summary["obs_exp"]["exp_parent_id"] + output_suffix + "_all_outcomes_series_table_10.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")
    
    '''
        write title text, while we have it
        
    '''
    title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "", facet=True, view_title="Top 10 parameter pairs")
    file = "title_text_" + "all_outcomes_series_table_10.html"
    with open(os.path.join(obs_data["path"], file), "w") as f:
        f.write(str(title_text['text']))
    
    


    '''
        reshape data for boxplot, write
    '''    
    import csv

    y_data = []
    data = { "cc" : [], "cd" : [], "dc" : [], "dd" : []}
    for k in df_outcomes:
        for s_d in z_data[k]:
            for x in s_d:
                data[k].append(float(x))
        y_data.append(data[k])

    file = "data_boxplot_all_outcome_distributions.csv"
    with open(os.path.join(obs_data["path"], file), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(y_data)
   
    '''
        boxplot plotly each outcome
    ''' 
    x_data = ['cc', 'cd', 'dc', 'dd']
    write_boxplot_plotly(obs_data, obs_data_summary, x_data, y_data)


    
    
    
    '''
        boxplot matplotlib
    '''
    #write_boxplot_matplotlib()

    
    '''
        write heatmap for each outcome
        
    '''

    write_heatmap_seaborn(obs_data, obs_data_summary, z_data, "cc", x_values, y_values, x_label, y_label)
    write_heatmap_seaborn(obs_data, obs_data_summary, z_data, "cd", x_values, y_values, x_label, y_label)
    write_heatmap_seaborn(obs_data, obs_data_summary, z_data, "dc", x_values, y_values, x_label, y_label)
    write_heatmap_seaborn(obs_data, obs_data_summary, z_data, "dd", x_values, y_values, x_label, y_label)
    

    
    
    
    
    
    
    
    
    view_utility().eo_ep_o_view_set_obs_data_end(obs_data, obs_data_summary)
    view_utility().eo_ep_o_view_write_obs_data_summary(obs_data, obs_data_summary)
    view_utility().eo_ep_o_view_write_obs_journal(obs_data, obs_data_summary)



def write_heatmap_seaborn(obs_data, obs_data_summary, z_data, outcome, x_values, y_values, x_label, y_label):
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    sns.set_theme()
    cmap = "Blues_r"
    
    x_axis_labels=x_values
    y_axis_labels=y_values
    
    # [TODO] rewrite range(__VALUE__) to input not fixed
    hm_data = [[0 for i in range(10)] for j in range(10)]
    for i, r in enumerate(z_data[outcome]):
        for j, rc in enumerate(r):
            hm_data[i][j] = float(rc)

    ax = sns.heatmap(hm_data, cmap=cmap, linewidth=0.1, linecolor='w', square=True, xticklabels=x_axis_labels, yticklabels=y_axis_labels, vmin=0, vmax=1)
    ax.set_title(heatmap_graph_title(obs_data, obs_data_summary, outcome_label = outcome.upper(), facet=False, view_title="Frequency Heatmap"))
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    file = "parameter_study_" + "heatmap_" + outcome + ".png"
    plt.savefig(os.path.join(obs_data["path"], file))
    plt.clf()



def heatmap_graph_title(obs_data, obs_data_summary, outcome_label, facet, view_title):
    if facet:
        outcome_label = "All Outcomes (CC, CD, DC, DD)."
    else:
        outcome_label = outcome_label.upper()
    agent_strategy_parameters = get_agent_strategy_parameters(obs_data_summary, obs_data)
    
    strategy_display_names = utility().strategy_display_names()
    gf_display_name = utility().retrieve_matrix_displayname(obs_data["gameform"])

    episode_tag = str(obs_data["episodes"]) + " episodes of " + str(obs_data["timesteps"]) + " timesteps)"

    return obs_data["exp_type"] + ": " + strategy_display_names[obs_data["strategy"]] + " " + outcome_label + " [Exp_ID: " + obs_data["exp_reference"] + "]"
    
    #+ view_title + " (episode-mean; " + episode_tag + "[Exp_ID: " + obs_data["exp_reference"] + "] [Gameform: " + gf_display_name + ", " + obs_data["reward_type"].capitalize() + agent_strategy_parameters





def write_boxplot_matplotlib():
    pass
    # import matplotlib.pyplot as plt 
    # import numpy as np
    
    # #data = [data_1, data_2, data_3, data_4] 
    # # y_data
    
    # fig = plt.figure(figsize =(10, 7)) 
    # ax = fig.add_subplot(111) 

    # ax = fig.add_axes([0, 0, 1, 1]) 

    # bp = ax.boxplot(y_data)       


    # ax.set_xticklabels(x_data) 

    # plt.title("Customized box plot") 

    # ax.get_xaxis().tick_bottom() 
    # ax.get_yaxis().tick_left() 

    # # show plot 
    # plt.show()



def write_boxplot_plotly(obs_data, obs_data_summary, x_data, y_data):

    fig = go.Figure()
    
    colors = ['rgba(93, 164, 214, 0.5)', 'rgba(255, 144, 14, 0.5)', 'rgba(44, 160, 101, 0.5)', 'rgba(255, 65, 54, 0.5)']
    for xd, yd, cls in zip(x_data, y_data, colors):
        fig.add_trace(go.Box(
            y=yd,
            name=xd,
            boxpoints='all',
            jitter=0.5,
            whiskerwidth=0.2,
            fillcolor=cls,
            marker_size=2,
            line_width=1)
        )


    fig.update_layout(
        title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label = "", facet=True, view_title="Outcome Distribution"),
        yaxis=dict(
            autorange=False,
            showgrid=True,
            # zeroline=True,
            dtick=0.1,
            gridcolor='rgb(255, 255, 255)',
            gridwidth=1,
            # zerolinecolor='rgb(255, 255, 255)',
            # zerolinewidth=2,
            type='linear',
            range=[0, 1],
            tickmode = 'linear', 
        ),
        margin=dict(
            l=40,
            r=30,
            b=80,
            t=100,
        ),
        #paper_bgcolor='rgb(243, 243, 243)',
        #plot_bgcolor='rgb(243, 243, 243)',
        showlegend=False
    )

    file = "boxplot_all_outcome_distributions.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")
    
    
    

def write_facet_graph_surface_map(obs_data, obs_data_summary, z_data, x_values, y_values, x_label, y_label):

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'surface'}, {'type': 'surface'}], [{'type': 'surface'}, {'type': 'surface'}]],
        horizontal_spacing=-0.01, vertical_spacing=-0.01,
    )

    fig.add_trace(go.Surface(x=x_values, y=y_values, z=z_data["cc"], showscale=False, ), row=1, col=1)      # contours={"x": {"show": True, "start": 0, "end": 100, "size": 0.2, "color":"white"}} adds a  weird artifact in one plot?
    fig.add_trace(go.Surface(x=x_values, y=y_values, z=z_data["dd"], showscale=False), row=1, col=2)
    fig.add_trace(go.Surface(x=x_values, y=y_values, z=z_data["cd"], showscale=False), row=2, col=1)
    fig.add_trace(go.Surface(x=x_values, y=y_values, z=z_data["dc"], showscale=False), row=2, col=2)

    camera = dict(
        up=dict(x=0, y=0, z=0.1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.5, y=1.5, z=0.001), #x=1.4, y=1.4, z=0.1)
    )

    scenes = {}
    for outcome_label in obs_data["outcome_labels"]:
        scenes[outcome_label] = build_scenes(obs_data["outcome_labels"][outcome_label], x_label, y_label)
    
    draft_template = go.layout.Template()
    draft_template.layout.annotations = [
        dict(
            name="draft watermark",
            text="<span style='font-size:12px;'>exp_" + obs_data["obs_exp"]["exp_parent_id"] + "</span>",
            textangle=0,
            opacity=0.15,
            font=dict(color="black", size=100),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
    ]
    

    
    fig.update_layout(
        template=draft_template,
        title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label, facet=True, view_title="Outcome Distribution"),
        autosize=True,
        #width=1200,
        margin=dict(l=0, r=0, b=20, t=40, pad=0),
        scene_aspectmode='cube',
        scene2_aspectmode='cube',
        scene3_aspectmode='cube',
        scene4_aspectmode='cube',
        scene = scenes["cc"],
        scene2 = scenes["dd"], 
        scene3 = scenes["cd"],
        scene4 = scenes["dc"],
        scene_camera=camera,
        scene2_camera=camera,
        scene3_camera=camera,
        scene4_camera=camera,
    )
    fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True))
    fig.update_scenes(xaxis_autorange="reversed")
    fig.update_scenes(yaxis_autorange="reversed")

    file = "facet_all_outcomes_distribution_surface_plot_parameter_study.html"
    fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")

    '''
        write title text, while we have it
        
    '''
    title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label, facet=True, view_title="Outcome Distribution")
    file = "title_text_facet_all_outcomes_distribution_surface_plot_parameter_study.html"
    with open(os.path.join(obs_data["path"], file), "w") as f:
        f.write(str(title_text['text']))



def write_parameter_study_outcome_distribution_graph(obs_data, obs_data_summary, x_label, y_label, z_data, x_values, y_values, outcome_distributions):

    for outcome_label in outcome_distributions:
        fig = go.Figure(data=[go.Surface(z=z_data[outcome_label], x=y_values, y=x_values, showscale=False)])
        
        camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=0.001), #x=1.4, y=1.4, z=0.1)
        )
        
        draft_template = go.layout.Template()
        draft_template.layout.annotations = [
            dict(
                name="draft watermark",
                text="<span style='font-size:12px;'>exp_" + obs_data["obs_exp"]["exp_parent_id"] + "</span>",
                textangle=0,
                opacity=0.15,
                font=dict(color="black", size=100),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ]
        
        _scene = build_scenes(outcome_label, x_label, y_label)
        
        fig.update_layout(
            template=draft_template,
            title=distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label, facet=False, view_title="Outcome Distribution"),
            autosize=True,
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=0,
                pad=0
            ),
            scene_aspectmode='cube',
            scene = _scene,
            scene_camera=camera,
        )
        
        
        '''
            write title text per outcome, while we have it
            
        '''
        title_text = distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label, facet=False, view_title="Outcome Distribution")
        file = "title_text_" + outcome_label + "_outcome_distribution_surface_plot_parameter_study.html"
        with open(os.path.join(obs_data["path"], file), "w") as f:
            f.write(str(title_text['text']))
        
        
        
        fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True))
        fig.update_scenes(xaxis_autorange="reversed")
        fig.update_scenes(yaxis_autorange="reversed")


        file = outcome_label + "_outcome_distribution_surface_plot_parameter_study.html"
        fig.write_html(os.path.join(obs_data["path"], file), include_plotlyjs="cdn")
        
        
        


def build_scenes(outcome_label, x_label, y_label):
    z_label = "%"
    _dtick = 0.1
    z_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    z_ticktext = ["0    ", "10", "20", "30", "40", "50    ", "60", "70", "80", "90", "100    "]
    
    default_xy_axis = dict(
        title_font = dict(size=1, color = 'rgba(0,0,0,0)'),
        tickfont = dict(size=10, color='slategrey'),
        type='linear',
        range=[0, 1],
        tickmode = 'linear',                
        tick0 = 0,
        dtick = _dtick,
        ticks='inside',
        ticklen=5,
    )
    default_z_axis = dict(
        title_text = "%",
        title_font = dict(size=10, color = 'rgba(0,0,0,0.3)'),
        tickfont = dict(size=10, color='slategrey'),
        range=[0, 1],
        tickmode = 'array',
        tickvals=z_ticks,
        ticktext=z_ticktext,
        ticks='inside',
        ticklen=5,
    )
    default_x_annotation = dict(
        showarrow=False,
        x=0.5,
        y=0,
        z=0,
        text=x_label,
        textangle=0,
        xanchor="center",
        xshift=40,
        yshift=-35,
        font = dict(size=8, color='slategrey'),
    )
    default_y_annotation = dict(
        showarrow=False,
        x=0,
        y=0.5,
        z=0,
        text=y_label,
        textangle=0,
        xanchor="center",
        xshift=-40,
        yshift=-35,
        font = dict(size=8, color='slategrey'),
    )
    default_z_annotation = dict(
        showarrow=False,
        x=0,
        y=1,
        z=1,
        text=z_label,
        textangle=0,
        xanchor="center",
        xshift=-60,
        yshift=-100,
        font = dict(size=10, color='slategrey'),
    )
    subplot_title_annotation = dict(
        showarrow=False,
        x=0,
        y=0,
        z=0,
        text=outcome_label,
        textangle=0,
        xanchor="center",
        xshift=0,
        yshift=-34,
        font = dict(size=10, color='black'),
    )
        
    default_annotations=[
        default_x_annotation,
        default_y_annotation,
        #default_z_annotation,
        subplot_title_annotation,    
    ]
    
    scene = dict(
        xaxis = default_xy_axis, 
        yaxis = default_xy_axis,
        zaxis = default_z_axis,
        annotations=default_annotations,
    )
    
    return scene


def distribution_graph_title_dict(obs_data, obs_data_summary, outcome_label, facet, view_title):
    if facet:
        outcome_label = "All Outcomes (CC, CD, DC, DD)."
    else:
        outcome_label = outcome_label.upper()
    agent_strategy_parameters = get_agent_strategy_parameters(obs_data_summary, obs_data)
    
    strategy_display_names = utility().strategy_display_names()
    gf_display_name = utility().retrieve_matrix_displayname(obs_data["gameform"])

    episode_tag = str(obs_data["episodes"]) + " episodes of " + str(obs_data["timesteps"]) + " timesteps)"

    return {
        'text' : "<span style='font-size:12px;font-weight:bold;'>" + obs_data["exp_type"] + ": " + strategy_display_names[obs_data["strategy"]] + " </span>" \
            + "<span style='font-size:12px;'>" + outcome_label + " " + view_title + " (episode-mean; " + episode_tag + "</span> " \
            + "<br><span style='font-size:8px;'>[Exp_ID: " + obs_data["exp_reference"] + "] " \
            + "[Gameform: " + gf_display_name + ", " + obs_data["reward_type"].capitalize() + "] </span>"
            + "<br><span style='font-size:8px;'>" + agent_strategy_parameters + "</span>",
        'y':0.975,
        'x':0.055,
        'xanchor': 'left',
        'yanchor': 'top',
    }
     
    

def get_agent_strategy_parameters(obs_data_summary, obs_data):
    parameter_string = ""
    for a in obs_data_summary["obs_exp"]["exp_subjobs"]["0"]["exp_summary"]["agent_parameters"]:
        parameter_string += "[<span style='font-weight:bold;'>" + a + "</span>:"
        for k, v in obs_data_summary["obs_exp"]["exp_subjobs"]["0"]["exp_summary"]["agent_parameters"][a]["strategy_parameters"].items():
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
    