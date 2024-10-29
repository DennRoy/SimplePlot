
from file_map_dictionary   import testing_file_map, full_file_map, update_data_filemap
from luminosity_dictionary import luminosities_with_normtag as luminosities

from utility_functions       import make_directory, print_setup_info

class setup_handler:
  def __init__(self):
    import argparse 
    self.parser = argparse.ArgumentParser(description='Make a standard Data/MC agreement plot.')
    # store_true : when the argument is supplied, store it's value as true
    # for 'testing' below, the default value is false if the argument is not specified
    self.parser.add_argument('--testing',      dest='testing',     default=False,       action='store_true')
    self.parser.add_argument('--final_state',  dest='final_state', default="mutau",     action='store')
    self.parser.add_argument('--jet_mode',     dest='jet_mode',    default="Inclusive", action='store')
    self.parser.add_argument('--era',          dest='era',         default="2022 EFG",  action='store')
    self.parser.add_argument('--use_NLO',      dest='use_NLO',     default=False,       action='store_true')
    self.parser.add_argument('--plot_dir',     dest='plot_dir',    default="plots",     action='store')
    self.parser.add_argument('--DeepTau',      dest='DeepTau_version', default="2p5",   action='store')
    self.parser.add_argument('--hide_plots',   dest='hide_plots',  default=False,       action='store_true')
    self.parser.add_argument('--hide_yields',  dest='hide_yields', default=False,       action='store_true')
    self.parser.add_argument('--do_JetFakes',  dest='do_JetFakes', default=True,        action='store')
    self.parser.add_argument('--semilep_mode', dest='semilep_mode', default="QCD",      action='store')
    self.parser.add_argument('--use_new',      dest='use_new',      default="True",    action='store')

    args = self.parser.parse_args()

    # state info
    # final_state_mode affects good_events, datasets, plotting vars, etc. automatically
    testing          = args.testing     # False by default, do full dataset unless otherwise specified
    final_state_mode = args.final_state # default mutau [possible values ditau, mutau, etau, dimuon]
    jet_mode         = args.jet_mode    # default Inclusive [possible values 0j, 1j, 2j, GTE1j, GTE2j]
    era              = args.era
    if testing: era = "2022 G"     # testing overrides era inputs
    lumi = luminosities[era]

    # file info
    infile_directory = self.set_infile_directory(era, final_state_mode)
    plot_dir_name = "FS_plots/" + args.plot_dir + "_" + final_state_mode + "_" + jet_mode
    plot_dir_name = make_directory(plot_dir_name, testing)
    logfile       = open('outputfile.log', 'w') # could be improved, not super important right now
    use_NLO       = args.use_NLO     # False by default, use LO DY if False
    file_map      = self.set_file_map(testing, use_NLO, era)

    # misc info
    hide_plots  = args.hide_plots  # False by default, show plots unless otherwise specified
    hide_yields = args.hide_yields # False by default, show yields unless otherwise specified
    DeepTau_version = args.DeepTau_version # default is 2p5 [possible values 2p1 and 2p5]
    do_JetFakes  = args.do_JetFakes  # True by default, set to False to remove contributions from Fakes
    semilep_mode = args.semilep_mode # default is QCD [possible values are Full, QCD, and WJ] (Full is both)

    # set three named tuples to collect class information that can be accessed later
    from collections import namedtuple
    state_info_template = namedtuple("State_info", "testing, final_state_mode, jet_mode, era, lumi")
    self.state_info     = state_info_template(testing, final_state_mode, jet_mode, era, lumi)
    file_info_template  = namedtuple("File_info", "infile_directory, plot_dir_name, logfile, use_NLO, file_map")
    self.file_info      = file_info_template(infile_directory, plot_dir_name, logfile, use_NLO, file_map)
    misc_info_template  = namedtuple("Misc_info", " hide_plots, hide_yields, DeepTau_version, do_JetFakes, semilep_mode")
    self.misc_info      = misc_info_template(hide_plots, hide_yields, DeepTau_version, do_JetFakes, semilep_mode)
  # end class init

  def set_infile_directory(self, era, final_state_mode):
    #lxplus_redirector = "root://cms-xrd-global.cern.ch//"
    #eos_dir           = "/eos/user/b/ballmond/NanoTauAnalysis/analysis/"
    era_modifier_2022 = "preEE" if (("C" in era) or ("D" in era)) else "postEE"
    full_dir = "/Users/giuliasorrentino/Desktop/HLepRareNtuples/HTauTau_2022"+era_modifier_2022+"_Hlep_" + final_state_mode
    #full_dir = "/Users/giuliasorrentino/Desktop/JulyNtuples/HTauTau_2022"+era_modifier_2022+"_step2_" + final_state_mode
    return full_dir


  
  def set_file_map(self, testing, use_NLO, era):
    file_map = testing_file_map if testing else full_file_map
    if (use_NLO == True):
      file_map.pop("DYInc")
      file_map.pop("WJetsInc")
    else: 
      file_map.pop("DYIncNLO")
      file_map.pop("WJetsIncNLO")
    file_map = update_data_filemap(era, file_map)
    return file_map


