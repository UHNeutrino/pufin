# could use hist.Draw("text") to draw text before making 6 plots!

import ROOT
import os
from array import array  # Use for ROOT-compatible arrays
import numpy as np 
import ParticlePlots as pp 
import Setup as s

s.setupRoot


# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")


file_path = "t2k-nova/FlatTrees/FLAT_NEUT_1.0GeV_1e7.root"
# dir_location = file_path
# fileName = f"{HOME}/{dir_location}"
# treeName = "FlatTree_VARS"

def constant_binning(x, y, file_path):
    # First get the data into a dataframe
    dir_location = file_path
    fileName = f"/data/{dir_location}"
    treeName = "FlatTree_VARS"
    df = ROOT.RDataFrame(treeName, fileName)


    histogramInfo = ("name", f"{y} vs {x} plot", 1000000, 0, 3, 1, 0, 3) #just need 1 bin in y


    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'
    df_filtered = df.Filter(cut1).Histo2D(histogramInfo, x, y)

    # Get the total number of events
    total_events = int(df_filtered.Integral())
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

def quantile_cutting(x, y, x_bins, file_path):
    """
    Returns:
    - A list of filtered RDataFrames, one for each quantile.
    """
    dir_location = file_path
    fileName = f"/data/{dir_location}"
    treeName = "FlatTree_VARS"  
    # Get each quantile into a separate dataframe
    df = ROOT.RDataFrame(treeName, fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")


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

def PlotQuantiles(x, y, histogramInfo, file_path, df, title, Normalize = 0):
    
    dir_location = file_path
    hist1 = df.Histo2D(histogramInfo,x,y)
    
    NameParts = s.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    
    hist = s.formatHist(NameParts, hist1 ,'Lepton Momentum', '(GeV)', 'cos #theta', '')
    if Normalize == 1:
       scale = 1/(hist.Integral())
       hist.Scale(scale)
       
    # **Set Z-axis max value**
    hist.SetMaximum(0.04)  # Ensures max value displayed is 0.04
    # Create a TLatex object to add text
    latex = ROOT.TLatex()
    latex.SetTextSize(0.05)  # Set the text size
    latex.SetTextAlign(22)   # Set text alignment to center (x=0.5, y=0.5)

    # Draw the text "hi" in the center of the canvas (normalized coordinates)
    latex.DrawLatexNDC(0.5, 0.5, "hi")
   
    c = ROOT.TCanvas()

    s.formatTcanvas(hist,c)
    ROOT.gStyle.SetOptStat(0)  # Remove statistics box
    c.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
        
    return hist 

def MultiPlot(histos, file_path):
    dir_location = file_path
    
    NameParts = s.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    # Create a canvas
    cFull = ROOT.TCanvas("cFull", "Canvas", 800, 600)

    # Set margins
    cFull.SetBottomMargin(0.25)
    cFull.SetLeftMargin(0.15)
    cFull.SetTopMargin(0.25)
    cFull.SetRightMargin(.15)

    # Divide the canvas into a 4x1 grid
    cFull.Divide(3, 2, 0, 0)

    # Set a color-blind friendly palette
    #ROOT.gStyle.SetPalette(112)  # kCividis (or use 111 for kViridis)
    # ROOT.gStyle.SetPalette(ROOT.kRainBow)    

    # Loop over list of histograms 
    for i in range(0, len(histos)):
        ROOT.gStyle.SetOptStat(0)  # Remove statistics box
        cFull.cd(i+1)  # Move to the correct sub-pad because pad 1 for root = histo 0 for python
        histos[i].SetStats(0)
        histos[i].SetTitle(";;")  # Remove titles
        histos[i].Draw("colz")  # Draw histogram 
        # If it's the first histogram, save the palette
        # if i == 0:
        #     palette = histos[i].GetListOfFunctions().FindObject("palette")

        #     # Remove the palette from the first histogram
        #     histos[i].GetListOfFunctions().Remove(palette)
        # else:
        #     histos[i].GetListOfFunctions().Remove(histos[i].GetListOfFunctions().FindObject("palette"))
        if i in [1, 2, 3, 4, 5]:  # Using a list

            histos[i].GetListOfFunctions().Remove(histos[i].GetListOfFunctions().FindObject("palette"))
                
    
        # Retrieve histogram title
        hist_title = histos[i].GetName()
        Plot_Title_Parts = hist_title.split('_')
        print(f"{Plot_Title_Parts}")

        # # # Add text box with histogram title
        title_text = ROOT.TLatex()
        title_text.SetTextSize(0.05)  # Adjust text size
        title_text.SetTextAlign(22)  # Center alignment
        title_text.SetNDC()  # Use normalized device coordinates
        title_text.DrawLatex(0.6, 0.45, Plot_Title_Parts[0])  # Position near top-center
        title_text.DrawLatex(0.6, 0.35, f"{Plot_Title_Parts[1]} events")
        #print(f"Histogram {i} title: {hist_title}")  # Debugging step
    
        # Go back to the main canvas to add a title and axis labels
    cFull.cd()


    # Add a global title
    title = ROOT.TLatex()
    title.SetTextSize(0.04)
    title.SetTextAlign(22)  # Center alignment
    title.DrawLatexNDC(0.5, 0.97, f"{NameParts[1]}: {NameParts[2]} 2P2H #nu_{{#mu}} events cut from {NameParts[3]} generated events")  # (x, y) in normalized device coordinates

    # Add X-axis label (centered at the bottom)
    xlabel = ROOT.TLatex()
    xlabel.SetTextSize(0.04)
    xlabel.SetTextAlign(22)
    xlabel.DrawLatexNDC(0.5, 0.02, "P_{#mu} (GeV)")  # Adjust as needed

    # Add Y-axis label (centered vertically on the left)
    ylabel = ROOT.TLatex()
    ylabel.SetTextSize(0.04)
    ylabel.SetTextAngle(90)  # Rotate text vertically
    ylabel.SetTextAlign(22)
    ylabel.DrawLatexNDC(0.02, 0.5, "COS #theta")  # Adjust as needed
    
    # Now, create a new pad for the palette, which will be placed outside the plotting region
    # cFull.SetRightMargin(0.45)  # Increase the right margin of the full canvas
    # cFull.Update()
    # palettePad = ROOT.TPad("palettePad", "palette", 0.80, 0.15, .98, .95)  # Adjust width to be more visible
    # palettePad.SetMargin(0, 0, 0, 0)  # Remove margins to fill the pad
    # #palettePad.SetLeftMargin(0)  # Adjust margins for better spacing
    # #palettePad.SetRightMargin(0)
    # palettePad.Draw()  # Draw the new pad

    # # Enter the palette pad to draw the palette
    # palettePad.cd()

    # # Draw the saved palette in the new pad
    # palette.Draw()

    # Save the canvas
    cFull.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/comparisons3.png")

if __name__ == "__main__":
    dir_location = file_path
    NameParts = s.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    # Make q0 vs q3 histogram to find quantiles with equal events
    x = 'q3'
    y = 'q0'
    
    
    x_bins, total_events = constant_binning(x, y, file_path=file_path)
    
    # Apply quantile_cutting to make a new dataframe for each quantile 
    quantile_dfs = quantile_cutting(x, y, x_bins, file_path=file_path)
        
    event_counts = {}  # Dictionary to store event counts
    # Check: Print the number of events in each quantile
    for i, df in enumerate(quantile_dfs):
        count = df.Count().GetValue()
        print(f"Quantile {i+1}: {count} events")
        event_counts[i] = count  # Store in dictionary
        
    # Make plots for each dataframe
    y = 'CosLep'
    x = 'PLep'
     
    histos = []  # Store histograms here in order to plot on divided canvas
    # Create and save a plot for each quantile
    for i, df in enumerate(quantile_dfs):
        # Define title to use as the name of the histogram for multiplot text
        lower_bound = x_bins[i]
        upper_bound = x_bins[i + 1]
        title = f"q3 range: {lower_bound:.2f} to {upper_bound:.2f} GeV_{event_counts[i]}"
        histInfo = (f"{title}", f"{y} vs {x} plot", 60, 0, 3.3, 102, -1.02, 1.02)
        hist = PlotQuantiles(x, y, histInfo, file_path=file_path, df=df, title = title, Normalize = 1)
        histos.append(hist)
    
    # Plot full q3 spectrum
    x = "PLep"
    y = "CosLep"
    
    # This is not working!
    # histInfo = (f"Full q3 Spectrum_{total_events}", f"{y} vs {x} 2P2H plot", 60, 0, 3.3, 102, -1.02, 1.02)

    # Generate the 2P2H histogram
    hist_Full2P2H, _ = pp.Plot2P2H(x, y, histInfo, file_path=file_path)
    scale = 1/(hist_Full2P2H.Integral())
    hist_Full2P2H.Scale(scale)
    hist_Full2P2H.SetMaximum(0.04)  # Ensures max value displayed is 0.04
    
    cfull2P2H = ROOT.TCanvas()
    s.formatTcanvas(hist_Full2P2H,cfull2P2H)
    
    title = hist_Full2P2H.GetName()
    print(f"{title}")
    cfull2P2H.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
    
    histos.append(hist_Full2P2H)
    MultiPlot(histos, file_path=file_path)
    






