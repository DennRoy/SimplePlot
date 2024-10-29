# libraries
import numpy as np
import matplotlib.pyplot as plt

### README
# this file contains functions to setup plotting interfaces and draw the plots themselves

from MC_dictionary        import MC_dictionary
from binning_dictionary   import binning_dictionary, label_dictionary
from triggers_dictionary  import triggers_dictionary

from luminosity_dictionary import luminosities_with_normtag as luminosities
from calculate_functions  import yields_for_CSV, calculate_underoverflow


def make_pie_chart(data_hist, MC_dictionary, use_data=False, use_fakes=False):
      sums, labels, colors = [], [], []
      for process in MC_dictionary:
        if ( (use_fakes == False) and (process=="QCD") ): pass
        else:
          sums.append(np.sum(MC_dictionary[process]["BinnedEvents"]))
          color, label, _ = set_MC_process_info(process, luminosity=-1)
          labels.append(label)
          colors.append(color)
      # add Data - MC
      total_sum = np.sum(sums)
      disagreement = np.sum(data_hist) - total_sum
      if (disagreement > 0):
        sums.append(disagreement)
        labels.append("Data-MC")
        colors.append("Grey")
      if (use_data == True):
        sums = [np.sum(data_hist)]
        labels = ["Data"]
        colors = ["White"]
      fig, ax = plt.subplots()
      ax.pie(sums, labels=labels, colors=colors, autopct='%1.1f%%')


def make_fraction_all_events(axis, xbins, h_data, h_backgrounds):
  color_array, label_array, percent_stack_array = [], [], []
  percent_QCD = np.ones(np.shape(h_data))
  for process in h_backgrounds.keys():
    color, label, _ = set_MC_process_info(process, luminosity=-1)
    color_array.append(color)
    label_array.append(label)
    h_bkgd = h_backgrounds[process]["BinnedEvents"]
    h_diff = h_data - h_bkgd
    h_percent = h_bkgd / h_data
    percent_stack_array.append(h_percent)
    percent_QCD -= h_percent
  percent_stack_array.append(percent_QCD)
  QCD_color, QCD_label, _ = set_MC_process_info("QCD", luminosity=-1)
  color_array.append(QCD_color)
  label_array.append(QCD_label)
  axis.stackplot(xbins[0:-1], percent_stack_array, step="post", edgecolor="black", colors=color_array, labels=label_array)


def make_fraction_fakes(axis, xbins, h_data, h_backgrounds, fake_processes=["TT", "WJ", "DYJet"]):
  color_array, label_array = [], []
  fakes_percent = []
  h_fakes_total = np.zeros(np.shape(h_data))
  h_bkgd_total = np.zeros(np.shape(h_data))
  for process in h_backgrounds.keys():
    h_bkgd = h_backgrounds[process]["BinnedEvents"]
    h_bkgd_total += h_bkgd
    if (process in fake_processes):
      color, label, _ = set_MC_process_info(process, luminosity=-1)
      color_array.append(color)
      label_array.append(label)
      h_fakes_total += h_bkgd
  h_QCD = h_data - h_bkgd_total
  h_fakes_total += h_QCD
  for process in fake_processes:
    h_bkgd = h_backgrounds[process]["BinnedEvents"]
    fakes_percent.append(h_bkgd / h_fakes_total)
  fakes_percent.append(h_QCD / h_fakes_total)
  QCD_color, QCD_label, _ = set_MC_process_info("QCD", luminosity=-1)
  QCD_label += " (Data-MC)"
  color_array.append(QCD_color)
  label_array.append(QCD_label)
  print(fake_processes, "QCD")
  print(fakes_percent)
  axis.stackplot(xbins[0:-1], fakes_percent, step="post", edgecolor="black", colors=color_array, labels=label_array)
 

def make_two_dimensional_plot(input_dictionary, final_state, x_var, y_var, 
                              add_to_title="", alt_x_bins=[], alt_y_bins=[]):
  fig, axis = plt.subplots()
  x_array = input_dictionary[x_var]
  y_array = input_dictionary[y_var]
  x_bins  = binning_dictionary[final_state][x_var] if len(alt_x_bins) == 0 else alt_x_bins
  y_bins  = binning_dictionary[final_state][y_var] if len(alt_y_bins) == 0 else alt_y_bins
  h2d, xbins, ybins = np.histogram2d(x_array, y_array, bins=(x_bins, y_bins))
  h2d = h2d.T # transpose from image coordinates to data coordinates
  cmesh = axis.pcolormesh(xbins, ybins, h2d) #pcolormesh uses data coordinates by default, imshow uses array of 1x1 squares
  axis.set_title(f"{final_state} :" + f" {add_to_title}")
  axis.set_xlabel(label_dictionary[x_var])
  axis.set_ylabel(label_dictionary[y_var])
  plt.colorbar(cmesh)


