# Authored by Braden Allmond, Sep 11, 2023

# libraries
import numpy as np
import sys
import matplotlib.pyplot as plt
import gc
import copy

# explicitly import used functions from user files, grouped roughly by call order and relatedness
from file_map_dictionary   import testing_file_map, full_file_map, testing_dimuon_file_map, dimuon_file_map
from file_map_dictionary   import pre2022_file_map, update_data_filemap
from file_functions        import load_process_from_file, append_to_combined_processes, sort_combined_processes

from luminosity_dictionary import luminosities_with_normtag as luminosities

from cut_and_study_functions import set_branches, set_vars_to_plot, set_good_events
from cut_and_study_functions import apply_HTT_FS_cuts_to_process, apply_AR_cut

from plotting_functions    import get_binned_data, get_binned_backgrounds, get_binned_signals
from plotting_functions    import setup_ratio_plot, make_ratio_plot, spruce_up_plot, spruce_up_legend
from plotting_functions    import setup_single_plot, spruce_up_single_plot
from plotting_functions    import plot_data, plot_MC, plot_signal, make_bins, make_pie_chart

from plotting_functions import get_midpoints, make_two_dimensional_plot

from binning_dictionary import label_dictionary

from calculate_functions   import calculate_signal_background_ratio, yields_for_CSV
from utility_functions     import time_print, make_directory, print_setup_info, log_print