def set_good_events(final_state_mode, AR_region=False, disable_triggers=False, useMiniIso=False):
  '''
  Return a string defining a 'good_events' flag used by uproot to preskim input events
  to only those passing these simple requirements. 'good_events' changes based on
  final_state_mode, and the trigger condition is removed if a trigger study is 
  being conducted (since requiring the trigger biases the study).
  '''
  good_events = ""
  if disable_triggers: print("*"*20 + " removed trigger requirement " + "*"*20)

  # relevant definitions from NanoTauAnalysis /// modules/TauPairSelector.py
  # HTT_SRevent and HTT_ARevent require opposite sign objects
  # HTT_SRevent = ((pdgIdPair < 0) 
  #            and ( ((LeptonIso < 0.2) and (abs(pdgIdPair)==11*13)) or (LeptonIso < 0.15)) 
  #            and TauPassVsJet and (self.leptons[finalpair[1]].pt > 15))
  # HTT_ARevent = ((pdgIdPair < 0) 
  #            and ( ((LeptonIso < 0.2) and (abs(pdgIdPair)==11*13)) or (LeptonIso < 0.15)) 
  #            and (not TauPassVsJet) and (self.leptons[finalpair[1]].pt > 15))
  #     # All SR requirements besides TauPassVsJet
  # HTT_SSevent = ((pdgIdPair > 0) 
  #            and ( ((LeptonIso < 0.2) and (abs(pdgIdPair)==11*13)) or (LeptonIso < 0.15)) 
  #            and TauPassVsJet and (self.leptons[finalpair[1]].pt > 15)) 
  #     # All SR requirements besides opposite sign
  
  # apply FS cut separately so it can be used with reject_duplicate_events
  # STANDARD!
  good_events =  "(METfilters) & (LeptonVeto==0)"
  jet_vetomaps = " & (JetMapVeto_EE_30GeV) & (JetMapVeto_HotCold_30GeV)"
  #jet_vetomaps = " & (JetMapVeto_EE_25GeV) & (JetMapVeto_HotCold_25GeV)"
  #jet_vetomaps = " & (JetMapVeto_EE_15GeV) & (JetMapVeto_HotCold_15GeV)"
  #jet_vetomaps = " & (JetMapVeto_EE_30GeV)"
  #jet_vetomaps = " & (JetMapVeto_EE_25GeV)"
  #jet_vetomaps = " & (JetMapVeto_EE_15GeV)"
  #jet_vetomaps = " & (JetMapVeto_EE_30GeV) & (JetMapVeto_TauEE)"
  #jet_vetomaps = " & (JetMapVeto_EE_30GeV) & (JetMapVeto_TauEE) & (JetMapVeto_TauHotCold)"
  #jet_vetomaps = " & (JetMapVeto_EE_15GeV) & (JetMapVeto_TauEE) & (JetMapVeto_TauHotCold)"
  #good_events = "(HTT_SRevent) & (METfilters) & (LeptonVeto==0) & (JetMapVeto_EE_30GeV) & (JetMapVeto_HotCold_30GeV)"
  HTT_preselect_events = "& (HTT_SRevent)"
  good_events += jet_vetomaps
  if AR_region: return good_events # give output with MET filters, lepton veto, and veto maps

  #good_events += HTT_preselect_events
  # UNDER STUDY!
  #good_events = "(HTT_SRevent) & (METfilters) & (LeptonVeto==0) & (JetMapVeto_EE_15GeV) & (JetMapVeto_HotCold_15GeV) "\
  #good_events = "(HTT_SRevent) & (METfilters) & (LeptonVeto==0) & (JetMapVeto_EE_15GeV) & (JetMapVeto_HotCold_15GeV) & "\
  #              "(JetMapVeto_TauHotCold) & (JetMapVeto_TauEE) & (JetMapVeto_TauMuon)"
  #good_events = "(HTT_SRevent) & (METfilters) & (LeptonVeto==0) & (JetMapVeto_EE_15GeV) & (JetMapVeto_HotCold_15GeV) & "\
  #              "(JetMapVeto_TauHotCold) & (JetMapVeto_TauEE) & (JetMapVeto_TauMuon)"
  #              "(JetMapVeto_TauHotCold) & (JetMapVeto_TauEE)"
                #"(JetMapVeto_TauMuon)"

  #good_events = "(HTT_SRevent) & (METfilters) & (LeptonVeto==0)"
  if final_state_mode == "ditau":
    triggers = "(HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1\
               | HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60\
               | HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75\
               | HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1\
               | HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1)"
    #triggers = "(HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1)"

    good_events += " & (abs(HTT_pdgId)==15*15) & " + triggers
    if disable_triggers: good_events = good_events.replace(" & (Trigger_ditau)", "")

  elif final_state_mode == "mutau":
    good_events += " & (abs(HTT_pdgId)==13*15) & (Trigger_mutau)"
    if disable_triggers: good_events = good_events.replace(" & (Trigger_mutau)", "")

  elif final_state_mode == "etau":
    good_events += " & (abs(HTT_pdgId)==11*15) & (Trigger_etau)"
    if disable_triggers: good_events = good_events.replace(" & (Trigger_etau)", "")

  elif final_state_mode == "emu":
    good_events += " & (abs(HTT_pdgId)==11*13) & (Trigger_emu) "
    #good_events += " & (abs(HTT_pdgId)==11*13) & (Trigger_emu) "
    if disable_triggers: good_events = good_events.replace(" & (Trigger_emu)", "")

  # non-HTT FS modes
  elif final_state_mode == "mutau_TnP": # remove HTT_SRevent
    good_events = "(METfilters) & (LeptonVeto==0) & (abs(HTT_pdgId)==13*15)"
    good_events += jet_vetomaps

  elif final_state_mode == "dimuon":
    # lepton veto must be applied manually for this final state
    if (useMiniIso == False):
      good_events = "(METfilters) & (HTT_pdgId==-13*13) & (HLT_IsoMu24)"
    if (useMiniIso == True):
      good_events = "(METfilters) & (LeptonVeto==0) & (HTT_pdgId==-13*13) & (HLT_IsoMu24)"
    if disable_triggers: good_events = good_events.replace(" & (HLT_IsoMu24)", "")

  return good_events

if __name__ == "__main__":
  setup = setup_handler()
  testing, final_state_mode, jet_mode, era, lumi = setup.state_info
  infile_directory, plot_dir_name, logfile, use_NLO, file_map = setup.file_info
  hide_plots, hide_yields, DeepTau_version, do_JetFakes, semilep_mode = setup.misc_info

  # test setup
  from branch_functions    import set_branches
  from plotting_functions  import set_vars_to_plot
  from file_map_dictionary import set_dataset_info

  good_events  = set_good_events(final_state_mode)
  branches     = set_branches(final_state_mode, DeepTau_version)
  vars_to_plot = set_vars_to_plot(final_state_mode, jet_mode=jet_mode)
  dataset, reject_datasets = set_dataset_info(final_state_mode)

  # show info to user
  print_setup_info(setup)


