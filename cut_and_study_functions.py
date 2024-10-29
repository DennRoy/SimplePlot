import numpy as np

### README
# this file contains functions to perform cuts and self-contained studies

from calculate_functions  import highest_mjj_pair, return_TLorentz_Jets
from utility_functions    import text_options, log_print

from cut_ditau_functions  import make_ditau_cut 
from cut_mutau_functions  import make_mutau_cut, make_mutau_TnP_cut
from cut_etau_functions   import make_etau_cut
from cut_dimuon_functions import make_dimuon_cut, manual_dimuon_lepton_veto
from cut_emu_functions   import make_emu_cut
 
from FF_functions         import make_ditau_SR_cut, make_mutau_SR_cut, make_etau_SR_cut, make_emu_SR_cut
from FF_functions         import make_ditau_AR_cut, make_mutau_AR_cut, make_etau_AR_cut, make_emu_AR_cut
from FF_functions         import add_FF_weights, apply_FF_weight_from_branch

from file_functions       import load_and_store_NWEvents, customize_DY
from plotting_functions   import final_state_vars, clean_jet_vars

def append_lepton_indices(event_dictionary):
  '''
  Read the entries of "FSLeptons" and extract the values to place in separate branches.
  It was easier to do this once when the data is first loaded than to do it every time
  that it is needed. 
  '''
  FSLeptons = event_dictionary["FSLeptons"]
  l1_indices, l2_indices = [], []
  for event in FSLeptons:
    if len(event)>2: print(f"More than one FS pair: {event}")
    l1_indices.append(event[0])
    l2_indices.append(event[1])
  event_dictionary["l1_indices"] = np.array(l1_indices)
  event_dictionary["l2_indices"] = np.array(l2_indices)
  return event_dictionary


def append_flavor_indices(event_dictionary, final_state_mode, keep_fakes=False):
  unpack_flav = ["l1_indices", "l2_indices", "Lepton_tauIdx", "Tau_genPartFlav"]
  unpack_flav = (event_dictionary.get(key) for key in unpack_flav)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_flav]
  FS_t1_flav, FS_t2_flav = [], []
  pass_gen_cuts, event_flavor = [], []
  for i, l1_idx, l2_idx, tau_idx, tau_flav in zip(*to_check):
    genuine, lep_fake, jet_fake = False, False, False
    t1_flav = -1
    t2_flav = -1
    if final_state_mode == "ditau":
      t1_flav = tau_flav[tau_idx[l1_idx]]
      t2_flav = tau_flav[tau_idx[l2_idx]]
      if (t1_flav == 5) and (t2_flav == 5):
        # genuine tau --> both taus are taus at gen level
        genuine = True
        event_flavor.append("G")
      elif (t1_flav == 0) or (t2_flav == 0):
        # jet fake --> one tau is faked by jet
        jet_fake = True
        event_flavor.append("J")
      elif (t1_flav < 5 and t1_flav > 0) or (t2_flav < 5 and t1_flav > 0):
        # lep fake --> both taus are faked by lepton
        # event with one tau faking jet enters category above first due to ordering
        # implies also the case where both are faked but one is faked by lepton 
        # is added to jet fakes, which i think is fine
        lep_fake = True
        event_flavor.append("L")
    elif ((final_state_mode == "mutau") or (final_state_mode == "etau") or (final_state_mode == "mutau_TnP")):
      t1_flav = tau_flav[tau_idx[l1_idx] + tau_idx[l2_idx] + 1] # update with NanoAODv12 samples
      if (t1_flav == 5):
        genuine = True
        event_flavor.append("G")
      elif (t1_flav == 0):
        jet_fake = True
        event_flavor.append("J")
      elif (t1_flav < 5 and t1_flav > 0):
        lep_fake = True
        event_flavor.append("L")

    else:
      print(f"No gen matching for that final state ({final_state_mode}), no branches appended")
      return event_dictionary
  
    if (keep_fakes==False) and ((genuine) or (lep_fake)):
      # save genuine background events and lep_fakes, remove jet fakes with gen matching
      # used in all categories because fakes are estimated with FF method
      FS_t1_flav.append(t1_flav)
      FS_t2_flav.append(t2_flav)
      pass_gen_cuts.append(i)

    if (keep_fakes==True) and ((genuine) or (lep_fake) or (jet_fake)):
      # save all events and their flavors, even if they are jet fakes
      # used to split DY to genuine, lep fakes, and jet fakes in all categories
      FS_t1_flav.append(t1_flav)
      FS_t2_flav.append(t2_flav)
      pass_gen_cuts.append(i)
      
  event_dictionary["FS_t1_flav"] = np.array(FS_t1_flav)
  event_dictionary["FS_t2_flav"] = np.array(FS_t2_flav)
  event_dictionary["pass_gen_cuts"] = np.array(pass_gen_cuts)
  event_dictionary["event_flavor"]  = np.array(event_flavor)
  return event_dictionary