def make_eta_phi_plot(process_dictionary, process_name, final_state_mode, jet_mode, label_suffix):
  eta_phi_by_FS_dict = {"ditau"  : ["FS_t1_eta", "FS_t1_phi", "FS_t2_eta", "FS_t2_phi"],
                        "mutau"  : ["FS_mu_eta", "FS_mu_phi", "FS_tau_eta", "FS_tau_phi"],
                        "etau"   : ["FS_el_eta", "FS_el_phi", "FS_tau_eta", "FS_tau_phi"],
                        "emu"    : ["FS_el_eta", "FS_el_phi", "FS_mu_eta", "FS_mu_phi"],
                        "mutau_TnP"  : ["FS_mu_eta", "FS_mu_phi", "FS_tau_eta", "FS_tau_phi"],
                        "dimuon" : ["FS_m1_eta", "FS_m1_phi", "FS_m2_eta", "FS_m2_phi"]}
  eta_phi_by_FS = eta_phi_by_FS_dict[final_state_mode]
  make_two_dimensional_plot(process_dictionary[process_name]["PlotEvents"], final_state_mode,
                            eta_phi_by_FS[0], eta_phi_by_FS[1], add_to_title=label_suffix)
  make_two_dimensional_plot(process_dictionary[process_name]["PlotEvents"], final_state_mode,
                            eta_phi_by_FS[2], eta_phi_by_FS[3], add_to_title=label_suffix)
  if (jet_mode == "1j"):
    make_two_dimensional_plot(process_dictionary[process_name]["PlotEvents"], final_state_mode,
                             "CleanJetGT30_eta_1", "CleanJetGT30_phi_1", add_to_title=label_suffix)


def plot_data(histogram_axis, xbins, data_dictionary, luminosity, 
              color="black", label="Data", marker="o", fillstyle="full"):
  '''
  Add the data histogram to the existing histogram axis, computing errors in a simple way.
  For data, since points and error bars are used, they are shifted to the center of the bins.
  TODO: The error calculation should be followed up and separated to another function. 
  '''
  data_info = data_dictionary["Data"]["BinnedEvents"]
  stat_error = np.sqrt(data_dictionary["Data"]["BinnedErrors"])
  sum_of_data = np.sum(data_info)
  midpoints   = get_midpoints(xbins)
  bin_width  = abs(xbins[0:-1]-xbins[1:])/2 # only works for uniform bin widths
  label = f"Data [{sum_of_data:>.0f}]" if label == "Data" else label
  histogram_axis.errorbar(midpoints, data_info, xerr=bin_width, yerr=stat_error, 
                          color=color, marker=marker, fillstyle=fillstyle, label=label,
                          linestyle='none', markersize=3)
  #below plots without error bars
  #histogram_axis.plot(midpoints, data_info, color="black", marker=marker, linestyle='none', markersize=3, label=label)


def plot_MC(histogram_axis, xbins, stack_dictionary, luminosity,
            custom=False, color="default", label="MC", fill=True):
  '''
  Add background MC histograms to the existing histogram axis. The input 'stack_dictionary'
  contains a list of backgrounds (which should be pre-grouped, normally), the name of which
  determines colors and labels of the stacked output. 
  '''
  color_array, label_array, stack_array = [], [], []
  total_error = 0
  stack_top   = 0
  for MC_process in stack_dictionary:
    if custom == True:
      pass
    else:
      color, label, _ = set_MC_process_info(MC_process, luminosity)
    current_hist = stack_dictionary[MC_process]["BinnedEvents"]
    current_hist = np.append(current_hist, 0) # adding empty element to get around step="post" in stackplot
    print(MC_process," and  ",current_hist.shape)
    stack_top   += current_hist
    if "QCD" not in MC_process:
      total_error += stack_dictionary[MC_process]["BinnedErrors"]
    label += f" [{np.sum(current_hist):>.0f}]"
    color_array.append(color)
    label_array.append(label)
    stack_array.append(current_hist)

  total_error = np.append(total_error, 0) # same as nearest above comment 
  total_error = np.sqrt(total_error)
  error_up    = stack_top + total_error
  error_down  = stack_top - total_error

  histogram_axis.stackplot(xbins, stack_array, step="post", edgecolor="black", colors=color_array, labels=label_array)
  histogram_axis.fill_between(xbins, error_down, error_up, step="post", color="gray", alpha=0.15)


def plot_signal(histogram_axis, xbins, signal_dictionary, luminosity,
            custom=False, color="default", label="MC", fill=False):
  '''
  Similar to plot_MC, except signals are not stacked, and the 'stair' method
  of matplotlib DOES expect histogram data, so no adjustment to xbins is necessary.
  '''
  for signal in signal_dictionary:
    if custom == True:
      pass
    else:
      color, label, _ = set_MC_process_info(signal, luminosity, scaling=True, signal=True)
    current_hist = signal_dictionary[signal]["BinnedEvents"]
    label += f" [{np.sum(current_hist):>.0f}]"
    stairs = histogram_axis.stairs(current_hist, xbins, color=color, label=label, fill=False)


