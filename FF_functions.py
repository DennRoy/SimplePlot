import numpy as np
from setup import set_good_events
from cut_ditau_functions import make_ditau_region, make_ditau_cut
from cut_mutau_functions import make_mutau_region, make_mutau_cut
from cut_etau_functions  import make_etau_region,  make_etau_cut
from cut_dimuon_functions  import make_dimuon_region, make_dimuon_cut
from cut_emu_functions  import make_emu_region, make_emu_cut
#from cut_and_study_functions import apply_AR_cut
from FF_dictionary import FF_fit_values, FF_mvis_weights
from calculate_functions import user_exp, user_line
from plotting_functions import set_vars_to_plot

def FF_control_flow(final_state_mode, semilep_mode, region, event_dictionary, DeepTau_version):
  if (final_state_mode == "ditau"):
    if (region == "SR"):        event_dictionary   = make_ditau_SR_cut(event_dictionary, DeepTau_version)
    if (region == "AR"):        event_dictionary   = make_ditau_AR_cut(event_dictionary, DeepTau_version)
    if (region == "DRsr"):      event_dictionary   = make_ditau_DRsr_cut(event_dictionary, DeepTau_version)
    if (region == "DRar"):      event_dictionary   = make_ditau_DRar_cut(event_dictionary, DeepTau_version)
    if (region == "SR_aiso"):   event_dictionary   = make_ditau_SR_aiso_cut(event_dictionary, DeepTau_version)
    if (region == "AR_aiso"):   event_dictionary   = make_ditau_AR_aiso_cut(event_dictionary, DeepTau_version)
    if (region == "DRsr_aiso"): event_dictionary   = make_ditau_DRsr_aiso_cut(event_dictionary, DeepTau_version)
    if (region == "DRar_aiso"): event_dictionary   = make_ditau_DRar_aiso_cut(event_dictionary, DeepTau_version)

  if (final_state_mode == "mutau"):
    if (region == "SR"):      event_dictionary = make_mutau_SR_cut(event_dictionary, DeepTau_version)
    if (region == "AR"):      event_dictionary = make_mutau_AR_cut(event_dictionary, DeepTau_version)
    if (region == "SR_aiso"): event_dictionary = make_mutau_SR_aiso_cut(event_dictionary, DeepTau_version)
    if (region == "AR_aiso"): event_dictionary = make_mutau_AR_aiso_cut(event_dictionary, DeepTau_version)

    if (semilep_mode == "QCD"):
      if (region == "DRsr"):      event_dictionary = make_mutau_DRsr_QCD_cut(event_dictionary, DeepTau_version)
      if (region == "DRar"):      event_dictionary = make_mutau_DRar_QCD_cut(event_dictionary, DeepTau_version)
      if (region == "DRsr_aiso"): event_dictionary = make_mutau_DRsr_aiso_QCD_cut(event_dictionary, DeepTau_version)
      if (region == "DRar_aiso"): event_dictionary = make_mutau_DRar_aiso_QCD_cut(event_dictionary, DeepTau_version)

    if (semilep_mode == "WJ"):
      if (region == "DRsr"):      event_dictionary = make_mutau_DRsr_WJ_cut(event_dictionary, DeepTau_version)
      if (region == "DRar"):      event_dictionary = make_mutau_DRar_WJ_cut(event_dictionary, DeepTau_version)
      if (region == "DRsr_aiso"): event_dictionary = make_mutau_DRsr_aiso_WJ_cut(event_dictionary, DeepTau_version)
      if (region == "DRar_aiso"): event_dictionary = make_mutau_DRar_aiso_WJ_cut(event_dictionary, DeepTau_version)

  if (final_state_mode == "etau"):
    if (region == "SR"):      event_dictionary = make_etau_SR_cut(event_dictionary, DeepTau_version)
    if (region == "AR"):      event_dictionary = make_etau_AR_cut(event_dictionary, DeepTau_version)
    if (region == "SR_aiso"): event_dictionary = make_etau_SR_aiso_cut(event_dictionary, DeepTau_version)
    if (region == "AR_aiso"): event_dictionary = make_etau_AR_aiso_cut(event_dictionary, DeepTau_version)

    if (semilep_mode == "QCD"):
      if (region == "DRsr"):      event_dictionary = make_etau_DRsr_QCD_cut(event_dictionary, DeepTau_version)
      if (region == "DRar"):      event_dictionary = make_etau_DRar_QCD_cut(event_dictionary, DeepTau_version)
      if (region == "DRsr_aiso"): event_dictionary = make_etau_DRsr_aiso_QCD_cut(event_dictionary, DeepTau_version)
      if (region == "DRar_aiso"): event_dictionary = make_etau_DRar_aiso_QCD_cut(event_dictionary, DeepTau_version)

    if (semilep_mode == "WJ"):
      if (region == "DRsr"):      event_dictionary = make_etau_DRsr_WJ_cut(event_dictionary, DeepTau_version)
      if (region == "DRar"):      event_dictionary = make_etau_DRar_WJ_cut(event_dictionary, DeepTau_version)
      if (region == "DRsr_aiso"): event_dictionary = make_etau_DRsr_aiso_WJ_cut(event_dictionary, DeepTau_version)
      if (region == "DRar_aiso"): event_dictionary = make_etau_DRar_aiso_WJ_cut(event_dictionary, DeepTau_version)

  if (final_state_mode == "dimuon"):
    if (region == "SR"):      event_dictionary = make_dimuon_SR_cut(event_dictionary)
    else: print("missing region condition")

  if (final_state_mode == "emu"):
    if (region == "SR"):        event_dictionary   = make_emu_SR_cut(event_dictionary)
    if (region == "AR"):        event_dictionary   = make_emu_AR_cut(event_dictionary)
    if (region == "DRsr"):      event_dictionary   = make_emu_DRsr_cut(event_dictionary)
    if (region == "DRar"):      event_dictionary   = make_emu_DRar_cut(event_dictionary)
    if (region == "SR_aiso"):   event_dictionary   = make_emu_SR_aiso_cut(event_dictionary)
    if (region == "AR_aiso"):   event_dictionary   = make_emu_AR_aiso_cut(event_dictionary)
    if (region == "DRsr_aiso"): event_dictionary   = make_emu_DRsr_aiso_cut(event_dictionary)
    if (region == "DRar_aiso"): event_dictionary   = make_emu_DRar_aiso_cut(event_dictionary)

  return event_dictionary