def make_jet_cut(event_dictionary, jet_mode):
  nEvents_precut = len(event_dictionary["Lepton_pt"])
  unpack_jetVars = ["nCleanJet", "CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "CleanJet_mass"]
  unpack_jetVars = (event_dictionary.get(key) for key in unpack_jetVars)
  to_check = [range(len(event_dictionary["Lepton_pt"])), *unpack_jetVars] # "*" unpacks a tuple
  nCleanJetGT30, pass_0j_cuts, pass_1j_cuts, pass_2j_cuts, pass_3j_cuts = [], [], [], [], []
  pass_GTE1j_cuts, pass_GTE2j_cuts = [], []
  CleanJetGT30_pt_1, CleanJetGT30_pt_2, CleanJetGT30_pt_3    = [], [], []
  CleanJetGT30_eta_1, CleanJetGT30_eta_2, CleanJetGT30_eta_3 = [], [], []
  CleanJetGT30_phi_1, CleanJetGT30_phi_2, CleanJetGT30_phi_3 = [], [], []
  mjj_array, detajj_array = [], []
  from ROOT import TLorentzVector 
  # TODO : this is the only place ROOT is used, removing it would speed things up
  for i, nJet, jet_pt, jet_eta, jet_phi, jet_mass in zip(*to_check):
    passingJets = 0
    passingJetsPt, passingJetsEta, passingJetsPhi, passingJetsMass = [], [], [], []
    for ijet in range(0, nJet):
      if (jet_pt[ijet] > 30.0) and (jet_eta[ijet] < 4.7):
        passingJets += 1
        passingJetsPt.append(jet_pt[ijet])
        passingJetsEta.append(jet_eta[ijet])
        passingJetsPhi.append(jet_phi[ijet])
        passingJetsMass.append(jet_mass[ijet])
    nCleanJetGT30.append(passingJets)

    if passingJets == 0: 
      pass_0j_cuts.append(i)

    if (passingJets == 1) and (jet_mode == "Inclusive" or jet_mode == "1j"): 
      pass_1j_cuts.append(i)
      CleanJetGT30_pt_1.append(passingJetsPt[0])
      CleanJetGT30_eta_1.append(passingJetsEta[0])
      CleanJetGT30_phi_1.append(passingJetsPhi[0])

    if (passingJets == 2) and (jet_mode == "Inclusive" or jet_mode == "2j"):
      pass_2j_cuts.append(i)
      TLorentzJets, j1_idx, j2_idx, mjj, ST = return_TLorentz_Jets(passingJetsPt, passingJetsEta, passingJetsPhi, passingJetsMass)
      j1_TVec, j2_TVec = TLorentzJets[j1_idx], TLorentzJets[j2_idx]
      CleanJetGT30_pt_1.append(passingJetsPt[j1_idx])
      CleanJetGT30_pt_2.append(passingJetsPt[j2_idx])
      CleanJetGT30_eta_1.append(passingJetsEta[j1_idx])
      CleanJetGT30_eta_2.append(passingJetsEta[j2_idx])
      CleanJetGT30_phi_1.append(passingJetsPhi[j1_idx])
      CleanJetGT30_phi_2.append(passingJetsPhi[j2_idx])
      mjj_array.append(mjj)
      #mjj_array.append((j1_TVec + j2_TVec).M())
      # TODO can try to make the comparison here
      detajj_array.append(abs(j1_TVec.Eta() - j2_TVec.Eta()))

    if (passingJets >= 2) and (jet_mode == "GTE2j"): 
      pass_GTE2j_cuts.append(i)
      TLorentzJets, j1_idx, j2_idx, mjj, ST = return_TLorentz_Jets(passingJetsPt, passingJetsEta, passingJetsPhi, passingJetsMass)
      j1_TVec, j2_TVec = TLorentzJets[j1_idx], TLorentzJets[j2_idx]
      CleanJetGT30_pt_1.append(passingJetsPt[j1_idx])
      CleanJetGT30_pt_2.append(passingJetsPt[j2_idx])
      CleanJetGT30_eta_1.append(passingJetsEta[j1_idx])
      CleanJetGT30_eta_2.append(passingJetsEta[j2_idx])
      CleanJetGT30_phi_1.append(passingJetsPhi[j1_idx])
      CleanJetGT30_phi_2.append(passingJetsPhi[j2_idx])
      mjj_array.append(mjj)
      #mjj_array.append((j1_TVec+j2_TVec).M())
      detajj_array.append(abs(j1_TVec.Eta()-j2_TVec.Eta()))

    if (passingJets >= 1) and (jet_mode == "GTE1j"): 
      pass_GTE1j_cuts.append(i)
      if (passingJets >= 2):
        TLorentzJets, j1_idx, j2_idx, mjj, ST = return_TLorentz_Jets(passingJetsPt, passingJetsEta, passingJetsPhi, passingJetsMass)
        j1_TVec, j2_TVec = TLorentzJets[j1_idx], TLorentzJets[j2_idx]
        CleanJetGT30_pt_1.append(passingJetsPt[j1_idx])
        CleanJetGT30_pt_2.append(passingJetsPt[j2_idx])
        CleanJetGT30_eta_1.append(passingJetsEta[j1_idx])
        CleanJetGT30_eta_2.append(passingJetsEta[j2_idx])
        CleanJetGT30_phi_1.append(passingJetsPhi[j1_idx])
        CleanJetGT30_phi_2.append(passingJetsPhi[j2_idx])
        mjj_array.append(mjj)
        #mjj_array.append((j1_TVec+j2_TVec).M())
        detajj_array.append(abs(j1_TVec.Eta()-j2_TVec.Eta()))
      else:
        CleanJetGT30_pt_1.append(passingJetsPt[0])
        CleanJetGT30_eta_1.append(passingJetsEta[0])
        CleanJetGT30_phi_1.append(passingJetsPhi[0])
        CleanJetGT30_pt_2.append(-1)
        CleanJetGT30_eta_2.append(-1)
        CleanJetGT30_phi_2.append(-1)
        mjj_array.append(-1)
        detajj_array.append(-1)

  event_dictionary["nCleanJetGT30"]   = np.array(nCleanJetGT30)

  if jet_mode == "pass":
    print("debug jet mode, only filling nCleanJetGT30")

  elif jet_mode == "Inclusive":
    pass
 
  # there is certainly a better way to do this 
  elif jet_mode == "0j":
    # literally don't do any of the above
    event_dictionary["pass_0j_cuts"]    = np.array(pass_0j_cuts)

  elif jet_mode == "1j":
    # only do the 1j things
    event_dictionary["pass_1j_cuts"]    = np.array(pass_1j_cuts)
    event_dictionary["CleanJetGT30_pt_1"]  = np.array(CleanJetGT30_pt_1)
    event_dictionary["CleanJetGT30_eta_1"] = np.array(CleanJetGT30_eta_1)
    event_dictionary["CleanJetGT30_phi_1"] = np.array(CleanJetGT30_phi_1)

  elif jet_mode == "2j":
    # only do the 2j things
    event_dictionary["pass_2j_cuts"]    = np.array(pass_2j_cuts)
    event_dictionary["CleanJetGT30_pt_1"]  = np.array(CleanJetGT30_pt_1)
    event_dictionary["CleanJetGT30_phi_1"] = np.array(CleanJetGT30_phi_1)
    event_dictionary["CleanJetGT30_eta_1"] = np.array(CleanJetGT30_eta_1)
    event_dictionary["CleanJetGT30_pt_2"]  = np.array(CleanJetGT30_pt_2)
    event_dictionary["CleanJetGT30_eta_2"] = np.array(CleanJetGT30_eta_2)
    event_dictionary["CleanJetGT30_phi_2"] = np.array(CleanJetGT30_phi_2)
    event_dictionary["FS_mjj"] = np.array(mjj_array)
    event_dictionary["FS_detajj"] = np.array(detajj_array)

  elif jet_mode == "3j" or jet_mode == "GTE2j":
    # importantly different from inclusive
    #event_dictionary["pass_3j_cuts"]    = np.array(pass_3j_cuts)
    event_dictionary["pass_GTE2j_cuts"]    = np.array(pass_GTE2j_cuts)
    event_dictionary["CleanJetGT30_pt_1"]  = np.array(CleanJetGT30_pt_1)
    event_dictionary["CleanJetGT30_pt_2"]  = np.array(CleanJetGT30_pt_2)
    #event_dictionary["CleanJetGT30_pt_3"]  = np.array(CleanJetGT30_pt_3)
    event_dictionary["CleanJetGT30_eta_1"] = np.array(CleanJetGT30_eta_1)
    event_dictionary["CleanJetGT30_eta_2"] = np.array(CleanJetGT30_eta_2)
    #event_dictionary["CleanJetGT30_eta_3"] = np.array(CleanJetGT30_eta_3)
    event_dictionary["CleanJetGT30_phi_1"] = np.array(CleanJetGT30_phi_1)
    event_dictionary["CleanJetGT30_phi_2"] = np.array(CleanJetGT30_phi_2)
    #event_dictionary["CleanJetGT30_phi_3"] = np.array(CleanJetGT30_phi_3)
    event_dictionary["FS_mjj"] = np.array(mjj_array)
    event_dictionary["FS_detajj"] = np.array(detajj_array)

  elif jet_mode == "GTE1j":
    event_dictionary["pass_GTE1j_cuts"]    = np.array(pass_GTE1j_cuts)
    event_dictionary["CleanJetGT30_pt_1"]  = np.array(CleanJetGT30_pt_1)
    event_dictionary["CleanJetGT30_pt_2"]  = np.array(CleanJetGT30_pt_2)
    event_dictionary["CleanJetGT30_eta_1"] = np.array(CleanJetGT30_eta_1)
    event_dictionary["CleanJetGT30_eta_2"] = np.array(CleanJetGT30_eta_2)
    event_dictionary["CleanJetGT30_phi_1"] = np.array(CleanJetGT30_phi_1)
    event_dictionary["CleanJetGT30_phi_2"] = np.array(CleanJetGT30_phi_2)
    event_dictionary["FS_mjj"] = np.array(mjj_array)
    event_dictionary["FS_detajj"] = np.array(detajj_array)

  return event_dictionary


def apply_cut(event_dictionary, cut_branch, protected_branches=[]):
  DEBUG = False # set this to true to show print output from this function
  '''
  Remove all entries in 'event_dictionary' not in 'cut_branch' using the numpy 'take' method.
  Branches that are added during previous cut steps are added here because their entries
  already pass cuts by construction.
  The returned event_dictionary now only contains events passing all cuts.

  If all events are removed by cut, print a message to alert the user.
  The deletion is actually handled in the main body when the size of the dictionary is checked.
  '''
  delete_sample = False
  if len(event_dictionary[cut_branch]) == 0:
    print(text_options["red"] + "ALL EVENTS REMOVED! SAMPLE WILL BE DELETED! " + text_options["reset"])
    delete_sample = True
    return None
 
  #if ("cut" in cut_branch):
  #  nEvents_precut  = len(event_dictionary["Lepton_pt"])
  #  nEvents_postcut = len(event_dictionary[cut_branch])
  #  log_print(f"nEvents before and after selection cut = {nEvents_precut}, {nEvents_postcut}", open('outputfile.log', 'w'))

  if DEBUG: print(f"cut branch: {cut_branch}")
  if DEBUG: print(f"protected branches: {protected_branches}")
  for branch in event_dictionary:
    if delete_sample:
      pass

    # special handling, will need to be adjusted by hand for excatly 2j or 3j studies # DEBUG
    # this only works for GTE2j, not Inclusive because the "apply_cut" method for jets is never called there # DEBUG
    if (("pass_GTE2j_cuts" in event_dictionary) and
        (branch == "HTT_DiJet_dEta_fromHighestMjj" or branch == "HTT_DiJet_MassInv_fromHighestMjj")):
      #print("very special GTE2j handling underway") # DEBUG
      event_dictionary[branch] = np.take(event_dictionary[branch], event_dictionary["pass_GTE2j_cuts"])
      #if (branch == "CleanJetGT30_pt_3" or branch == "CleanJetGT30_eta_3"):
      #  event_dictionary[branch] = np.take(event_dictionary[branch], event_dictionary["pass_3j_cuts"])

    elif ((branch != cut_branch) and (branch not in protected_branches)):
      if DEBUG: print(f"going to cut {branch}, {len(event_dictionary[branch])}")
      event_dictionary[branch] = np.take(event_dictionary[branch], event_dictionary[cut_branch])

  return event_dictionary


def make_run_cut(event_dictionary, good_runs):
  '''
  Given a set of runs, create a branch of events belonging to that set.
  The branch is later used to reject all other events.
  '''
  good_runs = np.sort(good_runs)
  first_run, last_run = good_runs[0], good_runs[-1]
  print(f"first run {first_run}, last run {last_run}")
  # check if it's within the range, then check if it's in the list
  pass_run_cut = []
  for i, run in enumerate(event_dictionary["run"]):
    if first_run <= run <= last_run:
      if run in good_runs:
        pass_run_cut.append(i) 

  event_dictionary["pass_run_cut"] = np.array(pass_run_cut)
  return event_dictionary


def apply_final_state_cut(event_dictionary, final_state_mode, DeepTau_version, useMiniIso=False):
  '''
  Organizational function that generalizes call to a (set of) cuts based on the
  final cut. Importantly, the function that rejects events, 'apply_cut',
  is called elsewhere
  '''
  # setting inclusive in the jet_mode includes all jet branches in protected branches
  # this is okay because in the current ordering (FS cut then jet cut), no jet branches are ever created yet.
  #if (final_state_mode == "mutau_TnP"):
  #  protected_branches = set_protected_branches(final_state_mode="mutau_TnP", jet_mode="Inclusive")
  #else:
  protected_branches = set_protected_branches(final_state_mode=final_state_mode, jet_mode="Inclusive")
  if final_state_mode == "ditau":
    event_dictionary = make_ditau_SR_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_SR_cuts", protected_branches)
    if (event_dictionary == None): return event_dictionary
    event_dictionary = make_ditau_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)
  elif final_state_mode == "mutau":
    event_dictionary = make_mutau_SR_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_SR_cuts", protected_branches)
    if (event_dictionary == None): return event_dictionary
    event_dictionary = make_mutau_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)
  elif final_state_mode == "mutau_TnP": # special mode for Tau TRG studies
    event_dictionary = make_mutau_SR_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_SR_cuts", protected_branches)
    if (event_dictionary == None): return event_dictionary
    event_dictionary = make_mutau_TnP_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)
  elif final_state_mode == "etau":
    event_dictionary = make_etau_SR_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_SR_cuts", protected_branches)
    if (event_dictionary == None): return event_dictionary
    event_dictionary = make_etau_cut(event_dictionary, DeepTau_version)
    event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)
  elif final_state_mode == "dimuon":
    # old samples need manual lepton veto
    if (useMiniIso == False):
      event_dictionary = manual_dimuon_lepton_veto(event_dictionary)
      event_dictionary = apply_cut(event_dictionary, "pass_manual_lepton_veto")
      event_dictionary = make_dimuon_cut(event_dictionary)
      event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)
    # new samples don't and they use a different iso
    if (useMiniIso == True):
      event_dictionary = make_dimuon_cut(event_dictionary, useMiniIso==True)
      event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)

  elif final_state_mode == "emu":
    event_dictionary = make_emu_SR_cut(event_dictionary)
    event_dictionary = apply_cut(event_dictionary, "pass_SR_cuts", protected_branches)
    if (event_dictionary == None): return event_dictionary
    event_dictionary = make_emu_cut(event_dictionary)
    event_dictionary = apply_cut(event_dictionary, "pass_cuts", protected_branches)
  else:
    print(f"No cuts to apply for {final_state_mode} final state.")
  return event_dictionary


