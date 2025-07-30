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
        print("NO such root files")

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        BinL = plots["Bins"]
        AxisInfo = []
        df = pp.CreateDataFrame(file_path, plots["Cut"])
        if(plots["EvisB"]):
            df = pp.DefineEvis(df)  
        if (plots["KinematicsB"]):
            df = pp.DefineKinematics(df)
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)
        if(plots["reWeight"][0]):
            df = pp.defineWeightsSpline(df,plots["reWeight"][1],plots["reWeight"][2])
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
            fileN = generator+flux+plots["Name"]+x
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
        df = pp.CreateDataFrame(file_path, stacks["Cut"])
        BinL = stacks["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(stacks["EvisB"]):
            df = pp.DefineEvis(df)
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
        df = pp.CreateDataFrame(file_path, overlap["Cut"])
        BinL = overlap["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(overlap["EvisB"]):
            df = pp.DefineEvis(df)
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

    c = ROOT.TCanvas()
    c.SetLeftMargin(0.18)
    c.SetBottomMargin(0.12)
    ROOT.gStyle.SetOptStat(0)
    legend = ROOT.TLegend(0.6, 0.6, 0.89, 0.79) ## most plots
    #legend = ROOT.TLegend(0.3, 0.6, 0.59, 0.79) ## better for cos theta plots
    
    norm = same1D.get("Norm")
    logz = same1D.get("logz")
    kin = same1D.get("KinematicsB", False)
    Evis = same1D.get("EvisB", False)
    histCounter = 0
    for plot in plots_list:
        
        key = plot["Key"]
        color_str = plot["Color"]
        label = plot["Label"]
        reweight_flag, rw_file, rw_flux = plot["reWeight"]
        spline = plot["Spline"]

        # Find matching file
        matches = glob.glob(f"{userFolder}/*{key}*.root")
        if not matches:
            print(f"No file found for key: {key}")
            continue

        file_path = matches[0]
        print(f"Processing {file_path}")

        df = pp.CreateDataFrame(file_path, same1D["Cut"])
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
        if reweight_flag:
            if spline:
                df = pp.defineWeightsSpline(df, rw_file, rw_flux)
            else:
                df = pp.defineWeights(df, rw_file, rw_flux)
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
            rdf_hist = df.Histo1D(histInfo, same1D["Var"], weight_col)
        else:
            rdf_hist = df.Histo1D(histInfo, same1D["Var"])

        hist_rdfs.append(rdf_hist)  # Keep RDF object alive
        hist = rdf_hist.GetValue()
        pp.HistoErrorBars(hist)
        if norm and hist.Integral() != 0:
            hist.Scale(1.0 / hist.Integral())
        hist = sf.formatHist(rdf_hist.GetValue(), xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PlotTitle)
        
        color = getattr(ROOT, color_str.split("+")[0]) + int(color_str.split("+")[1]) if "+" in color_str else getattr(ROOT, color_str)
        hist.SetLineColor(color)
        hist.SetLineWidth(1)
        if (histCounter == 0):
            hist.SetLineWidth(2)
        # ^This could be better

        if same1D["ErrorBars"]:
            draw_opt = "HIST E1" if len(hist_dict) == 0 else "HIST E1 SAME"
        else:
            draw_opt = "HIST" if len(hist_dict) == 0 else "HIST SAME"
        hist.Draw(draw_opt)
        legend.AddEntry(hist, label, "l")
        hist_dict[key] = hist
        histCounter += 1
    if logz:
        c.SetLogz()
    legend.Draw("SAME")

    outname = f"{HOME}/{same1D['Save']}/{same1D['Name']}.{same1D['Ext']}"
    c.SaveAs(outname)
# if (quantiles["Bool"]):
#     import PlotQuantiles as pq
#     pq.config = quantiles
#     exec(open("PlotQuantiles.py").read())
# if (quantiles["Bool"]):
#     import FourQuantiles as pq
#     pq.config = quantiles
#     exec(open("FourQuantiles.py").read())

if (quantiles["Bool"]):
    file_name = input("Give Root File name: ")
    file_path1 = f"/data/t2k-nova/FlatTrees/{file_name}"
    treeName = "FlatTree_VARS"
    
    df1 = ROOT.RDataFrame(treeName,file_path1)
    df1 = df1.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    df1 = pp.DefineKinematics(df1)

    Weight = False
    
    if quantiles["reWeight"][0]:
        Weight = True
        df1 = pp.defineWeightsSpline(df1, quantiles["reWeight"][1], quantiles["reWeight"][2])
        
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
            scale=quantiles["logz"], 
            frequency=quantiles["zaxis"], 
            Normalize=quantiles["Norm"])
    #elif quantiles["plot_type"] == "grid":
        #pq.PlotGrid(file_path1, x1, y1, x2, y2, xLabel, yLabel, mode_title, mode_label, max_energy, df=df_filtered, scale=logz, frequency=zaxis, Normalize=Norm)
    elif quantiles["plot_type"] == "compare":
        file_name2 = input("Give Root File name: ")
        file_path2 = f"/data/t2k-nova/FlatTrees/{file_name2}"
        treeName = "FlatTree_VARS"
    
        df1b = ROOT.RDataFrame(treeName,file_path2)
        df1b = df1b.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
        df1b = pp.DefineKinematics(df1b)
    
        if quantiles["reWeight2"][0]:
            Weight = True
            df1b = pp.defineWeightsSpline(df1b, quantiles["reWeight2"][1], quantiles["reWeight2"][2])
        
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
        df = pp.CreateDataFrame(file_path, Contour["Cut"])
        BinL = Contour["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(Contour["EvisB"]):
            df = pp.DefineEvis(df)
        if (Contour["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if(Contour["reWeight"][0]):
            df = pp.defineWeightsSpline(df,Contour["reWeight"][1],Contour["reWeight"][2])
        for word in Contour["AxisInfo"].split(','):
                AxisInfo.append(word)

        if Contour["AutoQuant"][0]:
            x = Contour["AutoQuant"][1]
            y = Contour["AutoQuant"][2]
            # Get the total number of events
            histogramInfo = ("name", f"{y} vs {x} plot", 1000000, 0, df.Max(x).GetValue(), 1, 0, df.Max(y).GetValue()) #just need 1 bin in y
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

            # Now that we have cumulative events, let's split them into 5 sections
            x_bins = [0]  # Start at 0
            target_events_per_section = total_events / 5

            for i in range(1, 5):  # Divide into 5 sections
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
            # print(cuts)
            # print(Legend)
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
        histlist = pp.PlotContEventCuts(df, Contour["Var1"], Contour["Var2"], histInfo, cuts)
        save_L = Contour["Save"]+ "/" + generator + '-' + flux + Contour["Name"] + "." +Contour["Ext"]
        pp.SaveContHist(histlist, AxisInfo, Legend, colors, save_L,Contour["logz"])
