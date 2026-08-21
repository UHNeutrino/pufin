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

GenieEventsPerChunk = 100000