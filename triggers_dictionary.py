### README
# This is a mapping of final_state_mode to HLT triggers included in branches "Trigger_[final_state_mode]"
# Very similar in design to "TriggerList.py" in NanoTauAnalysis.

triggers_dictionary = {
  "ditau" : [
             "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1",
             "HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60",
             "HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75",
             "HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1",
             "HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1",
          ],
          #   "HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1", # Run2, only for Era F study
          #   "HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1",  # Run2, only for Era F study
  "mutau" : [
             "HLT_IsoMu24", 
             "HLT_IsoMu27",
             "HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1", 
          ],
             #"HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1", # Run2, only for Era F study
  "mutau_TnP" : [
             "HLT_IsoMu24", 
             "HLT_IsoMu27",
             "HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1", 
          ],
  "etau"  : [
             "HLT_Ele30_WPTight_Gsf",
             "HLT_Ele32_WPTight_Gsf",
             "HLT_Ele35_WPTight_Gsf",
             "HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1",
          ],
  "dimuon": [
             "HLT_IsoMu24",
             "HLT_IsoMu27",
          ],

  "emu"  : [
             "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
             "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", #Naila Added
          ],
}


def study_triggers():
  '''
  Template function for returning ORs/ANDs of HLT triggers in an organized way.
  Will be extended at an opportune moment.
  '''
  Run2OR, Run2AND, Run3OR, Run3AND = 0, 0, 0, 0

  mutau_triggers = [data_events[trigger] for trigger in add_trigger_branches([], "mutau")]
  for HLT_single1, HLT_single2, HLT_crossRun2, HLT_crossRun3 in zip(*mutau_triggers):
    if HLT_single1 or HLT_single2 or HLT_crossRun2:
      Run2OR  += 1
    if HLT_single1 or HLT_single2 or HLT_crossRun3:
      Run3OR  += 1
    if (HLT_single1 or HLT_single2) and HLT_crossRun2:
      Run2AND += 1
    if (HLT_single1 or HLT_single2) and HLT_crossRun3:
      Run3AND += 1
 
  print(f"Run2 OR/AND: {Run2OR}\t{Run2AND}")
  print(f"Run3 OR/AND: {Run3OR}\t{Run3AND}")


def Era_F_trigger_study(data_events, final_state_mode):
  '''
  Compact function for 2022 era F trigger study, where ChargedIsoTau
  triggers were briefly enabled for Run2-Run3 Tau trigger studies. 
  '''
  from triggers_dictionary import triggers_dictionary
  FS_triggers = triggers_dictionary[final_state_mode]
  for trigger in FS_triggers:
    print(f" {trigger} has {np.sum(data_events[trigger])} events")

  good_runs = [361971, 361989, 361990, 361994, 362058, 362059, 362060, 
               362061, 362062, 362063, 362064, 362087, 362091, 362104, 
               362105, 362106, 362107, 362148, 362153, 362154, 362159, 
               362161, 362163, 362166, 362167]
  data_events = make_run_cut(data_events, good_runs)
  data_events = apply_cut(data_events, "pass_run_cut") # will break if used

  print("after reducing run range")
  for trigger in FS_triggers:
    print(f" {trigger} has {np.sum(data_events[trigger])} events")
  
  return data_events