def set_MC_process_info(process, luminosity, scaling=False, signal=False):
  '''
  Obtain process-specific styling and scaling information.
  MC_dictionary is maintained in a separate file.
  '''
  if "alt" in process: process = process.replace("_alt","")
  color = MC_dictionary[process]["color"]
  label = MC_dictionary[process]["label"]
  lumi_key = [key for key in luminosities.items() if key[1] == luminosity][0][0]
  if scaling:
    scaling = MC_dictionary[process]["XSecMCweight"] * MC_dictionary[process]["plot_scaling"]
    # hacky unscaling and rescaling so that "testing" still works
    if ("C" in lumi_key) or ("D" in lumi_key):
      scaling *= 1 / luminosities["2022 CD"]
    elif ("E" in lumi_key) or ("F" in lumi_key) or ("G" in lumi_key):
      scaling *= 1 / luminosities["2022 EFG"]
    else:
      print(f"unrecognized lumi_key: {lumi_key}")
    scaling *= luminosity
    if process=="myQCD": scaling = 1
  if signal:
    label += " x" + str(MC_dictionary[process]["plot_scaling"])
  return (color, label, scaling)


def setup_ratio_plot():
  '''
  Define a standard plot format with a plotting area on top, and a ratio area below.
  The plots share the x-axis, and other functions should handle cosmetic additions/subtractions.
  '''
  gs = gridspec_kw = {'height_ratios': [4, 1], 'hspace': 0.09}
  fig, (upper_ax, lower_ax) = plt.subplots(nrows=2, sharex=True, gridspec_kw=gridspec_kw)
  return (upper_ax, lower_ax)


def setup_single_plot():
  fig, ax = plt.subplots()
  return ax


def setup_TnP_plot():
  fig, ax = plt.subplots() #subplot?
  return ax


def add_CMS_preliminary(axis):
  '''
  Add text to plot following CMS plotting guidelines
  https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines#Example_ROOT_macro_python
  '''
  CMS_text = "CMS"
  axis.text(0.01, 1.02, CMS_text, transform=axis.transAxes, fontsize=16, weight='bold')
  preliminary_text = "Preliminary"
  axis.text(0.12, 1.02, preliminary_text, transform=axis.transAxes, fontsize=16, style='italic')


def add_final_state_and_jet_mode(axis, final_state_mode, jet_mode):
  final_state_str = {
    "ditau"  : r"${\tau_h}{\tau_h}$",
    "mutau"  : r"${\tau_{\mu}}{\tau_h}$",
    "mutau_TnP"  : r"$Z{\rightarrow}{\tau_\mu}{\tau_h}$",
    "etau"   : r"${\tau_e}{\tau_h}$",
    "dimuon" : r"${\mu}{\mu}$",
    "emu"    : r"${e}{\mu}$",
  }
  jet_mode_str = {
    "Inclusive" : "≥0j",
    "0j"    : "0j",
    "1j"    : "1j",
    "GTE1j" : "≥1j",
    "GTE2j" : "≥2j",
  }
  axis.text(0.05, 0.92, 
  #axis.text(0.45, -0.045, 
            final_state_str[final_state_mode] + " : " + jet_mode_str[jet_mode], 
            transform=axis.transAxes, fontsize=10)

def add_text(axis, text_to_add, loc=[0.05, 0.85], rotation=0, ha="left", va="baseline"):
  axis.text(loc[0], loc[1], text_to_add,
            transform=axis.transAxes, fontsize=10, 
            rotation=rotation, ha=ha, va=va)


def spruce_up_single_plot(axis, variable_name, ylabel, title, final_state_mode, jet_mode, yrange=None,
                           leg_on=True, leg_loc ="upper right",):
  add_CMS_preliminary(axis)
  add_final_state_and_jet_mode(axis, final_state_mode, jet_mode)
  axis.set_title(title, loc='right', y=0.98)
  axis.set_ylabel("Events / bin")
  axis.minorticks_on()
  axis.tick_params(which="both", top=True, bottom=True, right=True, direction="in")
  axis.set_xlabel(variable_name)
  axis.set_ylabel(ylabel)
  if (yrange != None): axis.set_ylim(yrange)
  if (leg_on):
    leg = axis.legend(loc=leg_loc, frameon=True, bbox_to_anchor=[0.6, 0.4, 0.4, 0.6],
                      labelspacing=0.35, handlelength=0.8, handleheight=0.8, handletextpad=0.4)


