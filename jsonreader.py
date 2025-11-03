import json5
import ROOT
import os
import datetime
import ParticlePlots as pp 
import SetupFunctions as sf
import PlotQuantiles as pq
import glob
import array

HOME = os.getenv("HOME", "/home/lboe")
sf.setupRoot
userFolder = f"/data/t2k-nova/FlatTrees"
# userFolder = f'{HOME}/t2k-nova/FlatTrees'
f = open(f'{HOME}/t2k-nova/main.json5')
data = json5.load(f)

quantiles = data.get("quantiles")
plots = data.get("plots")
stacks = data.get("stacks")
overlap = data.get("overlap")
same1D = data.get("1DSame")
Contour = data.get("Contour")

if (plots["Bool"]):
    root_files = glob.glob(userFolder + f'/*{plots["Gen"]}*{plots["Flux"]}*.root')
    if root_files == []:
        printMsg =  "NO such root files:"+f'/*{plots["Gen"]}*{plots["Flux"]}*.root'
        print(printMsg)

    for file_path in root_files:
        # print(file_path)
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        Tevents = file_name.split('_')[3]
        BinL = plots["Bins"]
        AxisInfo = []
        #df = pp.CreateDataFrame(file_path, plots["Cut"])
        df = pp.CreateDataFrame(file_path, cut ="None")
        if(plots["EvisB"]):
            df = pp.DefineEvis(df)  
        if (plots["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (plots["TkiB"]):
            df = pp.DefineTKI(df)
        if (plots["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)
        if plots.get("Cut"):
            df = df.Filter(plots["Cut"])
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)
        if(plots["reWeight"][0]):
            df = pp.defineWeightsSpline(df,plots["reWeight"][1],plots["reWeight"][2], Fscale = plots["reWeight"][3])
        if plots["Type"] == "1D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
            if(plots["reWeight"][0]):
                hist = df.Histo1D(histInfo,plots["Var1"],"weights")
            else:
                hist = df.Histo1D(histInfo,plots["Var1"])
        if plots["Type"] == "2D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
            if(plots["reWeight"][0]):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],"weights")
            else:
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"])
        if plots["Ext"] == "root":
            rootTitle = plots["Cut"]
            rootTitle = rootTitle.replace(" ","")
            out_file = ROOT.TFile(f"/data/t2k-nova/Histograms/{rootTitle}.root", "UPDATE")
            hist.Write()  # Write the histogram to the file
            out_file.Close()  # Close to finalize writing
        else:
            nx = datetime.datetime.now()
            x = str(nx)
            fileN = plots["Name"]+Tevents+generator+flux+x
            fileN = fileN.replace(" ", "-")
            pp.Savehist(hist,AxisInfo,plots["Save"],fileN,plots["Ext"],max = plots["max"], Normalize=plots["Norm"], logz = plots["logz"])

if (stacks["Bool"]):
    root_files = glob.glob(userFolder + f'/*{stacks["Gen"]}*{stacks["Flux"]}*.root')
    if root_files == []:
        print("NO such root files")

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        #df = pp.CreateDataFrame(file_path, stacks["Cut"])
        df = pp.CreateDataFrame(file_path, cut="None")
        BinL = stacks["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(stacks["EvisB"]):
            df = pp.DefineEvis(df)
        if(stacks["TkiB"]):
            df = pp.DefineTKI(df)
        if (stacks["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)
        if stacks.get("Cut"):
            df = df.Filter(stacks["Cut"])
        for word in stacks["AxisInfo"].split(','):
                AxisInfo.append(word)
        for cut,name in stacks["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for num in stacks["Colors"].split(","):
            colors.append(int(num))
        
        stack, histlist = pp.PlotStackedEventCuts(df, stacks["Var1"], histInfo, cuts, colors)
        save_L = stacks["Save"] + generator + '-' + flux + stacks["Name"] + "." +stacks["Ext"]
        pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,save_L, Normalize=stacks["Norm"])


if (overlap["Bool"]):
    root_files = glob.glob(userFolder + f'/*{overlap["Gen"]}*{overlap["Flux"]}*.root')
    if root_files == []:
        print("NO such root files")
        
    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        # df = pp.CreateDataFrame(file_path, overlap["Cut"])
        df = pp.CreateDataFrame(file_path, cut = "None")
        BinL = overlap["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(overlap["EvisB"]):
            df = pp.DefineEvis(df)
        if(overlap["TkiB"]):
            df = pp.DefineTKI(df)
        if (overlap["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)
        if overlap.get("Cut"):
            df = df.Filter(overlap["Cut"])
        for word in overlap["AxisInfo"].split(','):
                AxisInfo.append(word)
        for cut,name in overlap["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for num in overlap["Colors"].split(","):
            colors.append(int(num))
        
        histlist = pp.overlapPlots(df, overlap["Var1"], histInfo, cuts, colors)
        save_L = overlap["Save"] + generator + '-' + flux + overlap["Name"] + "." +overlap["Ext"]
        pp.SaveOverlapPlot(histlist, AxisInfo, Legend,save_L, Normalize=overlap["Norm"])
        
if (same1D["Bool"]):
    plots_list = same1D["Plots"]
    hist_dict = {}
    hist_rdfs = []  # Keep these alive to avoid ROOT segfaults
        
    AxisInfo = same1D["AxisInfo"].split(",")
    BinL = same1D["Bins"]
    xvar, xunit, yvar, yunit, PlotTitle = AxisInfo

    Add_Ratio = same1D.get("Add_Ratio", False)
    RatioOf = same1D.get("RatioOf", [])         
    RatioRange = same1D.get("RatioRange", [0.5, 1.5])
    c = ROOT.TCanvas()
    if Add_Ratio:
        topPad   = ROOT.TPad("topPad",   "top",   0.0, 0.30, 1.0, 1.0)
        ratioPad = ROOT.TPad("ratioPad", "ratio", 0.0, 0.00, 1.0, 0.30)
        topPad.SetBottomMargin(0.02)
        topPad.SetLeftMargin(0.18)
        ratioPad.SetTopMargin(0.06)
        ratioPad.SetBottomMargin(0.35)
        ratioPad.SetLeftMargin(0.18)
        ratioPad.SetGridy()

        topPad.Draw(); ratioPad.Draw()
        topPad.cd()
    else:
        c.SetLeftMargin(0.18)
        c.SetBottomMargin(0.12)
    ROOT.gStyle.SetOptStat(0)
    legend = ROOT.TLegend(0.6, 0.6, 0.89, 0.79) ## most plots
    #legend = ROOT.TLegend(0.3, 0.6, 0.59, 0.79) ## better for cos theta plots
    
    norm = same1D.get("Norm")
    logy = same1D.get("logy")
    kin = same1D.get("KinematicsB", False)
    Evis = same1D.get("EvisB", False)
    Tki = same1D.get("TkiB", False)
    Thresholds = same1D.get("ThresholdsB", False)
    
    histCounter = 0
    hist_order = []
    top_histo = True # so the top histo (drawn first) will not have x-labels
    for plot in plots_list:
        file = plot["File"]
        key = plot["Key"]
        color_str = plot["Color"]
        label = plot["Label"]
        reweight_flag, rw_file, rw_flux, Fscale = plot["reWeight"]
        Var = plot["Var"]
        hist_order.append(key)

        # Find matching file
        matches = glob.glob(f"{userFolder}/*{file}*.root")
        if not matches:
            print(f"No file found for key: {file}")
            continue

        file_path = matches[0]
        print(f"Processing {file_path}")

        #df = pp.CreateDataFrame(file_path, same1D["Cut"])
        df = pp.CreateDataFrame(file_path, cut = "None")
        unfiltered = df.Count().GetValue()
        df = df.Filter("Enu_true < 8.0 ")
        frakLost = 1.0 - df.Count().GetValue()/unfiltered
        print(f"Fraction lost from E Nu cut: {frakLost}")
        print(f"Events lost from E Nu cut: {unfiltered - df.Count().GetValue()}")
        print(f'Total Events {df.Count().GetValue()}')

        if Evis:
            df = pp.DefineEvis(df)
        if kin:
            df = pp.DefineKinematics(df)
        if Tki:
            df = pp.DefineTKI(df)
        if Thresholds:
            df = pp.FlagParticleThresholds(df)
        if same1D.get("Cut"):
            df = df.Filter(same1D["Cut"])
        if reweight_flag:
            df = pp.defineWeightsSpline(df, rw_file, rw_flux, Fscale = Fscale)
            weight_col = "weights"
        else:
            weight_col = ""
            
        bins = array.array('d',same1D["VBins"][1])

        histInfo = ("name", f"hist_{key}", BinL[0], BinL[1], BinL[2])
        # print("bins")
        # print(bins)
        # print("nbins")
        # print(len(bins) - 1)
        varBinInfo = ROOT.RDF.TH1DModel("h_varbins", f"hist_{key}", len(bins) - 1, bins)

        if same1D["VBins"][0]:
            histInfo = varBinInfo
        if weight_col:
            rdf_hist = df.Histo1D(histInfo, plot["Var"], weight_col)
        else:
            rdf_hist = df.Histo1D(histInfo, plot["Var"])

        hist_rdfs.append(rdf_hist)  # Keep RDF object alive
        hist = rdf_hist.GetValue()
        pp.HistoErrorBars(hist)
        if norm and hist.Integral() != 0:
            hist.Scale(1.0 / hist.Integral())
        #hist = sf.formatHist(rdf_hist.GetValue(), xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PlotTitle)
        hist = sf.formatHist(hist, xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PlotTitle)
        
        if Add_Ratio and top_histo:
            hist.GetXaxis().SetLabelSize(0)     # hide numbers
            hist.GetXaxis().SetTitleSize(0)     # hide title
            hist.GetXaxis().SetTickLength(0)    # hide ticks
            hist.GetXaxis().SetLabelOffset(999) # hide x axis labels
            top_histo = False
            
        color = getattr(ROOT, color_str.split("+")[0]) + int(color_str.split("+")[1]) if "+" in color_str else getattr(ROOT, color_str)
        hist.SetLineColor(color)
        hist.SetLineWidth(1)
        # if (histCounter == 0):
        #     hist.SetLineWidth(2)
        # ^This could be better

        if same1D["ErrorBars"]:
            draw_opt = "HIST E1" if len(hist_dict) == 0 else "HIST E1 SAME"
        else:
            draw_opt = "HIST" if len(hist_dict) == 0 else "HIST SAME"
        hist.Draw(draw_opt)
        legend.AddEntry(hist, label, "l")
        hist_dict[key] = hist
        histCounter += 1
    if logy:
        c.SetLogy()
        if Add_Ratio:
            topPad.SetLogy()
    else:
        print("NO LOG")
    if Add_Ratio:
        topPad.cd()
    legend.Draw("SAME")
    
    # Draw the Ratio Plot
    if Add_Ratio and len(hist_order) >= 2:
        # pick numerator / denominator
        if RatioOf and all(k in hist_dict for k in RatioOf[:2]):
            h_num = hist_dict[RatioOf[0]]
            h_den = hist_dict[RatioOf[1]]
            ratio_label = f"{RatioOf[0]}/{RatioOf[1]}"
        else:
            h_den = hist_dict[hist_order[0]]
            h_num = hist_dict[hist_order[1]]
            ratio_label = "second/first"

        # Make the ratio
        ratioPad.cd()
        h_ratio = h_num.Clone("h_ratio")
        h_ratio.SetDirectory(0)
        # Guard against zero bins in denominator; you can also sanitize bin-by-bin if needed
        h_ratio.Divide(h_den)

        # Style the ratio axes
        # -- Reset X axis that may have been hidden in the source histogram --
        xa = h_ratio.GetXaxis()
        xa.SetLabelOffset(0.01)   # undo the 999 offset
        xa.SetTickLength(0.04)    # visible ticks
        xa.SetTitleSize(0.12)
        xa.SetLabelSize(0.10)
        
        h_ratio.SetTitle("")
        h_ratio.GetYaxis().SetTitle(f"{RatioOf[0]} / {RatioOf[1]}")
        h_ratio.GetYaxis().SetNdivisions(505)
        h_ratio.GetYaxis().SetTitleSize(0.10)
        h_ratio.GetYaxis().SetTitleOffset(0.55)
        h_ratio.GetYaxis().SetLabelSize(0.10)
        h_ratio.GetXaxis().SetTitle(f"{xvar} {f'({xunit})' if xunit.strip() else ''}".strip())
        h_ratio.GetXaxis().SetTitleSize(0.12)
        h_ratio.GetXaxis().SetLabelSize(0.10)

        # Y-range if provided
        if RatioRange and len(RatioRange) == 2:
            h_ratio.SetMinimum(RatioRange[0])
            h_ratio.SetMaximum(RatioRange[1])

        h_ratio.SetLineColor(ROOT.kBlack)
        #h_ratio.Draw("E1")
        h_ratio.Draw()

        # Draw a horizontal line at 1
        xmin = h_ratio.GetXaxis().GetXmin()
        xmax = h_ratio.GetXaxis().GetXmax()
        line = ROOT.TLine(xmin, 1.0, xmax, 1.0)
        line.SetLineStyle(2)
        line.Draw("SAME")


    outname = f"{HOME}/{same1D['Save']}/{same1D['Name']}.{same1D['Ext']}"
    c.SaveAs(outname)

if (quantiles["Bool"]):
    file_name = input("Give Root File name: ")
    file_path1 = f"/data/t2k-nova/FlatTrees/{file_name}"
    #treeName = "FlatTree_VARS"
    df1 = pp.CreateDataFrame(file_path1, cut ="None")
    if(quantiles["EvisB"]):
        df1 = pp.DefineEvis(df1)  
    if (quantiles["KinematicsB"]):
        df1 = pp.DefineKinematics(df1)
    if (quantiles["TkiB"]):
        df1 = pp.DefineTKI(df1)
    if (quantiles["ThresholdsB"]):
        df1 = pp.FlagParticleThresholds(df1)
    if quantiles.get("Cut"):
        df1 = df.Filter(quantiles["Cut"])
    # df1 = ROOT.RDataFrame(treeName,file_path1)
    # df1 = df1.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    # df1 = pp.DefineKinematics(df1)
    # df1 = pp.DefineTKI(df1)

    Weight = False
    Flux =""
    
    if quantiles["reWeight"][0]:
        Weight = True
        Flux_parts = quantiles["reWeight"][1].split("/")
        if "NOvA" in Flux_parts[4]:
            Flux = "NOvA"
        else:
            Flux = "T2K"
        df1 = pp.defineWeightsSpline(df1, quantiles["reWeight"][1], quantiles["reWeight"][2], "flux1")
        
    df_filtered = df1.Filter(quantiles["cut"])
    
    # Run selected plot
    if quantiles["plot_type"] == "segments":
        pq.PlotSegments(
            file_path1, 
            quantiles["custom_quantiles"],
            quantiles["consistent_quantiles"],
            quantiles["x1"], 
            quantiles["y1"], 
            quantiles["x2"], 
            quantiles["y2"], 
            quantiles["xLabel"], 
            quantiles["yLabel"], 
            quantiles["mode_title"], 
            quantiles["mode_label"],
            quantiles["max_energy"],
            quantiles["AutoTitleB"],
            quantiles["Title"],
            quantiles["AutoNameB"],
            quantiles["SaveName"],
            quantiles["Save"],
            quantiles["Ext"],
            max = quantiles["zmax"], 
            min = quantiles["zmin"],
            df=df_filtered, 
            Weight=Weight,
            Flux=Flux, 
            scale=quantiles["logz"], 
            frequency=quantiles["zaxis"], 
            Normalize=quantiles["Norm"])
    #elif quantiles["plot_type"] == "grid":
        #pq.PlotGrid(file_path1, x1, y1, x2, y2, xLabel, yLabel, mode_title, mode_label, max_energy, df=df_filtered, scale=logz, frequency=zaxis, Normalize=Norm)
    elif quantiles["plot_type"] == "compare":
        file_name2 = input("Give Root File name: ")
        file_path2 = f"/data/t2k-nova/FlatTrees/{file_name2}"
        #treeName = "FlatTree_VARS"
        df1b = pp.CreateDataFrame(file_path2, cut ="None")
        if(quantiles["EvisB"]):
            df1b = pp.DefineEvis(df1b)  
        if (quantiles["KinematicsB"]):
            df1b = pp.DefineKinematics(df1b)
        if (quantiles["TkiB"]):
            df1b = pp.DefineTKI(df1b)
        if (quantiles["ThresholdsB"]):
            df1b = pp.FlagParticleThresholds(df1b)
        if quantiles.get("Cut"):
            df1b = df.Filter(quantiles["Cut"])
    
        # df1b = ROOT.RDataFrame(treeName,file_path2)
        # df1b = df1b.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
        # df1b = pp.DefineKinematics(df1b)
        # df1b = pp.DefineTKI(df1b)

        Flux2 =""
        if quantiles["reWeight2"][0]:
            Weight = True
            Flux_parts2 = quantiles["reWeight2"][1].split("/")
            if "NOvA" in Flux_parts2[4]:
                Flux2 = "NOvA"
            else:
                Flux2 = "T2K"
            df1b = pp.defineWeightsSpline(df1b, quantiles["reWeight2"][1], quantiles["reWeight2"][2], "flux2")
        
        df_filtered2 = df1b.Filter(quantiles["cut"])
        pq.PlotCompare(
            file_path1,
            file_path2,
            quantiles["custom_quantiles"],
            quantiles["consistent_quantiles"],
            quantiles["x1"], 
            quantiles["y1"], 
            quantiles["x2"], 
            quantiles["y2"], 
            quantiles["xLabel"], 
            quantiles["yLabel"], 
            quantiles["mode_title"], 
            quantiles["mode_label"],
            quantiles["max_energy"],
            quantiles["AutoTitleB"],
            quantiles["Title"],
            quantiles["AutoNameB"],
            quantiles["SaveName"],
            quantiles["Save"],
            quantiles["Ext"],
            max = quantiles["zmax"], 
            min = quantiles["zmin"],
            df=df_filtered, 
            df2=df_filtered2, 
            Weight=Weight,
            Flux=Flux,
            Flux2=Flux2, 
            scale=quantiles["logz"], 
            frequency=quantiles["zaxis"], 
            Normalize=quantiles["Norm"],
            Compare_type=quantiles["compare_type"])
    else:
        print("Invalid plot_type in config_PlotQuantiles.json5. Use 'segments', 'grid' or 'ratio'.")
    

if (Contour["Bool"]):
    root_files = glob.glob(userFolder + f'/*{Contour["Gen"]}*{Contour["Flux"]}*.root')
    if root_files == []:
        print("NO such root files")

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        #df = pp.CreateDataFrame(file_path, Contour["Cut"])
        df = pp.CreateDataFrame(file_path, cut ="None")
        BinL = Contour["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(Contour["EvisB"]):
            df = pp.DefineEvis(df)
            df = df.Filter("Evis_kin != -9999.9")
        if (Contour["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (Contour["TkiB"]):
            df = pp.DefineTKI(df)
        if (Contour["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)
        if Contour.get("Cut"):
            df = df.Filter(Contour["Cut"])
        if(Contour["reWeight"][0]):
            df = pp.defineWeightsSpline(df,Contour["reWeight"][1],Contour["reWeight"][2])
        for word in Contour["AxisInfo"].split(','):
                AxisInfo.append(word)
        if Contour["AutoQuant"][0]:
            x = Contour["AutoQuant"][1]
            y = Contour["AutoQuant"][2]
            # Get the total number of events
            histogramInfo = ("name", f"{y} vs {x} plot", 2000000, df.Min(x).GetValue(), df.Max(x).GetValue(), 1, 0, df.Max(y).GetValue()) #just need 1 bin in y
            if (df.HasColumn("weights")):
                cuthist = df.Histo2D(histogramInfo, x,y,"weights")
                print("weights activated1")
            else:
                cuthist = df.Histo2D(histogramInfo, x,y)
            total_events = int(cuthist.Integral())
            # print(f"Total events: {total_events}")
            # Define cumulative events array
            cumulative_events = [0]
            for i in range(1, cuthist.GetNbinsX() + 1):
                bin_total = sum(cuthist.GetBinContent(i, j) for j in range(1, cuthist.GetNbinsY() + 1))
                cumulative_events.append(cumulative_events[-1] + bin_total)

            # Now that we have cumulative events, let's split them into x sections
            x_bins = [df.Min(x).GetValue()]  # Start at -100
            target_events_per_section = total_events / Contour["AutoQuant"][4]

            for i in range(1, Contour["AutoQuant"][4]):  # Divide into i sections
                target = i * target_events_per_section
                # Find the first bin index where the cumulative event count exceeds the target
                bin_idx = min(range(len(cumulative_events)), key=lambda idx: abs(cumulative_events[idx] - target))
                x_bin_edge = cuthist.GetXaxis().GetBinLowEdge(bin_idx)
                x_bins.append(x_bin_edge)
            # Add the final bin edge to ensure full coverage
            x_bins.append(cuthist.GetXaxis().GetXmax())
            for i in range(len(x_bins) - 1):
                lower_bound = x_bins[i]
                upper_bound = x_bins[i + 1]

                # Define a filter string for the current quantile
                cuts.append(f"{lower_bound} <= {x} && {x} < {upper_bound}")
                Legend.append(f" {lower_bound:.2f} <= {x} < {upper_bound:.2f}")
            # save intermediary hist 
            if Contour["AutoQuant"][3]:
                save_L0 = Contour["Save"] + "/" + "INT" +Contour["Name"] + "." +Contour["Ext"]
                # c.SaveAs(save_L0)
                pp.SaveIntPlot(df,x,y,x_bins,save_L0)
        else:
            for cut,name in Contour["ConCuts"].items():
                cuts.append(cut)
                Legend.append(name)

        for num in Contour["Colors"].split(","):
            colors.append(int(num))
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
        print(AxisInfo)
        histlist = pp.PlotContEventCuts(df, Contour["Var1"], Contour["Var2"], histInfo, cuts, Contour["TotalPercents"])
        save_L = Contour["Save"]+ "/" + generator + '-' + flux + Contour["Name"] + "." +Contour["Ext"]
        if Contour["ContStyle"]:
            pp.SaveContHistStyles(histlist, AxisInfo, colors, Contour["styles"], Contour["Clabels"], Contour["Slabels"], save_L, Contour["logz"])
        else:
            pp.SaveContHist(histlist, AxisInfo, Legend, colors, Contour["TotalPercents"], save_L, Contour["logz"])