ditau_DeepTauVsJet_WP = 5
# ditau region cuts
def make_ditau_SR_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_SR_cuts" if iso_region == True else "pass_SR_aiso_cuts"
  event_dictionary = make_ditau_region(event_dictionary, name, FS_pair_sign=-1,
                       pass_DeepTau_t1_req=True, DeepTau_t1_value=ditau_DeepTauVsJet_WP,
                       pass_DeepTau_t2_req=iso_region, DeepTau_t2_value=ditau_DeepTauVsJet_WP, 
                       DeepTau_version="2p5")
  return event_dictionary

def make_ditau_AR_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_AR_cuts" if iso_region == True else "pass_AR_aiso_cuts"
  event_dictionary = make_ditau_region(event_dictionary, name, FS_pair_sign=-1,
                       pass_DeepTau_t1_req=False, DeepTau_t1_value=ditau_DeepTauVsJet_WP,
                       pass_DeepTau_t2_req=iso_region,  DeepTau_t2_value=ditau_DeepTauVsJet_WP, 
                       DeepTau_version="2p5")
  return event_dictionary

def make_ditau_DRsr_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRsr_cuts" if iso_region == True else "pass_DRsr_aiso_cuts"
  event_dictionary = make_ditau_region(event_dictionary, name, FS_pair_sign=1,
                       pass_DeepTau_t1_req=True, DeepTau_t1_value=ditau_DeepTauVsJet_WP,
                       pass_DeepTau_t2_req=iso_region, DeepTau_t2_value=ditau_DeepTauVsJet_WP, 
                       DeepTau_version="2p5")
  return event_dictionary

def make_ditau_DRar_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRar_cuts" if iso_region == True else "pass_DRar_aiso_cuts"
  event_dictionary = make_ditau_region(event_dictionary, name, FS_pair_sign=1,
                       pass_DeepTau_t1_req=False, DeepTau_t1_value=ditau_DeepTauVsJet_WP,
                       pass_DeepTau_t2_req=iso_region, DeepTau_t2_value=ditau_DeepTauVsJet_WP, 
                       DeepTau_version="2p5")
  return event_dictionary