def spruce_up_plot(histogram_axis, ratio_plot_axis, variable_name, title, final_state_mode, jet_mode,
                   set_x_log = False, set_y_log = False):
  '''
  Add title and axes labels
  Additionally:
    - hide a zero that overlaps with the upper plot.
    - add a horizontal line at y=1 to the ratio plot
  '''
  add_CMS_preliminary(histogram_axis)
  add_final_state_and_jet_mode(histogram_axis, final_state_mode, jet_mode)
  #histogram_axis.set_ylim([0, histogram_axis.get_ylim()[1]*1.2]) # scale top of graph up by 20%
  histogram_axis.set_title(title, loc='right', y=0.98)
  histogram_axis.set_ylabel("Events / bin")
  histogram_axis.minorticks_on()
  histogram_axis.tick_params(which="both", top=True, bottom=True, right=True, direction="in")
  #yticks = histogram_axis.yaxis.get_major_ticks()
  #yticks[0].label1.set_visible(false) # hides a zero that overlaps with the upper plot

  ratio_plot_axis.set_ylim([0.45, 1.55]) # 0.0, 2.0 also make sense
  ratio_plot_axis.set_xlabel(variable_name) # shared axis label
  if variable_name == "Trigger Indices":
    ratio_plot_axis.set_xlabel("") # shared axis label
    trig_labels = ["DiTau", "DiTau+Jet", "VBFRun3", "VBFRun2"]
    xpos  = 0.26
    xstep = 0.18
    ypos  = -0.35
    for i,nlabel in enumerate(trig_labels):
      add_text(ratio_plot_axis, nlabel, loc=[xpos+xstep*i, ypos], rotation=35, ha="center", va="center")
  ratio_plot_axis.set_ylabel("Obs. / Exp.")
  ratio_plot_axis.axhline(y=1, color='grey', linestyle='--')
  ratio_plot_axis.minorticks_on()
  ratio_plot_axis.tick_params(which="both", top=True, bottom=True, right=True, direction="in")
  ratio_plot_axis.yaxis.set_major_locator(plt.FixedLocator([0.6, 0.8, 1.0, 1.2, 1.4]))
  ratio_plot_axis.yaxis.set_major_formatter('{x:.1f}')
  ratio_plot_axis.yaxis.set_minor_locator(plt.MultipleLocator(0.05))

  if (set_x_log == True):
    # does not work how you think it should, need custom redefine
    #ax.set_xscale('function', functions=(1-log, inverse))
    histogram_axis.set_xscale('log')
    ratio_plot_axis.set_xscale('log')
  if (set_y_log == True):
    histogram_axis.set_yscale('log')
    ratio_plot_axis.set_yscale('log')


def spruce_up_TnP_plot(axis, variable_name, title):
  add_CMS_preliminary(axis)
  axis.set_title(title, loc='right', y=0.98)
  axis.set_ylabel("Efficiency (Probe/Tag)")
  axis.set_ylim([0.0, 1.1])
  axis.minorticks_on()
  axis.tick_params(which="both", top=True, bottom=True, right=True, direction="in")
  axis.set_xlabel(variable_name) # shared axis label
  axis.grid(True)


def spruce_up_legend(histogram_axis, final_state_mode):
  # this post has good advice about moving the legend off the plot
  # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-outside-the-plot
  # defaults are here, but using these to mimic ROOT defaults 
  # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
  leg = histogram_axis.legend(loc="upper right", frameon=True, bbox_to_anchor=[0.6, 0.4, 0.4, 0.6],
                        labelspacing=0.35, handlelength=0.8, handleheight=0.8, handletextpad=0.4)

  # some matplotlib documentation about transforming plotting coordinate systems
  # https://matplotlib.org/stable/users/explain/artists/transforms_tutorial.html
  # DEBUG
  #print(leg.get_bbox_to_anchor())
  #print(leg.get_bbox_to_anchor().transformed(histogram_axis.transAxes.inverted()))
  #print(leg.get_bbox_to_anchor().transformed(histogram_axis.transData))
  #plt.draw()
  #print(leg.get_bbox_to_anchor())
  #print("transAxes, inverted, transData, inverted")
  #print(leg.get_bbox_to_anchor().transformed(histogram_axis.transAxes))
  #print(leg.get_bbox_to_anchor().transformed(histogram_axis.transAxes.inverted()))
  #print(leg.get_bbox_to_anchor().transformed(histogram_axis.transData))
  #print(leg.get_bbox_to_anchor().transformed(histogram_axis.transData.inverted())) # this
  if final_state_mode == "dimuon":
    handles, original_labels = histogram_axis.get_legend_handles_labels()
    labels, yields = yields_for_CSV(histogram_axis)
    save_entry = [i for i,yield_ in enumerate(yields) if yield_ != 0]
    save_handles = [handles[entry] for entry in save_entry]
    save_labels  = [labels[entry] for entry in save_entry]
    histogram_axis.legend(save_handles, save_labels)
    print(f"Legend lables were previously {original_labels}")
    print("Removed samples with yield=0 from legend!")


