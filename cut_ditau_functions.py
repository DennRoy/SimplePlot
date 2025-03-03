import numpy as np

from calculate_functions import calculate_acoplan, return_TLorentz_Jets, calculate_mt, phi_mpi_pi
from branch_functions import add_trigger_branches, add_DeepTau_branches

def make_ditau_cut(event_dictionary, DeepTau_version, skip_DeepTau, tau_pt_cut):
#def make_ditau_cut(event_dictionary, DeepTau_version, skip_DeepTau=False, tau_pt_cut="None"):
  '''
  Use a minimal set of branches to define selection criteria and identify events which pass.
  A separate function uses the generated branch "pass_cuts" to remove the info from the
  loaded samples.
  Note: the zip method in python is a row-scanner, so the for loop below looks like this
  Events | pt | eta | tau_idx
  ###########################
       1 | 27 | 0.5 | 1
       2 | 35 | 1.5 | 0
       3 | 40 | 2.1 | 0
  i.e. we see variables of events sequentially.
  With this info, we make a simple check and store relevant variables.
  Note: stored variable branches are appended to other functions so that cutting
  events works properly
  '''
  nEvents_precut = len(event_dictionary["Lepton_pt"])
  unpack_ditau = ["Lepton_pt", "Lepton_eta", "Lepton_phi", "Lepton_tauIdx", 
                  "Tau_dxy", "Tau_dz", "Tau_decayMode", "Tau_charge", "Lepton_mass", "l1_indices", "l2_indices",
                  "PuppiMET_pt", "PuppiMET_phi", "HTT_m_vis",
                  "nCleanJet", "CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "CleanJet_mass",
                  "Tau_flightLengthSig", "Tau_flightLengthX", "Tau_flightLengthY", "Tau_flightLengthZ", 
                  "Tau_ipLengthSig", "Tau_ip3d", "Tau_track_lambda", "Tau_track_qoverp",
                  #"Tau_rawPNetVSjet", "Tau_rawPNetVSmu", "Tau_rawPNetVSe"
                  ]
  unpack_ditau = add_DeepTau_branches(unpack_ditau, DeepTau_version)
  unpack_ditau = add_trigger_branches(unpack_ditau, final_state_mode="ditau")
  unpack_ditau = (event_dictionary.get(key) for key in unpack_ditau)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_ditau] # "*" unpacks a tuple
  pass_cuts = []
  FS_t1_pt, FS_t1_eta, FS_t1_phi, FS_t1_dxy, FS_t1_dz, FS_t1_chg, FS_t1_DM, FS_t1_mass = [], [], [], [], [], [], [], []
  FS_t2_pt, FS_t2_eta, FS_t2_phi, FS_t2_dxy, FS_t2_dz, FS_t2_chg, FS_t2_DM, FS_t2_mass = [], [], [], [], [], [], [], []
  #FS_t1_PNet_v_jet, FS_t1_PNet_v_mu, FS_t1_PNet_v_e = [], [], []
  #FS_t2_PNet_v_jet, FS_t2_PNet_v_mu, FS_t2_PNet_v_e = [], [], []
  FS_t1_DeepTau_v_jet, FS_t1_DeepTau_v_mu, FS_t1_DeepTau_v_e = [], [], []
  FS_t2_DeepTau_v_jet, FS_t2_DeepTau_v_mu, FS_t2_DeepTau_v_e = [], [], []
  FS_trig_idx, pair_decayMode = [], []
  FS_mt_t1t2, FS_mt_t1_MET, FS_mt_t2_MET, FS_mt_TOT, FS_dphi_t1t2, FS_deta_t1t2 = [], [], [], [], [], []
  FS_t1_FLsig, FS_t1_FLX, FS_t1_FLY, FS_t1_FLZ, FS_t1_FLmag = [], [], [], [], []
  FS_t1_ipLsig, FS_t1_ip3d, FS_t1_tk_lambda, FS_t1_tk_qoverp = [], [], [], []
  FS_t2_FLsig, FS_t2_FLX, FS_t2_FLY, FS_t2_FLZ, FS_t2_FLmag = [], [], [], [], []
  FS_t2_ipLsig, FS_t2_ip3d, FS_t2_tk_lambda, FS_t2_tk_qoverp = [], [], [], []
      #PNetvJet, PNetvMu, PNetvE, vJet, vMu, vEle,\
  for i, lep_pt, lep_eta, lep_phi, tau_idx,\
      tau_dxy, tau_dz, tau_decayMode, tau_chg, tau_mass, l1_idx, l2_idx,\
      MET_pt, MET_phi, mvis,\
      nJet, jet_pt, jet_eta, jet_phi, jet_mass,\
      tau_FLsig, tau_FLX, tau_FLY, tau_FLZ, tau_ipLsig, tau_ip3d, tau_tk_lambda, tau_tk_qoverp,\
      vJet, vMu, vEle,\
      ditau_trig, ditau_jet_low_trig, ditau_jet_high_trig,\
      ditau_VBFRun2_trig, ditau_VBFRun3_trig in zip(*to_check):
    # assign object pts and etas
    t1_pt  = lep_pt[l1_idx]
    t2_pt  = lep_pt[l2_idx]
    t1_eta = lep_eta[l1_idx]
    t2_eta = lep_eta[l2_idx]
    t1_phi = lep_phi[l1_idx]
    t2_phi = lep_phi[l2_idx]
    j1_pt, j2_pt, mjj = -999, -999, -999 # dummy values to check kinem function
    deta_jj, avg_eta_jj, zepp = -999, -999, -999
    ST = False # special tag
    if nJet == 0: pass
    elif nJet == 1: j1_pt = jet_pt[0]
    else:
      TLorentzJets, j1_idx, j2_idx, mjj, ST = return_TLorentz_Jets(jet_pt, jet_eta, jet_phi, jet_mass)
      j1_pt = TLorentzJets[j1_idx].Pt()
      j2_pt = TLorentzJets[j2_idx].Pt()
      j1_eta = TLorentzJets[j1_idx].Eta()
      j2_eta = TLorentzJets[j2_idx].Eta()
      deta_jj    = j1_eta - j2_eta
      avg_eta_jj = abs((j1_eta + j2_eta)/2)
      zepp       = ( ( t1_eta - avg_eta_jj) + (t2_eta - avg_eta_jj) ) / (2 * deta_jj)

    triggers = [ditau_trig, ditau_jet_low_trig, ditau_jet_high_trig,\
                ditau_VBFRun2_trig, ditau_VBFRun3_trig]
    trig_results = pass_kinems_by_trigger(triggers, t1_pt, t2_pt, t1_eta, t2_eta, j1_pt, j2_pt, mjj, ST, nJet)
    passKinems = (True in trig_results) # kinematics are passed if any of the above triggers+kinems pass
    #if (passKinems and trig_results[0] != True): print(trig_results)
    #globalMjj  = 600
    #passKinems = (passKinems and (mjj <= globalMjj))

    trig_idx = np.where(trig_results)[0][0] if passKinems else -1
    # do i need to be excluding things greater than certain tau pts? probably...
    #if (trig_results[1] == True) or (trig_results[2] == True) or (trig_results[3] == True):
    #  print(trig_results)
    #  print(trig_idx)
   
    t1_br_idx = tau_idx[l1_idx]
    t2_br_idx = tau_idx[l2_idx]
 
    # Medium v Jet, VLoose v Muon, VVVLoose v Ele
    t1passDT   = (vMu[t1_br_idx] >= 1 and vEle[t1_br_idx] >= 2) # default is 1, 2
    t2passDT   = (vMu[t2_br_idx] >= 1 and vEle[t2_br_idx] >= 2)
    #t1passDT   = (t1passDT and (vJet[t1_br_idx] >= 6))
    #t2passDT   = (t2passDT and (vJet[t2_br_idx] >= 6))
    single_DM_encoder = {0: 0, 1: 1, 10:2, 11:3}
    t1_decayMode = int(tau_decayMode[t1_br_idx])
    t2_decayMode = int(tau_decayMode[t2_br_idx])
    encoded_t1_decayMode = single_DM_encoder[t1_decayMode]
    encoded_t2_decayMode = single_DM_encoder[t2_decayMode]
    pair_DM_encoder = { 0: 0,  100: 1,  1000: 2,  1100: 3, # 16 unique DM pairs from t1_DM*100 + t2_DM
                        1: 4,  101: 5,  1001: 6,  1101: 7,
                       10: 8,  110: 9,  1010: 10, 1110: 11,
                       11: 12, 111: 13, 1011: 14, 1111: 15 }
    encoded_pair_decayMode = pair_DM_encoder[t1_decayMode*100 + t2_decayMode]
    #good_tau_decayMode = ((t1_decayMode == 11) and (t2_decayMode == 11))
    #good_tau_decayMode = ((t1_decayMode == 0) and (t2_decayMode == 0))
    good_tau_decayMode = True

    t1_chg = tau_chg[t1_br_idx]
    t2_chg = tau_chg[t2_br_idx]

    #t1_mass = tau_mass[t1_br_idx]
    #t2_mass = tau_mass[t2_br_idx]
    t1_mass = tau_mass[l1_idx]
    t2_mass = tau_mass[l2_idx]

    # there is almost certainly a better way to do this...
    t1_FLsig = tau_FLsig[t1_br_idx]
    t2_FLsig = tau_FLsig[t2_br_idx]
    t1_FLX, t1_FLY, t1_FLZ = tau_FLX[t1_br_idx], tau_FLY[t1_br_idx], tau_FLZ[t1_br_idx]
    t1_FLmag = np.sqrt(t1_FLX*t1_FLX + t1_FLY*t1_FLY + t1_FLZ*t1_FLZ)
    t2_FLX, t2_FLY, t2_FLZ = tau_FLX[t2_br_idx], tau_FLY[t2_br_idx], tau_FLZ[t2_br_idx]
    t2_FLmag = np.sqrt(t2_FLX*t2_FLX + t2_FLY*t2_FLY + t2_FLZ*t2_FLZ)
    t1_ipLsig, t1_ip3d = tau_ipLsig[t1_br_idx], tau_ip3d[t1_br_idx]
    t2_ipLsig, t2_ip3d = tau_ipLsig[t2_br_idx], tau_ip3d[t2_br_idx]
    t1_tk_lambda, t1_tk_qoverp = tau_tk_lambda[t1_br_idx], tau_tk_qoverp[t1_br_idx]
    t2_tk_lambda, t2_tk_qoverp = tau_tk_lambda[t2_br_idx], tau_tk_qoverp[t2_br_idx]

    #if (tau_pt_cut == "None"): 
    #  subtau_req = True
    #else:
    cut_map = { "Low" : [25, 50],  "Mid" : [50, 70],  "High" : [70, 10000]  }
    subtau_req = True 
    if (tau_pt_cut == "None"): pass # do nothing
    else:
      subtau_req = (cut_map[tau_pt_cut][0] <= t2_pt <= cut_map[tau_pt_cut][1])
    #subtau_req = (25 <= t2_pt < 50) # 25-50, 40-50, 50-70, >70
    #subtau_req = (25 <= t2_pt < 40)
    #subtau_req = (40 <= t2_pt < 50)
    #subtau_req = (50 <= t2_pt < 70)
    #subtau_req = (70 <= t2_pt)
   
    # derived variables
    mt_t1t2   = calculate_mt(t1_pt, t1_phi, t2_pt, t2_phi) 
    mt_t1_MET = calculate_mt(t1_pt, t1_phi, MET_pt, MET_phi) 
    mt_t2_MET = calculate_mt(t2_pt, t2_phi, MET_pt, MET_phi) 
    mt_TOT    = np.sqrt(mt_t1t2 + mt_t1_MET + mt_t2_MET)

    dphi_t1t2 = np.acos(np.cos(t1_phi - t2_phi))
    deta_t1t2 = abs(t1_eta - t2_eta)

    mvis_req = (mvis > 50) # remove disagreement at low mvis values
    deta_t1t2_req = (deta_t1t2 < 1.5) # try 2 also

    #if (passKinems and t1passDT and t2passDT and good_tau_decayMode):
    #if (passKinems and t1passDT and t2passDT and good_tau_decayMode and deta_t1t2_req):
    #if (passKinems and t1passDT and t2passDT and good_tau_decayMode and deta_t1t2_req and mvis_req and subtau_req):
    #if (passKinems and t1passDT and t2passDT and good_tau_decayMode and mvis_req):
    if (passKinems and t1passDT and t2passDT and good_tau_decayMode and subtau_req):
    #if True:
      pass_cuts.append(i)
      FS_t1_pt.append(t1_pt)
      FS_t1_eta.append(t1_eta)
      FS_t1_phi.append(t1_phi)
      FS_t1_dxy.append(abs(tau_dxy[tau_idx[l1_idx]]))
      FS_t1_dz.append(abs(tau_dz[tau_idx[l1_idx]]))
      FS_t1_chg.append(t1_chg)
      FS_t1_DM.append(encoded_t1_decayMode)
      FS_t1_mass.append(t1_mass)
      #FS_t1_PNet_v_jet.append(PNetvJet[tau_idx[l1_idx]])
      #FS_t1_PNet_v_mu.append(PNetvMu[tau_idx[l1_idx]])
      #FS_t1_PNet_v_e.append(PNetvE[tau_idx[l1_idx]])
      FS_t1_DeepTau_v_jet.append(vJet[tau_idx[l1_idx]])
      FS_t1_DeepTau_v_mu.append(vMu[tau_idx[l1_idx]])
      FS_t1_DeepTau_v_e.append(vEle[tau_idx[l1_idx]])
      FS_t2_pt.append(t2_pt)
      FS_t2_eta.append(t2_eta)
      FS_t2_phi.append(t2_phi)
      FS_t2_dxy.append(abs(tau_dxy[tau_idx[l2_idx]]))
      FS_t2_dz.append(abs(tau_dz[tau_idx[l2_idx]]))
      FS_t2_chg.append(t2_chg)
      FS_t2_DM.append(encoded_t2_decayMode)
      FS_t2_mass.append(t2_mass)
      #FS_t2_PNet_v_jet.append(PNetvJet[tau_idx[l2_idx]])
      #FS_t2_PNet_v_mu.append(PNetvMu[tau_idx[l2_idx]])
      #FS_t2_PNet_v_e.append(PNetvE[tau_idx[l2_idx]])
      FS_t2_DeepTau_v_jet.append(vJet[tau_idx[l2_idx]])
      FS_t2_DeepTau_v_mu.append(vMu[tau_idx[l2_idx]])
      FS_t2_DeepTau_v_e.append(vEle[tau_idx[l2_idx]])
      FS_trig_idx.append(trig_idx)
      FS_mt_t1t2.append(mt_t1t2)
      FS_mt_t1_MET.append(mt_t1_MET)
      FS_mt_t2_MET.append(mt_t2_MET)
      FS_mt_TOT.append(mt_TOT)
      FS_dphi_t1t2.append(dphi_t1t2)
      FS_deta_t1t2.append(deta_t1t2)

      FS_t1_FLsig.append(t1_FLsig) 
      FS_t1_FLX.append(t1_FLX) 
      FS_t1_FLY.append(t1_FLY)
      FS_t1_FLZ.append(t1_FLZ)
      FS_t1_FLmag.append(t1_FLmag)
      FS_t1_ipLsig.append(t1_ipLsig)
      FS_t1_ip3d.append(t1_ip3d)
      FS_t1_tk_lambda.append(t1_tk_lambda)
      FS_t1_tk_qoverp.append(t1_tk_qoverp)

      FS_t2_FLsig.append(t2_FLsig) 
      FS_t2_FLX.append(t2_FLX) 
      FS_t2_FLY.append(t2_FLY)
      FS_t2_FLZ.append(t2_FLZ)
      FS_t2_FLmag.append(t2_FLmag)
      FS_t2_ipLsig.append(t2_ipLsig)
      FS_t2_ip3d.append(t2_ip3d)
      FS_t2_tk_lambda.append(t2_tk_lambda)
      FS_t2_tk_qoverp.append(t2_tk_qoverp)
      pair_decayMode.append(encoded_pair_decayMode)

  event_dictionary["pass_cuts"] = np.array(pass_cuts)
  event_dictionary["FS_t1_pt"]  = np.array(FS_t1_pt)
  event_dictionary["FS_t1_eta"] = np.array(FS_t1_eta)
  event_dictionary["FS_t1_phi"] = np.array(FS_t1_phi)
  event_dictionary["FS_t1_dxy"] = np.array(FS_t1_dxy)
  event_dictionary["FS_t1_dz"]  = np.array(FS_t1_dz)
  event_dictionary["FS_t1_chg"] = np.array(FS_t1_chg)
  event_dictionary["FS_t1_DM"] = np.array(FS_t1_DM)
  event_dictionary["FS_t1_mass"] = np.array(FS_t1_mass)
  #event_dictionary["FS_t1_rawPNetVSjet"] = np.array(FS_t1_PNet_v_jet)
  #event_dictionary["FS_t1_rawPNetVSmu"]  = np.array(FS_t1_PNet_v_mu)
  #event_dictionary["FS_t1_rawPNetVSe"]   = np.array(FS_t1_PNet_v_e)
  event_dictionary["FS_t1_DeepTauVSjet"] = np.array(FS_t1_DeepTau_v_jet)
  event_dictionary["FS_t1_DeepTauVSmu"]  = np.array(FS_t1_DeepTau_v_mu)
  event_dictionary["FS_t1_DeepTauVSe"]   = np.array(FS_t1_DeepTau_v_e)
  event_dictionary["FS_t2_pt"]  = np.array(FS_t2_pt)
  event_dictionary["FS_t2_eta"] = np.array(FS_t2_eta)
  event_dictionary["FS_t2_phi"] = np.array(FS_t2_phi)
  event_dictionary["FS_t2_dxy"] = np.array(FS_t2_dxy)
  event_dictionary["FS_t2_dz"]  = np.array(FS_t2_dz)
  event_dictionary["FS_t2_chg"] = np.array(FS_t2_chg)
  event_dictionary["FS_t2_DM"] = np.array(FS_t2_DM)
  event_dictionary["FS_t2_mass"] = np.array(FS_t2_mass)
  #event_dictionary["FS_t2_rawPNetVSjet"] = np.array(FS_t2_PNet_v_jet)
  #event_dictionary["FS_t2_rawPNetVSmu"]  = np.array(FS_t2_PNet_v_mu)
  #event_dictionary["FS_t2_rawPNetVSe"]   = np.array(FS_t2_PNet_v_e)
  event_dictionary["FS_t2_DeepTauVSjet"] = np.array(FS_t2_DeepTau_v_jet)
  event_dictionary["FS_t2_DeepTauVSmu"]  = np.array(FS_t2_DeepTau_v_mu)
  event_dictionary["FS_t2_DeepTauVSe"]   = np.array(FS_t2_DeepTau_v_e)
  event_dictionary["FS_trig_idx"]        = np.array(FS_trig_idx)
  event_dictionary["FS_mt_t1t2"]         = np.array(FS_mt_t1t2)
  event_dictionary["FS_mt_t1_MET"]       = np.array(FS_mt_t1_MET)
  event_dictionary["FS_mt_t2_MET"]       = np.array(FS_mt_t2_MET)
  event_dictionary["FS_mt_TOT"]          = np.array(FS_mt_TOT)
  event_dictionary["FS_dphi_t1t2"]       = np.array(FS_dphi_t1t2)
  event_dictionary["FS_deta_t1t2"]       = np.array(FS_deta_t1t2)
  event_dictionary["FS_t1_FLsig"]        = np.array(FS_t1_FLsig)
  event_dictionary["FS_t1_FLX"]          = np.array(FS_t1_FLX)
  event_dictionary["FS_t1_FLY"]          = np.array(FS_t1_FLY)
  event_dictionary["FS_t1_FLZ"]          = np.array(FS_t1_FLZ)
  event_dictionary["FS_t1_FLmag"]        = np.array(FS_t1_FLmag)
  event_dictionary["FS_t1_ipLsig"]       = np.array(FS_t1_ipLsig)
  event_dictionary["FS_t1_ip3d"]         = np.array(FS_t1_ip3d)
  event_dictionary["FS_t1_tk_lambda"]    = np.array(FS_t1_tk_lambda)
  event_dictionary["FS_t1_tk_qoverp"]    = np.array(FS_t1_tk_qoverp)
  event_dictionary["FS_t2_FLsig"]        = np.array(FS_t2_FLsig)
  event_dictionary["FS_t2_FLX"]          = np.array(FS_t2_FLX)
  event_dictionary["FS_t2_FLY"]          = np.array(FS_t2_FLY)
  event_dictionary["FS_t2_FLZ"]          = np.array(FS_t2_FLZ)
  event_dictionary["FS_t2_FLmag"]        = np.array(FS_t2_FLmag)
  event_dictionary["FS_t2_ipLsig"]       = np.array(FS_t2_ipLsig)
  event_dictionary["FS_t2_ip3d"]         = np.array(FS_t2_ip3d)
  event_dictionary["FS_t2_tk_lambda"]    = np.array(FS_t2_tk_lambda)
  event_dictionary["FS_t2_tk_qoverp"]    = np.array(FS_t2_tk_qoverp)
  event_dictionary["FS_pair_DM"]  = np.array(pair_decayMode)

  nEvents_postcut = len(np.array(pass_cuts))
  print(f"nEvents before and after ditau cuts = {nEvents_precut}, {nEvents_postcut}")
  return event_dictionary

