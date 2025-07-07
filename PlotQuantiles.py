import json5 as json
import ROOT
import os
import ParticlePlots as pp 
import SetupFunctions as SF
import glob

############## Set Up Plot Variables with config_PlotQuantiles.json5 First!!!! ######################
#################################################################################################

SF.setupRoot

# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"

def visualize_segements(hist, file_path, x_bins = None,  y_bins = None):
    title = "Sliced_q0vq3"
    NameParts = SF.formatName(file_path)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]

    hist = SF.formatHist( hist, 'q_{0}', '(GeV)','q_{3}', '(GeV)',NameParts=NameParts)
    c = ROOT.TCanvas()
    SF.formatTcanvas(hist,c)
    line_list = ROOT.TList()
    line_list2 = ROOT.TList()

    if x_bins is not None and y_bins is None:
        for i in range(1,len(x_bins)-1):
            print(f"saving line {i} at {x_bins[i]}")
            myline = ROOT.TLine(x_bins[i],0,x_bins[i],3)
            line_list.Add(myline)
            line_list[-1].Draw()
        c.SaveAs(f"{HOME}/t2k-nova/plots/2p2h{title}_q0_{Name}.png")
    elif y_bins is not None and x_bins is None:
        for i in range(1,len(y_bins)-1):
            print(f"saving line {i} at {y_bins[i]}")
            myline = ROOT.TLine(0,y_bins[i],3,y_bins[i])
            line_list.Add(myline)
            line_list[-1].Draw()
        c.SaveAs(f"{HOME}/t2k-nova/plots/{title}_q3_{Name}.png")

    else:
        for i in range(1,len(x_bins)-1):
            print(f"saving line {i} at {x_bins[i]}")
            myline = ROOT.TLine(x_bins[i],0,x_bins[i],3)
            line_list.Add(myline)
            line_list[-1].Draw()
        for i in range(1,len(y_bins)-1):
            print(f"saving line {i} at {y_bins[i]}")
            myline = ROOT.TLine(0,y_bins[i],3,y_bins[i])
            line_list2.Add(myline)
            line_list2[-1].Draw()  
        c.SaveAs(f"{HOME}/t2k-nova/plots/{title}_grid_{Name}.png")  

def constant_event_binning(x, y, file_path, Mode = None):
    # First get the data into a dataframe
    dir_location = file_path
    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"
    df = ROOT.RDataFrame(treeName, fileName)

    histogramInfo = ("name", f"{y} vs {x} plot", 1000000, 0, max_energy, 1, 0, max_energy) #just need 1 bin in y


    # Select Mode
    if Mode is not None:
        cut1 = f'Mode == {Mode}'
    else:   
        cut1 = cut
        
    df_filtered = df.Filter(cut1).Histo2D(histogramInfo, x, y)

    # Get the total number of events
    total_events = int(df_filtered.Integral())
    # print(f"Total events: {total_events}")

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

