import uproot
import numpy as np

from utility_functions import time_print, text_options, log_print
from MC_dictionary import MC_dictionary
from XSec import XSecRun3 as XSec 

### README ###
# This file contains the main method to load data from root files
# The wildcarding works for the 'concatenate' function of uproot, and might not in the future.
# This file also contains methods relevant to sorting samples from files.


def load_process_from_file(process, file_directory, file_map, log_file,
                           branches, good_events, final_state_mode, 
                           data=False, testing=False, direct_input=None):
  '''
  This will make more sense if you read the documentation on uproot.concatenate first:
  https://uproot.readthedocs.io/en/latest/basic.html#reading-many-files-into-big-arrays
  Most important function! Contains the only call to uproot in this library! 
  Loads into memory files relevant to the given 'final_state_mode' by reading
  'file_map' which is a python dictionary maintained in a separate file. 
  uproot.concatenate grabs all files matching the wildcard in 'file_map[process]'
  and loads ONLY the data specified by 'branches' which pass the cut 'good_events'.
  Both 'branches' and 'good_events' are specified in other places and depend on the
  final state mode.
  library='np' loads the data in a numpy array that looks like this
   {{"branch_1" : [event1, event2, event3, ..., eventN]},
    {"branch_2" : [event1, event2, event3, ..., eventN]},
    {"branch_3" : [event1, event2, event3, ..., eventN]}, etc.
    {"branch_N" : [event1, event2, event3, ..., eventN]}}
  This coding library is built using numpy arrays as the default and will not work
  with other types of arrays (although the methods could be copied and rewritten). 
  Note: that a numpy array is generated for each loaded process, which corresponds
  to a set of files. 
  '''
  if direct_input != None:
    # way to bypass filemapping and load files from different data directories
    log_print(f"Loading {direct_input}", log_file, time=True)
    file_string = direct_input + ".root:Events"
  else:
    log_print(f"Loading {file_map[process]}", log_file, time=True)
    file_string = file_directory + "/" + file_map[process] + ".root:Events"
  if data: 
    #Here data stores a boolean value. In standard_plot.py in load process you can get this.
    # if a branch isn't available in Data, don't try to load it
    branches_not_in_data = ["Generator_weight", "NWEvents", "Tau_genPartFlav", "XSecMCweight",
                            "Weight_DY_Zpt", "Weight_DY_Zpt_LO", "Weight_DY_Zpt_NLO",
                            "TauSFweight", "MuSFweight", "ElSFweight", "ElSFweight_Trig", "BTagSFfull",
                            "PUweight", "Weight_TTbar_NNLO", "Pileup_nPU"]
    for missing_branch in branches_not_in_data:
      branches = [branch for branch in branches if branch != missing_branch]
      #Here for data it is only saving branches that are not in "branches_not_in_data"
  try:
    processed_events = uproot.concatenate([file_string], branches, cut=good_events, library="np")
  except FileNotFoundError:
    log_print(text_options["yellow"] + "FILE NOT FOUND! " + text_options["reset"], log_file, end="")
    log_print(f"continuing without loading {file_string}...", log_file)
    return None
  process_list = {}
  process_list[process] = {}
  process_list[process]["info"] = processed_events
 
  return process_list


def sort_combined_processes(combined_processes_dictionary):
  data_dictionary, background_dictionary, signal_dictionary = {}, {}, {}
  for process in combined_processes_dictionary:
    if "Data" in process:
      data_dictionary[process]       = combined_processes_dictionary[process]
    elif ("VBF_TauTau" in process) or ("ggH_TauTau" in process):
      signal_dictionary[process]     = combined_processes_dictionary[process]
    else:
      background_dictionary[process] = combined_processes_dictionary[process]
  return data_dictionary, background_dictionary, signal_dictionary