def apply_flavor_cut(event_dictionary):
  # get list of event indices with events matching flavor key
  event_flavor_array = event_dictionary["Cuts"]["event_flavor"]
  # cut out other events
  event_dictionary = apply_cut(event_dictionary, "pass_flav_cut") # no protected branches
  return event_dictionary


def apply_jet_cut(event_dictionary, jet_mode):
  '''
  Organizational function to reduce event_dictionary to contain only
  events with jets passing certain criteria. Enables plotting of jet objects
  jet_mode can be "Inclusive", "0j", "1j", "2j", "3j", "GTE2j",
  '''
  jet_cut_branch = {
    "Inclusive" : "Inclusive",
    "pass"      : "Inclusive", #DEBUG
    "0j" : "pass_0j_cuts",
    "1j" : "pass_1j_cuts",
    "2j" : "pass_2j_cuts",
    "3j" : "pass_3j_cuts",
    "GTE1j" : "pass_GTE1j_cuts",
    "GTE2j" : "pass_GTE2j_cuts",
  }
  event_dictionary   = make_jet_cut(event_dictionary, jet_mode)
  protected_branches = set_protected_branches(final_state_mode="none", jet_mode=jet_mode)
  if jet_mode == "Inclusive" or jet_mode == "pass":
    print("jet mode is Inclusive, no jet cut performed")
  else:
    event_dictionary = apply_cut(event_dictionary, jet_cut_branch[jet_mode], protected_branches)
  return event_dictionary


