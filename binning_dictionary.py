import numpy as np

### README ###
# binning for different variables are defined below and are separated by use-case
# All variables are assumed to be linearly binned.

label_dictionary = {
  "FS_t1_pt"  : r'Leading Tau $p_T$ [GeV]',
  "FS_t1_eta" : r'Leading Tau $\eta$',
  "FS_t1_phi" : r'Leading Tau $\phi$',
  "FS_t1_DeepTauVSjet" : r'Leading Tau DeepTau Vs Jet',
  "FS_t1_DeepTauVSmu"  : r'Leading Tau DeepTau Vs Muon',
  "FS_t1_DeepTauVSe"   : r'Leading Tau DeepTau Vs Electron',
  "FS_t1_dxy"  : r'Leading Tau $D_{xy}$',
  "FS_t1_dz"   : r'Leading Tau $D_Z$',
  "FS_t1_chg"  : r'Leading Tau Charge',
  "FS_t1_DM"   : r'Leading Tau Decay Mode',

  "FS_t2_pt"  : r'Sub-leading Tau $p_T$ [GeV]',
  "FS_t2_eta" : r'Sub-leading Tau $\eta$',
  "FS_t2_phi" : r'Sub-leading Tau $\phi$',
  "FS_t2_DeepTauVSjet" : r'Sub-leading Tau DeepTau Vs Jet',
  "FS_t2_DeepTauVSmu"  : r'Sub-leading Tau DeepTau Vs Muon',
  "FS_t2_DeepTauVSe"   : r'Sub-leading Tau DeepTau Vs Electron',
  "FS_t2_dxy"  : r'Sub-leading Tau $D_{xy}$',
  "FS_t2_dz"   : r'Sub-leading Tau $D_Z$',
  "FS_t2_chg"  : r'Sub-leading Tau Charge',
  "FS_t2_DM"   : r'Sub-leading Tau Decay Mode',

  "FS_trig_idx" : r'Trigger Indices',

  "FS_m1_pt"   : r'Leading Muon $p_T$ [GeV]',
  "FS_m1_eta"  : r'Leading Muon $\eta$',
  "FS_m1_phi"  : r'Leading Muon $\phi$',
  "FS_m1_iso"  : r'Leading Muon Isolation',
  "FS_m1_dxy"  : r'Leading Muon $D_{xy}$',
  "FS_m1_dz"   : r'Leading Muon $D_z$',
  "FS_m1_chg"  : r'Leading Muon Charge',

  "FS_m2_pt"   : r'Sub-leading Muon $p_T$ [GeV]',
  "FS_m2_eta"  : r'Sub-leading Muon $\eta$',
  "FS_m2_phi"  : r'Sub-leading Muon $\phi$',
  "FS_m2_iso"  : r'Sub-leading Muon Isolation',
  "FS_m2_dxy"  : r'Sub-leading Muon $D_{xy}$',
  "FS_m2_dz"   : r'Sub-leading Muon $D_z$',
  "FS_m2_chg"  : r'Sub-leading Muon Charge',

  "FS_m_vis_tight" : r'$m_{vis}$ [GeV]',

  "FS_mu_pt"   : r'Muon $p_T$ [GeV]',
  "FS_mu_eta"  : r'Muon $\eta$',
  "FS_mu_phi"  : r'Muon $\phi$',
  "FS_mu_iso"  : r'Muon Isolation',
  "FS_mu_dxy"  : r'Muon $D_{xy}$',
  "FS_mu_dz"   : r'Muon $D_{z}$',
  "FS_mu_chg"  : r'Muon Charge',

  "FS_el_pt"   : r'Electron $p_T$ [GeV]',
  "FS_el_eta"  : r'Electron $\eta$',
  "FS_el_phi"  : r'Electron $\phi$',
  "FS_el_iso"  : r'Electron Isolation',
  "FS_el_dxy"  : r'Electron $D_{xy}$',
  "FS_el_dz"   : r'Electron $D_{z}$',
  "FS_el_chg"  : r'Electron Charge',

  "FS_tau_pt"  : r'Tau $p_T$ [GeV]',
  "FS_tau_eta" : r'Tau $\eta$',
  "FS_tau_phi" : r'Tau $\phi$',
  "FS_tau_dxy" : r'Tau $D_{xy}$',
  "FS_tau_dz"  : r'Tau $D_{z}$',
  "FS_tau_chg" : r'Tau Charge',
  "FS_tau_DM"  : r'Tau Decay Mode',

  "FS_mt"      : r'Transverse Mass',
  "FS_nbJet"   : r'Number of b-tagged Jets',
  "FS_acoplan" : r'Acoplanarity',

  "MET_pt"          : r'MET [GeV]',
  "PuppiMET_pt"     : r'PUPPI MET [GeV]',
  "PuppiMET_phi"    : r'PUPPI MET $\phi$',
  "nCleanJetGT30"   : r'Number of Jets',
  "CleanJetGT30_pt_1"  : r'Leading Jet $p_T$ [GeV]',
  "CleanJetGT30_eta_1" : r'Leading Jet $\eta$',
  "CleanJetGT30_phi_1" : r'Leading Jet $\phi$',
  "CleanJetGT30_pt_2"  : r'Sub-leading Jet $p_T$ [GeV]',
  "CleanJetGT30_eta_2" : r'Sub-leading Jet $\eta$',
  "CleanJetGT30_phi_2" : r'Sub-leading Jet $\phi$',
  "FS_mjj"    : r'Dijet Mass [GeV]',
  "FS_detajj" : r'|$\Delta\eta$|',

  "HTT_DiJet_MassInv_fromHighestMjj" : r'Dijet Mass [GeV]',
  "HTT_DiJet_dEta_fromHighestMjj"    : r'|$\Delta\eta$|',
  "HTT_H_pt_using_PUPPI_MET"         : r'Higgs $p_T$ [GeV]',
  "HTT_dR"      : r'$\Delta$R',
  "HTT_m_vis-KSUbinning" : r'$m_{vis}$ [GeV]',
  "HTT_m_vis-SFbinning"  : r'$m_{vis}$ [GeV]',
  "HTT_pT_l1l2" : r'$p_T^{ll}$',
  "FastMTT_mT"   : r'Fast MTT Transverse Mass [GeV]',
  "FastMTT_mass" : r'Fast MTT Mass [GeV]',
  "PV_npvs"     : r'Number of Primary Vertices',

  "pass_tag"    : r'Pass Tag Requirements',
  "pass_probe"    : r'Pass Probe Requirements',
}