def append_to_combined_processes(process, cut_events, vars_to_plot, combined_processes):
  if process in combined_processes.keys():
    print(f" !@#$%^&*&^%$#@! ADDING DUPLICATE PROCESS DATA FOR {process} NAMED {process}_alt !@#$%^&*&^%$#@!")
    process = process+"_alt"
  if "Data" not in process:
    combined_processes[process] = {
      "PlotEvents": {}, 
      "Cuts": {},
      "Generator_weight":  cut_events["Generator_weight"],
      "Weight_TTbar_NNLO": cut_events["Weight_TTbar_NNLO"],
      "Weight_DY_Zpt_LO":     cut_events["Weight_DY_Zpt_LO"],
      "Weight_DY_Zpt_NLO":     cut_events["Weight_DY_Zpt_NLO"],
      "TauSFweight": cut_events["TauSFweight"],
      "MuSFweight":  cut_events["MuSFweight"],
      "ElSFweight":  cut_events["ElSFweight"],
      "ElSFweight_Trig": cut_events["ElSFweight_Trig"],
      "BTagSFfull":  cut_events["BTagSFfull"],
      "PUweight"  :  cut_events["PUweight"],
      "SF_weight": np.ones(cut_events["Generator_weight"].shape)
    }
    #if "DY" in process: combined_processes[process]["Weight_DY_Zpt_by_hand"] = cut_events["Weight_DY_Zpt_by_hand"]
  elif "Data" in process:
    combined_processes[process] = { 
      "PlotEvents": {},
      "Cuts": {},
      "FFweight": cut_events["FFweight"]
    }

    if ("FF_weight" in cut_events.keys()):
      combined_processes[process]["FF_weight"] = cut_events["FF_weight"]
    
  for var in vars_to_plot:
    if ("Data" in process) and ("flav" in var): continue
    combined_processes[process]["PlotEvents"][var] = cut_events[var]
    #print(cut_events)
  for cut in ["pass_cuts", "event_flavor",
              "pass_0j_cuts", "pass_1j_cuts", "pass_2j_cuts", "pass_3j_cuts",
              "pass_GTE2j_cuts"]:
    if cut in cut_events.keys():
      if ("Data" in process) and ("flav" in cut): continue
      combined_processes[process]["Cuts"][cut] = cut_events[cut]
      
  return combined_processes


def load_and_store_NWEvents(process, event_dictionary):
  '''
  Read the NWEvents value for a sample and store it in the MC_dictionary,
  overriding the hardcoded values from V11 samples. Delete the NWEvents branch after.
  '''
  #MC_dictionary[process]["NWEvents"] = event_dictionary["NWEvents"][0]
  MC_dictionary[process]["XSecMCweight"] = event_dictionary["XSecMCweight"][0]
  #if "VBF" in process: # TODO: address this hardcoding at some point
  #  print("HARDCODING VBF NWEVENTS AND XSECMCWEIGHT")
  #  MC_dictionary[process]["XSecMCweight"] = 0.002829568
  if "ggH" in process: # TODO: address this hardcoding at some point, only necessary in preEE?
    print("HARDCODING ggH NWEVENTS AND XSECMCWEIGHT")
    MC_dictionary[process]["XSecMCweight"] = 0.002781924
  #print("XSecMCweight", process, MC_dictionary[process]["XSecMCweight"]) # DEBUG
  #event_dictionary.pop("NWEvents")
  event_dictionary.pop("XSecMCweight")


def customize_DY(process, final_state_mode):
  for DYtype in ["DYGen", "DYLep", "DYJet"]:
    MC_dictionary[DYtype]["XSecMCweight"] = MC_dictionary[process]["XSecMCweight"]
  label_text = { "ditau" : r"$Z{\rightarrow}{\tau_h}{\tau_h}$",
                 "mutau" : r"$Z{\rightarrow}{tau_{\mu}}{\tau_h}$",
                 "etau"  : r"$Z{\rightarrow}{tau_e}{\tau_h}$",
                 "emu"   : r"$Z{\rightarrow}{tau_e}{tau_{\mu}}$",
                 "mutau_TnP" : r"$Z{\rightarrow}{\mu}{\tau_h}$",
                 "dimuon": r"$Z{\rightarrow}{\mu}{\mu}$"}
  MC_dictionary["DYGen"]["label"] = label_text[final_state_mode]

