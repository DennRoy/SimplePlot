import numpy as np

def calculate_underoverflow(events, xbins, weights):
  '''
  Count the number of events falling outside (below and above) the specified bins. 
  For data, an array of ones is passed to the 'weights' variable.
  For MC, event weights must be passed correctly when the function is called.
  '''
  count_bin_values = [-999999., xbins[0], xbins[-1], 999999.]
  values, bins = np.histogram(events, count_bin_values, weights=weights)
  underflow_value, overflow_value = values[0], values[-1]
  return underflow_value, overflow_value

def calculate_yields(data, backgrounds, signals):
  '''
  TODO: rename function.
  Yields are calculated in plotting functions. 
  This can be used as a check, but name should be changed for clarity.
  Separately, various signal-to-background ratios are calculated here
  purely for convenience.
  '''
  yields = [np.sum(data)]
  total_background, total_signal = 0, 0
  for process in backgrounds: 
    process_yield = np.sum(backgrounds[process]["BinnedEvents"])
    yields.append(process_yield)
    total_background += process_yield
  for signal in signals:
    signal_yield = np.sum(backgrounds[process]["BinnedEvents"])
    yields.append(signal_yield)
    total_signal += signal_yield

  print("signal-to-background information")
  print(f"S/B      : {total_signal/total_background:.3f}")
  print(f"S/(S+B)  : {total_signal/(total_signal+total_background):.3f}")
  print(f"S/√(B)   : {total_signal/np.sqrt(total_background):.3f}")
  print(f"S/√(S+B) : {total_signal/np.sqrt(total_signal+total_background):.3f}")
  
  return yields


def calculate_mt(lep_pt, lep_phi, MET_pt, MET_phi):
  '''
  Calculates the experimental paricle physicist variable of "transverse mass"
  which is a measure a two-particle system's mass when known parts (neutrinos)
  are missing. 
  Notably, there is another variable called "transverse mass" which is what
  ROOT.Mt() calculates. This is not the variable we are interested in and instead
  calculate the correct transverse mass by hand. Either form below is equivalenetly valid.
  '''
  # useful also for etau, emu
  delta_phi = phi_mpi_pi(lep_phi - MET_phi)
  mt = np.sqrt(2 * lep_pt * MET_pt * (1 - np.cos(delta_phi) ) ) 
  #sum_pt_2  = (lep_pt + MET_pt)**2
  #sum_ptx_2 = (lep_pt*np.cos(lep_phi) + MET_pt*np.cos(MET_phi))**2
  #sum_pty_2 = (lep_pt*np.sin(lep_phi) + MET_pt*np.sin(MET_phi))**2
  #mt = sum_pt_2 - sum_ptx_2 - sum_pty_2 # alternate calculation, same quantity
  return mt
  

def calculate_dR(eta1, phi1, eta2, phi2): 
  '''return value of delta R cone defined by two objects'''
  delta_eta = eta1-eta2
  delta_phi = phi_mpi_pi(lep_phi - MET_phi)
  return np.sqrt(delta_eta*delta_eta + delta_phi*delta_phi)


def phi_mpi_pi(delta_phi):
  '''return phi between a range of negative pi and pi'''
  return 2 * np.pi - delta_phi if delta_phi > np.pi else 2 * np.pi + delta_phi if delta_phi < -1*np.pi else delta_phi