def make_ditau_SR_aiso_cut(event_dictionary, DeepTau_version):
  return make_ditau_SR_cut(event_dictionary, DeepTau_version, iso_region=False)

def make_ditau_AR_aiso_cut(event_dictionary, DeepTau_version):
  return make_ditau_AR_cut(event_dictionary, DeepTau_version, iso_region=False)

def make_ditau_DRsr_aiso_cut(event_dictionary, DeepTau_version):
  return make_ditau_DRsr_cut(event_dictionary, DeepTau_version, iso_region=False)

def make_ditau_DRar_aiso_cut(event_dictionary, DeepTau_version):
  return make_ditau_DRar_cut(event_dictionary, DeepTau_version, iso_region=False)


mutau_DeepTauVsJet_WP = 5
### begin mutau region cuts
def make_mutau_SR_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_SR_cuts" if iso_region == True else "pass_SR_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_mu_iso_req=iso_region, mu_iso_value=[0.00,0.15],
                         pass_DeepTau_req=True, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version=DeepTau_version,
                         pass_mt_req=True, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_mutau_AR_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_AR_cuts" if iso_region == True else "pass_AR_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_mu_iso_req=iso_region, mu_iso_value=[0.00,0.15],
                         pass_DeepTau_req=False, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version=DeepTau_version,
                         pass_mt_req=True, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_mutau_SR_aiso_cut(event_dictionary, DeepTau_version):
  return make_mutau_SR_cut(event_dictionary, DeepTau_version, iso_region=False)
 
def make_mutau_AR_aiso_cut(event_dictionary, DeepTau_version):
  return make_mutau_AR_cut(event_dictionary, DeepTau_version, iso_region=False)
 
### QCD 
def make_mutau_DRsr_QCD_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRsr_cuts" if iso_region == True else "pass_DRsr_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name,
                         FS_pair_sign=1, pass_mu_iso_req=iso_region, mu_iso_value=[0.05,0.15],
                         pass_DeepTau_req=True, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version="2p5",
                         pass_mt_req=True, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_mutau_DRar_QCD_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRar_cuts" if iso_region == True else "pass_DRar_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name,
                         FS_pair_sign=1, pass_mu_iso_req=iso_region, mu_iso_value=[0.05,0.15],
                         pass_DeepTau_req=False, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version="2p5",
                         pass_mt_req=True, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_mutau_DRsr_aiso_QCD_cut(event_dictionary, DeepTau_version):
  return make_mutau_DRsr_QCD_cut(event_dictionary, DeepTau_version, iso_region=False)

def make_mutau_DRar_aiso_QCD_cut(event_dictionary, DeepTau_version):
  return make_mutau_DRar_QCD_cut(event_dictionary, DeepTau_version, iso_region=False)

### WJ
def make_mutau_DRsr_WJ_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRsr_cuts" if iso_region == True else "pass_DRsr_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name,
                         FS_pair_sign=-1, pass_mu_iso_req=iso_region, mu_iso_value=[0.0,0.15],
                         pass_DeepTau_req=True, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version="2p5",
                         pass_mt_req=False, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_mutau_DRar_WJ_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRar_cuts" if iso_region == True else "pass_DRar_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name,
                         FS_pair_sign=-1, pass_mu_iso_req=iso_region, mu_iso_value=[0.0,0.15],
                         pass_DeepTau_req=False, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version="2p5",
                         pass_mt_req=False, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_mutau_DRsr_aiso_WJ_cut(event_dictionary, DeepTau_version):
  return make_mutau_DRsr_WJ_cut(event_dictionary, DeepTau_version, iso_region=False)

def make_mutau_DRar_aiso_WJ_cut(event_dictionary, DeepTau_version):
  return make_mutau_DRar_WJ_cut(event_dictionary, DeepTau_version, iso_region=False)

### TTBar (not used)
def make_mutau_DRsr_TT_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRsr_cuts" if iso_region == True else "pass_DRsr_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name,
                         FS_pair_sign=-1, pass_mu_iso_req=True, mu_iso_value=0.15,
                         pass_DeepTau_req=True, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version="2p5",
                         pass_mt_req=True, mt_value=50, pass_BTag_req=False)
  return event_dictionary

