# Authored by Braden Allmond, Sep 11, 2023

# libraries
import numpy as np
import sys
import matplotlib.pyplot as plt
import gc
import copy

# explicitly import used functions from user files, grouped roughly by call order and relatedness
from file_map_dictionary   import testing_file_map, full_file_map, testing_dimuon_file_map, dimuon_file_map
from file_map_dictionary   import pre2022_file_map
from file_functions        import load_process_from_file, append_to_combined_processes, sort_combined_processes

from luminosity_dictionary import luminosities_with_normtag as luminosities

from cut_and_study_functions import set_branches, set_vars_to_plot, set_good_events
from cut_and_study_functions import apply_HTT_FS_cuts_to_process, apply_AR_cut

from plotting_functions    import get_binned_data, get_binned_backgrounds, get_binned_signals
from plotting_functions    import setup_ratio_plot, make_ratio_plot, spruce_up_plot, spruce_up_legend
from plotting_functions    import plot_data, plot_MC, plot_signal, make_bins, setup_single_plot, spruce_up_single_plot

from plotting_functions import get_midpoints, make_pie_chart, make_fraction_all_events, make_fraction_fakes

from calculate_functions   import calculate_signal_background_ratio, yields_for_CSV
from utility_functions     import time_print, make_directory, print_setup_info, log_print

from cut_and_study_functions import append_lepton_indices, apply_cut, apply_jet_cut, add_FF_weights
from cut_and_study_functions import load_and_store_NWEvents, customize_DY, append_flavor_indices, set_protected_branches

from cut_ditau_functions import make_ditau_cut
from cut_mutau_functions import make_mutau_cut

from FF_functions import *

