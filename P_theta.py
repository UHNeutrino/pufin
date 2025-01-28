import ROOT
import os
from array import array  # Use for ROOT-compatible arrays
import numpy as np 
import ParticlePlots.py as pp 



ROOT.gStyle.SetStatX(0.85)  # Closer to the left edge
ROOT.gStyle.SetStatY(0.9)  # Slightly below the top edge

# Apply a modern color palette
ROOT.gStyle.SetPalette(ROOT.kRainBow)  # Choose a visually pleasing palette
ROOT.gStyle.SetNumberContours(50)     # Increase the number of colors in the gradient


# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")


def formatName(dir_location):
    fileName = f"{HOME}/{dir_location}"
    treeName = "FlatTree_VARS"
    parts = fileName.split('/')
    NameRoot = parts[5]
    NameParts = NameRoot.split('_')
    NameParts[3] = NameParts[3].split('.root')[0]
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    return fileName, treeName, NameParts, Name

def formatHist(NameParts, hist, xvar, xunit, yvar, yunit, max = -1):
    hist.SetStats(1) #1 for a legend 0 for no legend
    hist.GetXaxis().SetTitle(f"{xvar} {xunit}")
    hist.GetYaxis().SetTitle(f"{yvar} {yunit}")
    if max != -1:
        hist.SetMaximum(max)
    hist.SetTitle(f"{yvar} vs. {xvar} ({NameParts[1]}: {NameParts[3]} #nu_{{#mu}} events at {NameParts[2]})")
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)

    return hist.Clone()

def formatTcanvas(hist, c):
    # Adjust margins; Default is 0.1; increase as needed
    c.SetLeftMargin(0.15)  # Adjust the left margin to avoid cutting off the y-axis label
    c.SetRightMargin(0.15) #Adjust the right margin to make space for the legend
    c.SetBottomMargin(0.15) #Adjust the bottom margin to avoid cutting off the x-axis label
    hist.Draw("COLZ")
    # c.SetCanvasSize(600,500)
    c.SetCanvasSize(c.GetWw()+200,c.GetWh())

def constant_binning(x, y, file_path):
    # First get the data into a dataframe
    dir_location = file_path
    fileName, treeName, NameParts, Name = formatName(dir_location)
    df = ROOT.RDataFrame(treeName,fileName)
                         
    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'
    df_filtered = df.Filter(cut1).Histo2D(histogramInfo,x,y)
    
    # Get the total number of events
    total_events = df_filtered.Integral()
    print(f"Total events: {total_events}")
    
    # Define y-axis bins (60 bins from 0 to 3)
    y_bins = np.linspace(0, 3, 60)
    
    # Define x-axis bins based on equal-event sections
    cumulative_events = np.zeros(df_filtered.GetNbinsX() + 1)
    for i in range(1, df_filtered.GetNbinsX() + 1):
        cumulative_events[i] = cumulative_events[i - 1] + sum(df_filtered.GetBinContent(i, j) for j in range(1, df_filtered.GetNbinsY() + 1))
        
    x_bins = [0]  # Start at 0
    target_events_per_section = total_events / 5
    for i in range(1, 5):
        target = i * target_events_per_section
        bin_idx = np.searchsorted(cumulative_events, target, side='right')
        if bin_idx < len(cumulative_events):
            x_bin_edge = df_filtered.GetXaxis().GetBinUpEdge(int(bin_idx))
            x_bins.append(x_bin_edge)

    # Add the final bin edge to ensure full coverage
    x_bins.append(df_filtered.GetXaxis().GetXmax())
           
    print(f"x-axis bins (5 equal-event sections): {x_bins}")
    
    return x_bins, total_events

def quantile_cutting(x, y, x_bins, file_path):
    """
    Further divides events into 5 quantiles based on x_bins from constant_binning.
    
    Parameters:
    - x: The variable representing the x-axis.
    - y: The variable representing the y-axis.
    - x_bins: The bin edges calculated by constant_binning.
    - file_path: The path to the ROOT file.

    Returns:
    - A list of filtered RDataFrames, one for each quantile.
    """
    # First get the data into a dataframe
    dir_location = file_path
    fileName, treeName, NameParts, Name = formatName(dir_location)
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

    
def Plot2P2H_custom_bins(x_val, y_val, x_bins, y_bins, title, file_path):
    dir_location = file_path
    fileName, treeName, NameParts, Name = formatName(dir_location)
    df = ROOT.RDataFrame(treeName,fileName)
                         
    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'
    df_filtered = df.Filter(cut1)
    
    # Create a 2D histogram with the custom bins
    hist_custom = ROOT.TH2D(
        "hist_custom",
        f"{y_val} vs {x_val} (custom binning)",
        len(x_bins) - 1, array('d', x_bins),  # Custom x-axis bins
        len(y_bins) - 1, array('d', y_bins)  # Custom y-axis bins
    )
    
    # Convert the filtered data to NumPy arrays
    data_numpy = df_filtered.AsNumpy(columns=[x_val, y_val])
    x_data = data_numpy[x_val]
    y_data = data_numpy[y_val]

    # Fill the histogram with the NumPy data
    for x, y in zip(x_data, y_data):
        hist_custom.Fill(x, y)

    hist = formatHist(NameParts, hist_custom, 'cos theta', '(degrees)', 'ELep', '(GeV)')
    
    c = ROOT.TCanvas()

    formatTcanvas(hist, c)
    c.SaveAs(f"{HOME}/t2k-nova/plots_constant_q3/{title}_{NameParts[1]}_{NameParts[3]}.png")

    return hist

if __name__ == "__main__":
    x = 'q3'
    y = 'q0'
    histogramInfo = ("name", f"{y} vs {x} plot", 60, 0, 3, 60, 0, 3)
    
    x_bins, total_events = constant_binning(
        x, y, file_path="t2k-nova/FlatTrees/Flat_GenieNOvA_.7GeV_10E6.root")
    
    y_bins = np.linspace(0, 3, 60)
    
    # Plot using the custom histogram
    x_val = 'CosLep'
    y_val = 'ELep'
    Plot2P2H_custom_bins(x_val, y_val, x_bins, y_bins, "2P2H_hist", "t2k-nova/FlatTrees/Flat_GenieNOvA_.7GeV_10E6.root")