if __name__ == "__main__":
  '''
  Just read the code, it speaks for itself.
  Kidding.

  This is the main block, which calls a bunch of other functions from other files
  and uses local variables and short algorithms to, by final state
  1) load data from files
  2) apply bespoke cuts to reject events
  3) explicitly remove large objects after use
  4) create a lovely plot

  Ideally, if one wants to use this library to make another type of plot, they
  would look at this script and use its format as a template.

  This code sometimes loads very large files, and then makes very large arrays from the data.
  Because of this, I do a bit of memory management, which is atypical of python programs.
  This handling reduces the program burden on lxplus nodes, and subsequently leads to faster results.
  Usually, calling the garbage collector manually like this reduces code efficiency, and if the program
  runs very slowly in the future the memory consumption would be the first thing to check.
  In the main loop below, gc.collect() tells python to remove unused objects and free up resources,
  and del(large_object) in related functions lets python know we no longer need an object, and its resources can be
  reacquired at the next gc.collect() call
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
  parser.add_argument('--use_NLO',  dest='use_NLO',  default=False,        action='store')

  args = parser.parse_args() 
  testing     = args.testing     # False by default, do full dataset unless otherwise specified
  hide_plots  = args.hide_plots  # False by default, show plots unless otherwise specified
  hide_yields = args.hide_yields # False by default, show yields unless otherwise specified
  use_NLO  = args.use_NLO  # False by default, use LO DY if False
  lumi = luminosities["2022 G"] if testing else luminosities[args.lumi]
  if testing: args.lumi = "2022 G"
  DeepTau_version = args.DeepTau_version # default is 2p5 [possible values 2p1 and 2p5]

  # final_state_mode affects many things automatically, including good_events, datasets, plotting vars, etc.
  final_state_mode = args.final_state # default mutau [possible values ditau, mutau, etau, dimuon]
  jet_mode         = args.jet_mode # default Inclusive [possible values 0j, 1j, 2j, GTE2j]

  #lxplus_redirector = "root://cms-xrd-global.cern.ch//"
  eos_user_dir    = "/eos/user/b/ballmond/NanoTauAnalysis/analysis/HTauTau_2022_fromstep1_skimmed/" + final_state_mode
  # there's no place like home :)
  home_dir        = "/Users/ballmond/LocalDesktop/HiggsTauTau/Run3PreEEFSSplitSamples/" + final_state_mode
  era_modifier_2022 = "preEE" if (("C" in args.lumi) or ("D" in args.lumi)) else "postEE"
  home_dir        = "/Users/ballmond/LocalDesktop/HiggsTauTau/V12_PFRel_"+era_modifier_2022+"_Run3FSSplitSamples/" + final_state_mode
  #home_dir        = "/Users/ballmond/LocalDesktop/HiggsTauTau/V12_PFRel_postEE_Dennis_test_detector_holes/" + final_state_mode
  using_directory = home_dir
 
  good_events  = set_good_events(final_state_mode)
  branches     = set_branches(final_state_mode, DeepTau_version)
  vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode=jet_mode)
  plot_dir_name = "FS_plots_testing/" if testing==True else "FS_plots/"
  plot_dir = make_directory(plot_dir_name+args.plot_dir, final_state_mode+"_"+jet_mode, testing=testing)

  log_file = open('outputfile.log', 'w')

  # show info to user
  print_setup_info(final_state_mode, lumi, jet_mode, testing, DeepTau_version,
                   using_directory, plot_dir,
                   good_events, branches, vars_to_plot, log_file)

  file_map = testing_file_map if testing else full_file_map
  if (use_NLO == True): 
    file_map.pop("DYInc")
    file_map.pop("WJetsInc")
  else: 
    file_map.pop("DYIncNLO")
    file_map.pop("WJetsIncNLO")

  # add FF weights :) # almost the same as SR, except SS and 1st tau fails iso (applied in AR_cuts)

  common_selection = "(METfilters) & (LeptonVeto==0) & (JetMapVeto_EE_30GeV) & (JetMapVeto_HotCold_30GeV)"
  AR_region_ditau  = common_selection + " & (abs(HTT_pdgId)==15*15) & (Trigger_ditau)"
  AR_region_mutau  = common_selection + " & (abs(HTT_pdgId)==13*15) & (Trigger_mutau)"
  AR_region_etau   = common_selection + " & (abs(HTT_pdgId)==11*15) & (Trigger_etau)"
  AR_region_emu    = common_selection + " & (abs(HTT_pdgId)==11*13) & (Trigger_emu)"
  AR_region_dimuon = common_selection + " & (abs(HTT_pdgId)==13*13) & (HLT_IsoMu24)"

  dataset_dictionary = {"ditau" : "DataTau", "mutau" : "DataMuon", "etau" : "DataElectron", "emu" : "DataEMu",
                        "dimuon": "DataMuon"}
  reject_dataset_dictionary = {"ditau" : ["DataMuon", "DataElectron", "DataEMu"],
                               "mutau" : ["DataTau",  "DataElectron", "DataEMu"],
                               "etau"  : ["DataMuon", "DataTau",      "DataEMu"],
                               "emu"   : ["DataMuon", "DataElectron", "DataTau"],
                               "dimuon": ["DataTau",  "DataElectron", "DataEMu"], }
  AR_region_dictionary = {"ditau" : AR_region_ditau, "mutau" : AR_region_mutau, 
                          "etau" : AR_region_etau, "emu" : AR_region_emu,
                          "dimuon" : AR_region_dimuon}
  dataset = dataset_dictionary[final_state_mode]
  reject_datasets = reject_dataset_dictionary[final_state_mode]
  AR_region = AR_region_dictionary[final_state_mode]

  update_data_filemap(args.lumi, file_map)
 

  do_QCD = True
  semilep_mode = "QCD"
  if (jet_mode != "Inclusive") and (do_QCD==True):
    log_print(f"Processing ditau AR region!", log_file, time=True)
    AR_process_dictionary = load_process_from_file(dataset, using_directory, file_map, log_file,
                                            branches, AR_region, final_state_mode,
                                            data=True, testing=testing)
    AR_events = AR_process_dictionary[dataset]["info"]
    cut_events_AR = apply_AR_cut(dataset, AR_events, final_state_mode, jet_mode, semilep_mode, DeepTau_version)
    FF_dictionary = {}
    FF_dictionary["myQCD"] = {}
    FF_dictionary["myQCD"]["PlotEvents"] = {}
    FF_dictionary["myQCD"]["FF_weight"]  = cut_events_AR["FF_weight"]
    for var in vars_to_plot:
      if ("flav" in var): continue
      FF_dictionary["myQCD"]["PlotEvents"][var] = cut_events_AR[var]

  if (jet_mode == "Inclusive") and (do_QCD == True):
    temp_FF_dictionary = {}
    for internal_jet_mode in ["0j", "1j", "GTE2j"]:
      log_print(f"Processing {final_state_mode} AR region! {internal_jet_mode}", log_file, time=True)

      # reload AR dictionary here because it is cut in the next steps
      AR_process_dictionary = load_process_from_file(dataset, using_directory, file_map, log_file,
                                            branches, AR_region, final_state_mode,
                                            data=True, testing=testing)
      AR_events = AR_process_dictionary[dataset]["info"]
      cut_events_AR = apply_AR_cut(dataset, AR_events, final_state_mode, internal_jet_mode, semilep_mode, DeepTau_version)
      temp_FF_dictionary[internal_jet_mode] = {}
      temp_FF_dictionary[internal_jet_mode]["myQCD"] = {}
      temp_FF_dictionary[internal_jet_mode]["myQCD"]["PlotEvents"] = {}
      temp_FF_dictionary[internal_jet_mode]["myQCD"]["FF_weight"]  = cut_events_AR["FF_weight"]
      for var in vars_to_plot:
        if ("flav" in var): continue
        temp_FF_dictionary[internal_jet_mode]["myQCD"]["PlotEvents"][var] = cut_events_AR[var]

    temp_dict = {}
    if (do_QCD==True):
      temp_dict["myQCD"] = {}
      temp_dict["myQCD"]["PlotEvents"] = {}
      temp_dict["myQCD"]["FF_weight"]  = np.concatenate((temp_FF_dictionary["0j"]["myQCD"]["FF_weight"], 
                                                       temp_FF_dictionary["1j"]["myQCD"]["FF_weight"],
                                                       temp_FF_dictionary["GTE2j"]["myQCD"]["FF_weight"]))
      for var in vars_to_plot:
        if ("flav" in var): continue
        temp_dict["myQCD"]["PlotEvents"][var] = np.concatenate((temp_FF_dictionary["0j"]["myQCD"]["PlotEvents"][var],
                                                              temp_FF_dictionary["1j"]["myQCD"]["PlotEvents"][var],
                                                              temp_FF_dictionary["GTE2j"]["myQCD"]["PlotEvents"][var]))

    FF_dictionary = temp_dict

  do_WJFakes = True
  #semilep_mode = "WJ"
  #if (jet_mode != "Inclusive") and (do_QCD==True):
  #  log_print(f"Processing ditau AR region!", log_file, time=True)
  #  AR_process_dictionary = load_process_from_file(dataset, using_directory, file_map, log_file,
  #                                          branches, AR_region, final_state_mode,
  #                                          data=True, testing=testing)
  #  AR_events = AR_process_dictionary[dataset]["info"]
  #  cut_events_AR = apply_AR_cut(dataset, AR_events, final_state_mode, jet_mode, semilep_mode, DeepTau_version)
  #  FF_dictionary = {}
  #  FF_dictionary["myQCD"] = {}
  #  FF_dictionary["myQCD"]["PlotEvents"] = {}
  #  FF_dictionary["myQCD"]["FF_weight"]  = cut_events_AR["FF_weight"]
  #  for var in vars_to_plot:
  #    if ("flav" in var): continue
  #    FF_dictionary["myQCD"]["PlotEvents"][var] = cut_events_AR[var]



  # make and apply cuts to any loaded events, store in new dictionaries for plotting
  combined_process_dictionary = {}
  for process in file_map: 

    gc.collect()
    if (process in reject_datasets): continue

    if ("WJ" in process) and (do_WJFakes == True): continue
    if "DY" in process: branches = set_branches(final_state_mode, DeepTau_version, process="DY") # Zpt handling
    new_process_dictionary = load_process_from_file(process, using_directory, file_map, log_file,
                                              branches, good_events, final_state_mode,
                                              data=("Data" in process), testing=testing)
    if new_process_dictionary == None: continue # skip process if empty

    cut_events = apply_HTT_FS_cuts_to_process(process, new_process_dictionary, log_file, final_state_mode, jet_mode,
                                              DeepTau_version=DeepTau_version)
    if cut_events == None: continue

    # TODO : extendable to jet cuts (something I've meant to do for some time)
    if ("DY" in process) and (final_state_mode != "dimuon"):
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

  log_print("Processing finished!", log_file, time=True)
  ## end processing loop, begin plotting

  eta_phi_plot = True
  if (eta_phi_plot == True):
    processes = [process for process in background_dictionary.keys()]
    processes.append(dataset)
    do_processes = []
    eta_phi_by_FS_dict = {"ditau"  : ["FS_t1_eta", "FS_t1_phi", "FS_t2_eta", "FS_t2_phi"],
                          "mutau"  : ["FS_mu_eta", "FS_mu_phi", "FS_tau_eta", "FS_tau_phi"],
                          "etau"   : ["FS_el_eta", "FS_el_phi", "FS_tau_eta", "FS_tau_phi"],
                          "dimuon" : ["FS_m1_eta", "FS_m1_phi", "FS_m2_eta", "FS_m2_phi"]}
    eta_phi_by_FS = eta_phi_by_FS_dict[final_state_mode]
    for process in processes:
      if ("Data" in process):
        make_two_dimensional_plot(data_dictionary[dataset]["PlotEvents"], final_state_mode,
                                 eta_phi_by_FS[0], eta_phi_by_FS[1], add_to_title="Data")
        make_two_dimensional_plot(data_dictionary[dataset]["PlotEvents"], final_state_mode,
                                 eta_phi_by_FS[2], eta_phi_by_FS[3], add_to_title="Data")
        if (jet_mode == "1j"):
          make_two_dimensional_plot(data_dictionary[dataset]["PlotEvents"], final_state_mode,
                                   "CleanJetGT30_eta_1", "CleanJetGT30_phi_1", add_to_title="Data")
      elif (process in do_processes):
        make_two_dimensional_plot(background_dictionary[process]["PlotEvents"], final_state_mode,
                                 "FS_t1_eta", "FS_t1_phi", add_to_title=process)
      else:
        print(f"skipping eta-phi plot for {process}")

  vars_to_plot = [var for var in vars_to_plot if "flav" not in var]
  vars_to_plot = ["HTT_m_vis"]
  # remove mvis, replace with mvis_HTT and mvis_SF
  vars_to_plot.remove("HTT_m_vis")
  vars_to_plot.append("HTT_m_vis-KSUbinning")
  vars_to_plot.append("HTT_m_vis-SFbinning")
  for var in vars_to_plot:
    log_print(f"Plotting {var}", log_file, time=True)

    xbins = make_bins(var, final_state_mode)
    hist_ax, hist_ratio = setup_ratio_plot()
    #hist_ax = setup_single_plot()

    temp_var = var # hack to plot the same variable twice with two different binnings
    if "HTT_m_vis" in var: var = "HTT_m_vis"
    h_data = get_binned_data(data_dictionary, var, xbins, lumi)
    if (final_state_mode != "dimuon") and (do_QCD == True):
      background_dictionary["myQCD"] = FF_dictionary["myQCD"] # manually include QCD as background
    h_backgrounds, h_summed_backgrounds = get_binned_backgrounds(background_dictionary, var, xbins, lumi, jet_mode)
    h_signals = get_binned_signals(signal_dictionary, var, xbins, lumi, jet_mode) 
    var = temp_var

    # plot everything :)
    plot_data(   hist_ax, xbins, h_data,        lumi)
    plot_MC(     hist_ax, xbins, h_backgrounds, lumi)
    plot_signal( hist_ax, xbins, h_signals,     lumi)

    make_ratio_plot(hist_ratio, xbins, 
                    h_data, "Data", np.ones(np.shape(h_data)),
                    h_summed_backgrounds, "Data", np.ones(np.shape(h_summed_backgrounds)))

    # reversed dictionary search for era name based on lumi 
    title_era = [key for key in luminosities.items() if key[1] == lumi][0][0]
    title = f"{title_era}, {lumi:.2f}" + r"$fb^{-1}$"
    
    #set_x_log = True if "PNet" in var else False
    set_x_log = False
    spruce_up_plot(hist_ax, hist_ratio, label_dictionary[var], title, final_state_mode, jet_mode, set_x_log = set_x_log)
    #spruce_up_single_plot(hist_ax, label_dictionary[var], "Events/Bin", title, final_state_mode, jet_mode)
    spruce_up_legend(hist_ax, final_state_mode, h_data)

    plt.savefig(plot_dir + "/" + str(var) + ".png")

    if (var == "HTT_m_vis-KSUbinning"): make_pie_chart(h_data, h_backgrounds)

    # calculate and print these quantities only once
    if (var == "HTT_m_vis"): 
      calculate_signal_background_ratio(h_data, h_backgrounds, h_signals)
      labels, yields = yields_for_CSV(hist_ax, desired_order=["Data", "TT", "WJ", "DY", "VV", "ST", "ggH", "VBF"])
      log_print(f"Reordered     Labels: {labels}", log_file)
      log_print(f"Corresponding Yields: {yields}", log_file)

  if hide_plots: pass
  else: plt.show()