def quantile_cutting(x, x_bins, file_path, cut):
    
    """
    Returns:
    - A list of filtered RDataFrames, one for each quantile.
    """
    dir_location = file_path
    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"  
    # Get each quantile into a separate dataframe
    df = ROOT.RDataFrame(treeName, fileName)
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
    double cos_proton = -5.0;
    double max_proton_p = -1.0;
    int max_index = -1;

    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) {
            double p = std::sqrt(px[i]*px[i] + py[i]*py[i] + pz[i]*pz[i]);
            if (p > max_proton_p) {
                max_proton_p = p;
                max_index = i;
            }
        }
    }

    if (max_index >= 0 && max_proton_p > 0) {
        cos_proton = pz[max_index] / max_proton_p;
    }

    return cos_proton;
    """)

    df_filtered = df.Filter(cut)

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

        print(f"Quantile {i+1}: Events between {lower_bound} and {upper_bound}: {quantile_df.Count().GetValue()}")
    
    return quantile_dfs

def grid_cutting(x, y, x_bins, y_bins, file_path, cut):
    """
    Returns:
    - A list of filtered RDataFrames, one for each grid.
    """
    dir_location = file_path
    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"  
    # Get each quantile into a separate dataframe
    df = ROOT.RDataFrame(treeName, fileName)
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
    double cos_proton = -5.0;
    double max_proton_p = -1.0;
    int max_index = -1;

    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) {
            double p = std::sqrt(px[i]*px[i] + py[i]*py[i] + pz[i]*pz[i]);
            if (p > max_proton_p) {
                max_proton_p = p;
                max_index = i;
            }
        }
    }

    if (max_index >= 0 && max_proton_p > 0) {
        cos_proton = pz[max_index] / max_proton_p;
    }

    return cos_proton;
    """)
        
    df_filtered = df.Filter(cut)

    # Create a list to hold filtered DataFrames for each quantile
    grid_dfs = []

    # Loop through each quantile defined by x_bins
    for i in range(len(x_bins) - 1):
        x_lower_bound = x_bins[i]
        x_upper_bound = x_bins[i + 1]


        for j in range(len(y_bins) - 1 ):
            y_lower_bound = y_bins[j]
            y_upper_bound = y_bins[j+1]

            print()
            # Define a filter string for the current quantile
            cut_x = f"{x_lower_bound} <= {x} && {x} < {x_upper_bound}"
            cut_y = f"{y_lower_bound} <= {y} && {y} < {y_upper_bound}"
            
            # Apply the filter
            grid_df_x = df_filtered.Filter(cut_x)
            grid_df = grid_df_x.Filter(cut_y)
            grid_dfs.append(grid_df)
            # print(f"Events after x cut: {grid_df_x.Count().GetValue()} after both cuts: {grid_df.Count().GetValue()}")
            # print(f"Grid {i+1}, {j+1}: {grid_df.Count().GetValue()} Events within {x}: {x_lower_bound}-{x_upper_bound} and {y}: {y_lower_bound}-{y_upper_bound}")
    
    return grid_dfs



def PlotQuantiles(x, y, histogramInfo, file_path, df, title, xLabel, yLabel, mode_title, mode_label):
    ## mode_title for plot; mode_label for saving
    dir_location = file_path  
    hist1 = df.Histo2D(histogramInfo,x,y)
    NameParts = SF.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    
    hist = SF.formatHist(hist1 ,f'{xLabel}', '(GeV)', f'{mode_title} Grid: {yLabel}', '',NameParts = NameParts) 

    # Create a TLatex object to add text
    latex = ROOT.TLatex()
    latex.SetTextSize(0.05)  # Set the text size
    latex.SetTextAlign(22)   # Set text alignment to center (x=0.5, y=0.5)

    c = ROOT.TCanvas()
    
    SF.formatTcanvas(hist,c)
    #c.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
    #c.SaveAs(f"{HOME}/t2k-nova/{title}_{Name}.png")
    return hist 