from binning_dictionary import label_dictionary

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
  parser.add_argument('--use_DY_NLO',  dest='use_DY_NLO',  default=False,        action='store')

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
  era_modifier_2022 = "preEE" if (("C" in args.lumi) or ("D" in args.lumi)) else "postEE"
  home_dir        = "/Users/ballmond/LocalDesktop/HiggsTauTau/V12_PFRel_"+era_modifier_2022+"_Run3FSSplitSamples/" + final_state_mode
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
  if (use_DY_NLO == True): 
    file_map.pop("DYInc")
    file_map.pop("WJetsInc")
  else: 
    file_map.pop("DYIncNLO")
    file_map.pop("WJetsIncNLO")

  common_selection = "(METfilters) & (LeptonVeto==0) & (JetMapVeto_EE_30GeV) & (JetMapVeto_HotCold_30GeV)"
  ditau_selection  = common_selection + " & (abs(HTT_pdgId)==15*15) & (Trigger_ditau)"
  mutau_selection  = common_selection + " & (abs(HTT_pdgId)==13*15) & (Trigger_mutau)"
  final_state_selection_dict = {"ditau": ditau_selection, "mutau" : mutau_selection}
  base_selection = final_state_selection_dict[final_state_mode]

  dataset_dictionary = {"ditau" : "DataTau", "mutau" : "DataMuon", "etau" : "DataElectron", "emu" : "DataEMu"}
  reject_dataset_dictionary = {"ditau" : ["DataMuon", "DataElectron", "DataEMu"],
                               "mutau" : ["DataTau",  "DataElectron", "DataEMu"],
                               "etau"  : ["DataMuon", "DataTau",      "DataEMu"],
                               "emu"   : ["DataMuon", "DataElectron", "DataTau"]}

  dataset = dataset_dictionary[final_state_mode]
  reject_datasets = reject_dataset_dictionary[final_state_mode]


  do_QCD = False
  semilep_mode = "QCD" #"QCD" or "WJ"
  #for region in ["AR", "DRsr", "DRar", "SR_aiso", "AR_aiso", "DRsr_aiso", "DRar_aiso"]:
  for region in ["DRar"]:

    vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode=jet_mode)

    # make and apply cuts to any loaded events, store in new dictionaries for plotting
    combined_process_dictionary = {}
    for process in file_map: 

      gc.collect()
      if (process in reject_datasets): continue

      new_process_dictionary = load_process_from_file(process, using_directory, file_map, log_file,
                                              branches, base_selection, final_state_mode,
                                              data=("Data" in process), testing=testing)
      event_dictionary = new_process_dictionary[process]["info"]
      if (event_dictionary == None): continue

      #protected_branches = ["FS_t1_flav", "FS_t2_flav", "pass_gen_cuts", "event_flavor"]
      #event_dictionary = append_lepton_indices(event_dictionary)
      #if ("Data" not in process):
      #  load_and_store_NWEvents(process, event_dictionary)
      #  if ("DY" in process): customize_DY(process, final_state_mode)
      #  #event_dictionary = append_flavor_indices(event_dictionary, final_state_mode, keep_fakes=True)
      #  keep_fakes = False
      #  if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and (final_state_mode=="mutau")):
      #    # when FF method is finished/improved no longer need to keep TT and WJ fakes
      #    keep_fakes = True
      #  if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and (final_state_mode=="etau")):
      #    # when FF method is finished/improved no longer need to keep TT and WJ fakes
      #    keep_fakes = True
      #  if (("DY" in process) and (final_state_mode=="ditau")):
      #    keep_fakes = True
      #  #event_dictionary = append_flavor_indices(event_dictionary, final_state_mode, keep_fakes=keep_fakes)
      #  event_dictionary = append_flavor_indices(event_dictionary, final_state_mode, keep_fakes=False)
      #  event_dictionary = apply_cut(event_dictionary, "pass_gen_cuts", protected_branches=protected_branches)
      #  if (event_dictionary==None or len(event_dictionary["run"])==0): continue
      
      protected_branches = ["None"]
      event_dictionary = append_lepton_indices(event_dictionary)
      if ("Data" not in process):
        load_and_store_NWEvents(process, event_dictionary)
        if ("DY" in process): customize_DY(process, final_state_mode)
        event_dictionary = append_flavor_indices(event_dictionary, final_state_mode, keep_fakes=True)

      event_dictionary = FF_control_flow(final_state_mode, semilep_mode, region, event_dictionary, DeepTau_version)
      event_dictionary = apply_cut(event_dictionary, "pass_"+region+"_cuts", protected_branches)

      if (event_dictionary==None or len(event_dictionary["run"])==0): continue
      event_dictionary   = apply_jet_cut(event_dictionary, jet_mode)
      if (event_dictionary==None or len(event_dictionary["run"])==0): continue


      if (final_state_mode == "ditau"):
        event_dictionary   = make_ditau_cut(event_dictionary, DeepTau_version) # no DeepTau or Charge requirements
        if (event_dictionary==None or len(event_dictionary["run"])==0): continue

      if (final_state_mode == "mutau"):
        event_dictionary   = make_mutau_cut(event_dictionary, DeepTau_version) # no DeepTau or Charge requirements
        if (event_dictionary==None or len(event_dictionary["run"])==0): continue

      protected_branches = set_protected_branches(final_state_mode=final_state_mode, jet_mode="none")
      event_dictionary   = apply_cut(event_dictionary, "pass_cuts", protected_branches)
      if (event_dictionary==None or len(event_dictionary["run"])==0): continue


      if ((final_state_mode == "mutau") or (final_state_mode == "etau")) and (semilep_mode == "WJ"):
        if ("Data" in process) and (do_QCD == True): 
          event_dictionary = add_FF_weights(event_dictionary, final_state_mode, 
                                            jet_mode, DeepTau_version, determining_FF=False,
                                                # [FF int, slope, OS SS int, slope]
                                                #bypass = [0.278, -0.000577, 1, 0])
                                                # ditau
                                                # Medium
                                                #bypass = [2.27e-01, -3.19e-06, 1, 0] #DRsr/ar iso eras EFG Inc
                                                #bypass = [2.78e-01, -5.70e-04, 1, 0] #DRsr/ar iso eras EFG 0j RedX=4.14
                                                #bypass = [2.30e-01, -4.93e-04, 1, 0] #DRsr/ar iso eras EFG 1j RedX=4.15
                                                #bypass = [2.36e-01, -9.53e-04, 1, 0] #DRsr/ar iso eras EFG 2j RedX=3.70
                                                # Tight
                                                #bypass = [1.74e-01, -4.71e-04, 1, 0] #DRsr/ar iso eras EFG Inc RedX=2.52
                                                # Medium aiso
                                                #bypass = [1.91e-01, -7.43e-06, 1, 0] #DRsr/ar aiso era G
                                                #bypass = [2.41e-01, -6.12e-04, 1, 0] #DRsr/ar aiso eras EFG
                                                # mutau
                                                #bypass = [0.0262364,-1.88738e-05, 1, 0] # old, hacky
                                                bypass = [0.0790, 0.000444, 1, 0] # DRsr/ar iso eras EFG Inc RedX=27 # 30min
                                                )



      # TODO : extendable to jet cuts (something I've meant to do for some time)
      if "DY" in process:
        event_flavor_arr = event_dictionary["event_flavor"]
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
        background_gen_deepcopy = copy.deepcopy(event_dictionary)
        background_gen_deepcopy["pass_flavor_cut"] = np.array(pass_gen_flav)
        background_gen_deepcopy = apply_cut(background_gen_deepcopy, "pass_flavor_cut", protected_branches)
        if background_gen_deepcopy == None: continue

        background_lep_deepcopy = copy.deepcopy(event_dictionary)
        background_lep_deepcopy["pass_flavor_cut"] = np.array(pass_lep_flav)
        background_lep_deepcopy = apply_cut(background_lep_deepcopy, "pass_flavor_cut", protected_branches)
        if background_lep_deepcopy == None: continue

        background_jet_deepcopy = copy.deepcopy(event_dictionary)
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
        combined_process_dictionary = append_to_combined_processes(process, event_dictionary, vars_to_plot, 
                                                                   combined_process_dictionary)

    # after loop, sort big dictionary into three smaller ones
    data_dictionary, background_dictionary, signal_dictionary = sort_combined_processes(combined_process_dictionary)

    if ((final_state_mode == "mutau") or (final_state_mode == "etau")) and (semilep_mode == "WJ"):
      QCD_dictionary = {}
      QCD_dictionary["myQCD"] = {}
      QCD_dictionary["myQCD"]["PlotEvents"] = {}
      QCD_dictionary["myQCD"]["FF_weight"]  = data_dictionary[dataset]["FF_weight"]
      for var in vars_to_plot:
        if ("flav" in var): continue
        QCD_dictionary["myQCD"]["PlotEvents"][var] = data_dictionary[dataset]["PlotEvents"][var]

      background_dictionary["myQCD"] = QCD_dictionary["myQCD"] # manually include QCD as background

    log_print("Processing finished!", log_file, time=True)
    ## end processing loop, begin plotting

    vars_to_plot = [var for var in vars_to_plot if "flav" not in var]
    # remove mvis, replace with mvis_HTT and mvis_SF
    vars_to_plot.remove("HTT_m_vis")
    vars_to_plot.append("HTT_m_vis-KSUbinning")
    if (final_state_mode == "ditau"):
      vars_to_plot = ["HTT_m_vis-KSUbinning", 
                    "FS_t1_pt", "FS_t1_eta", "FS_t1_phi",
                    "FS_t2_pt", "FS_t2_eta", "FS_t2_phi", "PuppiMET_pt"]
    if (final_state_mode == "mutau"):
      vars_to_plot = ["HTT_m_vis-KSUbinning", 
                    "FS_tau_pt", "FS_tau_eta", "FS_tau_phi",
                    "FS_mu_pt", "FS_mu_eta", "FS_mu_phi", "PuppiMET_pt", "FS_mt"]
    # and add back variables unique to the jet mode
    if (jet_mode == "1j") or (jet_mode == "GTE2j"): vars_to_plot.append("CleanJetGT30_pt_1")
    if (jet_mode == "GTE2j"): vars_to_plot.append("CleanJetGT30_pt_2")
    for var in vars_to_plot:
      log_print(f"Plotting {var}", log_file, time=True)

      xbins = make_bins(var, final_state_mode)
      hist_ax = setup_single_plot()

      temp_var = var
      if "HTT_m_vis" in var: var = "HTT_m_vis"
      h_data = get_binned_data(data_dictionary, var, xbins, lumi)
      h_backgrounds, h_summed_backgrounds = get_binned_backgrounds(background_dictionary, var, xbins, lumi, jet_mode)
      h_signals = get_binned_signals(signal_dictionary, var, xbins, lumi, jet_mode) 
      var = temp_var

      # plot everything :)
      plot_data(hist_ax, xbins, h_data, lumi)
      plot_MC(hist_ax, xbins, h_backgrounds, lumi)
      plot_signal(hist_ax, xbins, h_signals, lumi)

      # reversed dictionary search for era name based on lumi 
      title_era = [key for key in luminosities.items() if key[1] == lumi][0][0]
      title = f"{semilep_mode} {region} {title_era}, {lumi:.2f}" + r"$fb^{-1}$"
      
      spruce_up_single_plot(hist_ax, label_dictionary[var], "Events/Bin", title, final_state_mode, jet_mode)
      spruce_up_legend(hist_ax, final_state_mode, h_data)

      plt.savefig(plot_dir + "/" + str(var) + "_" + semilep_mode + "_" + region + ".png")

      if (var == "HTT_m_vis-KSUbinning"): 
        make_pie_chart(h_data, h_backgrounds)
        # fraction should be of fakes only, not including genuine background
        new_ax = setup_single_plot()
        make_fraction_all_events(new_ax, xbins, h_data, h_backgrounds)
        spruce_up_single_plot(new_ax, label_dictionary[var], "Fraction of All Events", title, final_state_mode, jet_mode)

        newer_ax = setup_single_plot()
        fake_processes = ["TT", "WJ", "DYJet"]
        make_fraction_fakes(newer_ax, xbins, h_data, h_backgrounds, fake_processes)
        spruce_up_single_plot(newer_ax, label_dictionary[var], "Fraction of All Jet Fakes", title, final_state_mode, jet_mode)

      # calculate and print these quantities only once
      if (var == "HTT_m_vis"): 
        calculate_signal_background_ratio(h_data, h_backgrounds, h_signals)
        labels, yields = yields_for_CSV(hist_ax, desired_order=["Data", "TT", "WJ", "DY", "VV", "ST", "ggH", "VBF"])
        print(f"Reordered     Labels: {labels}")
        print(f"Corresponding Yields: {yields}")

    if hide_plots: pass
    else: plt.show()
    log_print(f"Finished plots for {region} region!", log_file, time=True)


