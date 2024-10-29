import numpy as np
import math 
#import ROOT

### README
# this file contains functions to perform simple calculations and return or print the result


def calculate_underoverflow(events, xbins, weights):
  '''
  Count the number of events falling outside (below and above) the specified bins. 
  For data, an array of ones is passed to the 'weights' variable.
  For MC, event weights must be passed correctly when the function is called.
  '''
  count_bin_values = [-999999., xbins[0], xbins[-1], 999999.]
  values, _ = np.histogram(events, count_bin_values, weights=weights)
  underflow_value, overflow_value = values[0], values[-1]
  if (underflow_value > 1000) or (overflow_value > 100000):
    print(f"large under/over flow values: {underflow_value}, {overflow_value}")
  values_error, _ = np.histogram(events, count_bin_values, weights=weights*weights)
  underflow_error, overflow_error = values_error[0], values[-1]
  return underflow_value, overflow_value, underflow_error, overflow_error


def check_nEvents(combined_process_dict):
  # for checking nEvents in samples and entering SR
  for key in combined_process_dict.keys():
    nEvents = len(combined_process_dict[key]["Cuts"]["pass_cuts"])
    print(f"{key}, {nEvents}")


def calculate_signal_background_ratio(data, backgrounds, signals):
  '''
  Calculate and display signal-to-background ratios.
  '''
  yields = [np.sum(data)]
  total_background, total_signal = 0, 0
  for process in backgrounds: 
    process_yield = np.sum(backgrounds[process]["BinnedEvents"])
    yields.append(process_yield)
    total_background += process_yield
  for signal in signals:
    signal_yield = np.sum(signals[signal]["BinnedEvents"])
    if "VBF_TauTau" in signal: signal_yield = signal_yield / 500.0 # VBF scaling # TODO: handle automatically
    if "ggH_TauTau" in signal: signal_yield = signal_yield / 100.0 # ggH scaling
    yields.append(signal_yield)
    total_signal += signal_yield
  S_o_sqrt_SpB = total_signal/np.sqrt(total_signal+total_background)
  #print("signal-to-background information")
  #print(f"S/B      : {total_signal/total_background:.3f}")
  #print(f"S/(S+B)  : {total_signal/(total_signal+total_background):.3f}")
  #print(f"S/√(B)   : {total_signal/np.sqrt(total_background):.3f}")
  #print(f"S/√(S+B) : {total_signal/np.sqrt(total_signal+total_background):.3f}")
  return f"{S_o_sqrt_SpB:.3f}"


def calculate_mt(lep_pt, lep_phi, MET_pt, MET_phi):
  '''
  Calculates the experimental paricle physicist variable of "transverse mass"
  which is a measure a two-particle system's mass when known parts (neutrinos)
  are missing. 
  Notably, there is another variable called "transverse mass" which is what
  ROOT.Mt() calculates. This is not the variable we are interested in and we instead
  calculate the correct transverse mass by hand. Either form in the function below is 
  mathematically equivalenetly and valid.
  '''
  # used in mutau, etau, emu
  delta_phi = phi_mpi_pi(lep_phi - MET_phi)
  mt = np.sqrt(2 * lep_pt * MET_pt * (1 - np.cos(delta_phi) ) ) 
  '''
  alternate calculation, same quantity up to 4 decimal places
  lep_x = lep_pt*np.cos(lep_phi)
  lep_y = lep_pt*np.sin(lep_phi)
  MET_x = MET_pt*np.cos(MET_phi)
  MET_y = MET_pt*np.sin(MET_phi)
  sum_pt_2  = (lep_pt + MET_pt) * (lep_pt + MET_pt)
  sum_ptx_2 = (lep_x + MET_x) * (lep_x + MET_x)
  sum_pty_2 = (lep_y + MET_y) * (lep_y + MET_y)
  mt_2      = (sum_pt_2 - sum_ptx_2 - sum_pty_2)
  mt = 9999
  if mt_2 < 0:
    # this is floating-point calculation error, all values within 0.01 of 0
    mt = 0
    print("negative value, set mt to zero")
    print(mt_2)
  else: 
    mt = np.sqrt(mt_2) 
  #mt = np.sqrt(mt_2)
  '''
  return mt

#Calculating transverse mass in 2 object system
#Useful for emu case
def calculate_mt_emu(m1, m2, pt1, pt2, phi1, phi2):
  et1 = np.sqrt(m1**2 + pt1**2)
  et2 = np.sqrt(m2**2 + pt2**2)
  delta_phi = phi1 - phi2
  delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))
  mt_emu = np.sqrt(2 * et1 * et2 * (1 - np.cos(delta_phi)))
    
  return mt_emu