def apply_HTT_FS_cuts_to_process(process, process_dictionary, log_file,
                                 final_state_mode, jet_mode="Inclusive", 
                                 DeepTau_version="2p5", useMiniIso=False):
  '''
  Organizational function to hold two function calls and empty list handling that
  is performed for all loaded datasets in our framework.
  Can be extended to hold additional standard cuts (i.e. jets) or the returned
  value can be cut on as needed.
  '''
  log_print(f"Processing {process}", log_file)
  process_events = process_dictionary[process]["info"]
  if len(process_events["run"])==0: 
    print(f"Uh oh, no events in sample.")
    return None

  process_events = append_lepton_indices(process_events)
  protected_branches = ["FS_t1_flav", "FS_t2_flav", "pass_gen_cuts", "event_flavor"]

  if ("Data" not in process) and (final_state_mode != "dimuon"):
    if ("TTToSemiLeptonic" in process): process = "TTToSemiLeptonic"
    load_and_store_NWEvents(process, process_events)
    if ("DY" in process): 
      customize_DY(process, final_state_mode)
      #append_Zpt_weight(process_events)
    keep_fakes = False
    #keep_fakes = True # TODO : fix this block
    #'''
    if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and ("mutau" in final_state_mode)):
      # when FF method is finished/improved no longer need to keep TT and WJ fakes
      keep_fakes = True
    if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and ("etau" in final_state_mode)):
      # when FF method is finished/improved no longer need to keep TT and WJ fakes
      keep_fakes = True
    #if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and ("ditau" in final_state_mode)):
    if ( (("DY" in process) or ("QCD" in process)) and (final_state_mode=="ditau")):
      keep_fakes = True
    if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and ("emu" in final_state_mode)):
      # when FF method is finished/improved no longer need to keep TT and WJ fakes
      keep_fakes = True
    
    #Uncomment for etau and mutau and ditau
    process_events = append_flavor_indices(process_events, final_state_mode, keep_fakes=keep_fakes)
    process_events = apply_cut(process_events, "pass_gen_cuts", protected_branches=protected_branches)
    if (process_events==None or len(process_events["run"])==0): return None

  FS_cut_events = apply_final_state_cut(process_events, final_state_mode, DeepTau_version, useMiniIso=useMiniIso)
  if (FS_cut_events==None or len(FS_cut_events["run"])==0): return None 
  cut_events = apply_jet_cut(FS_cut_events, jet_mode)
  if (cut_events==None or len(cut_events["run"])==0): return None

  # TODO : want to move to this
  # re TODO actually want to move to a splitting/copying paradigm instead of modification in place
  #jet_cut_events = apply_jet_cut(process_events, jet_mode)
  #if len(jet_cut_events["run"])==0: return None
  #FS_cut_events = apply_final_state_cut(jet_cut_events, final_state_mode, DeepTau_version, useMiniIso=useMiniIso)
  #if len(FS_cut_events["run"])==0: return None  

  return FS_cut_events

