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



#######################
# Particles Macro #####
#######################
import ParticlePlots as pp
import PlotQuantiles as pq
import glob
import os
import ROOT


HOME = os.getenv("HOME", "/home/lboe")


userFolder = f"/data/t2k-nova/FlatTrees"
root_files = glob.glob(userFolder + '/*NEUT*.root')

print(root_files)

max_frequency_1PI = -float('inf')  # Initialize with the smallest possible value
max_frequency_2P2H = -float('inf')

for file in root_files:
    # format correctly
    file_path = file.split('t2k-nova')[1]
    file_path = 't2k-nova' + file_path
  
    x = 'q3'
    y = 'q0' 
    
    AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
    histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    pp.SavePlot(hist,"1PI_W_vs_Q2", AxisInfo, path)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist, "1PI_hist_max", AxisInfo, path, max = .035, Normalize=1)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist,"1PI_hist_Normalized", AxisInfo,path, Normalize = 1)

    x = 'W'
    y = 'Q2'
    AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    pp.SavePlot(hist,"2P2H_q3_vs_q0", AxisInfo, path)
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist_max", AxisInfo, path, max = .016, Normalize = 1)
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist_Normalized", AxisInfo, path, Normalize = 1)


    # # Make q0 vs q3 histogram to find quantiles with equal events
    # x = 'q3'
    # y = 'q0'
    
    
    # x_bins, total_events = pq.constant_binning(x, y, file_path=file_path)
    
    # # Apply quantile_cutting to make a new dataframe for each quantile 
    # quantile_dfs = pq.quantile_cutting(x, y, x_bins, file_path=file_path)
    
    # # Check: Print the number of events in each quantile
    # for i, df in enumerate(quantile_dfs):
    #     print(f"Quantile {i+1}: {df.Count().GetValue()} events")
        
    # # Make plots for each dataframe
    # y = 'CosLep'
    # x = 'PLep'
    
    # #AxisInfo = ['cos{theta}', '', 'E Lep', '(GeV)'] not using this yet
    # histInfo = ("name", f"{y} vs {x} plot", 60, 0, 3.5,102, -1.02, 1.02)
    
    # # Create and save a plot for each quantile
    # for i, df in enumerate(quantile_dfs):
    #     # Define a title for the current quantile plot
    #     title = f"Quantile_{i+1}"
    #     pq.PlotQuantiles(x, y, histInfo, file_path=file_path, df = df, title = title)


    
# print(f"The highest frequency across all normalized 1PI plots is: {max_frequency_1PI}")
# print(f"The highest frequency across all normalized 2P2H plots is: {max_frequency_2P2H}")

# Now plot constant frequency (z axis) files using max_frequency_1PI and max_frequency_2P2H
# currently not fixed to reflect PP changes
fixed = False
if fixed:
    for file in root_files:
        # format correctly
        file_path = file.split('t2k-nova')[1]
        file_path = 't2k-nova' + file_path
        
        x = 'W'
        y = 'Q2'
        histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
        histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
        
        pp.Plot1PI(x,y,histInfo1,"1PI_hist_max",file_path, max = max_frequency_1PI, Normalize=1)
        
        x = 'q3'
        y = 'q0' 
        
        pp .Plot2P2H(x,y,histInfo2,"2P2H_hist_max",file_path, max = max_frequency_2P2H, Normalize=1)







#####################
## Quantiles Macro ##
#####################
import PlotQuantiles as pq
import ParticlePlots as pp
import SetupFunctions as sf
import os 
import glob

HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"
montecarlo = input("Enter the name of your montecarlo: NEUT, NOvA, or ICARUS. If you want to generate plots for all Flat Trees in the directory hit 'enter' ")

#root_files = glob.glob(userFolder + '/*NOvA*.root')
root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')
print(f"Root Files: {root_files}")

modeDic = sf.modeDic()

print("Making File Plots: ")

for file_path in root_files :

    pq.PlotSegments(file_path=file_path)
    pq.PlotGrid(file_path=file_path)