def make_ratio_plot(ratio_axis, xbins, 
                    numerator_data, numerator_type, numerator_weight,
                    denominator_data, denominator_type, denominator_weight, no_midpoints = False, no_plot = False,
                    label=None, color="black"):
  '''
  Uses provided numerator and denominator info to make a ratio to add to given plotting axis.
  Errors are also calculated using the same matplotlib function as used in plot_data.
  '''
  ratio = numerator_data/denominator_data
  ratio[np.isnan(ratio)] = 0 # numpy idiom to set "nan" values to 0
  # TODO : technically errors from stack should be individually calculated, not one stack
  
  # the error bars on a ratio plot of a histogram A divided by a histogram B is:
  # (A/B) * √[ (errA / A)^2 + (errB / B)^2 ]
  # for data, error = √ [N] \ where A and B are simply N events in a bin
  # for MC  , error = √ [ Σ (w)^2] \ where w is "event weights" in a bin
  #if (numerator_type=="MC") and (denominator_type=="MC"):
    # ratio error = (A/B) * √ [ ( √ [Σ (w_A)^2] / A)^2 + ( √ [Σ (w_B)^2] / B)^2 ] \
  #if (numerator_type=="Data") and (denominator_type=="MC"):
    # ratio error = (A/B) * √ [ (1/A) + ( √ [Σ (w_B)^2] / B)^2 ] \
  if (numerator_type=="Data") and (denominator_type=="Data"):
    # ratio error = (A/B) * √ [ (1/A) + (1/B) ] \
    statistical_error = np.array([ ratio[i] * np.sqrt( (1/numerator_data[i]) + (1/denominator_data[i]))
                        if ((denominator_data[i] > 0) and (numerator_data[i] > 0)) else 0
                        for i,_ in enumerate(denominator_data)]) 
  statistical_error[np.isnan(statistical_error)] = 0
  if no_plot == True:
    pass
  else:
    midpoints = get_midpoints(xbins)
    bin_width  = abs(xbins[0:-1]-xbins[1:])/2
    ratio_axis.errorbar(midpoints, ratio, xerr=bin_width, yerr=statistical_error,
                      color=color, marker="o", linestyle='none', markersize=2, label=label)

  return ratio, statistical_error


def make_bins(variable_name, final_state_mode):
  '''
  Information for binning is referenced from a python dictionary in a separate file.
  '''
  try: 
    xbins = binning_dictionary[final_state_mode][variable_name]
  except KeyError:
    xbins = binning_dictionary["common"][variable_name]
  return xbins


def get_midpoints(input_bins):
  '''
  From an input array of increasing values, return the values halfway between each value.
  The input array is size N, and the output array is size N-1
  '''
  midpoints = []
  for i, ibin in enumerate(input_bins):
    if (i+1 != len(input_bins)):
      midpoints.append( ibin + (input_bins[i+1] - ibin)/2 )
  midpoints = np.array(midpoints)
  return midpoints


def adjust_scaling(final_state, process, scaling):
  '''
  Try to read a dictionary of factors to scale up processes, changing with final state.
  If it doesn't exist, don't adjust the factor (multiply by one and send it back).
  Scaling is N ignored files (only ignored during testing)
  '''
  adjustment_dictionary = {
    "mutau" : {
      "TTTo2L2Nu" : 15,
      "TTToSemiLeptonic" : 27,
    },
    "etau"  : {
      #"TTTo2L2Nu" : 1,
      #"TTToSemiLeptonic" : 1,
    },
    "dimuon" : {
      "DYInc" : 6.482345 # for "New DiMuon DY", whatever that means :)
    },
    "emu" : {
      "TTTo2L2Nu" : 68,
    },
  }
  try:
    adjustment_factor = adjustment_dictionary[final_state][process]
  except KeyError:
    adjustment_factor = 1
  return scaling * adjustment_factor


def get_binned_info(final_state, testing, process_name, process_variable, xbins, process_weights, luminosity):
  '''
  Take in a list of events and produce a histogram (values binned in a numpy array).
  'scaling' is either set to 1 for data (no scaling) or retrieved from the MC_dictionary.
  Underflows and overflows are included in the first and final bins of the output histogram by default.
  Note: 'process_variable' is a list of events
  '''
  scaling = 1 if "Data" in process_name else set_MC_process_info(process_name, luminosity, scaling=True)[2]
  if testing == True: scaling = adjust_scaling(final_state, process_name, scaling)
  weights = scaling * process_weights
  underflow, overflow, underflow_error, overflow_error = calculate_underoverflow(process_variable, xbins, weights)
  binned_values, _    = np.histogram(process_variable, xbins, weights=weights)
  binned_values[0]   += underflow
  binned_values[-1]  += overflow
  binned_weight_2, _  = np.histogram(process_variable, xbins, weights=weights*weights)
  binned_weight_2[0]  += underflow_error
  binned_weight_2[-1] += overflow_error
  return binned_values, binned_weight_2