def ROOT_mt(lep_pt, lep_eta, lep_phi, lep_mass, MET_pt, MET_phi): #import ROOT to use this function
  # this is the non-collider-physics definition of "transverse mass"
  # which is what is implemented by ROOT's .Mt() method
  Lep_vec = ROOT.TLorentzVector()
  Lep_vec.SetPtEtaPhiE(lep_pt, lep_eta, lep_phi, lep_mass)
  MET_vec = ROOT.TLorentzVector(MET_pt, MET_phi)
  ROOT_mt = (Lep_vec + MET_vec).Mt()
  return ROOT_mt


def calculate_mt_pyROOT(lep_pt, lep_eta, lep_phi, lep_mass, # import ROOT to use this function
                        MET_pt, MET_phi):
  delta_phi = phi_mpi_pi(lep_phi - MET_phi)
  mt = ROOT.TMath.Sqrt(2 * lep_pt * MET_pt * (1 - ROOT.TMath.Cos(delta_phi)))
  # this is the same as calculate_mt, except here ROOT builtins are used
  '''
  Lep_vec = ROOT.TLorentzVector()
  MET_vec = ROOT.TLorentzVector()
  Lep_vec.SetPtEtaPhiM(lep_pt, lep_eta, lep_phi, lep_mass)
  MET_vec.SetPtEtaPhiM(MET_pt, 0, MET_phi, 0)
  met_x = MET_vec.Pt()*ROOT.TMath.Cos(MET_vec.Phi())
  met_y = MET_vec.Pt()*ROOT.TMath.Sin(MET_vec.Phi())
  met_pt = ROOT.TMath.Sqrt(met_x*met_x + met_y*met_y)
  sum_pt_2 = (Lep_vec.Pt() + met_pt) * (Lep_vec.Pt() + met_pt)
  sum_px_2 = (Lep_vec.Px() + met_x)  * (Lep_vec.Px() + met_x)
  sum_py_2 = (Lep_vec.Py() + met_y)  * (Lep_vec.Py() + met_y)
  mt2 = sum_pt_2 - sum_px_2 - sum_py_2
  mt = 9999
  if mt2 < 0:
    print("weird value, setting mt to 0")
    mt = 0
    print(mt2)
  else:
    mt = ROOT.TMath.Sqrt( mt2 )
  #mt = ROOT.TMath.Sqrt( mt2 )
  '''
  return mt

def calculate_acoplan(l1_phi, l2_phi):
  '''return value of acoplanarity defined by two leptons (small in elastic collisions)'''
  #A = 1 − |∆φ(l, l′)|/π
  return 1 - (abs(phi_mpi_pi(l1_phi - l2_phi))/np.pi)
  

def calculate_dR(eta1, phi1, eta2, phi2): 
  '''return value of delta R cone defined by two objects'''
  delta_eta = eta1-eta2
  delta_phi = phi_mpi_pi(lep_phi - MET_phi)
  return np.sqrt(delta_eta*delta_eta + delta_phi*delta_phi)


def phi_mpi_pi(delta_phi):
  '''return phi between a range of negative pi and pi'''
  return 2 * np.pi - delta_phi if delta_phi > np.pi else 2 * np.pi + delta_phi if delta_phi < -1*np.pi else delta_phi


def yields_for_CSV(histogram_axis, desired_order=[]):
    # uses label name, not process name...
    handles, labels = histogram_axis.get_legend_handles_labels()
    desired_order    = labels if desired_order == [] else desired_order
    reordered_labels = []
    corresponding_yields = []
    for compare_label in desired_order:
      for original_label in labels:
        if compare_label in original_label:
          reordered_labels.append(original_label)
          label_yield_start = original_label.find("[")
          label_yield_end   = original_label.find("]")
          label_yield       = original_label[label_yield_start+1:label_yield_end]
          corresponding_yields.append(int(label_yield))
    return reordered_labels, corresponding_yields


def hasbit(value, bit):
  # copied from Dennis' ProcessWeights.py
  return (value & (1 << bit))>0

def getBin(var, axis):
  # copied from Dennis' ProcessWeights.py
  mybin = axis.FindBin(var)
  nbins = axis.GetNbins()
  if mybin<1: mybin=1
  elif mybin>nbins: mybin=nbins
  return mybin