def make_mutau_DRar_TT_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_DRar_cuts" if iso_region == True else "pass_DRar_aiso_cuts"
  event_dictionary   = make_mutau_region(event_dictionary, name,
                         FS_pair_sign=-1, pass_mu_iso_req=True, mu_iso_value=0.15,
                         pass_DeepTau_req=False, DeepTau_value=mutau_DeepTauVsJet_WP, DeepTau_version="2p5",
                         pass_mt_req=True, mt_value=50, pass_BTag_req=False)
  return event_dictionary

def make_mutau_DRsr_aiso_TT_cut(event_dictionary, DeepTau_version, iso_region):
  return make_mutau_DRsr_TT_cut(event_dictionary, DeepTau_version, iso_region=False)

def make_mutau_DRar_aiso_TT_cut(event_dictionary, DeepTau_version):
  return make_mutau_DRar_TT_cut(event_dictionary, DeepTau_version, iso_region=False)


# etau
etau_DeepTauVsJet_WP = 5
def make_etau_SR_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_SR_cuts" if iso_region == True else "pass_SR_aiso_cuts"
  event_dictionary   = make_etau_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_el_iso_req=iso_region, el_iso_value=0.15,
                         pass_DeepTau_req=True, DeepTau_value=etau_DeepTauVsJet_WP, DeepTau_version=DeepTau_version,
                         pass_mt_req=True, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_etau_AR_cut(event_dictionary, DeepTau_version, iso_region=True):
  name = "pass_AR_cuts" if iso_region == True else "pass_AR_aiso_cuts"
  event_dictionary   = make_etau_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_el_iso_req=iso_region, el_iso_value=0.15,
                         pass_DeepTau_req=False, DeepTau_value=etau_DeepTauVsJet_WP, DeepTau_version=DeepTau_version,
                         pass_mt_req=True, mt_value=50, pass_BTag_req=True)
  return event_dictionary

def make_etau_SR_aiso_cut(event_dictionary, DeepTau_version):
  return make_etau_SR_cut(event_dictionary, DeepTau_version, iso_region=False)
 
def make_etau_AR_aiso_cut(event_dictionary, DeepTau_version):
  return make_etau_AR_cut(event_dictionary, DeepTau_version, iso_region=False)

# dimuon
def make_dimuon_SR_cut(event_dictionary, iso_region=True):
  name = "pass_SR_cuts" if iso_region == True else "pass_SR_aiso_cuts"
  event_dictionary     = make_dimuon_region(event_dictionary, name, FS_pair_sign=-1)
  return event_dictionary

#emu region cuts
def make_emu_SR_cut(event_dictionary, iso_region_el=True, iso_region_mu=True):
  name = "pass_SR_cuts" if ((iso_region_el == True) and (iso_region_mu ==True)) else "pass_SR_aiso_cuts"
  event_dictionary   = make_emu_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_el_iso_req=iso_region_el, el_iso_value=[0.00,0.15],
                         pass_mu_iso_req=iso_region_mu, mu_iso_value=[0.00,0.15],
                         pass_BTag_req=True)
  print("passed SR")
  return event_dictionary

def make_emu_AR_cut(event_dictionary, iso_region_el=True, iso_region_mu=True):
  name = "pass_AR_cuts" if ((iso_region_el == True) and (iso_region_mu ==True)) else "pass_AR_aiso_cuts"
  event_dictionary = make_emu_region(event_dictionary, name, 
                         FS_pair_sign=1, pass_el_iso_req=iso_region_el, el_iso_value=[0.00,0.15],
                         pass_mu_iso_req=iso_region_mu, mu_iso_value=[0.00,0.15],
                         pass_BTag_req=True)
  print("passed AR")
  return event_dictionary

def make_emu_DRsr_cut(event_dictionary, iso_region_el=True, iso_region_mu=False):
  name = "pass_DRsr_cuts" if ((iso_region_el == True) and (iso_region_mu == False)) else "pass_DRsr_aiso_cuts"
  event_dictionary = make_emu_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_el_iso_req=iso_region_el, el_iso_value=[0.00,0.15],
                         pass_mu_iso_req=iso_region_mu, mu_iso_value=[0.00,0.15],
                         pass_BTag_req=True)
  print("passed DRsr")
  return event_dictionary