def MultiPlot(histos, slice, x, file_path, scale, frequency, Normalize, max, xLabel, yLabel, mode_title, mode_label): 
    ## histos = list of histograms to plot
    ## x is plotting variable x 
    ## scale (boolean: true = logz); frequency (boolean: true = show z color axis); Normalize (boolean: true = normalize); max (int or "None")
    ## mode_title for plot; mode_label for saving
    
    dir_location = file_path
    file_name = file_path.split('/')[-1]
    generator = file_name.split('_')[1]
    flux = file_name.split('_')[2]
    
    NameParts = SF.formatName(dir_location)
    

    # Create a canvas
    cFull = ROOT.TCanvas("cFull", "Canvas with Subdivisions", 1200, 800)  


    # Set margins
    cFull.SetBottomMargin(0.25)
    cFull.SetLeftMargin(0.25)
    cFull.SetTopMargin(0.25)
    cFull.SetRightMargin(.25)

    ROOT.gStyle.SetOptStat(0)
    #ROOT.gStyle.SetPalette(ROOT.kRainBow)
    ROOT.gStyle.SetPalette(ROOT.kBird)
    
    hist_pad = ROOT.TPad("hist_pad", "Histograms", 0.04, 0.04, .95, .95)  # Left side for histograms
    hist_pad.Divide(3, 2)
    hist_pad.Draw()

    hist_pad.cd()

    # Loop over list of histograms 
    for i in range(0, len(histos)):
        #ROOT.gStyle.SetOptStat(0)  # Remove statistics box
        hist_pad.cd(i+1)  # Move to the correct sub-pad because pad 1 for root = histo 0 for python
        
        # **Adjust the margins of the current sub-pad**
        ROOT.gPad.SetLeftMargin(0.15)   # Increase left margin
        ROOT.gPad.SetRightMargin(0.15)  # Increase right margin
        ROOT.gPad.SetTopMargin(0.05)    # Increase top margin
        ROOT.gPad.SetBottomMargin(0.05) # Increase bottom margin
        
        histos[i].SetStats(0)
        histos[i].SetTitle(";;")  # Remove titles
        if scale:
            ROOT.gPad.SetLogz()
        if frequency:
            histos[i].Draw("colz")
        else:
            histos[i].Draw("col")
        if Normalize:
            normal = 1/(histos[i].Integral())
            histos[i].Scale(normal)
        if max is not None and max != "None":
            histos[i].SetMaximum(max) 
        elif max == "None":
            histos[i].SetMaximum()
        # Retrieve histogram title
        hist_title = histos[i].GetName()
        Plot_Title_Parts = hist_title.split('_')
        Plot_Title_0_Parts = Plot_Title_Parts[0].split(':')
        selected_events = int(Plot_Title_Parts[1])
        percent = round((selected_events / 1e7*100), 2)
        print(f"{Plot_Title_Parts}")

        # # # Add text box with histogram title
        title_text = ROOT.TLatex()
        title_text.SetTextSize(0.05)  # Adjust text size
        title_text.SetTextAlign(22)  # Center alignment
        title_text.SetNDC()  # Use normalized device coordinates
        title_text.DrawLatex(0.6, 0.55, f"{Plot_Title_0_Parts[0]}:")  # Position near top-center
        if len(Plot_Title_0_Parts) > 1:
            title_text.DrawLatex(0.6, 0.45, f"{Plot_Title_0_Parts[1]}")
        title_text.DrawLatex(0.6, 0.35, f"{Plot_Title_Parts[1]} events")
        title_text.DrawLatex(0.6, 0.25, f"{percent}%")
        title_text.DrawLatex(0.6, 0.15, "of total generated")
        #print(f"Histogram {i} title: {hist_title}")  # Debugging step

    
    # Add a global title
    cFull.cd()  # Return to full canvas
    title = ROOT.TLatex()
    title.SetTextSize(0.035)
    title.SetTextAlign(22)  # Center alignment
    if AutoTitleB:
        title.DrawLatexNDC(0.5, 0.97, f"{NameParts[1]}: {NameParts[2]} {mode_title} #nu_{{#mu}} events cut from {NameParts[3]} generated events (binned in {slice})")  # (x, y) in normalized device coordinates
    else:
        title.DrawLatexNDC(0.5, 0.97, f"{Title}")
    # Add X-axis label (centered at the bottom) 
    xlabel = ROOT.TLatex()
    xlabel.SetTextSize(0.04)
    xlabel.SetTextAlign(22)
    #xlabel.DrawLatexNDC(0.5, 0.02, "P_{#mu} (GeV/c)")  # Adjust as needed
    xlabel.DrawLatexNDC(0.5, 0.02, f"P_{{{xLabel}}} (GeV/c)")

    # Add Y-axis label (centered vertically on the left)
    ylabel = ROOT.TLatex()
    ylabel.SetTextSize(0.04)
    ylabel.SetTextAngle(90)  # Rotate text vertically
    ylabel.SetTextAlign(22)
    ylabel.DrawLatexNDC(0.02, 0.5, f"{yLabel}")  # Adjust as needed
    
    ROOT.gPad.Update()
    cFull.Update()
    # Save the canvas
    #cFull.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{generator}_{NameParts[2]}_{mode_label}_{slice}_Quantiles_{x}.png")
    #cFull.SaveAs(f"{HOME}/t2k-nova/test.png")
    if AutoNameB:
        cFull.SaveAs(f"{HOME}/{Save}/{generator}_{NameParts[2]}_{mode_label}_{slice}_Quantiles_{x}.{Ext}")
    else:
        cFull.SaveAs(f"{HOME}/{Save}/{Name}.{Ext}")