#  channel {
#    "var"  : (xmin, xmax, nBins),
#  }
binning_dictionary = {
  "ditau" : {
    "FS_t1_pt"   : np.linspace(0, 180, 36+1),
    "FS_t1_eta"  : np.linspace(-3, 3, 30+1),
    "FS_t1_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_t1_DeepTauVSjet" : np.linspace(1, 9, 8+1),
    "FS_t1_DeepTauVSmu"  : np.linspace(1, 5, 4+1),
    "FS_t1_DeepTauVSe"   : np.linspace(1, 9, 8+1),
    "FS_t1_dxy"  : np.linspace(0, 0.20, 50+1),
    "FS_t1_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_t1_chg"  : np.linspace(-2, 2, 5+1),
    "FS_t1_DM"   : np.linspace(0, 19, 20+1),
    "FS_t1_rawPNetVSjet" : np.linspace(0, 1, 50+1),
    "FS_t1_rawPNetVSmu"  : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),
    "FS_t1_rawPNetVSe"   : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),

    "FS_t2_pt"   : np.linspace(0, 120, 24+1),
    "FS_t2_eta"  : np.linspace(-3, 3, 30+1),
    "FS_t2_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_t2_DeepTauVSjet" : np.linspace(1, 9, 8+1),
    "FS_t2_DeepTauVSmu"  : np.linspace(1, 5, 4+1),
    "FS_t2_DeepTauVSe"   : np.linspace(1, 9, 8+1),
    "FS_t2_dxy"  : np.linspace(0, 0.20, 50+1),
    "FS_t2_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_t2_chg"  : np.linspace(-2, 2, 5+1),
    "FS_t2_DM"   : np.linspace(0, 19, 20+1),
    "FS_t2_rawPNetVSjet" : np.linspace(0, 1, 50+1),
    "FS_t2_rawPNetVSmu"  : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),
    "FS_t2_rawPNetVSe"   : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),

    "FS_trig_idx" : np.linspace(-1, 4, 5+1),
  },

  "mutau" : {
    "FS_mu_pt"   : np.linspace(0, 120, 40+1),
    "FS_mu_eta"  : np.linspace(-3, 3, 30+1),
    "FS_mu_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_mu_iso"  : np.linspace(0, 1, 25+1),
    "FS_mu_dxy"  : np.linspace(0, 0.025, 50+1),
    "FS_mu_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_mu_chg"  : np.linspace(-2, 2, 5+1),

    "FS_tau_pt"  : np.linspace(0, 180, 36+1),
    "FS_tau_eta" : np.linspace(-3, 3, 30+1),
    "FS_tau_phi" : np.linspace(-3.2, 3.2, 32+1),
    "FS_tau_dxy" : np.linspace(0, 0.20, 50+1),
    "FS_tau_dz"  : np.linspace(0, 0.25, 50+1),
    "FS_tau_chg" : np.linspace(-2, 2, 5+1),
    "FS_tau_DM"  : np.linspace(0, 19, 20+1),

    "FS_tau_rawPNetVSjet" : np.linspace(0, 1, 50+1),
    "FS_tau_rawPNetVSmu"  : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]), # plot logx
    "FS_tau_rawPNetVSe"   : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),
  },

  "etau" : {
    "FS_el_pt"   : np.linspace(20, 100, 49+1), #0, 120, 60+1
    "FS_el_eta"  : np.linspace(-3, 3, 30+1),
    "FS_el_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_el_iso"  : np.linspace(0, 1, 25+1),
    "FS_el_dxy"  : np.linspace(0, 0.05, 50+1),
    "FS_el_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_el_chg"  : np.linspace(-2, 2, 5+1),

    "FS_tau_pt"  : np.linspace(20, 100, 49+1), #0, 180, 36+1
    "FS_tau_eta" : np.linspace(-3, 3, 30+1),
    "FS_tau_phi" : np.linspace(-3.2, 3.2, 32+1),
    "FS_tau_dxy" : np.linspace(0, 0.20, 50+1),
    "FS_tau_dz"  : np.linspace(0, 0.25, 50+1),
    "FS_tau_chg" : np.linspace(-2, 2, 5+1),
    "FS_tau_DM"  : np.linspace(0, 19, 20+1),

    "FS_tau_rawPNetVSjet" : np.linspace(0, 1, 50+1),
    "FS_tau_rawPNetVSmu"  : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]), # plot logx
    "FS_tau_rawPNetVSe"   : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),
  },

  "mutau_TnP" : {
    "FS_mu_pt"   : np.linspace(0, 120, 40+1),
    "FS_mu_eta"  : np.linspace(-3, 3, 30+1),
    "FS_mu_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_mu_iso"  : np.linspace(0, 1, 25+1),
    "FS_mu_dxy"  : np.linspace(0, 0.025, 50+1),
    "FS_mu_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_mu_chg"  : np.linspace(-2, 2, 5+1),

    "FS_tau_pt"  : np.linspace(0, 180, 36+1),
    "FS_tau_eta" : np.linspace(-3, 3, 30+1),
    "FS_tau_phi" : np.linspace(-3.2, 3.2, 32+1),
    "FS_tau_dxy" : np.linspace(0, 0.20, 50+1),
    "FS_tau_dz"  : np.linspace(0, 0.25, 50+1),
    "FS_tau_chg" : np.linspace(-2, 2, 5+1),
    "FS_tau_DM"  : np.linspace(0, 19, 20+1),

    "FS_tau_rawPNetVSjet" : np.linspace(0, 1, 50+1),
    "FS_tau_rawPNetVSmu"  : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]), # plot logx
    "FS_tau_rawPNetVSe"   : np.array([0, 0.95, 0.96, 0.97, 0.98, 0.99, 1]),

    "pass_tag"   : np.linspace(0, 2, 2+1),
    "pass_probe"   : np.linspace(0, 2, 2+1),
  },

  "dimuon" : {
    "FS_m1_pt"   : np.linspace(0, 300, 60+1),
    "FS_m1_eta"  : np.linspace(-2.5, 2.5, 99+1),
    "FS_m1_phi"  : np.linspace(-3.2, 3.2, 64+1),
    "FS_m1_iso"  : np.linspace(0, 1, 25+1),
    "FS_m1_dxy"  : np.linspace(0, 0.05, 50+1),
    "FS_m1_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_m1_chg"  : np.linspace(-2, 2, 5+1),

    "FS_m2_pt"   : np.linspace(0, 300, 60+1),
    "FS_m2_eta"  : np.linspace(-2.5, 2.5, 99+1),
    "FS_m2_phi"  : np.linspace(-3.2, 3.2, 64+1),
    "FS_m2_iso"  : np.linspace(0, 1, 25+1),
    "FS_m2_dxy"  : np.linspace(0, 0.05, 50+1),
    "FS_m2_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_m2_chg"  : np.linspace(-2, 2, 5+1),
    "FS_m_vis_tight" : np.linspace(70, 110, 80+1),
  },
  #Naila
  "emu" : {
    "FS_el_pt"   : np.linspace(0, 120, 40+1),
    "FS_el_eta"  : np.linspace(-3, 3, 30+1),
    "FS_el_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_el_iso"  : np.linspace(0, 1, 25+1),
    "FS_el_dxy"  : np.linspace(0, 0.05, 50+1),
    "FS_el_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_el_chg"  : np.linspace(-2, 2, 5+1),

    "FS_mu_pt"   : np.linspace(0, 120, 40+1),
    "FS_mu_eta"  : np.linspace(-3, 3, 30+1),
    "FS_mu_phi"  : np.linspace(-3.2, 3.2, 32+1),
    "FS_mu_iso"  : np.linspace(0, 1, 25+1),
    "FS_mu_dxy"  : np.linspace(0, 0.025, 50+1),
    "FS_mu_dz"   : np.linspace(0, 0.25, 50+1),
    "FS_mu_chg"  : np.linspace(-2, 2, 5+1), #What is m_vis_tightfor muon in dimuon
  },  

  "common" : {
    # calculated on the fly
    "FS_mt"         : np.linspace(0, 200, 40+1),
    "FS_nbJet"      : np.linspace(0, 4, 4+1),
    "FS_acoplan"    : np.linspace(0, 1, 10+1),
    "nCleanJetGT30" : np.linspace(0, 8, 8+1), # GT(E) = Greater Than (Equal to)
    "CleanJetGT30_pt_1"  : np.linspace(0, 300, 60+1),
    "CleanJetGT30_pt_2"  : np.linspace(0, 300, 60+1),
    "CleanJetGT30_pt_3"  : np.linspace(0, 300, 60+1),
    "CleanJetGT30_eta_1" : np.linspace(-5, 5, 50+1),
    "CleanJetGT30_eta_2" : np.linspace(-5, 5, 50+1),
    "CleanJetGT30_eta_3" : np.linspace(-5, 5, 50+1),
    "CleanJetGT30_phi_1" : np.linspace(-3.2, 3.2, 32+1),
    "CleanJetGT30_phi_2" : np.linspace(-3.2, 3.2, 32+1),
    "CleanJetGT30_phi_3" : np.linspace(-3.2, 3.2, 32+1),
    "FS_mjj"    : np.linspace(0, 1500, 30+1),
    "FS_detajj" : np.linspace(0, 7, 31+1),

    # from branches
    "MET_pt"      : np.linspace(0, 150, 30+1),
    "MET_phi"     : np.linspace(-3.2, 3.2, 32+1),
    "PuppiMET_pt" : np.linspace(0, 150, 50+1),
    "PuppiMET_phi": np.linspace(-3.2, 3.2, 32+1),
    "nCleanJet"   : np.linspace(0, 8, 8+1),
    "CleanJet_pt" : np.linspace(20, 200, 30+1),
    "CleanJet_eta": np.linspace(-5, 5, 50+1),
    "HTT_DiJet_MassInv_fromHighestMjj" : np.linspace(0, 1500, 30+1),
    "HTT_DiJet_dEta_fromHighestMjj"    : np.linspace(0, 7, 35+1),
    "HTT_H_pt_using_PUPPI_MET"         : np.linspace(0, 300, 30+1),
    "HTT_dR"                : np.linspace(0, 6, 60+1),
    "HTT_m_vis-KSUbinning"  : np.linspace(0, 300, 30+1),
    "HTT_m_vis-SFbinning"   : np.linspace(0, 200, 40+1),
    "HTT_pT_l1l2" : np.linspace(0, 150, 30+1),
    "FastMTT_mT"   : np.linspace(0, 400, 40+1),
    "FastMTT_mass" : np.linspace(0, 400, 20+1),
    "FS_t1_flav" : np.linspace(0, 11, 11+1),
    "FS_t2_flav" : np.linspace(0, 11, 11+1),
    "PV_npvs"    : np.linspace(0, 90, 30+1),
  }
}
