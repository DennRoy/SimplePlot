### README ###
# This file contains mappings of process names (shared with XSec.py) to wildcards for related samples.
# The :testing" file maps are subsets of full filelists for faster processing times.

dataset_dictionary = {"ditau" : "DataTau", 
                      "mutau" : "DataMuon", 
                      "etau"  : "DataElectron", 
                      "emu"   : "DataEMu",
                      "mutau_TnP" : "DataMuon", 
                      "dimuon"    : "DataMuon",}

reject_dataset_dictionary = {"ditau" : ["DataMuon", "DataElectron", "DataEMu"],
                             "mutau" : ["DataTau",  "DataElectron", "DataEMu"],
                             "etau"  : ["DataMuon", "DataTau",      "DataEMu"],
                             "emu"   : ["DataMuon", "DataElectron", "DataTau"],
                             "mutau_TnP" : ["DataTau",  "DataElectron", "DataEMu"],
                             "dimuon"    : ["DataTau",  "DataElectron", "DataEMu"], }

def set_dataset_info(final_state_mode):
  use_dataset     = dataset_dictionary[final_state_mode]
  reject_datasets = reject_dataset_dictionary[final_state_mode]
  return use_dataset, reject_datasets



def update_data_filemap(luminosity_key, file_map): 
  if luminosity_key == "2022 C":
    file_map["DataTau"]      = "Data/Tau_Run2022C*"
    file_map["DataMuon"]     = "Data/Muon_Run2022C*"
    file_map["DataElectron"] = "Data/EGamma_Run2022C*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022C*"
  if luminosity_key == "2022 D":
    file_map["DataTau"]      = "Data/Tau_Run2022D*"
    file_map["DataMuon"]     = "Data/Muon_Run2022D*"
    file_map["DataElectron"] = "Data/EGamma_Run2022D*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022D*"
  if luminosity_key == "2022 CD":
    file_map["DataTau"]      = "Data/Tau_Run2022*"
    file_map["DataMuon"]     = "Data/Muon_Run2022*"
    file_map["DataElectron"] = "Data/EGamma_Run2022*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022*"
  if luminosity_key == "2022 E":
    file_map["DataTau"]      = "Data/Tau_Run2022E*"
    file_map["DataMuon"]     = "Data/Muon_Run2022E*"
    file_map["DataElectron"] = "Data/EGamma_Run2022E*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022E*"
  if luminosity_key == "2022 F":
    file_map["DataTau"]      = "Data/Tau_Run2022F*"
    file_map["DataMuon"]     = "Data/Muon_Run2022F*"
    file_map["DataElectron"] = "Data/EGamma_Run2022F*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022F*"
  if luminosity_key == "2022 G":
    file_map["DataTau"]      = "Data/Tau_Run2022G*"
    file_map["DataMuon"]     = "Data/Muon_Run2022G*"
    file_map["DataElectron"] = "Data/EGamma_Run2022G*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022G*"
  if luminosity_key == "2022 EFG":
    file_map["DataTau"]      = "Data/Tau_Run2022*"
    file_map["DataMuon"]     = "Data/Muon_Run2022*"
    file_map["DataElectron"] = "Data/EGamma_Run2022*"
    file_map["DataEMu"]      = "Data/MuonEG_Run2022*"
  return file_map 

testing_file_map = {
  "DataTau"  : "Data/Tau_Run*G*",
  "DataMuon" : "Data/Muon_Run*G*",
  "DataElectron" : "Data/EGamma*G*",
  "DataEMu"  : "Data/MuonEG_Run*G*",

  "TTToFullyHadronic" : "TT/TTToFullyHadronic*",

  "DYInc"    : "DY/DYJetsToLL_M-50_LO_HTauTau*",
  "DYIncNLO" : "DY_NLO/DYJetsToLL_M-50_HTauTau*",

  "TTTo2L2Nu"       : "TT/TTTo2L2Nu_HTauTau_2022postEE_step2_part10*",
  "TTToFullyHadronic" : "TT/TTToFullyHadronic*",
  "TTToSemiLeptonic"  : "TT/TTToSemiLeptonic*",

  "WJetsInc"    : "WJ/WJetsToLNu_LO_HTauTau*",
  "WJetsIncNLO" : "WJ/WJetsToLNu_HTauTau*",

  "VBF_TauTau"   : "Signal/VBF_TauTau_HTauTau*",
  "ggH_TauTau"   : "Signal/ggH_TauTau_HTauTau_*",
}


