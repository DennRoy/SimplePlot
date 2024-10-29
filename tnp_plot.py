# Authored by Braden Allmond, Sep 11, 2023

# libraries
import numpy as np
import sys
import matplotlib.pyplot as plt
import gc
import copy

# explicitly import used functions from user files, grouped roughly by call order and relatedness
from file_map_dictionary   import testing_file_map, full_file_map, testing_dimuon_file_map, dimuon_file_map, TnP_file_map
from file_map_dictionary   import pre2022_file_map
from file_functions        import load_process_from_file, append_to_combined_processes, sort_combined_processes

from luminosity_dictionary import luminosities_with_normtag as luminosities

from cut_and_study_functions import set_branches, set_vars_to_plot, set_good_events
from cut_and_study_functions import apply_HTT_FS_cuts_to_process, apply_AR_cut

from plotting_functions    import get_binned_data, get_binned_backgrounds, get_binned_signals
from plotting_functions    import setup_ratio_plot, setup_TnP_plot, make_ratio_plot
from plotting_functions    import spruce_up_plot, spruce_up_TnP_plot, spruce_up_legend
from plotting_functions    import plot_data, plot_MC, plot_signal, make_bins

from plotting_functions import get_midpoints

from calculate_functions   import calculate_signal_background_ratio, yields_for_CSV
from utility_functions     import time_print, make_directory, print_setup_info

def match_objects_to_trigger_bit():
  '''
  Current work in progress
  Using the final state object kinematics, check if the filter bit of a used trigger is matched
  '''
  #FS ditau - two taus, match to ditau
  #FS mutau - one tau, one muon
  # - if not cross-trig, match muon to filter
  # - if cross-trig, use cross-trig filters to match both
  match = False
  # step 1 check fired triggers
  # step 2 ensure correct trigger bit is fired
  # step 3 calculate dR and compare with 0.5
  dR_trig_offline = calculate_dR(trig_eta, trig_phi, off_eta, off_phi)

