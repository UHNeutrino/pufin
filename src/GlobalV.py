# List of Global Variables used elsewhere:

Flavors = ["NuMu","NuMuBar","NuE","NuEBar"]

FlavorToNuType = {
    "NuMu": "numu",
    "NuMuBar": "numubar",
    "NuE": "nue",
    "NuEBar": "nuebar",
}

targetpdg = {
    "Carbon":1000060120,
    "Hydrogen":1000010010,
    "Oxygen":1000080160,
    "Titanium":1000220480,
    "Chlorine":1000170350,
    "Argon":1000180400,
}
NeutTargetLabels = {
    "Carbon":"C12",
    "Hydrogen":"H1",
    "Oxygen":"O16",
    "Titanium":"Ti48"
}
NeutLabelTargets ={
    "C12":"Carbon",
    "H1":"Hydrogen",
    "O16":"Oxygen",
    "Ti48":"Titanium"
}
NeutCardTargets = {
    "Carbon":"NEUT-NUMBNDN 6 \n NEUT-NUMBNDP 6 \n NEUT-NUMATOM 12 \n NEUT-NUMFREP 0 \n",
    "Hydrogen":"NEUT-NUMBNDN 6 \n NEUT-NUMBNDP 6 \n NEUT-NUMATOM 12 \n NEUT-NUMFREP 10000 \n",
    "Oxygen":"NEUT-NUMBNDN 8 \n NEUT-NUMBNDP 8 \n NEUT-NUMATOM 16 \n NEUT-NUMFREP 0 \n",
    "Titanium":"NEUT-NUMBNDN 26 \n NEUT-NUMBNDP 22 \n NEUT-NUMATOM 48 \n NEUT-NUMFREP 0 \n",
    "Chlorine": "NOOOOOOOOOOOOOOO"
}
FGD1 = {
    "Carbon": 0.8537,
    "Hydrogen":.07503,
    "Oxygen":0.04472,
    "Titanium":0.1632
}

NeutCardModes = {"CC": "NEUT-CRS 1 1 1 1 1 0 0 0 0  0  0  0  0  1  0  1  0  0  1  0  0  0  1  0  1  0  0  1  1  0\n",
                 "NC": "NEUT-CRS 0 0 0 0 0 1 1 1 1  1  1  1  1  0  1  0  1  1  0  1  1  1  0  1  0  1  1  0  0  1\n"}
AntiNeutCardModes = {"CC": "NEUT-CRSB 1 1 1 1 1 0 0 0 0  0  0  0  0  1  0  1  0  0  1  0  0  0  1  0  1  0  0  1  1  0\n",
                 "NC": "NEUT-CRSB 0 0 0 0 0 1 1 1 1  1  1  1  1  0  1  0  1  1  0  1  1  1  0  1  0  1  1  0  0  1\n"}

NeutCardFlavors = {"NuMu": "EVCT-IDPT 14 \n",
                    "NuMuBar":"EVCT-IDPT -14 \n",
                    "NuE": "EVCT-IDPT 12 \n",
                    "NuEBar": "EVCT-IDPT -12 \n"}
NeutCardTunes = {
    "Prod7E":"""EVCT-MPOS 1
EVCT-POS  0. 0. 0.
EVCT-MDIR 1
EVCT-DIR 0. 0. 1.
EVCT-MPV 3
EVCT-INMEV 0
NEUT-PAUL 1
NEUT-IRADCORR 2
NEUT-MODE   -1
NEUT-MAQE 1.21
NEUT-MDLQE 402
NEUT-SFCORRNNFRAC 0.3
NEUT-MDL2P2H 2
NEUT-RAND 0
NEUT-QUIET 2
EVCT-FILENM 'flat_flux_0-8GeV.root'
EVCT-HISTNM 'FlatHist'
NEUT-RAND 1""",
    "Nuis": """EVCT-MPOS 1
EVCT-POS  0. 0. 0.
EVCT-MDIR 1
EVCT-DIR 0. 0. 1.
EVCT-MPV 3
EVCT-INMEV 0
NEUT-MODE -1
NEUT-MDL2P2H 2
NEUT-MDLQE 402
EVCT-FILENM 'flat_flux_0-8GeV.root'
EVCT-HISTNM 'FlatHist'
NEUT-RAND 1
"""
}

NuPDGs = {
    12: "NuE",
    -12: "NuEBar",
    14: "NuMu",
    -14: "NuMuBar",
}

NovaTargets = {
    "C": {
        "name": "Carbon",
        "label": "C12",
        "pdg": "1000060120[1.0]",
    },
    "H": {
        "name": "Hydrogen",
        "label": "H1",
        "pdg": "1000010010[1.0]",
    },
    "O": {
        "name": "Oxygen",
        "label": "O16",
        "pdg": "1000080160[1.0]",
    },
    "Cl": {
        "name": "Chlorine",
        "label": "Cl35",
        "pdg": "1000170350[1.0]",
    },
    "Ti": {
        "name": "Titanium",
        "label": "Ti48",
        "pdg": "1000220480[1.0]",
    },
    "Ar": {
        "name": "Argon",
        "label": "Ar40",
        "pdg": "1000180400[1.0]",
    },

}

