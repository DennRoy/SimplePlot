from XSec import XSecRun3 as XSec
# introduces crashes
#from ROOT import TColor, kBlack, kWhite, kGray, kAzure, kBlue, kCyan,\
#                 kGreen, kSpring, kTeal, kYellow,\
#                 kOrange, kRed, kPink, kMagenta, kViolet

### README ###
# this file contains small dictionaries combining information for MC processes 
# MC_dictionary SHOULD contain one entry for each type of sample, it should    
# it references the smaller dictionaries color_dictionary and label_dictionary 
# for additionaly information. Plot scaling for all non-signal processes are set to 1 by default.
#
# following most color definitions from here
# https://github.com/oponcet/TauFW/blob/8984be701ef6a5e4d126a16c390b4efb4afe101a/Plotter/python/sample/SampleStyle.py#L116
# except using RGB values converted from here using a color picker
# https://root.cern.ch/doc/master/classTColor.html

color_dictionary = {
  "ggH": "#0000ff", # kBlue
  "VBF": "#ff0000", # kRed
  "DY" : "#ffcc66", # DY yellow # kOrange - 4
  "DYGen" : "#ffcc66", # above
  "DYLep" : "#3399cc", # # kAzure +5
  "DYJet" : "#66cc66", # # kGreen -6
  "TT" : "#9999cc", # light purple, kBlue - 8 
  #"ST" : "#660099", # dark purple
  "ST": "#8cb4dc", # their dark purple, from RGB 140 180 220 
  "WJ" : "#e44e4e", # dark red
  "VV" : "#de8c6a", # sandy red, from RGB 222 140 106
  #"VV" : "#808080", # grey
  "QCD": "#ffccff", # pink kMagenta -10
  "DYInc" : "#ffcc66",
}
label_dictionary = {
 "ggH_TauTau" : "ggH",
 "VBF_TauTau" : "VBF",
 "DY"  : "DY",
 "DYInc"  : "DYInc",
 "TT"  : "TT",
 "ST"  : "ST",
 "WJ"  : "WJ",
 "VV"  : "VV",
 "QCD" : "QCD",
 "myQCD" : "FF Jet Fakes",
}
 
