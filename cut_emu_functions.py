import numpy as np

from ROOT import TLorentzVector

from calculate_functions import calculate_mt_emu 
from branch_functions import add_trigger_branches

def make_emu_cut(event_dictionary):
  '''
  Works similarly to 'make_ditau_cut'.
  Notably, the mutau cuts are more complicated, but it is simple to 
  extend the existing methods as long as one can stomach the line breaks.
  '''
  nEvents_precut = len(event_dictionary["Lepton_pt"])
  unpack_emu = ["Lepton_pt", "Lepton_eta", "Lepton_phi", "Lepton_iso",
                "Electron_dxy", "Electron_dz", "Electron_charge", 
                "Muon_dxy", "Muon_dz", "Muon_charge", 
                "PuppiMET_pt", "PuppiMET_phi",
                "Lepton_elIdx", "Lepton_muIdx", "l1_indices", "l2_indices", 
                "CleanJet_btagWP", "HTT_PZeta_using_PUPPI_MET", "HTT_mT_l1l2met_using_PUPPI_MET"
                 ]
  
  unpack_emu = add_trigger_branches(unpack_emu, final_state_mode="emu")
  unpack_emu = (event_dictionary.get(key) for key in unpack_emu)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_emu] # "*" unpacks a tuple
  
  FS_mu_pt, FS_mu_eta, FS_mu_phi,FS_mu_iso , FS_mu_dxy, FS_mu_dz, FS_mu_chg = [], [], [], [], [], [], []
  FS_el_pt, FS_el_eta, FS_el_phi, FS_el_iso, FS_el_dxy, FS_el_dz, FS_el_chg = [], [], [], [], [], [], []
  pass_cuts,  FS_nbJet, FS_PZeta, FS_mt = [], [], [], []
  #FS_tau_PNet_v_jet, FS_tau_PNet_v_mu, FS_tau_PNet_v_e = [], [], []
  # goes after l1_idx, l2_idx,
      #PNetvJet, PNetvMu, PNetvE,\
  for i, lep_pt, lep_eta, lep_phi, lep_iso,\
      el_dxy, el_dz, el_chg, mu_dxy, mu_dz, mu_chg,\
      MET_pt, MET_phi, el_idx, mu_idx,\
      l1_idx, l2_idx, btag,\
      crosstrg_1, crosstrg_2, pzeta, mtVal in zip(*to_check):
    
    # some handling to figure out which FS index applies to what lepton
    # note for the DeepTauID we use the tau branch index directly instead of the lepton branch
    # (for tau branches we need the tau_idx, for lepton branches we can simply use the l1_idx, l2_idx)
    elFSLoc, elBranchLoc, muFSLoc, muBranchLoc = 999, 999, 999, 999
    if (el_idx[l1_idx] != -1 and mu_idx[l2_idx] != -1):
      elFSLoc = l1_idx
      elBranchLoc = el_idx[l1_idx]
      muLoc  = l2_idx
      muBranchLoc = mu_idx[l2_idx]
    elif (el_idx[l2_idx] != -1 and mu_idx[l1_idx] != -1):
      elFSLoc = l2_idx
      elBranchLoc = el_idx[l2_idx]
      muLoc  = l1_idx
      muBranchLoc = mu_idx[l1_idx]
    else:
      print("Should not print :)")

    muPtVal    = lep_pt[muLoc] 
    muEtaVal   = lep_eta[muLoc]
    muPhiVal   = lep_phi[muLoc]
    muIsoVal   = lep_iso[muLoc]
    muDxyVal   = abs(mu_dxy[muBranchLoc])
    muDzVal    = abs(mu_dz[muBranchLoc])
    muChgVal   = mu_chg[muBranchLoc]
    elPtVal    = lep_pt[elFSLoc] 
    elEtaVal   = lep_eta[elFSLoc]
    elPhiVal   = lep_phi[elFSLoc]
    elIsoVal   = lep_iso[elFSLoc]
    elDxyVal   = abs(el_dxy[elBranchLoc])
    elDzVal    = el_dz[elBranchLoc]
    elChgVal   = el_chg[elBranchLoc]

    #HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ
    passCrossTrigger_1 = ((crosstrg_1) and (muPtVal > 23.0) and (abs(muEtaVal) < 2.4) 
                                      and (elPtVal > 12.0) and (abs(elEtaVal) < 2.5))
    #HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ
    passCrossTrigger_2 = ((crosstrg_2) and (muPtVal > 8.0) and (abs(muEtaVal) < 2.4) 
                                      and (elPtVal > 23.0) and (abs(elEtaVal) < 2.5))
    
    passPZeta = (pzeta > -30)
    #passMT = (mtVal < 60)

    pass_bTag = True
    nbJet = 0
    for value in btag:
      if (value > 0): 
        pass_bTag = False
        nbJet += 1     

    #if ((passCrossTrigger_1 or passCrossTrigger_2) and passPZeta and passMT):
    if ((passCrossTrigger_1 or passCrossTrigger_2) and passPZeta):
    #if (passCrossTrigger_2 and passPZeta):

      pass_cuts.append(i)
      FS_el_pt.append(elPtVal)
      FS_el_eta.append(elEtaVal)
      FS_el_phi.append(elPhiVal)
      FS_el_iso.append(elIsoVal)
      FS_el_dxy.append(elDxyVal)
      FS_el_dz.append(elDzVal)
      FS_el_chg.append(elChgVal)
      FS_mu_pt.append(muPtVal)
      FS_mu_eta.append(muEtaVal)
      FS_mu_phi.append(muPhiVal)
      FS_mu_iso.append(muIsoVal)
      FS_mu_dxy.append(muDxyVal)
      FS_mu_dz.append(muDzVal)
      FS_mu_chg.append(muChgVal)
      FS_nbJet.append(nbJet)
      #FS_PZeta.append(pzeta)
      #FS_mt.append(mtVal)

  event_dictionary["pass_cuts"]      = np.array(pass_cuts)
  event_dictionary["FS_el_pt"]       = np.array(FS_el_pt)
  event_dictionary["FS_el_eta"]      = np.array(FS_el_eta)
  event_dictionary["FS_el_phi"]      = np.array(FS_el_phi)
  event_dictionary["FS_el_iso"]      = np.array(FS_el_iso)
  event_dictionary["FS_el_dxy"]      = np.array(FS_el_dxy)
  event_dictionary["FS_el_dz"]       = np.array(FS_el_dz)
  event_dictionary["FS_el_chg"]      = np.array(FS_el_chg)
  event_dictionary["FS_mu_pt"]       = np.array(FS_mu_pt)
  event_dictionary["FS_mu_eta"]      = np.array(FS_mu_eta)
  event_dictionary["FS_mu_phi"]      = np.array(FS_mu_phi)
  event_dictionary["FS_mu_iso"]      = np.array(FS_mu_iso)
  event_dictionary["FS_mu_dxy"]      = np.array(FS_mu_dxy)
  event_dictionary["FS_mu_dz"]       = np.array(FS_mu_dz)
  event_dictionary["FS_mu_chg"]      = np.array(FS_mu_chg)
  event_dictionary["FS_nbJet"]       = np.array(FS_nbJet)
  #event_dictionary["FS_PZeta"]       = np.array(FS_PZeta)
  #event_dictionary["FS_mt"]          = np.array(FS_mt)

  nEvents_postcut = len(np.array(pass_cuts))
  print(f"nEvents before and after emu cuts = {nEvents_precut}, {nEvents_postcut}")
  return event_dictionary


