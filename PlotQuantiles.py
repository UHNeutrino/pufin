# could use hist.Draw("text") to draw text before making 6 plots!

# to change x variable (ex: muon momentum, proton momentum):
# change xlabel around line 349 and variable around line 269, 391, & 397

# Set log scale in PlotQuantiles (line 245) and MultiPlot (line 265)

# change binning between q0 and q3 by switching x1 and y1 (line 370) - choose x1 to be the variable you want to cut quantiles

import ROOT
import os
import ParticlePlots as pp 
import SetupFunctions as SF
import glob

SF.setupRoot
#max1 = 3000

# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")

userFolder = f"/data/t2k-nova/FlatTrees"
# Use this option to run 1 file (change file name):
#root_files = glob.glob(userFolder + '/*GenieNOvA_3.0*.root')

# Use this option to run all files, or all files for a specific generator:
# montecarlo = input("Enter the name of your montecarlo: NEUT, NOvA, or AR23. If you want to generate plots for all Flat Trees in the directory hit 'enter'")
# root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')

# Use this option to run all files for a specific flux:
flux = input("Enter the flux of the root files you want to select: 0.5, 0.6, 0.7, 1.0, 1.5, 2.0, 3.0: ")
root_files = glob.glob(userFolder + f'/*{flux}*.root')

print(f"Root Files: {root_files}")