def make_emu_DRar_cut(event_dictionary, iso_region_el=True, iso_region_mu=False):
  name = "pass_DRar_cuts" if ((iso_region_el == True) and (iso_region_mu == False)) else "pass_DRar_aiso_cuts"
  event_dictionary = make_emu_region(event_dictionary, name, 
                         FS_pair_sign=-1, pass_el_iso_req=iso_region_el, el_iso_value=[0.00,0.15],
                         pass_mu_iso_req=iso_region_mu, mu_iso_value=[0.00,0.15],
                         pass_BTag_req=True)
  print("passed DRar")
  return event_dictionary

def make_emu_SR_aiso_cut(event_dictionary,):
  return make_emu_SR_cut(event_dictionary, iso_region_el=False, iso_region_mu=True)

def make_emu_AR_aiso_cut(event_dictionary):
  return make_emu_AR_cut(event_dictionary, iso_region_el=False, iso_region_mu=True)

def make_emu_DRsr_aiso_cut(event_dictionary):
  return make_emu_DRsr_cut(event_dictionary, iso_region_el=False, iso_region_mu=False)

def make_emu_DRar_aiso_cut(event_dictionary):
  return make_emu_DRar_cut(event_dictionary, iso_region_el=False, iso_region_mu=False)

#########################################################################################
# Calculation Functions
#########################################################################################