full_file_map = {

  "DataTau"  : "Data/Tau_Run*",
  "DataMuon" : "Data/Muon_Run*",
  "DataElectron" : "Data/EGamma_Run*",
  "DataEMu"  : "Data/MuonEG_Run*",

  "DYInc" : "DY/DYJetsToLL_M-50_LO_HTauTau*",
#  "DYInc" : "DY/DYJetsToLL_M-50_NLO_HTauTau*",

  #"DYJetsToLL_M-50_1J" : "DY/DYJetsToLL_M-50_1J*",
  #"DYJetsToLL_M-50_2J" : "DY/DYJetsToLL_M-50_2J*",
  #"DYJetsToLL_M-50_3J" : "DY/DYJetsToLL_M-50_3J*",
  #"DYJetsToLL_M-50_4J" : "DY/DYJetsToLL_M-50_4J*",

  "DYIncNLO" : "DY/DYJetsToLL_M-50_NLO_HTauTau*",

  "TTTo2L2Nu"         : "TT/TTTo2L2Nu*",
  "TTToFullyHadronic" : "TT/TTToFullyHadronic*",
  "TTToSemiLeptonic"  : "TT/TTToSemiLeptonic*",

  "ST_s-channel_Tbar"  : "ST/ST_s-channel_antitop*",
  "ST_t-channel_Tbar"  : "ST/ST_t-channel_antitop*",
  "ST_TbarWplus_2L2Nu" : "ST/ST_TbarWplus_2L2Nu*",
  "ST_TbarWplus_4Q"    : "ST/ST_TbarWplus_4Q*",
  "ST_TbarWplus_LNu2Q" : "ST/ST_TbarWplus_LNu2Q*",
  "ST_s-channel_T"     : "ST/ST_s-channel_top*",
  "ST_t-channel_T"     : "ST/ST_t-channel_top*",
  "ST_TWminus_2L2Nu"   : "ST/ST_TWminus_2L2Nu*", 
  "ST_TWminus_4Q"      : "ST/ST_TWminus_4Q*",
  "ST_TWminus_LNu2Q"   : "ST/ST_TWminus_LNu2Q*",

  "WJetsInc"    : "WJ/WJetsToLNu_LO_HTauTau*",
#  "WJetsInc" : "WJ/WJetsToLNu_HTauTau*",
  "WJetsIncNLO" : "WJ/WJetsToLNu_HTauTau*",
  #"WJetsIncNLO" : "WJ/WJetsToLNu_HTauTau*",
  #"WJetsToLNu_1J" : "WJ/W1JetsToLNu*",
  #"WJetsToLNu_2J" : "WJ/W2JetsToLNu*",
  #"WJetsToLNu_3J" : "WJ/W3JetsToLNu*",
  #"WJetsToLNu_4J" : "WJ/W4JetsToLNu*",

  #"WW"        : "VV/WW*", # WW Inc. available but untested
  "WWTo2L2Nu" : "VV/WWTo2L2Nu*",
  "WWTo4Q"    : "VV/WWTo4Q*",
  "WWToLNu2Q" : "VV/WWToLNu2Q*",
  "ggH_WW"    : "WW/ggH_WW_HTauTau*",
  "ttH_WW"    : "WW/ttH_WW*",
  "VBF_WW"    : "WW/VBF_WW*",
  

  #"WZ"        : "VV/WZ*", # WZ Inc. available but untested
  "WZTo3LNu"  : "VV/WZTo3LNu*",
  "WZTo2L2Q"  : "VV/WZTo2L2Q*",
  "WZToLNu2Q" : "VV/WZToLNu2Q*",


  #"ZZ"        : "VV/ZZ*", # ZZ Inc. available but untested
  "ZZTo2L2Nu" : "VV/ZZTo2L2Nu*",
  "ZZTo2L2Q"  : "VV/ZZTo2L2Q*", 
  "ZZTo2Nu2Q" : "VV/ZZTo2Nu2Q*",
  "ZZTo4L"    : "VV/ZZTo4L*", 

  # Do Not Use
  #"QCD_HT-70to100"    : "QCD/QCD_HT70to100_HTauTau*",
  #"QCD_HT-100to200"   : "QCD/QCD_HT100to200_HTauTau*",
  #"QCD_HT-200to400"   : "QCD/QCD_HT200to400_HTauTau*",
  #"QCD_HT-400to600"   : "QCD/QCD_HT400to600_HTauTau*",
  #"QCD_HT-600to800"   : "QCD/QCD_HT600to800_HTauTau*",
  #"QCD_HT-800to1000"  : "QCD/QCD_HT800to1000_HTauTau*",
  #"QCD_HT-1000to1200" : "QCD/QCD_HT1000to1200_HTauTau*",
  #"QCD_HT-1200to1500" : "QCD/QCD_HT1200to1500_HTauTau*",
  #"QCD_HT-1500to2000" : "QCD/QCD_HT1500to2000_HTauTau*",
  #"QCD_HT-2000"       : "QCD/QCD_HT2000toInf_HTauTau*",

  "VBF_TauTau"   : "Signal/VBF_TauTau_HTauTau_*",
  "ggH_TauTau"   : "Signal/ggH_TauTau_HTauTau_*",
}