def get_binned_process(final_state, testing, process_dictionary, variable, xbins_, lumi_):
  '''
  Standard loop to get only the plotted variable from a dictionary containing info and multiple variables.
  This is written to only get on process at a time. Other functions combine the processes when necessary.
  '''
  h_processes = {}
  for process in process_dictionary:
    process_variable = process_dictionary[process]["PlotEvents"][variable]
    if len(process_variable) == 0: continue
    if "Data" in process:
      process_weights = np.ones(np.shape(process_variable)) # weights of one for data
    elif process == "myQCD":  
      process_weights = process_dictionary[process]["FF_weight"]
    else:
      process_weights = get_MC_weights(process_dictionary, process)
    h_processes[process] = {}
    binned_values, binned_errors = get_binned_info(final_state, testing, process, process_variable, xbins_, process_weights, lumi_)
    h_processes[process]["BinnedEvents"] = binned_values
    h_processes[process]["BinnedErrors"] = binned_errors
  return h_processes


def get_binned_data(final_state, testing, data_dictionary, variable, xbins_, lumi_):
  h_data_by_dataset = get_binned_process(final_state, testing, data_dictionary, variable, xbins_, lumi_)
  h_data = {}
  h_data["Data"] = {}
  h_data["Data"]["BinnedEvents"], h_data["Data"]["BinnedErrors"] = accumulate_datasets(h_data_by_dataset)
  return h_data


def accumulate_datasets(dataset_dictionary):
  # Add datasets (Muon, Tau, EGamma, MuonEG) together
  # No use case in 2022
  # In 2023, VBFParking could be added to any relevant dataset
  accumulated_values = 0
  accumulated_errors = 0
  for dataset in dataset_dictionary:
    accumulated_values += dataset_dictionary[dataset]["BinnedEvents"]
    accumulated_errors += dataset_dictionary[dataset]["BinnedErrors"] #still squared errors
  return accumulated_values, accumulated_errors


def get_binned_backgrounds(final_state, testing, background_dictionary, variable, xbins_, lumi_):
  '''
  Treat each MC process, then group the output by family into flat dictionaries.
  Also, sum all backgrounds into h_summed_backgrounds to use in ratio plot.
  '''
  h_MC_by_process = get_binned_process(final_state, testing, background_dictionary, variable, xbins_, lumi_)

  # add together subprocesses of each MC family
  h_MC_by_family = {}
  if "myQCD" in background_dictionary.keys(): # QCD is on bottom of stack since it is first called
    h_MC_by_family["myQCD"] = {}
    h_MC_by_family["myQCD"]["BinnedEvents"] = h_MC_by_process["myQCD"]["BinnedEvents"]
    h_MC_by_family["myQCD"]["BinnedErrors"] = h_MC_by_process["myQCD"]["BinnedErrors"]
    all_MC_families  = ["TT", "ST", "WJ", "VV",  "DYInc", "DYIncNLO"] #giulia far left is bottom of stack
  else:
    all_MC_families  = ["QCD", "TT", "ST", "WJ", "VV", "DYInc", "DYIncNLO"]
  used_MC_families = []
  for family in all_MC_families:
    for process in h_MC_by_process:
      if (("WW" in process) or ("WZ" in process) or ("ZZ" in process)) and ("VV" not in used_MC_families):
        used_MC_families.append("VV")
      elif (family in process) and (family not in used_MC_families):
        used_MC_families.append(family)

  for family in used_MC_families:
    h_MC_by_family[family] = {}
    # only split here for readability
    h_MC_by_family[family]["BinnedEvents"], _ = accumulate_MC_subprocesses(family, h_MC_by_process)
    _, h_MC_by_family[family]["BinnedErrors"] = accumulate_MC_subprocesses(family, h_MC_by_process)
  return h_MC_by_family


def get_summed_backgrounds(h_backgrounds):
  '''
  Return a dictionary of summed backgrounds
  Expecting h_backgrounds to be split and binned already
  '''
  accumulated_values = 0
  accumulated_errors = 0
  for background in h_backgrounds:
    accumulated_values += h_backgrounds[background]["BinnedEvents"]
    accumulated_errors += h_backgrounds[background]["BinnedErrors"]
  h_summed_backgrounds = {}
  h_summed_backgrounds["Bkgd"] = {}
  h_summed_backgrounds["Bkgd"]["BinnedEvents"] = accumulated_values
  h_summed_backgrounds["Bkgd"]["BinnedErrors"] = accumulated_errors #still squared errors
  return h_summed_backgrounds


def get_binned_signals(final_state, testing, signal_dictionary, variable, xbins_, lumi_):
  h_signals = get_binned_process(final_state, testing, signal_dictionary, variable, xbins_, lumi_)
  return h_signals