def make_emu_region(event_dictionary, new_branch_name, FS_pair_sign, 
                      pass_el_iso_req, el_iso_value, 
                      pass_mu_iso_req, mu_iso_value, 
                      pass_BTag_req):
  
  unpack_emu_vars = ["event", "Lepton_elIdx", "Lepton_muIdx", "Lepton_iso", 
                       "l1_indices", "l2_indices", "HTT_pdgId",
                       "Lepton_pt", "Lepton_phi", "PuppiMET_pt", "PuppiMET_phi",
                       "CleanJet_btagWP", "HTT_PZeta_using_PUPPI_MET", "HTT_mT_l1l2met_using_PUPPI_MET"]
  
  unpack_emu_vars = (event_dictionary.get(key) for key in unpack_emu_vars)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_emu_vars]
  pass_cuts = []
  for i, event, el_idx, mu_idx, lep_iso, l1_idx, l2_idx, signed_pdgId,\
      lep_pt, lep_phi, MET_pt, MET_phi, btag, pzeta, mt in zip(*to_check):

    mu_lep_idx = l1_idx if mu_idx[l1_idx] != -1 else l2_idx
    mu_iso     = lep_iso[mu_lep_idx]
    pass_mu_iso = (mu_iso_value[0] < mu_iso < mu_iso_value[1])

    el_lep_idx = l1_idx if el_idx[l1_idx] != -1 else l2_idx
    el_iso     = lep_iso[el_lep_idx]
    pass_el_iso = (el_iso_value[0]< el_iso < el_iso_value[1])

    #passMT     = (mt < 60)
    passPZeta = (pzeta > -30)

    passBTag = True
    for value in btag:
      if (value > 0): passBTag = False

      # if ( (np.sign(signed_pdgId) == FS_pair_sign) and 
      #     (pass_mu_iso == pass_mu_iso_req) and (pass_el_iso == pass_el_iso_req) and 
      #     (passBTag == pass_BTag_req) and (passPZeta) and (passMT)):
      #   pass_cuts.append(i)
    
    if ( (np.sign(signed_pdgId) == FS_pair_sign) and 
         (pass_mu_iso == pass_mu_iso_req) and (pass_el_iso == pass_el_iso_req) and 
         (passBTag == pass_BTag_req) and (passPZeta)):
      pass_cuts.append(i)

  event_dictionary[new_branch_name] = np.array(pass_cuts)
  return event_dictionary
