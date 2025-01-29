import ROOT
import os
from array import array  # Use for ROOT-compatible arrays
import numpy as np 
import ParticlePlots as pp 

ROOT.gStyle.SetStatX(0.85)  # Closer to the left edge
ROOT.gStyle.SetStatY(0.9)  # Slightly below the top edge

# Apply a modern color palette
ROOT.gStyle.SetPalette(ROOT.kRainBow)  # Choose a visually pleasing palette
ROOT.gStyle.SetNumberContours(50)     # Increase the number of colors in the gradient


# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")

file_path="t2k-nova/FlatTrees/Flat_GenieNOvA_.7GeV_10E6.root"
dir_location = file_path
fileName = f"{HOME}/{dir_location}"
treeName = "FlatTree_VARS"

def constant_binning(x, y):
    # First get the data into a dataframe
    df = ROOT.RDataFrame(treeName, fileName)

    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'
    df_filtered = df.Filter(cut1).Histo2D(histogramInfo, x, y)

    # Get the total number of events
    total_events = df_filtered.Integral()
    print(f"Total events: {total_events}")

    # Define cumulative events array
    cumulative_events = [0]
    for i in range(1, df_filtered.GetNbinsX() + 1):
        bin_total = sum(df_filtered.GetBinContent(i, j) for j in range(1, df_filtered.GetNbinsY() + 1))
        cumulative_events.append(cumulative_events[-1] + bin_total)

    # Now that we have cumulative events, let's split them into 5 sections
    x_bins = [0]  # Start at 0
    target_events_per_section = total_events / 5

    for i in range(1, 5):  # Divide into 5 sections
        target = i * target_events_per_section

        # Find the first bin index where the cumulative event count exceeds the target
        bin_idx = min(range(len(cumulative_events)), key=lambda idx: abs(cumulative_events[idx] - target))
        x_bin_edge = df_filtered.GetXaxis().GetBinLowEdge(bin_idx)
        x_bins.append(x_bin_edge)

    # Add the final bin edge to ensure full coverage
    x_bins.append(df_filtered.GetXaxis().GetXmax())

    print(f"x-axis bins (5 equal-event sections): {x_bins}")

    return x_bins, total_events

def quantile_cutting(x, y, x_bins):
    """
    Returns:
    - A list of filtered RDataFrames, one for each quantile.
    """
    # Get each quantile into a separate dataframe
    df = ROOT.RDataFrame(treeName, fileName)
                         
    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'
    df_filtered = df.Filter(cut1)

    # Create a list to hold filtered DataFrames for each quantile
    quantile_dfs = []

    # Loop through each quantile defined by x_bins
    for i in range(len(x_bins) - 1):
        lower_bound = x_bins[i]
        upper_bound = x_bins[i + 1]

        # Define a filter string for the current quantile
        cut_quantile = f"{lower_bound} <= {x} && {x} < {upper_bound}"
        
        # Apply the filter
        quantile_df = df_filtered.Filter(cut_quantile)
        quantile_dfs.append(quantile_df)

        print(f"Quantile {i+1}: Events between {lower_bound} and {upper_bound}")
    
    return quantile_dfs

def PlotQuantiles(x, y, histogramInfo):
   
    hist1 = df.Histo2D(histogramInfo,x,y)
    
    NameParts = pp.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    
    hist = pp.formatHist(NameParts, hist1 ,'cos theta', '', 'E Lep', '(GeV)')
   
    c = ROOT.TCanvas()

    pp.formatTcanvas(hist,c)
    
    c.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
        
    return hist 

if __name__ == "__main__":
    # Make q0 vs q3 histogram to find quantiles with equal events
    x = 'q3'
    y = 'q0'
    histogramInfo = ("name", f"{y} vs {x} plot", 1200, 0, 3, 1, 0, 3) #just need 1 bin in y
    
    x_bins, total_events = constant_binning(x, y)
    
    # Apply quantile_cutting to make a new dataframe for each quantile 
    quantile_dfs = quantile_cutting(x, y, x_bins)
    
    # Check: Print the number of events in each quantile
    for i, df in enumerate(quantile_dfs):
        print(f"Quantile {i+1}: {df.Count().GetValue()} events")
        
    # Make plots for each dataframe
    x = 'CosLep'
    y = 'ELep'
    
    #AxisInfo = ['cos{theta}', '', 'E Lep', '(GeV)'] not using this yet
    histInfo = ("name", f"{y} vs {x} plot", 20, 0, 1, 60, 0, 3)
    
    # Create and save a plot for each quantile
    for i, df in enumerate(quantile_dfs):
        # Define a title for the current quantile plot
        title = f"Quantile_{i+1}"
        PlotQuantiles(x, y, histInfo)
        
    