def accumulate_MC_subprocesses(parent_process, process_dictionary):
  '''
  Add up separate MC histograms for processes belonging to the same family.
  For example, with three given inputs of the same family, the output is the final line:
    WWToLNu2Q = [0.0, 1.0, 5.5, 0.5]
    WZTo2L2Nu = [0.0, 2.0, 7.5, 0.2]
    ZZTo4L    = [0.0, 3.0, 4.5, 0.1]
    --------------------------------
    VV        = [0.0, 6.0, 17.5, 0.8]
  Inputs not belonging to the specified 'parent_process' are ignored,
  therefore, this function is called once for each parent process
  '''
  accumulated_values = 0
  accumulated_errors = 0
  for MC_process in process_dictionary:
    skip_process = False
    if (MC_process == "DYGen") or (MC_process == "DYGenNLO"):
      skip_process = True
    if (MC_process == "DYLep") or (MC_process == "DYLepNLO"):
      skip_process = True
    if (MC_process == "DYJet") or (MC_process == "DYJetNLO"):
      skip_process = True
    if get_parent_process(MC_process, skip_process=skip_process) == parent_process:
      accumulated_values += process_dictionary[MC_process]["BinnedEvents"]
      accumulated_errors += process_dictionary[MC_process]["BinnedErrors"]
  return accumulated_values, accumulated_errors


def get_parent_process(MC_process, skip_process=False):
  '''
  Given some process, return a corresponding parent_process, effectively grouping
  related processes (i.e. DYInclusive, DY1, DY2, DY3, and DY4 all belong to DY).
  TODO: simplify this code, it is currently written in a brain-dead way
  '''
  parent_process = ""
  # TODO
  # pass through for no parent process
  # this parent process is most helpful for VV, but for the rest...
  # it would be useful to have a mode where no automatic combining takes place
  #if   "JetFakes" in MC_process:  parent_process = "DYJetFakes" # DEBUG
  #elif "LepFakes" in MC_process:  parent_process = "DYLepFakes" # DEBUG
  #elif "Genuine"  in MC_process:  parent_process = "DY" # DEBUG
  if skip_process: parent_process = MC_process
  elif "DYInc"    in MC_process: parent_process = "DYInc"
  elif ("QCD" in MC_process) and (MC_process != "myQCD"): parent_process = "QCD"
  elif "WJets" in MC_process:  parent_process = "WJ"
  elif "TT"    in MC_process:  parent_process = "TT"
  elif "ST"    in MC_process:  parent_process = "ST"
  elif ("WW"   in MC_process or 
        "WZ"   in MC_process or 
        "ZZ"   in MC_process): parent_process = "VV"
  else:
    if (MC_process == "myQCD") or ("Fakes" in MC_process):
      pass
    else:
      print(f"No matching parent process for {MC_process}, continuing as individual process...")
  return parent_process


def get_MC_weights(MC_dictionary, process):
  gen     = MC_dictionary[process]["Generator_weight"]
  PU      = MC_dictionary[process]["PUweight"]
  TauSF   = MC_dictionary[process]["TauSFweight"]
  MuSF    = MC_dictionary[process]["MuSFweight"]
  ElSF    = MC_dictionary[process]["ElSFweight"]
  BTagSF  = MC_dictionary[process]["BTagSFfull"]
  DY_Zpt  = MC_dictionary[process]["Weight_DY_Zpt_LO"]
  TT_NNLO = MC_dictionary[process]["Weight_TTbar_NNLO"]
  full_weights = gen * PU * TauSF * MuSF * ElSF *\
                 BTagSF * DY_Zpt * TT_NNLO

  # use this to achieve no SF weights
  skip_SFs = False
  if skip_SFs == True:
    print("  NO SFs APPLIED!  "*100)
    return MC_dictionary[process]["Generator_weight"]
  return full_weights


