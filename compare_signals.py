# Authored by Braden Allmond, Sep 11, 2023
DEBUG = False

# libraries
import numpy as np
import sys
import matplotlib.pyplot as plt
import gc
import copy

# explicitly import used functions from user files, grouped roughly by call order and relatedness
# import statements for setup
from setup import setup_handler, set_good_events
from branch_functions import set_branches
from plotting_functions import set_vars_to_plot
from file_map_dictionary import set_dataset_info

# import statements for data loading and processing
from file_functions        import load_process_from_file, append_to_combined_processes, sort_combined_processes
from FF_functions        import set_JetFakes_process
from cut_and_study_functions import apply_HTT_FS_cuts_to_process
from cut_and_study_functions import apply_cut, set_protected_branches

# plotting
from plotting_functions import get_midpoints, make_eta_phi_plot
from luminosity_dictionary import luminosities_with_normtag as luminosities
from plotting_functions    import get_binned_data, get_binned_backgrounds, get_binned_signals
from plotting_functions    import setup_ratio_plot, make_ratio_plot, spruce_up_plot, spruce_up_legend
from plotting_functions    import setup_single_plot, spruce_up_single_plot, add_text
from plotting_functions    import plot_data, plot_MC, plot_signal, make_bins, make_pie_chart

from binning_dictionary import label_dictionary

from calculate_functions   import calculate_signal_background_ratio, yields_for_CSV
from utility_functions     import time_print, make_directory, print_setup_info, log_print

if __name__ == "__main__":
  # do setup
  setup = setup_handler()
  testing, final_state_mode, jet_mode, era, lumi = setup.state_info
  using_directory, plot_dir, log_file, use_NLO, file_map = setup.file_info
  hide_plots, hide_yields, DeepTau_version, do_JetFakes, semilep_mode = setup.misc_info

 
  print_setup_info(setup)

  # make and apply cuts to any loaded events, store in new dictionaries for plotting
  combined_process_dictionary = {}

  good_events  = set_good_events(final_state_mode) 
  vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode=jet_mode)

  home_dir = "/Users/ballmond/LocalDesktop/HiggsTauTau"
  process_list = ["ggH_old", "ggH_new"]
  direct_input_list = [
     # home_dir + "/V12_PFRel_postEE_Dennis_test_detector_holes/ditau/Signal/ggH_TauTau_private_HTauTau_2022postEE_step2",
      home_dir + "/V12_PFRel_preEE_notriggermatching/ditau/Signal/ggH_TauTau_HTauTau_2022preEE_step2",
      home_dir + "/V12_PFRel_preEE_nominal/ditau/Signal/ggH_TauTau_HTauTau_2022preEE_step2",
      #home_dir + "/V12_PFRel_postEE_nominal/ditau/Signal/ggH_TauTau_HTauTau_2022postEE_step2",
      #home_dir + "/V12_PFRel_postEE_notriggermatching/ditau/Signal/ggH_TauTau_HTauTau_2022postEE_step2",
  ]
  #process_list = ["VBF_old", "VBF_new"]
  #direct_input_list = [
  #    home_dir + "/V12_PFRel_postEE_nominal/ditau/Signal/VBF_TauTau_private_HTauTau_2022postEE_step2",
  #    #home_dir + "/V12_PFRel_postEE_notriggermatching/ditau/Signal/VBFHToTauTau_private_HTauTau_2022postEE_step2",
  #    #home_dir + "/V12_PFRel_postEE_notriggermatching/ditau/Signal/VBF_UD_TauTau_HTauTau_2022postEE_step2",
  #    home_dir + "/V12_PFRel_postEE_nominal/ditau/Signal/VBF_TauTau_HTauTau_2022postEE_step2",
  #]

  for process, direct_input in zip(process_list, direct_input_list):
    branches     = set_branches(final_state_mode, DeepTau_version, process)

    new_process_dictionary = load_process_from_file(process, using_directory, file_map, log_file,
                                              branches, good_events, final_state_mode,
                                              data=False, testing=testing, direct_input=direct_input)
    if new_process_dictionary == None: continue # skip process if empty
    cut_events = apply_HTT_FS_cuts_to_process(process, new_process_dictionary, log_file, final_state_mode, jet_mode,
                                              DeepTau_version=DeepTau_version)
    if cut_events == None: continue

    combined_process_dictionary = append_to_combined_processes(process, cut_events, vars_to_plot, 
                                                               combined_process_dictionary)

  # end loop, sort big dictionary into three smaller ones
  _, _, signal_dictionary = sort_combined_processes(combined_process_dictionary)

  old_signal_dict = {}
  new_signal_dict = {}
  process_org = process_list[0]
  process_alt = process_list[1]
  old_signal_dict[process_org] = signal_dictionary[process_org]
  new_signal_dict[process_alt] = signal_dictionary[process_alt]

  log_print("Processing finished!", log_file, time=True)

  vars_to_plot = [var for var in vars_to_plot if "flav" not in var]
  vars_to_plot = ["HTT_m_vis"]
  # remove mvis, replace with mvis_HTT and mvis_SF
  vars_to_plot.remove("HTT_m_vis")
  vars_to_plot.append("HTT_m_vis-KSUbinning")
  vars_to_plot.append("HTT_m_vis-SFbinning")
  text = ""
  for var in vars_to_plot:
    if DEBUG: log_print(f"Plotting {var}", log_file, time=True)

    xbins = make_bins(var, final_state_mode)
    hist_ax, hist_ratio = setup_ratio_plot()

    temp_var = var # hack to plot the same variable twice with two different binnings
    if "HTT_m_vis" in var: var = "HTT_m_vis"
    h_signals_old = get_binned_signals(final_state_mode, testing, old_signal_dict, var, xbins, lumi) 
    h_signals_new = get_binned_signals(final_state_mode, testing, new_signal_dict, var, xbins, lumi) 
    var = temp_var

    # plot everything :)
    plot_signal( hist_ax, xbins, h_signals_old,     lumi, custom=True, color="red",  label=f"{process_org}")
    plot_signal( hist_ax, xbins, h_signals_new,     lumi, custom=True, color="blue", label=f"{process_alt}")

    make_ratio_plot(hist_ratio, xbins, 
                    h_signals_old[process_org]["BinnedEvents"], "Data", np.ones(np.shape(h_signals_old)),
                    h_signals_new[process_alt]["BinnedEvents"], "Data", np.ones(np.shape(h_signals_new)))

    # reversed dictionary search for era name based on lumi 
    title_era = [key for key in luminosities.items() if key[1] == lumi][0][0]
    title = f"{title_era}, {lumi:.2f}" + r"$fb^{-1}$"
    
    spruce_up_plot(hist_ax, hist_ratio, label_dictionary[var], title, final_state_mode, jet_mode, set_x_log=False)
    spruce_up_legend(hist_ax, final_state_mode)

    plt.savefig(plot_dir + "/" + str(var) + ".png")

  print(f"Plots are in {plot_dir}")
  if hide_plots: pass
  else: plt.show()


