def set_branches(final_state_mode, DeepTau_version, process="None"):
  common_branches = [
    "run", "luminosityBlock", "event", "Generator_weight", "NWEvents", "XSecMCweight",
    "TauSFweight", "MuSFweight", "ElSFweight", "ElSFweight_Trig", "BTagSFfull", "Weight_DY_Zpt_LO", "Weight_DY_Zpt_NLO", "PUweight", "Weight_TTbar_NNLO",
    "FSLeptons", "Lepton_pt", "Lepton_eta", "Lepton_phi", "Lepton_iso",
    "Tau_genPartFlav", "Tau_decayMode",
    "nCleanJet", "CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "CleanJet_mass",
    "HTT_m_vis", "HTT_dR", "HTT_pT_l1l2", "FastMTT_mT", "FastMTT_mass",
    #"HTT_m_vis", "HTT_dR", "HTT_pT_l1l2",
    "HTT_pdgId",
    #"Tau_rawPNetVSjet", "Tau_rawPNetVSmu", "Tau_rawPNetVSe",
    "PV_npvs", "Pileup_nPU",
    #"HTT_DiJet_dEta_fromHighestMjj", "HTT_DiJet_MassInv_fromHighestMjj",
  ]
  branches = common_branches
  branches = add_final_state_branches(branches, final_state_mode)
  if final_state_mode != ["dimuon", "emu"]: branches = add_DeepTau_branches(branches, DeepTau_version)
  branches = add_trigger_branches(branches, final_state_mode)  
  if ((final_state_mode == "emu"  or final_state_mode == "etau") and ("Data" in process)): branches = add_FFweight_branch(branches)
  if ("DY" in process): branches = add_Zpt_branches(branches)
  return branches


def add_final_state_branches(branches_, final_state_mode):
  '''
  Helper function to add only relevant branches to loaded branches based on final state.
  '''
  final_state_branches = {
    "ditau"  : ["Lepton_tauIdx", "Tau_dxy", "Tau_dz", "Tau_charge", "PuppiMET_pt", "PuppiMET_phi"],

    "mutau"  : ["Muon_dxy", "Muon_dz", "Muon_charge",
                "Tau_dxy", "Tau_dz", "Tau_charge",
                "Lepton_tauIdx", "Lepton_muIdx",
                "PuppiMET_pt", "PuppiMET_phi", "CleanJet_btagWP"],

    "mutau_TnP"  : ["Muon_dxy", "Muon_dz", "Muon_charge",
                "Tau_dxy", "Tau_dz", "Tau_charge",
                "Lepton_tauIdx", "Lepton_muIdx",
                "PuppiMET_pt", "PuppiMET_phi", "CleanJet_btagWP"],

    "etau"   : ["Electron_dxy", "Electron_dz", "Electron_charge", 
                "Tau_dxy", "Tau_dz", "Tau_charge", 
                "Lepton_tauIdx", "Lepton_elIdx",
                "PuppiMET_pt", "PuppiMET_phi", "CleanJet_btagWP"],

    "dimuon" : ["Lepton_pdgId", "Lepton_muIdx",
                "Muon_dxy", "Muon_dz", "Muon_charge",
                "PuppiMET_pt", "PuppiMET_phi", "CleanJet_btagWP"],

    "emu"   : ["Electron_dxy", "Electron_dz", "Electron_charge", 
                "Muon_dxy", "Muon_dz", "Muon_charge", 
                "Lepton_elIdx", "Lepton_muIdx",
                "PuppiMET_pt", "PuppiMET_phi", "Lepton_tauIdx", 
                "Electron_mass", "Muon_mass",
                "CleanJet_btagWP", "HTT_PZeta_using_PUPPI_MET", "HTT_mT_l1l2met_using_PUPPI_MET"],   #Naila: DO we need Lepton_pdgID in emu state ?      
  }

  branch_to_add = final_state_branches[final_state_mode]
  for new_branch in branch_to_add:
    branches_.append(new_branch)
  
  return branches_


from triggers_dictionary import triggers_dictionary

def add_trigger_branches(branches_, final_state_mode):
  '''
  Helper function to add HLT branches used by a given final state
  '''
  for trigger in triggers_dictionary[final_state_mode]:
    branches_.append(trigger)
  return branches_


def add_DeepTau_branches(branches_, DeepTauVersion):
  ''' Helper function to add DeepTauID branches '''
  if DeepTauVersion == "2p1":
    for DeepTau_v2p1_branch in ["Tau_idDeepTau2017v2p1VSjet", "Tau_idDeepTau2017v2p1VSmu", "Tau_idDeepTau2017v2p1VSe"]:
      branches_.append(DeepTau_v2p1_branch)

  elif DeepTauVersion == "2p5":
    for DeepTau_v2p5_branch in ["Tau_idDeepTau2018v2p5VSjet", "Tau_idDeepTau2018v2p5VSmu", "Tau_idDeepTau2018v2p5VSe"]:
      branches_.append(DeepTau_v2p5_branch)

  else:
    print(f"no branches added with argument {DeepTauVersion}. Try 2p1 or 2p5.")

  return branches_


def add_Zpt_branches(branches_,):
  ''' Helper function to add branches for Zpt calculation '''
  Zpt_weight_branches = [
    "nGenPart", "GenPart_pdgId", "GenPart_status", "GenPart_statusFlags",
    "GenPart_pt", "GenPart_eta", "GenPart_phi", "GenPart_mass",
  ]
  for branch in Zpt_weight_branches:
    branches_.append(branch)

  return branches_

def add_FFweight_branch(branches_,):

  FFweight_branches = ["FFweight"]
  for branch in FFweight_branches:
    branches_.append(branch)
  return branches_