final_state_vars = {
    # can't put nanoaod branches here because this dictionary is used to protect branches created internally
    "none"   : [],
    "ditau"  : ["FS_t1_pt", "FS_t1_eta", "FS_t1_phi", "FS_t1_dxy", "FS_t1_dz", "FS_t1_chg", "FS_t1_DM",
                "FS_t2_pt", "FS_t2_eta", "FS_t2_phi", "FS_t2_dxy", "FS_t2_dz", "FS_t2_chg", "FS_t2_DM",
                "FS_t1_flav", "FS_t2_flav", 
                #"FS_t1_rawPNetVSjet", "FS_t1_rawPNetVSmu", "FS_t1_rawPNetVSe",
                #"FS_t2_rawPNetVSjet", "FS_t2_rawPNetVSmu", "FS_t2_rawPNetVSe",
                "FS_t1_DeepTauVSjet", "FS_t1_DeepTauVSmu", "FS_t1_DeepTauVSe", 
                "FS_t2_DeepTauVSjet", "FS_t2_DeepTauVSmu", "FS_t2_DeepTauVSe", 
                "FS_trig_idx",
               ],

    "mutau"  : ["FS_mu_pt", "FS_mu_eta", "FS_mu_phi", "FS_mu_iso", "FS_mu_dxy", "FS_mu_dz", "FS_mu_chg",
                "FS_tau_pt", "FS_tau_eta", "FS_tau_phi", "FS_tau_dxy", "FS_tau_dz", "FS_tau_chg", "FS_tau_DM",
                "FS_mt", "FS_t1_flav", "FS_t2_flav", "FS_nbJet", "FS_acoplan",
                #"FS_tau_rawPNetVSjet", "FS_tau_rawPNetVSmu", "FS_tau_rawPNetVSe"
               ],

    "mutau_TnP"  : ["FS_mu_pt", "FS_mu_eta", "FS_mu_phi", "FS_mu_iso", "FS_mu_dxy", "FS_mu_dz", "FS_mu_chg",
                    "FS_tau_pt", "FS_tau_eta", "FS_tau_phi", "FS_tau_dxy", "FS_tau_dz", "FS_tau_chg", "FS_tau_DM",
                    "FS_mt", "FS_t1_flav", "FS_t2_flav", "FS_nbJet", "FS_acoplan", "pass_tag", "pass_probe"
                   ],

    "etau"   : ["FS_el_pt", "FS_el_eta", "FS_el_phi", "FS_el_iso", "FS_el_dxy", "FS_el_dz", "FS_el_chg",
                "FS_tau_pt", "FS_tau_eta", "FS_tau_phi", "FS_tau_dxy", "FS_tau_dz", "FS_tau_chg", "FS_tau_DM",
                "FS_mt", "FS_t1_flav", "FS_t2_flav", "FS_nbJet",
               ],

    "dimuon" : ["FS_m1_pt", "FS_m1_eta", "FS_m1_phi", "FS_m1_iso", "FS_m1_dxy", "FS_m1_dz",
                "FS_m2_pt", "FS_m2_eta", "FS_m2_phi", "FS_m2_iso", "FS_m2_dxy", "FS_m2_dz",
               ],

    "emu"    : ["FS_el_pt", "FS_el_eta", "FS_el_phi", "FS_el_iso", "FS_el_dxy", "FS_el_dz", "FS_el_chg",
                "FS_mu_pt", "FS_mu_eta", "FS_mu_phi", "FS_mu_iso", "FS_mu_dxy", "FS_mu_dz", "FS_mu_chg",
                "FS_nbJet", 
               ],
}

# TODO this is ugly and bad and i am only doing this out of desperation
# need to make a jet cut function folder, where this would be more at home...
clean_jet_vars = {
    "Inclusive" : ["nCleanJetGT30",
      #"CleanJetGT30_pt_1", "CleanJetGT30_eta_1",
      #"CleanJetGT30_pt_2", "CleanJetGT30_eta_2",
      #"CleanJetGT30_pt_3", "CleanJetGT30_eta_3",
    ],

    "0j" : ["nCleanJetGT30"],
    "1j" : ["nCleanJetGT30", "CleanJetGT30_pt_1", "CleanJetGT30_eta_1", "CleanJetGT30_phi_1"],
    "GTE1j" : ["nCleanJetGT30", 
               "CleanJetGT30_pt_1", "CleanJetGT30_eta_1", "CleanJetGT30_phi_1",
               "CleanJetGT30_pt_2", "CleanJetGT30_eta_2", "CleanJetGT30_phi_2",
               "FS_mjj", "FS_detajj",
              ],
    "GTE2j" : ["nCleanJetGT30", 
               "CleanJetGT30_pt_1", "CleanJetGT30_eta_1", "CleanJetGT30_phi_1",
               "CleanJetGT30_pt_2", "CleanJetGT30_eta_2", "CleanJetGT30_phi_2",
               "FS_mjj", "FS_detajj",
              ],
}

def set_vars_to_plot(final_state_mode, jet_mode="none"):
  '''
  Helper function to keep plotting variables organized
  Shouldn't this be in  plotting functions?
  '''
  vars_to_plot = ["HTT_m_vis", "HTT_dR", "HTT_pT_l1l2", #"FastMTT_PUPPIMET_mT", 
                  #giulia "FastMTT_mass",
                  "PuppiMET_pt", "PuppiMET_phi", "PV_npvs"]
 
#  vars_to_plot = ["HTT_m_vis", "HTT_dR", "HTT_pT_l1l2", #"FastMTT_PUPPIMET_mT", 
#                  "FastMTT_mass",
#                  "PuppiMET_pt", "PuppiMET_phi", "PV_npvs", "HTT_mT_l1l2met_using_PUPPI_MET"]
#                  #"HTT_DiJet_MassInv_fromHighestMjj", "HTT_DiJet_dEta_fromHighestMjj"] 
#                  # common to all final states # add Tau_decayMode
#
  FS_vars_to_add = final_state_vars[final_state_mode]
  for var in FS_vars_to_add:
    vars_to_plot.append(var)

  jet_vars_to_add = clean_jet_vars[jet_mode]
  #if (jet_mode=="Inclusive") or (jet_mode=="GTE2j"):
  #  jet_vars_to_add += ["HTT_DiJet_dEta_fromHighestMjj", "HTT_DiJet_MassInv_fromHighestMjj"]
  for jet_var in jet_vars_to_add:
    vars_to_plot.append(jet_var)

  return vars_to_plot