def add_FF_weights(event_dictionary, final_state_mode, jet_mode, semilep_mode, closure=False, bypass=[]):
  # interface to read FF_dictionary
  unpack_FF_vars = ["Lepton_pt", "HTT_m_vis", "l1_indices", "l2_indices", "Lepton_iso"]
  unpack_FF_vars = (event_dictionary.get(key) for key in unpack_FF_vars)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_FF_vars]
  FF_weights = []
  QCD_fitvals   = FF_fit_values[final_state_mode][jet_mode]["QCD"]
  if (final_state_mode != "ditau"):
    WJ_fitvals   = FF_fit_values[final_state_mode][jet_mode]["WJ"]
  if bypass != []:  QCD_fitvals, WJ_fitvals = bypass, bypass
  for i, lep_pt, m_vis, l1_idx, l2_idx, lep_iso in zip(*to_check):
    if (final_state_mode == "etau"):
      m_vis = m_vis if m_vis < 180.0 else 179.0 
    else:
      m_vis = m_vis if m_vis < 300.0 else 299.0
    fakeleg_idx = l1_idx if final_state_mode == "ditau" else l2_idx # mutau/etau is always l2, ditau is always l1
    lepleg_idx  = l2_idx if final_state_mode == "ditau" else l1_idx
    tau_pt = lep_pt[fakeleg_idx]
    low_val = 20.0 if final_state_mode == "ditau" else 30.0
    #low_val = 40.0 if final_state_mode == "ditau" else 30.0
    hi_val  = 140.0 if final_state_mode == "ditau" else 200
    tau_pt = tau_pt if tau_pt > low_val else low_val
    tau_pt = tau_pt if tau_pt < hi_val else hi_val

    if (final_state_mode == "etau"):
       if (m_vis <=40): m_vis_idx = 1
       else: m_vis_idx = int(m_vis // 20)
    else: m_vis_idx = int(m_vis // 10) #hard-coding mvis bins of 10 GeV, starting at 0 and ending at 300 ( // is modulo division )
    f_QCD     = FF_mvis_weights[final_state_mode][jet_mode]["QCD"][m_vis_idx] if not closure else 1
    user_func = user_line if final_state_mode == "ditau" else user_exp
    #FF_QCD    = user_func(tau_pt, *QCD_fitvals)
    FF_QCD    = user_line(tau_pt, *QCD_fitvals)

    if (final_state_mode != "ditau"): # else pass
      f_WJ       = FF_mvis_weights[final_state_mode][jet_mode]["WJ"][m_vis_idx] if not closure else 1
      FF_WJ      = user_func(tau_pt, *WJ_fitvals)
    else: pass
    if (semilep_mode == "Full"):
      FF_weight = f_QCD * FF_QCD * 1.1 # OS/SS bias
      if (final_state_mode != "ditau"):
        FF_weight += f_WJ * FF_WJ
    else: 
      if   (semilep_mode == "QCD"):  FF_weight = f_QCD* FF_QCD
      elif (semilep_mode == "WJ"):   FF_weight = f_WJ  * FF_WJ
      else: print("add_FF_weights function error")
    if (FF_weight <= 0):
      print("non-positive FF weights!")
      print("FF_weight: ", FF_weight)
      print("tau_pt: ", tau_pt)
      print("m_vis, m_vis_idx: ", m_vis, m_vis_idx)
    FF_weights.append(FF_weight)
  event_dictionary["FF_weight"] = np.array(FF_weights)
  return event_dictionary

def apply_FF_weight_from_branch(event_dictionary, final_state_mode, process):
  if ((final_state_mode == "emu" ) and ("Data" in process)):
    unpack_FF_vars = ["Lepton_pt", "HTT_m_vis", "FFweight"]
    unpack_FF_vars = (event_dictionary.get(key) for key in unpack_FF_vars)
    to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_FF_vars]
    FF_weights = []
    for i, lep_pt, m_vis, ff in zip(*to_check):
      FF_weights.append(ff)
      event_dictionary["FFweight"] = np.array(FF_weights)
    event_dictionary['AR'] = apply_AR_cut(process, event_dictionary, final_state_mode, jet_mode, semilep_mode, skip_DeepTau=True)
    # Ensure 'FFweight' branch exists in the event dictionary
    if 'FFweight' in event_dictionary:
        # Apply FFweight directly to the AR events
        event_dictionary['QCD'] = event_dictionary['AR'] * event_dictionary['FFweight']
    else:
        raise KeyError("The event dictionary does not contain the 'FFweight' branch.")
    
    return event_dictionary  

from producers import produce_FF_weight
def set_JetFakes_process(setup, fakesLabel, semilep_mode):
  # TODO could be improved by reducing variable name size and simplifying below operations
  JetFakes_dictionary = {}
  _, final_state_mode, jet_mode, _, _ = setup.state_info
  _, _, _, do_JetFakes, _ = setup.misc_info
  vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode)
  if (jet_mode != "Inclusive") and (do_JetFakes==True):
    JetFakes_dictionary = produce_FF_weight(setup, jet_mode, semilep_mode)
  if (final_state_mode == "emu") and (do_JetFakes==True):
    JetFakes_dictionary = apply_FF_weight_from_branch(event_dictionary,final_state_mode,process)
  if (jet_mode == "Inclusive") and (do_JetFakes==True):
    fakesLabel = fakesLabel
    temp_JetFakes_dictionary = {}
    JetFakes_dictionary[fakesLabel] = {}
    JetFakes_dictionary[fakesLabel]["PlotEvents"] = {}
    JetFakes_dictionary[fakesLabel]["FF_weight"]  = {} 
    jetCategories = ["0j", "1j", "GTE2j"] if final_state_mode == "ditau" else ["0j", "GTE1j"]
    for internal_jet_mode in jetCategories:
      temp_JetFakes_dictionary[internal_jet_mode] = produce_FF_weight(setup, internal_jet_mode, semilep_mode)
      if ("0j" in internal_jet_mode):
        JetFakes_dictionary[fakesLabel]["FF_weight"]  = temp_JetFakes_dictionary[internal_jet_mode][fakesLabel]["FF_weight"]
      else:
        JetFakes_dictionary[fakesLabel]["FF_weight"]  = np.concatenate((JetFakes_dictionary[fakesLabel]["FF_weight"],
                                          temp_JetFakes_dictionary[internal_jet_mode][fakesLabel]["FF_weight"]))
      for var in vars_to_plot:
        if ("flav" in var): continue
        if ("0j" in internal_jet_mode): 
          JetFakes_dictionary[fakesLabel]["PlotEvents"][var] = temp_JetFakes_dictionary[internal_jet_mode][fakesLabel]["PlotEvents"][var]
        else:
          JetFakes_dictionary[fakesLabel]["PlotEvents"][var]  = np.concatenate((JetFakes_dictionary[fakesLabel]["PlotEvents"][var],
                                                  temp_JetFakes_dictionary[internal_jet_mode][fakesLabel]["PlotEvents"][var]))
  return JetFakes_dictionary

if __name__ == "__main__":
  from setup import setup_handler
  setup = setup_handler()
  FF_dictionary = produce_FF_weight(setup, setup.state_info.jet_mode)
  print(FF_dictionary)
