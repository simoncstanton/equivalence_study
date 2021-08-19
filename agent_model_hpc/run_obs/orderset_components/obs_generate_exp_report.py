#!/usr/bin/env python3
# file: obs_generate_exp_report.py

# bit hacky, but ok for internal use. easier to read than json in text editor ...

import sys, os, getopt
from time import process_time_ns, time_ns
import re
from datetime import datetime
from fpdf import FPDF

from run_obs.obs_util import Obs_utility as obs_utility

def main(argv):

    hpc_config = obs_utility().load_hpc_config()
    
    obs_data = initialise_obs_data()
    parse_input(argv, obs_data)
    obs_utility().set_basepath(obs_data)

    obs_utility().eo_gen_e_r_set_obs_data_start(obs_data)    

    #print(obs_data)
    # first, load obs_{__PBS_PARENT_JOBID__}_summary.json
    
    data = obs_utility().read_obs_data_summary(obs_data)

    
    report_pdf = FPDF(orientation='P', unit='mm', format='A4')
    report_pdf.add_page()
    report_pdf.set_font('courier', size=6)
    
    indent = 0
    for key, value in data.items():
        
        if type(value) == dict:
            indent += 1
            report_pdf.cell(40, 3, key, ln=1)
            pdf_print_dict(report_pdf, key, value, indent)
            
        else:
            pdf_print_key_value(report_pdf, key, value, indent)
    
    
    obs_utility().write_report(obs_data, data, report_pdf)



    
    

def pdf_print_key_value(report_pdf, key, value, indent):

    for i in range(indent):
        report_pdf.cell(5, 3, '')

    multicell_width = 140 - (5*indent)
    
    report_pdf.cell(40, 3, key)    
    report_pdf.multi_cell(multicell_width, 3, str(value), ln=1)
    


def pdf_print_dict(report_pdf, key, value, indent):

    for k, v in value.items():
        if type(v) == dict:
        
            for i in range(indent):
                report_pdf.cell(5, 3, '')
            
            report_pdf.cell(40, 3, k, ln=1)
            indent += 1
            
            pdf_print_dict(report_pdf, k, v, indent)
            indent -= 1
            
        else:
        
            pdf_print_key_value(report_pdf, k, v, indent) 
    
    indent -= 1        
  

    
    
    




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
        "report_output_filename"        : "",
        "journal_obs_summary_filename"  : "",
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
            "localhost"             : False,
            "home"				    : "",
            "basepath"				: "",
        },

        
    }
    
    

if __name__ == '__main__':
    main(sys.argv[1:])  