for file_path in root_files:
    file_name = file_path.split('/')[-1]
    generator = file_name.split('_')[1]
    flux = file_name.split('_')[2]


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

        histogramInfo = ("name", f"{y} vs {x} plot", 1000000, 0, 3, 1, 0, 3) #just need 1 bin in y


        # Mode 2 is the 2P2H interaction
        if Mode is not None:
            cut1 = f'Mode == {Mode}'
        else:   
            cut1 = 'Mode == 1'
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

    def quantile_cutting(x, x_bins, file_path):
        
        
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

            print(f"Quantile {i+1}: Events between {lower_bound} and {upper_bound}: {quantile_df.Count().GetValue()}")
        
        return quantile_dfs

    def grid_cutting(x, y, x_bins, y_bins, file_path):
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


        # Mode 2 is the 2P2H interaction
        cut1 = 'Mode == 2'
        df_filtered = df.Filter(cut1)

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



    def PlotQuantiles(x, y, histogramInfo, file_path, df, title, Normalize = 0, max = None):
        
        dir_location = file_path
        hist1 = df.Histo2D(histogramInfo,x,y)
        
        NameParts = SF.formatName(dir_location)
        Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
        
        hist = SF.formatHist(hist1 ,'Lepton Momentum', '(GeV)', 'cos #theta', '',NameParts = NameParts)
        if Normalize == 1:
            scale = 1/(hist.Integral())
            hist.Scale(scale)
        
        # **Set Z-axis max value**
        #if max is not None:
            #hist.SetMaximum(max)  # Ensures max value displayed is 0.04

        # Create a TLatex object to add text
        latex = ROOT.TLatex()
        latex.SetTextSize(0.05)  # Set the text size
        latex.SetTextAlign(22)   # Set text alignment to center (x=0.5, y=0.5)
    
        c = ROOT.TCanvas()
        #c.SetLogz()
        SF.formatTcanvas(hist,c)
        #ROOT.gStyle.SetOptStat(0)  # Remove statistics box
        #c.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
        #c.SaveAs(f"{HOME}/t2k-nova/{title}_{Name}.png")
        return hist 

    def MultiPlot(histos, slice, x, file_path):
        dir_location = file_path
        
        NameParts = SF.formatName(dir_location)
        # Create a canvas
        cFull = ROOT.TCanvas("cFull", "Canvas with Subdivisions", 1200, 800)  


        # Set margins
        cFull.SetBottomMargin(0.25)
        cFull.SetLeftMargin(0.25)
        cFull.SetTopMargin(0.25)
        cFull.SetRightMargin(.15)
        #cFull.SetLogz()

        # --- Draw the dummy histogram to generate the color scale ---
        x = "PLep"
        #x = "PProton1"
        y = "CosLep"
        histInfo = ("dummy_hist", "", 60, 0, 3.3, 102, -1.02, 1.02)

        # Generate the full 2P2H histogram as the dummy histogram
        dummy_hist, _ = pp.Plot2P2H(x, y, histInfo, file_path=file_path, Normalize = 1)
        #dummy_hist.SetMaximum(.35)

        ROOT.gStyle.SetOptStat(0)
        #ROOT.gStyle.SetPalette(ROOT.kRainBow)
        ROOT.gStyle.SetPalette(ROOT.kBird)

        dummy_hist.Draw("COLZ")  # Draw the full dummy histogram with legend
        dummy_hist.SetStats(0)
        dummy_hist.GetZaxis().SetTitle("")
        dummy_hist.GetZaxis().SetLabelSize(0.06)
        dummy_hist.GetZaxis().SetTitleSize(0.06)
        dummy_hist.GetZaxis().SetTitleOffset(1.2)

        cFull.Update()  # Ensure the color legend is drawn

        # --- Cover the dummy histogram with a white rectangle ---
        cover = ROOT.TPaveText(0.0, 0.0, 0.1, 1.0, "NDC")  # Covers 85% of the canvas
        cover.SetFillColor(ROOT.kWhite)  # White background to hide dummy histogram
        cover.SetBorderSize(0)
        cover.Draw()

        cFull.Update()  # Refresh the canvas after covering
        
        hist_pad = ROOT.TPad("hist_pad", "Histograms", 0.04, 0.04, 0.88, .95)  # Left side for histograms
        hist_pad.Divide(3, 2)
        hist_pad.Draw()

        hist_pad.cd()

        # Loop over list of histograms 
        for i in range(0, len(histos)):
            #ROOT.gStyle.SetOptStat(0)  # Remove statistics box
            hist_pad.cd(i+1)  # Move to the correct sub-pad because pad 1 for root = histo 0 for python
            histos[i].SetStats(0)
            histos[i].SetTitle(";;")  # Remove titles
            if i==0:
                histos[i].Draw("colz")  # Draw full histogram with scale - take off "z" to get rid of scale
            else:
                 histos[i].Draw("colz")   # Draw sub-histograms with scale - take off "z" to get rid of scale
        
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
        title.SetTextSize(0.04)
        title.SetTextAlign(22)  # Center alignment
        title.DrawLatexNDC(0.5, 0.97, f"{NameParts[1]}: {NameParts[2]} 2P2H #nu_{{#mu}} events cut from {NameParts[3]} generated events (binned in {slice})")  # (x, y) in normalized device coordinates

        # Add X-axis label (centered at the bottom) - CHANGE X-LABEL WHEN NEEDED!!!!
        xlabel = ROOT.TLatex()
        xlabel.SetTextSize(0.04)
        xlabel.SetTextAlign(22)
        xlabel.DrawLatexNDC(0.5, 0.02, "P_{#mu} (GeV/c)")  # Adjust as needed
        #xlabel.DrawLatexNDC(0.5, 0.02, "P_{Leading Proton} (GeV/c)")  # Adjust as needed

        # Add Y-axis label (centered vertically on the left)
        ylabel = ROOT.TLatex()
        ylabel.SetTextSize(0.04)
        ylabel.SetTextAngle(90)  # Rotate text vertically
        ylabel.SetTextAlign(22)
        ylabel.DrawLatexNDC(0.02, 0.5, "COS #theta")  # Adjust as needed
        
        ROOT.gPad.Update()
        cFull.Update()
        # Save the canvas
        cFull.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{generator}_{NameParts[2]}_2P2H_{slice}_Quantiles_{x}.png")
        #cFull.SaveAs(f"{HOME}/t2k-nova/test.png")

    def PlotSegments(file_path):
        dir_location = file_path
        NameParts = SF.formatName(dir_location)
        Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
        
        # Make q0 vs q3 histogram to find quantiles with equal events
        x1 = 'q3'
        y1 = 'q0'
        
        # Now define slice after x1 and y1 exist
        slice = x1  
        
        x_bins, total_events = constant_event_binning(x1, y1, file_path=file_path, Mode=2)
        
        # Apply quantile_cutting to make a new dataframe for each quantile 
        quantile_dfs = quantile_cutting(x1, x_bins, file_path=file_path)
            
        event_counts = {}  # Dictionary to store event counts
        # Check: Print the number of events in each quantile
        for i, df in enumerate(quantile_dfs):
            count = df.Count().GetValue()
            print(f"Quantile {i+1}: {count} events")
            event_counts[i] = count  # Store in dictionary
            
        # Make plots for each dataframe
        y = 'CosLep'
        x = 'PLep'
        #x = 'PProton1'
        
        histos = []  # Store histograms here in order to plot on divided canvas
        
        # Plot full q3/q0 spectrum
        x = "PLep"
        #x = "PProton1"
        y = "CosLep"
        histInfo = (f"Full {slice} Spectrum_{total_events}", f"{y} vs {x} 2P2H plot", 60, 0, 3.3, 102, -1.02, 1.02)

        # Generate the full 2P2H histogram
        hist_Full2P2H, _ = pp.Plot2P2H(x, y, histInfo, file_path=file_path, Normalize = 1)

        # max = hist_Full2P2H.GetMaximum()
        #hist_Full2P2H.SetMaximum(max) 
        

        cfull2P2H = ROOT.TCanvas()
        #cfull2P2H.SetLogz() I don't think we need this here for log scale
        SF.formatTcanvas(hist_Full2P2H,cfull2P2H)
        
        title = hist_Full2P2H.GetName()
        print(f"{title}")
        #cfull2P2H.SaveAs(f"{HOME}/t2k-nova/plots_quantiles/{title}_{Name}.png")
        histos.append(hist_Full2P2H)
        
        # Create and save a plot for each quantile
        for i, df in enumerate(quantile_dfs):
            # Define title to use as the name of the histogram for multiplot text
            lower_bound = x_bins[i]
            upper_bound = x_bins[i + 1]
            title = f"{slice} range: {lower_bound:.2f} to {upper_bound:.2f} GeV_{event_counts[i]}"
            histInfo = (f"{title}", f"{y} vs {x} plot", 60, 0, 3.3, 102, -1.02, 1.02)
            #hist = PlotQuantiles(x, y, histInfo, file_path=file_path, df=df, title = title, Normalize = 1, max=.03)
            hist = PlotQuantiles(x, y, histInfo, file_path=file_path, df=df, title = title, Normalize = 1)
        
            #hist.SetMaximum(max1)
            #hist.SetMaximum(max)
            histos.append(hist)
        

        MultiPlot(histos, slice, x, file_path=file_path)

    def PlotGrid(file_path):
        # dir_location = file_path
        # NameParts = SF.formatName(dir_location)
        # Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
        # Make q0 vs q3 histogram to find quantiles with equal events
        x1 = 'q0'
        y1 = 'q3'
        
        x_bins, total_events = constant_event_binning(x1, y1, file_path=file_path)
        y_bins, total_events = constant_event_binning(y1,x1, file_path=file_path)
        
        # Apply quantile_cutting to make a new dataframe for each quantile 
        quantile_dfs = grid_cutting(x1, y1, x_bins, y_bins, file_path=file_path)
            
        event_counts = {}  # Dictionary to store event counts
        # Check: Print the number of events in each quantile
        k=0
        for i in range(len(x_bins)-1):
            for j in range(len(y_bins)-1):
                count = quantile_dfs[k].Count().GetValue()
                print(f"Grid {i+1}, {j+1}: {count} events")
                event_counts[i] = count  # Store in dictionary
                k+=1
            
        # Make plots for each dataframe
        y = 'CosLep'
        x = 'PLep'
        
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
                histInfo = (f"{title}", f"{y} vs {x} plot", 60, 0, 3.3, 102, -1.02, 1.02)
                hist = PlotQuantiles(x, y, histInfo, file_path=file_path, df=quantile_dfs[k], title = title)
                histos.append(hist)
                k+=1


    if __name__ == "__main__":
        #file_name = input("Give Root File name: ")
        #file_path = f"/data/t2k-nova/FlatTrees/{file_name}"
        # file_path = 't2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e7.root'


        # x = 'q3'
        # y = 'q0' 
        # x_bins, total_events = constant_event_binning(x, y, file_path, Mode = 1)
        # histInfo2 = ("name",f"1P1H {x} vs {y} plot",60,0,3,60,0,3)
        # AxisInfo = ['q_{0}', '(GeV)','q_{3}', '(GeV)']
        # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path, Mode = 2)
        # visualize_segements(hist, file_path, x_bins=x_bins)
        PlotSegments(file_path=file_path)
        # PlotGrid(file_path=file_path)




    
    