GenFlavorScales = {
    "NuMu": 1.0,
    "NuMuBar": 0.1,
    "NuE": 0.01,
    "NuEBar": 0.01,
}

GenModeScales = {
    "CC": 1.0,
    "NC": 0.1,
}

T2KRWPresets = {
    "Test":{
        "dial":"PionFSI_AbsProb",
        "value":3.0,
        "group_name":"Pion Abs Test",
        "value_name":"3Sigma",
        "description":"Just a preset with a single dial to see if this works"
    }
}
T2KRWDialPresets = {
    "NeutAll": [
        "MaCCQE",
        "MaRES",
        "CA5RES",
        "BgSclRES",
        "NucleonFSI_Double",
        "NucleonFSI_Elastic",
        "NucleonFSI_Single",
        "NucleonFSI_Total",
        "RadCorr_rate"
    ],
    "ZeroToOne":[
        "SRCFrac_C",
        "SRCFrac_O",
        "MECTwkDial_2p2hEdep_highEnu",
        "MECTwkDial_2p2hEdep_highEnubar"
        "MECTwkDial_2p2hEdep_lowEnu",
        "MECTwkDial_2p2hEdep_lowEnubar",
        "SF_PBTwkDial_NuclMom_C12_nu",
        "SF_PBTwkDial_NuclMom_piProd_C12",
        "SF_PBTwkDial_NuclMom_O16_nu",
        "SF_PBTwkDial_NuclMom_piProd_O16",
        "SF_OptPotTwkDial_C12",
        "SF_OptPotTwkDial_O16",
    ],
    "NeutPionList":[    
        "PionFSI_AbsProb",
        "PionFSI_QELowMomProb",
        "PionFSI_QEHighMomProb",
        "PionFSI_CExLowMomProb",
        "PionFSI_CExHighMomProb",
        "PionFSI_InelProb"
    ],
    "NIWGList":[
    "QETwk_LowQ2Weight_1",
    "QETwk_LowQ2Weight_2",
    "QETwk_LowQ2Weight_3",
    "QETwk_LowQ2Weight_4",
    "QETwk_HighQ2Weight_1",
    "QETwk_HighQ2Weight_2",
    "QETwk_HighQ2Weight_3",
    "SF_P1_2Shell_MeanF_Norm_O",
    "SF_P1_2Shell_MeanF_PMissShape_O",
    "SF_P3_2Shell_MeanF_Norm_O",
    "SF_P3_2Shell_MeanF_PMissShape_O",
    "SF_PShell_MeanF_Norm_C",
    "SF_PShell_MeanF_PMissShape_C",
    "SF_SShell_MeanF_Norm_C",
    "SF_SShell_MeanF_Norm_O",
    "SF_SShell_MeanF_PMissShape_C",
    "SF_SShell_MeanF_PMissShape_O",
    "SF_SRC_Norm_C",
    "SF_SRC_Norm_O",
    "MECTwkDial_Norm_C12",
    "MECTwkDial_Norm_O16",
    "MECTwkDial_Norm_Other",
    "MECTwkDial_PDDWeight_C12",
    "MECTwkDial_PDDWeight_C12_NN",
    "MECTwkDial_PDDWeight_C12_np",
    "MECTwkDial_PDDWeight_O16",
    "MECTwkDial_PDDWeight_O16_NN",
    "MECTwkDial_PDDWeight_O16_np",
    "MECTwkDial_PNNN_Shape",
    "TwkDial_FateNucleonFSI",
    "SPPTwk_LowQ2Suppression", 
    "SPP_Pi0Norm",
    "SPPTwk_LowPpi2020",
    "AdHocPiMom_CC_n_pim",
    "AdHocPiMom_CC_n_pip",
    "AdHocPiMom_CC_p_pim",
    "AdHocPiMom_CC_p_pip",
    "CC_Coh_Norm",
    "RES_Eb_C_numu",
    "RES_Eb_C_numubar",
    "RES_Eb_O_numu",
    "RES_Eb_O_numubar",
    "DIS_BY_corr_on_off",
    "DIS_BY_corr_on_off_evgentemplates",
    "MultiPi_BY_corr_on_off",
    "MultiPi_BY_corr_on_off_evgentemplates",
    "MultiPi_BY_Vector",
    "MultiPi_BY_Axial",
    "MultiPi_BY_SeaQFrac",
    "MultiPi_BY_RLongMod",
    "MultiPi_Multiplicity_TotXSec",
    "MultiPi_Multiplicity_Shape",
    "DIS_BY_corr_on_off_NC",
    "MultiPi_BY_corr_on_off_NC",
    "MultiPi_Multiplicity_Shape_NC",
    "MultiPi_Multiplicity_TotXSec_NC",
    "SF_toCRPASuSAv2HybridTwkDial",
    "SF_toCRPATwkDial",
    "SF_toHFTwkDial",
    "SF_toLFGTwkDial",
    "SF_toSuSAv2TwkDial",
    "Nuc_NueNumuTwkDial_C12_nu",
    "Nuc_NueNumuTwkDial_O16_nu",
    "Nuc_NueNumuTwkDial_C12_nubar",
    "Nuc_NueNumuTwkDial_O16_nubar"
    ]
}
