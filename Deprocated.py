import ROOT
# This holds all deprocated functions:


####################
# Particle Plots####
####################
def Plot2P2H(x, y, histogramInfo, file_path = None, Mode = None, Normalize = 0, max = None):
    # First get the data into a dataframe
    if file_path is None:
        dir_location = input("Give Full Flat Tree Directory Location: ")
    else:
        dir_location = file_path
    
    
    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"
    print(fileName)

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    
    df = df.Define("PProton1", """
    double max_proton_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) { // Proton
            double p_magnitude = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
            if (p_magnitude > max_proton_p) {
                max_proton_p = p_magnitude;
            }
        }
    }
    return max_proton_p;
    """)

    df = df.Define("CosProton", """
    double cos_proton = -5.0; // Default value if no proton found
    double max_proton_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) { // Proton
        double p_magnitude = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
        if (p_magnitude > max_proton_p) {
            max_proton_p = p_magnitude;
        }
        }
        if (max_proton_p > 0) {
            cos_proton = pz[i] / max_proton_p; // Dot product with (0, 0, 1)
        }
    }
    return cos_proton;
    """)                    

    # Mode 2 is the 2P2H interaction
    if Mode is not None:
        cut1 = f'Mode == {Mode}'

    else:
        cut1 = 'Mode == 2'
    hist = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    if Normalize==1:
        scale = 1/(hist.Integral())
        hist.Scale(scale)
    
    # **Set Z-axis max value**
    # if max is not None:
    #     hist.SetMaximum(max)  # Ensures max value displayed is consistent
    
    return hist, file_path


def Plot1PI(x, y, histogramInfo, file_path = None):
    if file_path is None:
        dir_location = input("Give Full Flat Tree Directory Location: ")
    else:
        dir_location = file_path

    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    
    
    # Modes for single Pi are 11-16
    cut1 = 'Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 '
    hist = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    return hist, file_path

def Create2DHistogram(df,x,y,histInfo):
    hist = df.Histo2D(histInfo,x,y)
    return hist

def Create1DHistogram(df,x,histInfo):
    hist = df.Histo1D(histInfo,x)
    return hist
