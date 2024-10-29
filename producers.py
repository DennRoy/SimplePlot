# this is messy and bad, need to fix by more clearly separating functions and files...
from setup import set_good_events
from file_functions import load_process_from_file, customize_DY, load_and_store_NWEvents
from branch_functions import set_branches
from plotting_functions import set_vars_to_plot
from utility_functions import log_print
from file_map_dictionary import set_dataset_info
from file_functions import load_process_from_file
from cut_and_study_functions import apply_AR_cut


def set_AR_region(final_state_mode):
  common_selection = set_good_events(final_state_mode, AR_region=True)
  #AR_region_ditau  = common_selection + " & (abs(HTT_pdgId)==15*15) & (Trigger_ditau)"
  AR_region_ditau  = common_selection + " & (abs(HTT_pdgId)==15*15) & (Trigger_ditau | Trigger_ditauplusjet | Trigger_VBFditau)"
  AR_region_mutau  = common_selection + " & (abs(HTT_pdgId)==13*15) & (Trigger_mutau)"
  AR_region_etau   = common_selection + " & (abs(HTT_pdgId)==11*15) & (Trigger_etau)"
  AR_region_emu    = common_selection + " & (abs(HTT_pdgId)==11*13) & (Trigger_emu)"
  AR_region_dimuon = common_selection + " & (abs(HTT_pdgId)==13*13) & (HLT_IsoMu24)"

  AR_region_dictionary = {"ditau" : AR_region_ditau, "mutau" : AR_region_mutau, "etau" : AR_region_etau, "emu" : AR_region_emu,
                          "mutau_TnP" : AR_region_mutau, "dimuon" : AR_region_dimuon}
  AR_region = AR_region_dictionary[final_state_mode]
  return AR_region


def produce_FF_weight(setup, jet_mode, semilep_mode):
    # kinda weird, but okay
    testing, final_state_mode, _, _, _ = setup.state_info
    using_directory, _, log_file, _, file_map = setup.file_info
    _, _, DeepTau_version, _, _ = setup.misc_info

    fakesLabel = "myQCD"
    jet_mode = jet_mode.removesuffix("_testing")
    dataset, _ = set_dataset_info(final_state_mode)
    AR_region    = set_AR_region(final_state_mode) # same role as "set_good_events"
    vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode)
    branches     = set_branches(final_state_mode, DeepTau_version, process=dataset)
 
    log_print(f"Processing ditau AR region!", log_file, time=True)
    AR_process_dictionary = load_process_from_file(dataset, using_directory, file_map, log_file,
                                            branches, AR_region, final_state_mode,
                                            data=True, testing=testing)
    AR_events = AR_process_dictionary[dataset]["info"]
    cut_events_AR = apply_AR_cut(dataset, AR_events, final_state_mode, jet_mode, semilep_mode, DeepTau_version)
    FF_dictionary = {}
    FF_dictionary[fakesLabel] = {}
    FF_dictionary[fakesLabel]["PlotEvents"] = {}
    FF_dictionary[fakesLabel]["FF_weight"]  = cut_events_AR["FF_weight"]
    for var in vars_to_plot:
      if ("flav" in var): continue
      FF_dictionary[fakesLabel]["PlotEvents"][var] = cut_events_AR[var]

    return FF_dictionary