# TODO fix this function and make it more straightforward
# way too easy to get confused with it currently
def set_protected_branches(final_state_mode, jet_mode, DeepTau_version="none"):
  '''
  Set branches to be protected (i.e. not cut on) when using "apply_cut."
  Generally, you should protect any branches introduced by a cut.

  protect all "FS" branches for FS cuts
  protect all "pass_xj_cuts" and "JetGT30_" branches for jet cuts
  '''

  if final_state_mode != "none": # not cutting FS branches
    protected_branches = final_state_vars[final_state_mode]
    # all "HTT_" branches automatically handled, just protecting "FS_" branches which were introduced by a cut
  
  elif final_state_mode == "none":
    if jet_mode == "Inclusive" or jet_mode=="pass": # cutting FS branches, but not the jet branches
      jet_mode = "Inclusive"
      protected_branches = ["pass_0j_cuts", "pass_1j_cuts", "pass_2j_cuts", "pass_3j_cuts", "pass_GTE2j_cuts"]
      # should fromHighestMjj branches be protected? it seems not
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

    elif jet_mode == "0j": # cutting FS branches, protecting just one jet branch
      protected_branches = ["pass_0j_cuts"]
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

    elif jet_mode == "1j":
      protected_branches = ["pass_0j_cuts", "pass_1j_cuts"]
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

    elif jet_mode == "2j":
      protected_branches = ["pass_0j_cuts", "pass_1j_cuts", "pass_2j_cuts"]
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

    elif jet_mode == "3j":
      protected_branches = ["pass_0j_cuts", "pass_1j_cuts", "pass_2j_cuts", "pass_3j_cuts"]
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

    elif jet_mode == "GTE1j":
      protected_branches = ["pass_0j_cuts", "pass_1j_cuts", "pass_2j_cuts", "pass_3j_cuts", "pass_GTE2j_cuts"]
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

    elif jet_mode == "GTE2j":
      protected_branches = ["pass_0j_cuts", "pass_1j_cuts", "pass_2j_cuts", "pass_3j_cuts", "pass_GTE2j_cuts"]
      protected_branches += clean_jet_vars[jet_mode]
      protected_branches = [var for var in protected_branches if var != "nCleanJetGT30"] # unprotect one branch

  else:
    print("final state mode must be specified as 'none' or a valid final state to properly protect your branches")

  return protected_branches