MC_dictionary = {
  "myQCD" : {"label": "QCD", "color": color_dictionary["QCD"]},
  "QCD" : {"label": "QCD", "color": color_dictionary["QCD"]},
  "DY"  : {"label": "DY", "color": color_dictionary["DY"]},
  "DYInc"  : {"label": "DYInc", "color": color_dictionary["DYInc"]},
  "TT"  : {"label": "TT", "color": color_dictionary["TT"]},
  "ST"  : {"label": "ST", "color": color_dictionary["ST"]},
  "WJ"  : {"label": "W+Jets", "color": color_dictionary["WJ"]},
  "VV"  : {"label": "Diboson", "color": color_dictionary["VV"]},

  #########################################################
  # above are dummy dictionaries for grouped subprocesses #
  # below are real dictionaries for subprocesses          #
  #########################################################

  "ggH_TauTau" : {"XSec": XSec["ggH_TauTau"], "NWEvents": 19289464.362, 
           "label": "ggH", "color": color_dictionary["ggH"],
           "plot_scaling" : 100},

  "VBF_TauTau" : {"XSec": XSec["VBF_TauTau"], "NWEvents": 2402853.147599998, 
           "label": "VBF", "color": color_dictionary["VBF"],
           "plot_scaling" : 100},

  # copies of DYInc with different colors and labels
  "DYGen"    : {"label": r"$Z{\rightarrow}{\tau_\mu}{\tau_h}$", "color": color_dictionary["DYGen"], "plot_scaling" : 1.12},
  "DYLep"    : {"label": r"$Z{\rightarrow}ll, l{\rightarrow}{\tau_h}$", "color": color_dictionary["DYLep"], "plot_scaling" : 1.12},
  "DYJet"    : {"label": r"$DY, j{\rightarrow}{\tau_h}$", "color": color_dictionary["DYJet"], "plot_scaling" : 1.12},

  "DYIncNLO" : {"label": "DY", "color": color_dictionary["DY"], "plot_scaling" : 1},
  "DYInc" : {"label": "DY", "color": color_dictionary["DY"], "plot_scaling" : 1},
  # copies of DYIncNLO with different colors and labels
  "DYGenNLO" : {"label": r"$Z{\rightarrow}{\tau_\mu}{\tau_h}$", "color": color_dictionary["DYGen"], "plot_scaling" : 1},
  "DYLepNLO" : {"label": r"$Z{\rightarrow}ll, l{\rightarrow}{\tau_h}$", "color": color_dictionary["DYLep"], "plot_scaling" : 1},
  "DYJetNLO" : {"label": r"$DY, j{\rightarrow}{\tau_h}$", "color": color_dictionary["DYJet"], "plot_scaling" : 1},



  "TTTo2L2Nu"          : {"label": "TT", "color": color_dictionary["TT"], "plot_scaling" : 1},
  "TTToFullyHadronic"  : {"label": "TT", "color": color_dictionary["TT"], "plot_scaling" : 1},
  "TTToSemiLeptonic"   : {"label": "TT", "color": color_dictionary["TT"], "plot_scaling" : 1},

  "ST_s-channel_Tbar"  : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling": 1},
  "ST_s-channel_T"     : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling": 1},
  "ST_t-channel_Tbar"  : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling": 1},
  "ST_t-channel_T"     : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling": 1},
  "ST_TWminus_2L2Nu"   : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling" : 1},
  "ST_TbarWplus_2L2Nu" : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling" : 1},
 
  "ST_TWminus_4Q"      : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling" : 1},
  "ST_TbarWplus_4Q"    : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling" : 1},
  "ST_TWminus_LNu2Q"   : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling" : 1},
  "ST_TbarWplus_LNu2Q" : {"label": "ST", "color": color_dictionary["ST"], "plot_scaling" : 1},

  "WJetsInc"           : {"label": "WJ", "color": color_dictionary["WJ"], "plot_scaling" : 1.125552349}, #k-factor from Stitching config in NanoTauAnalysis
  "WJetsIncNLO"        : {"label": "WJ", "color": color_dictionary["WJ"], "plot_scaling" : 1},
  "WJetsToLNu_1J"      : {"label": "WJ", "color": color_dictionary["WJ"], "plot_scaling" : 1},
  "WJetsToLNu_2J"      : {"label": "WJ", "color": color_dictionary["WJ"], "plot_scaling" : 1},
  "WJetsToLNu_3J"      : {"label": "WJ", "color": color_dictionary["WJ"], "plot_scaling" : 1},
  "WJetsToLNu_4J"      : {"label": "WJ", "color": color_dictionary["WJ"], "plot_scaling" : 1},

  "WWTo2L2Nu"          : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "WWTo4Q"             : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "WWToLNu2Q"          : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},

  "WZTo3LNu"           : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "WZTo2L2Q"           : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "WZToLNu2Q"          : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},

  "ZZTo2L2Nu"          : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "ZZTo2L2Q"           : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "ZZTo2Nu2Q"          : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},
  "ZZTo4L"             : {"label": "VV", "color": color_dictionary["VV"], "plot_scaling" : 1},

  "ggH_WW"       : {"XSec": XSec["ggH_WW"], "NWEvents": 1,
                    "label": "VV", "color": color_dictionary["VV"],
                    "plot_scaling" : 1},

  "ttH_WW"        : {"XSec": XSec["ttH_nonbb"], "NWEvents": 1,
                    "label": "VV", "color": color_dictionary["VV"],
                    "plot_scaling" : 1},

  "VBF_WW"        : {"XSec": XSec["VBF_WW"], "NWEvents": 1,
                    "label": "VV", "color": color_dictionary["VV"],
                    "plot_scaling" : 1},

  "myQCD"   : {"XSec": 1, "NWEvents": 1,
             "label": "Jet Fakes", "color": color_dictionary["QCD"],
             "plot_scaling" : 1, "XSecMCweight" : 1},  # dummy value for MCweight

  "QCD_HT-70to100"    : {"XSec": XSec["QCD_HT-70to100"],    "NWEvents": 1.973e+16, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-100to200"   : {"XSec": XSec["QCD_HT-100to200"],   "NWEvents": 1.142e+16, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-200to400"   : {"XSec": XSec["QCD_HT-200to400"],   "NWEvents": 1.208e+15, # branch value
                       "label": "MC QCD", "color": color_dictionary["QCD"],
                       "plot_scaling" : 1},
  "QCD_HT-400to600"   : {"XSec": XSec["QCD_HT-400to600"],   "NWEvents": 7.184e+13, # branch value
                       "label": "MC QCD", "color": color_dictionary["QCD"],
                       "plot_scaling" : 1},
  "QCD_HT-600to800"   : {"XSec": XSec["QCD_HT-600to800"],   "NWEvents": 1.019e+13, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-800to1000"  : {"XSec": XSec["QCD_HT-800to1000"],  "NWEvents": 2.530e+12, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-1000to1200" : {"XSec": XSec["QCD_HT-1000to1200"], "NWEvents": 8.112e+11, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-1200to1500" : {"XSec": XSec["QCD_HT-1200to1500"], "NWEvents": 3.579e+11, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-1500to2000" : {"XSec": XSec["QCD_HT-1500to2000"], "NWEvents": 1.063e+11, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},
  "QCD_HT-2000"       : {"XSec": XSec["QCD_HT-2000"],       "NWEvents": 2.274e+10, # branch value
                         "label": "MC QCD", "color": color_dictionary["QCD"],
                         "plot_scaling" : 1},

  "QCD_HT-70to100"     : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-100to200"    : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-200to400"    : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-400to600"    : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-600to800"    : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-800to1000"   : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-1000to1200"  : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-1200to1500"  : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-1500to2000"  : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
  "QCD_HT-2000"        : {"label": "MC QCD", "color": color_dictionary["QCD"], "plot_scaling" : 1},
}