if __name__ == "__main__":
  '''
  '''

  import argparse 
  parser = argparse.ArgumentParser(description='Make a standard Data-MC agreement plot.')
  # store_true : when the argument is supplied, store it's value as true
  # for 'testing' below, the default value is false if the argument is not specified
  parser.add_argument('--testing',     dest='testing',     default=False,       action='store_true')
  parser.add_argument('--hide_plots',  dest='hide_plots',  default=False,       action='store_true')
  parser.add_argument('--hide_yields', dest='hide_yields', default=False,       action='store_true')
  parser.add_argument('--final_state', dest='final_state', default="mutau",     action='store')
  parser.add_argument('--plot_dir',    dest='plot_dir',    default="plots",     action='store')
  parser.add_argument('--lumi',        dest='lumi',        default="2022 EFG",  action='store')
  parser.add_argument('--jet_mode',    dest='jet_mode',    default="Inclusive", action='store')
  parser.add_argument('--DeepTau',     dest='DeepTau_version', default="2p5",   action='store')
  parser.add_argument('--use_DY_NLO',  dest='use_DY_NLO',  default=True,        action='store')

  args = parser.parse_args() 
  testing     = args.testing     # False by default, do full dataset unless otherwise specified
  hide_plots  = args.hide_plots  # False by default, show plots unless otherwise specified
  hide_yields = args.hide_yields # False by default, show yields unless otherwise specified
  use_DY_NLO  = args.use_DY_NLO  # True  by default, use LO DY if False
  lumi = luminosities["2022 G"] if testing else luminosities[args.lumi]
  DeepTau_version = args.DeepTau_version # default is 2p5 [possible values 2p1 and 2p5]

  # final_state_mode affects many things automatically, including good_events, datasets, plotting vars, etc.
  final_state_mode = args.final_state # default mutau [possible values ditau, mutau, etau, dimuon]
  jet_mode         = args.jet_mode # default Inclusive [possible values 0j, 1j, 2j, GTE2j]

  #lxplus_redirector = "root://cms-xrd-global.cern.ch//"
  eos_user_dir    = "/eos/user/b/ballmond/NanoTauAnalysis/analysis/HTauTau_2022_fromstep1_skimmed/" + final_state_mode
  # there's no place like home :)
  home_dir        = "/Users/ballmond/LocalDesktop/HiggsTauTau/Run3PreEEFSSplitSamples/" + final_state_mode
  # TODO : parse pre/post EE file location
  home_dir        = "/Users/ballmond/LocalDesktop/HiggsTauTau/V12_postEE_Run3FSSplitSamples/" + "mutau"
  #home_dir        = "/Volumes/IDrive/HTauTau_Data/2022postEE/" # unskimmed data (i.e. final states combined)
  using_directory = home_dir
 
  good_events  = set_good_events(final_state_mode)
  branches     = set_branches(final_state_mode, DeepTau_version)
  vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode=jet_mode)
  plot_dir = make_directory("FS_plots/"+args.plot_dir, final_state_mode+"_"+jet_mode, testing=testing)

  # show info to user
  print_setup_info(final_state_mode, lumi, jet_mode, testing, DeepTau_version,
                   using_directory, plot_dir,
                   good_events, branches, vars_to_plot)

  file_map = testing_file_map if testing else full_file_map
  file_map = TnP_file_map
  #if (use_DY_NLO == True): file_map.pop("DYInc")
  #else: file_map.pop("DYIncNLO")

  # make and apply cuts to any loaded events, store in new dictionaries for plotting
  combined_process_dictionary = {}
  for process in file_map: 

    gc.collect()
    if   final_state_mode == "ditau"  and (process=="DataMuon" or process=="DataElectron"): continue
    elif final_state_mode == "mutau"  and (process=="DataTau"  or process=="DataElectron"): continue
    elif final_state_mode == "etau"   and (process=="DataTau"  or process=="DataMuon"):     continue
    elif final_state_mode == "dimuon" and not (process=="DataMuon" or "DY" in process): continue

    if "DY" in process: branches = set_branches(final_state_mode, DeepTau_version, process="DY") # Zpt handling
    new_process_dictionary = load_process_from_file(process, using_directory, file_map,
                                              branches, good_events, final_state_mode,
                                              data=("Data" in process), testing=testing)
    if new_process_dictionary == None: continue # skip process if empty

    # special flag for Tau TRG studies
    cut_events = apply_HTT_FS_cuts_to_process(process, new_process_dictionary, 
                                              final_state_mode="mutau_TnP", jet_mode="Inclusive",
                                              DeepTau_version=DeepTau_version)
    if cut_events == None: continue

    # split based on tag/probe (convert boolean to list of indices)
    if "Data" in process:
      event_tag_arr   = cut_events["pass_tag"]
      event_probe_arr = cut_events["pass_probe"]
      pass_tag, pass_probe = [], []
      for i, event_tag, event_probe in zip(range(len(event_tag_arr)), event_tag_arr, event_probe_arr):
        if event_tag   == True: pass_tag.append(i)
        if event_probe == True: pass_probe.append(i)

      from cut_and_study_functions import apply_cut, set_protected_branches
      protected_branches = set_protected_branches(final_state_mode="none", jet_mode="Inclusive")
      data_tag_deepcopy = copy.deepcopy(cut_events)
      data_tag_deepcopy["pass_tag"] = np.array(pass_tag)
      data_tag_deepcopy = apply_cut(data_tag_deepcopy, "pass_tag", protected_branches)
      if data_tag_deepcopy == None: continue

      data_probe_deepcopy = copy.deepcopy(cut_events)
      data_probe_deepcopy["pass_probe"] = np.array(pass_probe)
      data_probe_deepcopy = apply_cut(data_probe_deepcopy, "pass_probe", protected_branches)
      if data_probe_deepcopy == None: continue

      combined_process_dictionary = append_to_combined_processes("DataTag", data_tag_deepcopy, vars_to_plot, 
                                                                 combined_process_dictionary)
      combined_process_dictionary = append_to_combined_processes("DataProbe", data_probe_deepcopy, vars_to_plot, 
                                                                 combined_process_dictionary)
 

    # TODO : extendable to jet cuts (something I've meant to do for some time)
    if "DY" in process:
      event_flavor_arr = cut_events["event_flavor"]
      pass_gen_flav, pass_lep_flav, pass_jet_flav = [], [], []
      for i, event_flavor in enumerate(event_flavor_arr):
        if event_flavor == "G":
          pass_gen_flav.append(i)
        if event_flavor == "L":
          pass_lep_flav.append(i)
        if event_flavor == "J":
          pass_jet_flav.append(i)
    
      from cut_and_study_functions import apply_cut, set_protected_branches
      protected_branches = set_protected_branches(final_state_mode="none", jet_mode="Inclusive")
      background_gen_deepcopy = copy.deepcopy(cut_events)
      background_gen_deepcopy["pass_flavor_cut"] = np.array(pass_gen_flav)
      background_gen_deepcopy = apply_cut(background_gen_deepcopy, "pass_flavor_cut", protected_branches)
      if background_gen_deepcopy == None: continue

      background_lep_deepcopy = copy.deepcopy(cut_events)
      background_lep_deepcopy["pass_flavor_cut"] = np.array(pass_lep_flav)
      background_lep_deepcopy = apply_cut(background_lep_deepcopy, "pass_flavor_cut", protected_branches)
      if background_lep_deepcopy == None: continue

      background_jet_deepcopy = copy.deepcopy(cut_events)
      background_jet_deepcopy["pass_flavor_cut"] = np.array(pass_jet_flav)
      background_jet_deepcopy = apply_cut(background_jet_deepcopy, "pass_flavor_cut", protected_branches)
      if background_jet_deepcopy == None: continue

      combined_process_dictionary = append_to_combined_processes("DYGen", background_gen_deepcopy, vars_to_plot, 
                                                                 combined_process_dictionary)
      combined_process_dictionary = append_to_combined_processes("DYLep", background_lep_deepcopy, vars_to_plot, 
                                                                 combined_process_dictionary)
      combined_process_dictionary = append_to_combined_processes("DYJet", background_jet_deepcopy, vars_to_plot, 
                                                                 combined_process_dictionary)
      
    else:
      combined_process_dictionary = append_to_combined_processes(process, cut_events, vars_to_plot, 
                                                                 combined_process_dictionary)

  # after loop, sort big dictionary into three smaller ones
  data_dictionary, background_dictionary, signal_dictionary = sort_combined_processes(combined_process_dictionary)

  time_print("Processing finished!")
  ## end processing loop, begin plotting

  data_dict_tag = {"DataTag" : data_dictionary["DataTag"]}
  data_dict_probe = {"DataProbe" : data_dictionary["DataProbe"]}

  DEBUG=False
  if DEBUG == True:
    vars_to_plot = [var for var in vars_to_plot if "flav" not in var]
  else:
  # restrict
    vars_to_plot = ["FS_mu_pt", "FS_mu_eta", "FS_mu_phi",
                    "FS_tau_pt", "FS_tau_eta", "FS_tau_phi"] # npu? 
  for var in vars_to_plot:
    time_print(f"Plotting {var}")

    xbins = make_bins(var, final_state_mode)
    ax_TnP = setup_TnP_plot()
    if DEBUG==True:
      hist_ax, hist_ratio = setup_ratio_plot() # these aren't hists at all ! They're axes!

    h_data_tag   = get_binned_data(data_dict_tag, var, xbins, lumi)
    h_data_probe = get_binned_data(data_dict_probe, var, xbins, lumi)

    # dump bin content
    print(var)
    for i in range(len(xbins)):
      if i == len(xbins)-1: continue
      else: 
        print(f"bin : {i}, xbinvalue: {xbins[i]}-{xbins[i+1]}")
        print(f"num : {h_data_probe[i]}, den: {h_data_tag[i]}, ratio: {h_data_probe[i]/h_data_tag[i]}")
        print(f"error bar = +/- {np.sqrt((1/h_data_probe[i]) + (1/h_data_tag[i]))}")

    # plot everything :)
    title_era = [key for key in luminosities.items() if key[1] == lumi][0][0]
    title = f"{title_era}, {lumi:.2f}" + r"$fb^{-1}$"
    if DEBUG==True:
      plot_data(hist_ax, xbins, h_data_tag, lumi, color="red", label="tag")
      plot_data(hist_ax, xbins, h_data_probe, lumi, color="blue", label="probe")
      make_ratio_plot(hist_ratio, xbins, h_data_probe, h_data_tag)
      spruce_up_plot(hist_ax, hist_ratio, var, title, final_state_mode, jet_mode)
      spruce_up_legend(hist_ax, final_state_mode, h_data_tag)
    else:
      make_ratio_plot(ax_TnP, xbins, h_data_probe, h_data_tag)
      spruce_up_TnP_plot(ax_TnP, var, title)

    plt.savefig(plot_dir + "/" + str(var) + ".png")

  if hide_plots: pass
  else: plt.show()