def apply_AR_cut(process, event_dictionary, final_state_mode, jet_mode, semilep_mode, DeepTau_version):
  '''
  Organizational function
  added 'skip_DeepTau' to apply a partial selection (all but leading tau deeptau reqs)
  The block below for gen matching normally is not executed since this function is only called with Data
  in standard plot
  '''
  protected_branches = ["None"]
  event_dictionary = append_lepton_indices(event_dictionary)
  if ("Data" not in process) and (final_state_mode != "dimuon"):
    load_and_store_NWEvents(process, event_dictionary)
    if ("DY" in process): customize_DY(process, final_state_mode)
    #event_dictionary = append_flavor_indices(event_dictionary, final_state_mode, keep_fakes=True)
    keep_fakes = False
    if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and (final_state_mode=="mutau")):
    #if ((("TT" in process) or ("DY" in process)) and (final_state_mode=="mutau")):
      # when FF method is finished/improved no longer need to keep TT and WJ fakes
      keep_fakes = True
    if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and (final_state_mode=="etau")):
      # when FF method is finished/improved no longer need to keep TT and WJ fakes
      keep_fakes = True
    if (("DY" in process) and (final_state_mode=="ditau")):
      keep_fakes = True
    if ((("TT" in process) or ("WJ" in process) or ("DY" in process)) and (final_state_mode=="emu")):
      # when FF method is finished/improved no longer need to keep TT and WJ fakes
      keep_fakes = True
    process_events = append_flavor_indices(process_events, final_state_mode, keep_fakes=keep_fakes)
    process_events = apply_cut(process_events, "pass_gen_cuts", protected_branches=protected_branches)
    if (process_events==None or len(process_events["run"])==0): return None
  if (final_state_mode != "dimuon"):
    if (final_state_mode == "ditau"):
      event_dictionary = make_ditau_AR_cut(event_dictionary, DeepTau_version)
      event_dictionary = apply_cut(event_dictionary, "pass_AR_cuts", protected_branches)
      event_dictionary = apply_jet_cut(event_dictionary, jet_mode)
      event_dictionary = make_ditau_cut(event_dictionary, DeepTau_version, skip_DeepTau=True)
    if (final_state_mode == "mutau"):
      event_dictionary = make_mutau_AR_cut(event_dictionary, DeepTau_version)
      event_dictionary = apply_cut(event_dictionary, "pass_AR_cuts", protected_branches)
      event_dictionary = apply_jet_cut(event_dictionary, jet_mode)
      event_dictionary = make_mutau_cut(event_dictionary, DeepTau_version, skip_DeepTau=True)
    if (final_state_mode == "etau"):
      event_dictionary = make_etau_AR_cut(event_dictionary, DeepTau_version)
      event_dictionary = apply_cut(event_dictionary, "pass_AR_cuts", protected_branches)
      event_dictionary = apply_jet_cut(event_dictionary, jet_mode)
      event_dictionary = make_etau_cut(event_dictionary, DeepTau_version, skip_DeepTau=True)
    if (final_state_mode == "emu"):
      event_dictionary = make_emu_AR_cut(event_dictionary, iso_region_el=True, iso_region_mu=True)
      event_dictionary = apply_cut(event_dictionary, "pass_AR_cuts", protected_branches)
      event_dictionary = apply_jet_cut(event_dictionary, jet_mode)
      event_dictionary = make_emu_cut(event_dictionary, DeepTau_version, skip_DeepTau=True)
      print(len(event_dictionary['FFweight']))
      event_dictionary = apply_FF_weight_from_branch(event_dictionary)
    protected_branches = set_protected_branches(final_state_mode=final_state_mode, jet_mode="none")
    event_dictionary   = apply_cut(event_dictionary, "pass_cuts", protected_branches)
    # weights associated with jet_mode key (testing suffix automatically removed)
    event_dictionary   = add_FF_weights(event_dictionary, final_state_mode, jet_mode, semilep_mode)
  else:
    print(f"{final_state_mode} : {jet_mode} not possible. Continuing without AR or FF method applied.")
  return event_dictionary