def pass_kinems_by_trigger(triggers, t1_pt, t2_pt, t1_eta, t2_eta, 
                           j1_pt, j2_pt, mjj, special_tag, nJet):
  passTrig = False
  passTauKinems = False
  passJetKinems = False
  ditau_trig, ditau_jet_low_trig, ditau_jet_high_trig, ditau_VBFRun2_trig, ditau_VBFRun3_trig = triggers
  # if block intended to be mutually exclusive, allowing least strict reading of cross-triggers
  # DiTau > DiTau + Jet > DiTau + Jet Backup > DiTau VBFRun3 > DiTau VBFRun2
  # 2 taus > 2 taus + 1 jet > 2 tau + 1 jet w higher kinems > 2 taus + 2 jets > 2 taus + 2 jets w higher kinems
  passTrig, passTauKinems, passJetKinems = False, False, False
  pass_ditau = False
  if ditau_trig:
    passTrig = True
    passTauKinems = (t1_pt > 40 and t2_pt > 40 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    passJetKinems = True
    if (passTrig and passTauKinems and passJetKinems): pass_ditau = True
  passTrig, passTauKinems, passJetKinems = False, False, False
  pass_ditau_jet = False
  if (ditau_jet_low_trig or ditau_jet_high_trig) and not (ditau_trig):
  #if (ditau_jet_low_trig or ditau_jet_high_trig):
    passTrig = True
    passTauKinems = (t1_pt > 35 and t2_pt > 35 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    #passJetKinems = (j1_pt > 65)
    passJetKinems = (j1_pt > 65 and j2_pt > 30)
    if (passTrig and passTauKinems and passJetKinems): pass_ditau_jet = True
  passTrig, passTauKinems, passJetKinems = False, False, False
  pass_ditau_VBFRun3 = False
  if (ditau_VBFRun3_trig) and not (ditau_trig or ditau_jet_low_trig or ditau_jet_high_trig):
  #if (ditau_VBFRun3_trig):
    passTrig = True
    passTauKinems = (t1_pt > 50 and t2_pt > 25 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    passJetKinems = (j1_pt > 45 and j2_pt > 45 and mjj > 600)
    if (passTrig and passTauKinems and passJetKinems): pass_ditau_VBFRun3 = True
  passTrig, passTauKinems, passJetKinems = False, False, False
  pass_ditau_VBFRun2 = False
  if (ditau_VBFRun2_trig) and not (ditau_trig or ditau_jet_low_trig or ditau_jet_high_trig or ditau_VBFRun3_trig):
    passTrig = True
    passTauKinems = (t1_pt > 25 and t2_pt > 25 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    passJetKinems = (j1_pt > 115 and j2_pt > 40 and mjj > 670) or (special_tag == True)
    # This trigger checks that there is a dijet pair w mass above 700, two jets with pT > 40, and one jet w pT > 120
    # This results in a 2jet case and a 3jet case, hence the special tag :)
    if (passTrig and passTauKinems and passJetKinems): pass_ditau_VBFRun2 = True

  #return [pass_ditau, False, False, False] # test removing all cross-triggers
  #return [pass_ditau, pass_ditau_jet, False, False] # test removing VBF trigger decisions
  return [pass_ditau, pass_ditau_jet, pass_ditau_VBFRun3, False] # test removing VBF Run2 trigger decision
  #return [pass_ditau, False, pass_ditau_VBFRun3, False] # test removing ditau+jet and VBF Run2
  #return [pass_ditau, False, pass_ditau_VBFRun3, pass_ditau_VBFRun2] # test removing ditau+jet
  #return [pass_ditau, False, False, pass_ditau_VBFRun2] # test using only VBFRun2
  #return [pass_ditau, pass_ditau_jet, pass_ditau_VBFRun3, pass_ditau_VBFRun2]

'''
def pass_kinems_by_trigger(triggers, t1_pt, t2_pt, t1_eta, t2_eta, 
                           j1_pt, j2_pt, mjj, special_tag, nJet):
  #Helper function to apply different object kinematic criteria depending on trigger used
  ditau_trig, ditau_jet_low_trig, ditau_jet_high_trig, ditau_VBFRun2_trig, ditau_VBFRun3_trig = triggers
  # if block intended to be mutually exclusive, allowing least strict reading of cross-triggers
  # DiTau > DiTau + Jet > DiTau + Jet Backup > DiTau VBFRun3 > DiTau VBFRun2
  # 2 taus > 2 taus + 1 jet > 2 tau + 1 jet w higher kinems > 2 taus + 2 jets > 2 taus + 2 jets w higher kinems
  passTrig, passTauKinems, passEventJetKinems = False, False, False

  if (nJet == 0): 
  #  print("nJet = 0")
    passEventJetKinems = True # no jet requirements in nJet=0 category
  elif (nJet == 1):
    passEventJetKinems = (j1_pt > 30.)
  else: # nJet >= 2
  #  print("nJet > 1")
    passEventJetKinems = ((j1_pt > 30.) and (j2_pt > 30.))

  pass_ditau = False
  if ditau_trig:
    passTrig = True
    passTauKinems = (t1_pt > 40 and t2_pt > 40 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    if (passTrig and passTauKinems and passEventJetKinems): pass_ditau = True
  passTrig, passTauKinems = False, False
  pass_ditau_jet = False
  if (ditau_jet_low_trig or ditau_jet_high_trig) and not (ditau_trig):
    passTrig = True
    passTauKinems = (t1_pt > 35 and t2_pt > 35 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    passTrigJetKinems = ((passEventJetKinems) and (j1_pt > 65))
    if (passTrig and passTauKinems and passTrigJetKinems): pass_ditau_jet = True
  passTrig, passTauKinems, passTrigJetKinems = False, False, False
  pass_ditau_VBFRun3 = False
  if (ditau_VBFRun3_trig) and not (ditau_trig or ditau_jet_low_trig or ditau_jet_high_trig):
    passTrig = True
    passTauKinems = (t1_pt > 50 and t2_pt > 25 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    passTrigJetKinems = ((passEventJetKinems) and (j1_pt > 45 and j2_pt > 45 and mjj > 600))
    if (passTrig and passTauKinems and passTrigJetKinems): pass_ditau_VBFRun3 = True
  passTrig, passTauKinems, passTrigJetKinems = False, False, False
  pass_ditau_VBFRun2 = False
  if (ditau_VBFRun2_trig) and not (ditau_trig or ditau_jet_low_trig or ditau_jet_high_trig or ditau_VBFRun3_trig):
    passTrig = True
    passTauKinems = (t1_pt > 25 and t2_pt > 25 and abs(t1_eta) < 2.1 and abs(t2_eta) < 2.1)
    passTrigJetKinems = ((passEventJetKinems) and ((j1_pt > 115 and j2_pt > 40 and mjj > 670) or (special_tag == True)))
    # This trigger checks that there is a dijet pair w mass above 670, two jets with pT > 40, and one jet w pT > 115
    # This results in a 2jet case and a 3jet case, hence the special tag :)
    if (passTrig and passTauKinems and passTrigJetKinems): pass_ditau_VBFRun2 = True

  #return [pass_ditau, False, False, False] # old nominal
  return [pass_ditau, pass_ditau_jet, pass_ditau_VBFRun3, False] # new nominal
  #return [pass_ditau, pass_ditau_jet, False, False] # test removing VBF trigger decisions
  #return [pass_ditau, False, pass_ditau_VBFRun3, False] # test removing ditau+jet and VBF Run2
  #return [pass_ditau, False, pass_ditau_VBFRun3, pass_ditau_VBFRun2] # test removing ditau+jet
  #return [pass_ditau, False, False, pass_ditau_VBFRun2] # test using only VBFRun2
  #return [pass_ditau, pass_ditau_jet, pass_ditau_VBFRun3, pass_ditau_VBFRun2]
'''

def make_ditau_region(event_dictionary, new_branch_name, FS_pair_sign,
                      pass_DeepTau_t1_req, DeepTau_t1_value,
                      pass_DeepTau_t2_req, DeepTau_t2_value, DeepTau_version):
  unpack_ditau_vars = ["Lepton_tauIdx", "l1_indices", "l2_indices", "HTT_pdgId"]
  unpack_ditau_vars = add_DeepTau_branches(unpack_ditau_vars, DeepTau_version)
  unpack_ditau_vars = (event_dictionary.get(key) for key in unpack_ditau_vars)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_ditau_vars]
  pass_cuts = []
  for i, tau_idx, l1_idx, l2_idx, signed_pdgId, vJet, _, _ in zip(*to_check):

    pass_DeepTau_t1_minimum = (vJet[tau_idx[l1_idx]] >= 1) # 1 is VVVLoose (AN 109, 2p1DeepTau), 2 is VVLoose
    pass_DeepTau_t2_minimum = (vJet[tau_idx[l2_idx]] >= 1)
    pass_DeepTau_t1 = (vJet[tau_idx[l1_idx]] >= DeepTau_t1_value)
    pass_DeepTau_t2 = (vJet[tau_idx[l2_idx]] >= DeepTau_t2_value)

    if ( (np.sign(signed_pdgId) == FS_pair_sign) and
         ((pass_DeepTau_t1_req == "None") or (pass_DeepTau_t2_req == "None")) ):
      pass_cuts.append(i)
    elif ( (np.sign(signed_pdgId) == FS_pair_sign) and 
         (pass_DeepTau_t1_minimum) and (pass_DeepTau_t2_minimum) and
         (pass_DeepTau_t1 == pass_DeepTau_t1_req) and (pass_DeepTau_t2 == pass_DeepTau_t2_req) ):
      pass_cuts.append(i)
    else: pass
  
  event_dictionary[new_branch_name] = np.array(pass_cuts)
  return event_dictionary