def PlotSegments(file_path, x1, y1, cut, x2, y2, xLabel, yLabel, mode_title, mode_label, scale, frequency, Normalize): 
    # x1 and y1 binning variables; x2 and y2 plotting variables
    # mode_title plotting title; mode_label saving title
    # scale (boolean: true = logz); frequency (boolean: true = show z color axis); Normalize (boolean: true = normalize); max (int or "None")
    dir_location = file_path
    NameParts = SF.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    
    histos = []  # Store histograms here in order to plot on divided canvas
    
    # Make q0 vs q3 histogram to find quantiles with equal events 
    slice = x1 
    x_bins, total_events = constant_event_binning(x1, y1, file_path=file_path, Mode=None)
    
    # Plot full q3/q0 spectrum in x2 and y2 variables
    # Generate the full events histogram
    df1=pp.CreateDataFrame(file_path, cut=cut)
    df1 = df1.Define("PProton1", """
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
    df1 = df1.Define("CosProton", """
    double cos_proton = -5.0;
    double max_proton_p = -1.0;
    int max_index = -1;

    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) {
            double p = std::sqrt(px[i]*px[i] + py[i]*py[i] + pz[i]*pz[i]);
            if (p > max_proton_p) {
                max_proton_p = p;
                max_index = i;
            }
        }
    }

    if (max_index >= 0 && max_proton_p > 0) {
        cos_proton = pz[max_index] / max_proton_p;
    }

    return cos_proton;
    """)
    
    histInfo = (f"Full {slice} Spectrum_{total_events}", f"{y2} vs {x2} {cut} plot", 60, 0, max_energy, 102, -1.02, 1.02)
    hist_AllEvents = df1.Histo2D(histInfo,x2,y2)
    cAllEvents = ROOT.TCanvas()
    
    SF.formatTcanvas(hist_AllEvents,cAllEvents)
    
    title = hist_AllEvents.GetName()
    print(f"{title}")
    #cAllEvents.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
    histos.append(hist_AllEvents)
    
    # Apply quantile_cutting to make a new dataframe for each quantile 
    quantile_dfs = quantile_cutting(x1, x_bins, file_path=file_path, cut=cut)
        
    event_counts = {}  # Dictionary to store event counts
    # Check: Print the number of events in each quantile
    for i, df in enumerate(quantile_dfs):
        count = df.Count().GetValue()
        print(f"Quantile {i+1}: {count} events")
        event_counts[i] = count  # Store in dictionary
    
    # Create and save a plot for each quantile
    for i, df in enumerate(quantile_dfs):
        # Define title to use as the name of the histogram for multiplot text
        lower_bound = x_bins[i]
        upper_bound = x_bins[i + 1]
        title = f"{slice} range: {lower_bound:.2f} to {upper_bound:.2f} GeV_{event_counts[i]}"
        histInfo = (f"{title}", f"{y2} vs {x2} plot", 60, 0, max_energy, 102, -1.02, 1.02)
        hist = PlotQuantiles(x2, y2, histInfo, file_path=file_path, df=df, title = title, xLabel=xLabel, yLabel=yLabel, mode_title=mode_title, mode_label=mode_label)
        histos.append(hist)
    

    MultiPlot(histos, slice, x2, file_path=file_path, scale=scale, frequency=frequency, Normalize=Normalize, max = max, xLabel=xLabel, yLabel=yLabel, mode_title=mode_title, mode_label=mode_label)


# Need to add scale, frequency, Normalize and max to this function!!!
def PlotGrid(file_path, x1, y1, cut, x2, y2, xLabel, yLabel, mode_title, mode_label, scale, frequency, Normalize):
    # x1 and y1 binning variables; x2 and y2 plotting variables
    # mode_title plotting title; mode_label saving title
    # scale (boolean: true = logz); frequency (boolean: true = show z color axis); Normalize (boolean: true = normalize); max (int or "None")
    dir_location = file_path
    NameParts = SF.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    
    # Make q0 vs q3 histogram to find quantiles with equal events
    slice = x1
    x_bins, total_events = constant_event_binning(x1, y1, file_path=file_path, Mode=None)
    y_bins, total_events = constant_event_binning(y1,x1, file_path=file_path, Mode=None)
    
    # Apply quantile_cutting to make a new dataframe for each quantile 
    quantile_dfs = grid_cutting(x1, y1, x_bins, y_bins, file_path=file_path, cut=cut)
        
    event_counts = {}  # Dictionary to store event counts
    # Check: Print the number of events in each quantile
    k=0
    for i in range(len(x_bins)-1):
        for j in range(len(y_bins)-1):
            count = quantile_dfs[k].Count().GetValue()
            print(f"Grid {i+1}, {j+1}: {count} events")
            event_counts[i] = count  # Store in dictionary
            k+=1
    
    histos = []  # Store histograms here in order to plot on divided canvas
    # Create and save a plot for each quantile
    k=0
    for i in range(len(x_bins) -1 ):
        # Define title to use as the name of the histogram for multiplot text
        x_lower_bound = x_bins[i]
        x_upper_bound = x_bins[i + 1]

        for j in range(len(y_bins)-1):
            y_lower_bound = y_bins[j]
            y_upper_bound = y_bins[j + 1]


            title = f"Grid{i+1}_{j+1}_{x1}_{x_lower_bound:.2f}-{x_upper_bound:.2f}_{y1}_{y_lower_bound}-{y_upper_bound}"
            histInfo = (f"Full {slice} Spectrum_{total_events}", f"{y2} vs {x2} {cut} plot", 60, 0, max_energy, 102, -1.02, 1.02)
            hist = PlotQuantiles(x2, y2, histInfo, file_path=file_path, df=quantile_dfs[k], title = title, xLabel=xLabel, yLabel=yLabel, mode_title=mode_title, mode_label=mode_label)
            c = ROOT.TCanvas()
            ## add functions to grab scale, frequency, Normalize
            if scale:
                c.SetLogz()
            if frequency:
                hist.Draw("colz")
            else:
                hist.Draw("col")
            if Normalize:
                normal = 1/(histos[i].Integral())
                hist.Scale(normal)
            if max is not None and max != "None":
                hist.SetMaximum(max) 
            elif max == "None":
                hist.SetMaximum()
            #hist.Draw("COLZ") # Or whatever draw option you prefer
            histos.append(hist)
            c.SaveAs(f"{HOME}/t2k-nova/{mode_label}-{x2}:grid{k}.png")
            k+=1
    
if __name__ == "__main__":
    # Load config from JSON
    # with open("config_PlotQuantiles.json5") as f:
    #     config = json.load(f)
        
    with open("main.json5") as f:
        all_config = json.load(f)
    config = all_config.get("quantiles", {})

        
    file_name = input("Give Root File name: ")
    file_path1 = f"/data/t2k-nova/FlatTrees/{file_name}"
    
    # Assign config variables
    globals().update(config)  # Makes all config keys accessible as variables
    
    # Run selected plot
    if config.get("plot_type") == "segments":
        PlotSegments(file_path1, x1, y1, cut, x2, y2, xLabel, yLabel, mode_title, mode_label, scale=logz, frequency = zaxis, Normalize=Norm)
    elif config.get("plot_type") == "grid":
        PlotGrid(file_path1, x1, y1, cut, x2, y2, xLabel, yLabel, mode_title, mode_label, scale=logz, frequency=zaxis, Normalize=Norm)
    else:
        print("Invalid plot_type in config_PlotQuantiles.json5. Use 'segments' or 'grid'.")