def highest_mjj_pair(TLorentzVector_Jets):
  mjj = -999;
  j1_idx = -1;
  j2_idx = -1;
  for j_jet in range(len(TLorentzVector_Jets)):
    for k_jet in range(len(TLorentzVector_Jets)):
      #print(j_jet, k_jet)
      if (k_jet <= j_jet): continue
      j1 = TLorentzVector_Jets[j_jet]
      j2 = TLorentzVector_Jets[k_jet]
      temp_mjj = (j1+j2).M()
      if (temp_mjj > mjj):
        mjj = temp_mjj
        j1_idx = j_jet
        j2_idx = k_jet
  if (j1_idx*j2_idx < 0): print("jet index unassigned!")
  #return TLorentzVector_Jets[j1_idx], TLorentzVector_Jets[j2_idx]
  return j1_idx, j2_idx

def return_TLorentz_Jets(passingJetsPt, passingJetsEta, passingJetsPhi, passingJetsMass):
  ''' only use with ≥2 jets '''
  TLorentzVector_Jets = []
  from ROOT import TLorentzVector 
  for i in range(len(passingJetsPt)):
    temp_jet_vec = TLorentzVector()
    temp_jet_vec.SetPtEtaPhiM(passingJetsPt[i], passingJetsEta[i], passingJetsPhi[i], passingJetsMass[i])
    TLorentzVector_Jets.append(temp_jet_vec)
  j1_idx, j2_idx = highest_mjj_pair(TLorentzVector_Jets)
  mjj = (TLorentzVector_Jets[j1_idx] + TLorentzVector_Jets[j2_idx]).M()
  # add special tag for Run2 VBF trigger
  special_tag = False
  if len(TLorentzVector_Jets) >= 3:
    if mjj > 700: # HARDCODED VALUE FOR RUN2 VBF TRIGGER
      for jet in TLorentzVector_Jets:
        if jet.Pt() > 120: # HARDCODED VALUE FOR RUN2 VBF TRIGGER
          special_tag = True
  return TLorentzVector_Jets, j1_idx, j2_idx, mjj, special_tag

def user_exp(x, a, b, c, d):
    return a*np.exp(-b*(x-c)) + d

def user_pol_np(x, par):
    '''
    Defines function given length of parameters as
    par[0]*x^n + par[1]*x^n-1 + ... + par[n]*x^0 
    '''
    return np.polyval(par, x)

def user_line(x, a, b):
    # y = mx + b # par[0]*x^1 + par[1]*x^0
    #return np.polyval([a, b], x)  # for len(par) == 2, this is a line
    return a*x + b


def append_Zpt_weight(event_dictionary):
  unpack_Zpt = [
    "nGenPart", "GenPart_pdgId", "GenPart_status", "GenPart_statusFlags",
    "GenPart_pt", "GenPart_eta", "GenPart_phi", "GenPart_mass",
  ]
  unpack_Zpt = (event_dictionary.get(key) for key in unpack_Zpt)
  Gen_Zpt, Gen_Z_mass, Gen_Zpt_weight = [], [], []

  # could make our own weights like this with a little effort
  # load 2D ROOT hist from local file
  from ROOT import TLorentzVector, TFile, TH2
  zptroot = TFile("SFs/zpt_reweighting_LO_2022.root", "open")
  zpthist = zptroot.Get("zptmass_histo")
  for nGen, pdgId, status, statusFlags, pt, eta, phi, mass in zip(*unpack_Zpt):
    good_lep_vecs = []
    for iparticle in range(nGen):
      pdgId_part  = abs(pdgId[iparticle])
      status_part = status[iparticle]
      flags_part  = statusFlags[iparticle]
      if ( ((pdgId_part==11 or pdgId_part==13) and status_part==1 and hasbit(flags_part, 8))
        or (pdgId_part==15 and status_part==2 and hasbit(flags_part, 8)) ): # 8 : fromHardProcess
        lep_vec = TLorentzVector() # surprisingly, you can't combine this with the following line
        lep_vec.SetPtEtaPhiM(pt[iparticle], eta[iparticle], phi[iparticle], mass[iparticle])
        good_lep_vecs.append(lep_vec)
    # end loop over particles in event
    #print(f"Z boson lep cands in event: {len(good_lep_vecs)}") # always 2
    zmass, zpt = 0.0, 0.0
    if (len(good_lep_vecs) == 2):
      zboson = good_lep_vecs[0] + good_lep_vecs[-1] # adding only cands in the list
      zmass = zboson.M()
      zpt   = zboson.Pt()

    zptweight = 1.0
    if not (zmass==0.0 and zpt==0.0):
      xbin = getBin(zmass, zpthist.GetXaxis())
      ybin = getBin(zpt, zpthist.GetYaxis())
      zptweight = zpthist.GetBinContent(xbin, ybin)
      if zptweight<=0.0: zptweight=1.0
    Gen_Zpt_weight.append(zptweight)

  event_dictionary["Weight_DY_Zpt_by_hand"] = np.array(Gen_Zpt_weight)
  return event_dictionary






