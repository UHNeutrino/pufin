import ROOT
import os
import json5
import datetime
import src.ParticlePlots as pp 
import src.SetupFunctions as sf
import glob
import array




def GrabFluxReWeights(GlobalSettings):
    frwDict = GlobalSettings.get("FluxReweight")
    
    if not frwDict:
        return [False, "", "", 1, "X", False, False, "", "", "", "", "", "", 1]

    reweight_flag = True
    rw_file = frwDict.get("FluxPath")
    rw_flux = frwDict.get("FluxHistogram")
    targets_file = frwDict.get("TargetWeightsFile")
    detector = frwDict.get("Detector")
    target = frwDict.get("Target")
    xsectype = frwDict.get("XsecType")
    areaB = frwDict.get("AreaNormFlag")
    undoNormB = frwDict.get("UndoFluxNormFlag")
    xsecmode = frwDict.get("XsecMode")
    flavor = frwDict.get("Flavor")
    xsecpath = frwDict.get("XsecPath")
    nucpert = frwDict.get("NucleonsPerTarget")

    if areaB:
        Fscale = 1
    else:
        Fscale = CalculateTargetWeightFactor(targets_file, detector, target)
    # Fscale = frwDict.get("Fscale")
    
    reweight_cfg = [
        reweight_flag,
        rw_file,
        rw_flux,
        Fscale,
        xsectype,
        areaB,
        undoNormB,
        xsecmode,
        flavor,
        target,
        xsecpath,
        nucpert,
    ]
    print(f"Using Fscale for {detector} {target}: {Fscale:.18e}")
    return reweight_cfg



def CalculateTargetWeightFactor(targets_file, detector, target):
    with open(targets_file, "r") as f:
        targets_cfg = json5.load(f)

    if detector not in targets_cfg:
        available = sorted(targets_cfg.keys())
        raise ValueError(f"Detector '{detector}' not found. Available detectors: {available}")

    detector_cfg = targets_cfg[detector]

    required_fields = [
        "exp_pot",
        "flux_pot",
        "fv_nucleon_targets",
        "xsec_units",
        "flux_gev_norm",
        "flux_cm_conv",
        "target_percent",
    ]

    missing_fields = [field for field in required_fields if field not in detector_cfg]
    if missing_fields:
        raise ValueError(f"Configuration '{detector}' is missing fields: {missing_fields}")

    for field in required_fields[:-1]:
        if detector_cfg[field] is None:
            raise ValueError(f"Configuration '{detector}' field '{field}' has not been assigned")

    target_percents = detector_cfg["target_percent"]

    if target not in target_percents:
        available = sorted(target_percents.keys())
        raise ValueError(f"Target '{target}' not found for detector '{detector}'. Available targets: {available}")

    exp_pot = float(detector_cfg["exp_pot"])
    flux_pot = float(detector_cfg["flux_pot"])
    fv_nucleon_targets = float(detector_cfg["fv_nucleon_targets"])
    xsec_units = float(detector_cfg["xsec_units"])
    flux_gev_norm = float(detector_cfg["flux_gev_norm"])
    flux_cm_conv = float(detector_cfg["flux_cm_conv"])
    target_percent = float(target_percents[target])

    if flux_pot == 0:
        raise ValueError(f"Configuration '{detector}' has flux_pot = 0")

    if flux_gev_norm == 0:
        raise ValueError(f"Configuration '{detector}' has flux_gev_norm = 0")

    if target_percent < 0:
        raise ValueError(f"Target percentage for '{target}' cannot be negative")

    Fscale = (
        exp_pot
        * fv_nucleon_targets
        * target_percent
        * xsec_units
        * flux_cm_conv
        / flux_pot
        / flux_gev_norm
    )

    return Fscale

def MakePlots(plots, GlobalSettings):
    reweight_cfg = GrabFluxReWeights(GlobalSettings)
    reweight_flag = reweight_cfg[0]
    areaB = reweight_cfg[5]
    
    userFolder = GlobalSettings["userFolder"]
    root_files = glob.glob( userFolder+ f'/*{plots["Gen"]}*{plots["Description"]}*.root')
    if root_files == []:
        printMsg =  "NO such root files:"+f'/*{plots["Gen"]}*{plots["Description"]}*.root'
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
        VbinBool = "VBins" in plots
        if VbinBool:
            Vbins = array.array('d',plots["VBins"][1])
            varBinInfo = ROOT.RDF.TH1DModel("h_varbins","h", len(Vbins) - 1, Vbins)


        if(GlobalSettings["EvisB"]):
            df = pp.DefineEvis(df)  
        if (GlobalSettings["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (GlobalSettings["TkiB"]):
            df = pp.DefineTKI(df)
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)
        if reweight_flag:
            df, bin_integral_unnorm = pp.defineWeightsSpline(df, reweight_cfg)
            weight_col = "weights"
        else:
            weight_col = ""

        if plots["Type"] == "1D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
            if VbinBool:
                histInfo = varBinInfo
            if reweight_flag:
                hist = df.Histo1D(histInfo,plots["Var1"],"weights")
            else:
                hist = df.Histo1D(histInfo,plots["Var1"])
        if plots["Type"] == "2D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
            if VbinBool:
                histInfo = varBinInfo
            if(reweight_flag):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],"weights")
            else:
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"])
            if(plots["profileX"]):
                h2 = hist.GetValue()
                h2.SetDirectory(0)
                p1 = h2.ProfileX("hProfileX", 1, -1, "s")
                p1.SetDirectory(0)

        ################################################################
        #Histogram scaling for event rates
        if not areaB and weight_col:
            target_integral = bin_integral_unnorm
            current = df.Sum(weight_col).GetValue()
            s = target_integral / current
            hist.Scale(s)
            if GlobalSettings["DebugPrint"] != 0:  
                print("uncut bin integral")
                print(current)
                print("uncut scaled bin integral")
                print(hist.Integral())

            
                    
        if (GlobalSettings["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)  
        if plots.get("Cut"):
            df_cut = df.Filter(plots["Cut"])
        else:
            df_cut = df
        #df_cut = df  # uncomment if trying to scale using a specific interaction cross section 
        
        # Build the CUT histogram, still using weights if you have them
        if plots["Type"] == "1D":
            if weight_col:
                rdf_cut = df_cut.Histo1D(histInfo, plots["Var1"], weight_col)
            else:
                rdf_cut = df_cut.Histo1D(histInfo, plots["Var1"])
        if plots["Type"] == "2D":
            if weight_col:
                rdf_cut = df_cut.Histo2D(histInfo, plots["Var1"], plots["Var2"], weight_col)
            else:
                rdf_cut = df_cut.Histo2D(histInfo, plots["Var1"],plots["Var2"])
            
        hist_cut = rdf_cut.GetValue()
        hist_cut.SetDirectory(0)
        
        # Scale cut histogram by the same global factor s
        if areaB:
            area_integral = hist_cut.Integral()
            if area_integral <= 0:
                raise RuntimeError("Cut weighted histogram has zero area")
            hist_cut.Scale(1.0 / area_integral)
        elif weight_col:
            hist_cut.Scale(s)
        if GlobalSettings["DebugPrint"] != 0:
            print("scaled bin integral (cut hist)")
            print(hist_cut.Integral())
        xvar, xunit, yvar, yunit, PlotTitle = AxisInfo
        hist = sf.formatHist(hist_cut, xvar, xunit, yvar, yunit, max=plots["max"], PlotTitle=PlotTitle)
        ########################################################################################################################
            
        if plots["Ext"] == "root":
            hist.SetName("h")
            saveLoc = GlobalSettings["Save"]+"/"+plots["Name"]
            out_file = ROOT.TFile(f"{saveLoc}.root", "RECREATE")
            print(f"Saved {saveLoc}.root")
            hist.Write()  # Write the histogram to the file
            out_file.Close()  # Close to finalize writing
        else:
            nx = datetime.datetime.now()
            x = str(nx)
            fileN = plots["Name"]
            fileN = fileN.replace(" ", "-")
            if (plots["profileX"]): 
                pp.Savehist2DWithProfile(hist, p1,AxisInfo,GlobalSettings["Save"],fileN,plots["Ext"],max = plots["max"], Normalize=False, logz = plots["logz"], diagonal=plots["diagonal"]) 
            else:
                pp.Savehist(hist,AxisInfo,GlobalSettings["Save"],fileN,plots["Ext"],max = plots["max"], Normalize=False, logz = plots["logz"])
                
def Make2DRatio(Ratio2D, GlobalSettings):
    reweight_cfg = GrabFluxReWeights(GlobalSettings)
    reweight_flag = reweight_cfg[0]
    areaB = reweight_cfg[5]
    
    userFolder = GlobalSettings["userFolder"]
    root_files1 = glob.glob( userFolder+ f'/*{Ratio2D["File1"]}*.root')
    root_files2 = glob.glob( userFolder+ f'/*{Ratio2D["File2"]}*.root')

    if root_files1 == []:
        printMsg =  "NO such root files:"+f'/*{Ratio2D["File1"]}*.root'
        raise ValueError(printMsg)
    if root_files2 == []:
        printMsg =  "NO such root files:"+f'/*{Ratio2D["File2"]}*.root'
        raise ValueError(printMsg)

    if len(root_files1) > 1 or len(root_files2) > 1:
        raise ValueError(f"Got too many files: {root_files1} and {root_files2}")

    # print(file_path)
    # file_name1, file_name2 = root_files1.split('/')[-1], root_files2.split('/')[-1]
    # generator = file_name.split('_')[1]
    # flux = file_name.split('_')[2]
    # Tevents = file_name.split('_')[3]
    BinX = Ratio2D["BinsX"]
    BinY = Ratio2D["BinsY"]
    AxisInfo = []
    df1, df2 = pp.CreateDataFrame(root_files1, cut ="None"), pp.CreateDataFrame(root_files2, cut ="None")

    if(GlobalSettings["EvisB"]):
        df1, df2 = pp.DefineEvis(df1), pp.DefineEvis(df2)
    if (GlobalSettings["KinematicsB"]):
        df1, df2 = pp.DefineKinematics(df1), pp.DefineKinematics(df2)
    if (GlobalSettings["TkiB"]):
        df1, df2 = pp.DefineTKI(df1), pp.DefineTKI(df2)
    for word in Ratio2D["AxisInfo"].split(','):
        AxisInfo.append(word)
    if reweight_flag:
        df1, bin_integral_unnorm1 = pp.defineWeightsSpline(df1, reweight_cfg)
        df2, bin_integral_unnorm2 = pp.defineWeightsSpline(df2, reweight_cfg)
        weight_col = "weights"
    else:
        weight_col = ""


    histInfo = (AxisInfo[-1],AxisInfo[-1],BinX[0],BinX[1],BinX[2],BinY[0],BinY[1],BinY[2])
    if(reweight_flag):
        hist1, hist2 = df1.Histo2D(histInfo,Ratio2D["Var1"],Ratio2D["Var2"],"weights"), df2.Histo2D(histInfo,Ratio2D["Var1"],Ratio2D["Var2"],"weights")
    else:
        hist1, hist2 = df1.Histo2D(histInfo,Ratio2D["Var1"],Ratio2D["Var2"]), df2.Histo2D(histInfo,Ratio2D["Var1"],Ratio2D["Var2"])

    ################################################################
    #Histogram scaling for event rates
    if not areaB and weight_col:
        target_integral1, target_integral2 = bin_integral_unnorm1, bin_integral_unnorm2
        current1, current2 = df1.Sum(weight_col).GetValue(), df2.Sum(weight_col).GetValue()
        s1, s2 = target_integral1/current1, target_integral2/current2
        hist1.Scale(s1), hist2.Scale(s2)
        if GlobalSettings["DebugPrint"] != 0:  
            print("uncut bin integral")
            print(f"hist1: {current1} hist2: {current2}")
            print("uncut scaled bin integral")
            print(f"hist1: {hist1.Integral()} hist2: {hist2.Integral()}")

        
                
    if (GlobalSettings["ThresholdsB"]):
        df1, df2 = pp.FlagParticleThresholds(df1), pp.FlagParticleThresholds(df2)
    if Ratio2D.get("Cut"):
        df_cut1, df_cut2 = df1.Filter(Ratio2D["Cut"]), df2.Filter(Ratio2D["Cut"])
    else:
        df_cut1,  df_cut2 = df1, df2      
    # Build the CUT histogram, still using weights if you have them
    if weight_col:
        rdf_cut1, rdf_cut2 = df_cut1.Histo2D(histInfo, Ratio2D["Var1"], Ratio2D["Var2"], weight_col), df_cut2.Histo2D(histInfo, Ratio2D["Var1"], Ratio2D["Var2"], weight_col)
    else:
        rdf_cut1, rdf_cut2 = df_cut1.Histo2D(histInfo, Ratio2D["Var1"],Ratio2D["Var2"]), df_cut2.Histo2D(histInfo, Ratio2D["Var1"],Ratio2D["Var2"])
        
    hist_cut1, hist_cut2 = rdf_cut1.GetValue(), rdf_cut2.GetValue()
    hist_cut1.SetDirectory(0), hist_cut2.SetDirectory(0)
    
    # Scale cut histogram by the same global factor s
    if areaB:
        area_integral1, area_integral2 = hist_cut1.Integral(), hist_cut2.Integral()
        if area_integral1 <= 0 or area_integral2 <= 0:
            raise RuntimeError("Cut weighted histogram has zero area")
        hist_cut1.Scale(1.0 / area_integral1), hist_cut2.Scale(1.0/area_integral2)
    elif weight_col:
        hist_cut1.Scale(s1), hist_cut2.Scale(s2)
    if GlobalSettings["DebugPrint"] != 0:
        print("scaled bin integral (cut hist)")
        print(f"hist 1 {hist_cut1.Integral()} hist 2 {hist_cut1.Integral()}")
    xvar, xunit, yvar, yunit, PlotTitle = AxisInfo
    Fhist1, Fhist2 = sf.formatHist(hist_cut1, xvar, xunit, yvar, yunit, max=Ratio2D.get("max"), PlotTitle=PlotTitle), sf.formatHist(hist_cut2, xvar, xunit, yvar, yunit, max=Ratio2D.get("max"), PlotTitle=PlotTitle)
    ########################################################################################################################
    Fhist1.SetName("h1"), Fhist2.SetName("h2")
    saveLoc = GlobalSettings["Save"]+"/"+Ratio2D["Name"]
    

    ratio = Fhist1.Clone("ratio")
    ratio.Divide(Fhist2)
    Fhist1.SetStats(0), Fhist2.SetStats(0), ratio.SetStats(0)
    if Ratio2D.get("RatioMin")!= None and Ratio2D.get("RatioMax"):
        ratio.SetMinimum(Ratio2D["RatioMin"])
        ratio.SetMaximum(Ratio2D["RatioMax"])

    nx = datetime.datetime.now()
    x = str(nx)
    fileN = Ratio2D["Name"]
    fileN = fileN.replace(" ", "-")
    Ext = "png"
    pp.Savehist(ratio,AxisInfo,GlobalSettings["Save"],fileN,Ext,max = Ratio2D.get("max"), Normalize=False, logz = Ratio2D["logz"])

    out_file = ROOT.TFile(f"{saveLoc}.root", "RECREATE")
    print(f"Saved {saveLoc}.root")
    c = ROOT.TCanvas("ratio", "ratio", 800, 600)
    ROOT.gStyle.SetPalette(ROOT.kBird)
    ratio.Draw("COLZ")
    c.Write() 
    c1 = ROOT.TCanvas("hist1", "hist1", 800, 600)
    Fhist1.Draw("COLZ")  # Write the histogram to the file
    c1.Write()
    c2 = ROOT.TCanvas("hist2", "hist2", 800, 600)
    Fhist2.Draw("COLZ")  # Write the histogram to the file
    c2.Write()
    out_file.Close()  # Close to finalize writing
    



def MakeStacks(stacks,GlobalSettings):
    reweight_cfg = GrabFluxReWeights(GlobalSettings)
    reweight_flag = reweight_cfg[0]
    areaB = reweight_cfg[5]
    userFolder = GlobalSettings["userFolder"]
    root_files = glob.glob( userFolder+ f'/*{stacks["Gen"]}*{stacks["Description"]}*.root')
    if root_files == []:
        print("NO such root files")

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        #df = pp.CreateDataFrame(file_path, stacks["Cut"])
        df = pp.CreateDataFrame(file_path, cut="None")
        weight_col = ""
        BinL = stacks["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(GlobalSettings["EvisB"]):
            df = pp.DefineEvis(df)
        if (GlobalSettings["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if(GlobalSettings["TkiB"]):
            df = pp.DefineTKI(df)
        if reweight_flag:
            df, bin_integral_unnorm = pp.defineWeightsSpline(df, reweight_cfg)
            weight_col = "weights"
        else:
            weight_col = ""

        if reweight_flag and not areaB:
            target_integral = bin_integral_unnorm
            current = df.Sum(weight_col).GetValue()

            if current <= 0:
                raise RuntimeError(
                    "Uncut weighted dataframe sum is non-positive"
                )

            s = target_integral / current

            print("Stack normalization:")
            print(f"target integral = {target_integral:.6e}")
            print(f"current integral = {current:.6e}")
            print(f"scale factor = {s:.6e}")
            
        if (GlobalSettings["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)
        if stacks.get("Cut"):
            df = df.Filter(stacks["Cut"])
        for word in stacks["AxisInfo"].split(','):
                AxisInfo.append(word)
        for cut,name in stacks["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for color_spec in stacks["Colors"].split(","):
            colors.append(sf.parse_color(color_spec))
        
        stack, histlist = pp.PlotStackedEventCuts(df, stacks["Var1"], histInfo, cuts, colors, weights= weight_col)
        
        if areaB:
            total_integral = sum(hist.Integral() for hist in histlist)
            
            if total_integral <= 0:
                raise RuntimeError("Stacked weighted histograms have zero area")
            
            for hist in histlist:
                hist.Scale(1.0 / total_integral)
                print(f"hist integral = {hist.Integral()}")
                
            print("Total stack integral after normalization:",
                sum(hist.Integral() for hist in histlist))
            
        elif weight_col:
            for hist in histlist:
                hist.Scale(s)   
        
        # Rebuild the stack from the scaled histograms
        stack = ROOT.THStack("stack_scaled", "")
        for hist in histlist:
            stack.Add(hist)      

        save_L = GlobalSettings["Save"] + "/" + stacks["Name"] + "." + stacks["Ext"]

        pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,save_L)


def MakeOverlap(overlap,GlobalSettings):
    reweight_cfg = GrabFluxReWeights(GlobalSettings)
    reweight_flag = reweight_cfg[0]
    areaB = reweight_cfg[5]
    userFolder = GlobalSettings["userFolder"]
    root_files = glob.glob( userFolder + f'/*{overlap["Gen"]}*{overlap["Description"]}*.root')
    if root_files == []:
        print("NO such root files")
        
    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        # df = pp.CreateDataFrame(file_path, overlap["Cut"])
        df = pp.CreateDataFrame(file_path, cut = "None")
        weight_col = ""
        if reweight_flag:
            df, bin_integral_unnorm = pp.defineWeightsSpline(df,reweight_cfg)
            weight_col = "weights"
        else:
            weight_col = ""

        if reweight_flag and not areaB:
            target_integral = bin_integral_unnorm
            current = df.Sum(weight_col).GetValue()

            if current <= 0:
                raise RuntimeError(
                    "Uncut weighted dataframe sum is non-positive"
                )

            s = target_integral / current

            print("Overlap normalization:")
            print(f"target integral = {target_integral:.6e}")
            print(f"current integral = {current:.6e}")
            print(f"scale factor = {s:.6e}")
            
        BinL = overlap["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(GlobalSettings["EvisB"]):
            df = pp.DefineEvis(df)
        if (GlobalSettings["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if(GlobalSettings["TkiB"]):
            df = pp.DefineTKI(df)
        if (GlobalSettings["ThresholdsB"]):
            df = pp.FlagParticleThresholds(df)
        if overlap.get("Cut"):
            df = df.Filter(overlap["Cut"])
        for word in overlap["AxisInfo"].split(','):
                AxisInfo.append(word)
        for cut,name in overlap["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for color_spec in overlap["Colors"].split(","):
            colors.append(sf.parse_color(color_spec))
        
        histlist = pp.overlapPlots(df, overlap["Var1"], histInfo, cuts, colors, weights= weight_col)
        if areaB:
            total_integral = sum(hist.Integral() for hist in histlist)

            if total_integral <= 0:
                raise RuntimeError("Overlap weighted histograms have zero total area")

            for hist in histlist:
                hist.Scale(1.0 / total_integral)

            print(
                "Total overlap integral after normalization:",
                sum(hist.Integral() for hist in histlist),
            )

        elif weight_col:
            for hist in histlist:
                hist.Scale(s)
        save_L = GlobalSettings["Save"] + "/" + overlap["Name"] + "." +overlap["Ext"]
        pp.SaveOverlapPlot(histlist, AxisInfo, Legend,save_L, Normalize=False)
        
def MakeSame1D(same1D,GlobalSettings):
    userFolder = GlobalSettings["userFolder"]
    plots_list = same1D["Plots"]
    hist_dict = {}
    hist_rdfs = []  # Keep these alive to avoid ROOT segfaults
        
    AxisInfo = same1D["AxisInfo"].split(",")
    BinL = same1D["Bins"]
    xvar, xunit, yvar, yunit, PlotTitle = AxisInfo

    Add_Ratio = same1D.get("Add_Ratio", False)
    RatioNominal = same1D.get("RatioNominal", "")
    RatioPlots = same1D.get("RatioPlots", "all")         
    RatioRange = same1D.get("RatioRange", "auto")
    
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
    # legend = ROOT.TLegend(0.3, 0.6, 0.59, 0.79) ## better for cos theta plots
    
    logy = same1D.get("logy")
    kin = GlobalSettings.get("KinematicsB", False)
    Evis = GlobalSettings.get("EvisB", False)
    Tki = GlobalSettings.get("TkiB", False)
    Thresholds = GlobalSettings.get("ThresholdsB", False)
    
    histCounter = 0
    hist_order = []
    top_histo = True # so the top histo (drawn first) will not have x-labels
    for plot in plots_list:
        file = plot["File"]
        key = plot["Key"]
        label = plot["Label"]

        # reweight_flag, rw_file, rw_flux, Fscale, xsectype, areaB, undoNormB = GrabFluxReWeights(plot)
        if "FluxReweight" in plot:
            reweight_cfg = GrabFluxReWeights(plot)
        else:
            reweight_cfg = GrabFluxReWeights(GlobalSettings)
        reweight_flag = reweight_cfg[0]
        areaB = reweight_cfg[5]
        hist_order.append(key)

        # Find matching file
        matches = glob.glob( f"{userFolder}/*{file}*.root")
        if not matches:
            print(f"No file found for key: {file}")
            continue

        file_path = matches[0]
        print(f"Processing {file_path}")
        df = pp.CreateDataFrame(file_path, cut = "None")


        if kin:
            df = pp.DefineKinematics(df)
        if Evis:
            df = pp.DefineEvis(df)
        if Tki:
            df = pp.DefineTKI(df)
        if Thresholds:
            df = pp.FlagParticleThresholds(df)


        if reweight_flag:
            df, bin_integral_unnorm = pp.defineWeightsSpline(df, reweight_cfg)
            weight_col = "weights"
        else:
            weight_col = ""
            
        bins = array.array('d',same1D["VBins"][1])

        histInfoScale = (f"h_scale_{key}", f"hist_{key}", 160, 0, 8)
        histInfo = (f"h_{key}", f"hist_{key}", BinL[0], BinL[1], BinL[2])
        varBinInfo = ROOT.RDF.TH1DModel(f"h_varbins_{key}", f"hist_{key}", len(bins) - 1, bins)

        if same1D["VBins"][0]:
            histInfo = varBinInfo
        if weight_col:
            rdf_hist = df.Histo1D(histInfoScale, 'Enu_true', weight_col)
            #rdf_hist = df.Histo1D(histInfoScale, 'Ev', weight_col) ## for gst files
        else:
            rdf_hist = df.Histo1D(histInfo, plot["Var"])

        hist_rdfs.append(rdf_hist)  # Keep RDF object alive
        hist = rdf_hist.GetValue()
        pp.HistoErrorBars(hist)
        if reweight_flag and not areaB:
            target_integral = bin_integral_unnorm
            current = df.Sum(weight_col).GetValue()
            # current = hist.Integral() 
            print(f"\n[{key}] Applying weight normalization factor")
            print(f"target integral = {target_integral:.6e}")
            print(f"current = {current:.6e}")
            s = target_integral / current
            hist.Scale(s)
            print("uncut scaled bin integral after weight normalization")
            print(hist.Integral())     
        if same1D.get("Cut"):
            df_cut = df.Filter(same1D["Cut"])
        else:
            df_cut = df
        
        if plot.get("Cut"):
            df_cut = df_cut.Filter(plot["Cut"])
        
        # Build the CUT histogram, still using weights if you have them
        if weight_col:
            rdf_cut = df_cut.Histo1D(histInfo, plot["Var"], weight_col)
        else:
            rdf_cut = df_cut.Histo1D(histInfo, plot["Var"])
            
        hist_cut = rdf_cut.GetValue()
        hist_cut.SetDirectory(0)

        if areaB:
            area_integral = hist_cut.Integral()

            if area_integral <= 0:
                raise RuntimeError(
                    f"{key} final weighted histogram has zero integral"
                )

            hist_cut.Scale(1.0 / area_integral)

            print(
                f"[{key}] separately area-normalized integral = "
                f"{hist_cut.Integral()}"
            )

        elif reweight_flag:
            hist_cut.Scale(s)

            print(
                f"[{key}] event-rate-scaled cut integral = "
                f"{hist_cut.Integral():.6e}"
            )
            
        print("scaled bin integral (cut hist)")
        print(hist_cut.Integral())
        hist = sf.formatHist(hist_cut, xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PlotTitle)
        
        if "Style" in plot:
            styleint = plot["Style"]
        else:
            styleint = 1
        
        color = sf.parse_color(plot["Color"])
        hist.SetLineStyle(styleint)
        hist.SetLineColor(color)
        hist.SetLineWidth(1)
        
        hist_dict[key] = hist
        legend.AddEntry(hist, label, "l")
        histCounter += 1

        highest_max = max(hist.GetMaximum() for hist in hist_dict.values())

        if same1D["max"] > 0:
            plot_max = same1D["max"]
        else:
            plot_max = highest_max * 1.15

        print(f"Highest histogram maximum = {highest_max}")
        print(f"Common plotted maximum = {plot_max}")
        
        if Add_Ratio:
            topPad.cd()
        else:
            c.cd()

        first_hist = True

        for key in hist_order:
            if key not in hist_dict:
                continue

            hist = hist_dict[key]
            hist.SetMaximum(plot_max)

            if first_hist and Add_Ratio:
                hist.GetXaxis().SetLabelSize(0)     # hide numbers
                hist.GetXaxis().SetTitleSize(0)     # hide title
                hist.GetXaxis().SetTickLength(0)    # hide ticks
                hist.GetXaxis().SetLabelOffset(999) # hide x axis labels


            if same1D["ErrorBars"]:
                draw_opt = "HIST E1" if first_hist else "HIST E1 SAME"
            else:
                draw_opt = "HIST" if first_hist else "HIST SAME"

            hist.Draw(draw_opt)
            first_hist = False
        # if same1D["ErrorBars"]:
        #     draw_opt = "HIST E1" if len(hist_dict) == 0 else "HIST E1 SAME"
        # else:
        #     draw_opt = "HIST" if len(hist_dict) == 0 else "HIST SAME"
        # hist.Draw(draw_opt)
        # legend.AddEntry(hist, label, "l")
        # hist_dict[key] = hist
        # histCounter += 1
    if logy:
        c.SetLogy()
        if Add_Ratio:
            topPad.SetLogy()
    else:
        print("NO LOG")
    if Add_Ratio:
        topPad.cd()
    legend.Draw("SAME")
    
    # Draw selected plots divided by the nominal plot
    ratio_dict = {}

    if Add_Ratio:
        if not RatioNominal:
            raise ValueError(
                "Add_Ratio is true, but RatioNominal was not specified"
            )

        if not RatioPlots:
            raise ValueError(
                "Add_Ratio is true, but RatioPlots is empty"
            )


        # Make it a list if its just one
        if isinstance(RatioNominal, str):
            RatioNominalList = [RatioNominal]
        else:
            RatioNominalList = RatioNominal

        ratio_dict = pp.MakeRatiosToNominal(
            hist_dict,
            RatioNominalList,
            RatioPlots,
            hist_order,
        )

        if not ratio_dict:
            raise RuntimeError(
                "No ratio histograms were created"
            )

        if isinstance(RatioRange, str):
            if RatioRange.lower() != "auto":
                raise ValueError(
                    "RatioRange must be 'auto' or [minimum, maximum]"
                )

            ratio_ymin, ratio_ymax = pp.GetRatioRange(ratio_dict)

        elif (
            isinstance(RatioRange, list)
            and len(RatioRange) == 2
        ):
            ratio_ymin = float(RatioRange[0])
            ratio_ymax = float(RatioRange[1])

            if ratio_ymin >= ratio_ymax:
                raise ValueError(
                    "RatioRange minimum must be smaller than maximum"
                )

        else:
            raise TypeError(
                "RatioRange must be 'auto' or [minimum, maximum]"
            )
        ratioPad.cd()
        first_ratio = True

        for ratio_key, h_ratio in ratio_dict.items():
            h_ratio.SetTitle("")

            # Restore the x-axis because it may have been hidden
            xa = h_ratio.GetXaxis()
            xa.SetLabelOffset(0.01)
            xa.SetTickLength(0.04)
            xa.SetTitle(
                f"{xvar} {f'({xunit})' if xunit.strip() else ''}".strip()
            )
            xa.SetTitleSize(0.12)
            xa.SetLabelSize(0.10)

            ya = h_ratio.GetYaxis()
            ya.SetTitle(same1D["RatioLabel"])
            ya.SetNdivisions(505)
            ya.SetTitleSize(0.10)
            ya.SetTitleOffset(0.55)
            ya.SetLabelSize(0.10)

            h_ratio.SetMinimum(ratio_ymin)
            h_ratio.SetMaximum(ratio_ymax)

            if same1D["ErrorBars"]:
                draw_opt = "E1" if first_ratio else "E1 SAME"
            else:
                draw_opt = "HIST" if first_ratio else "HIST SAME"

            h_ratio.Draw(draw_opt)
            first_ratio = False

        # Horizontal reference line at ratio = 1
        first_ratio_hist = next(iter(ratio_dict.values()))

        xmin = first_ratio_hist.GetXaxis().GetXmin()
        xmax = first_ratio_hist.GetXaxis().GetXmax()

        line = ROOT.TLine(xmin, 1.0, xmax, 1.0)
        line.SetLineStyle(2)
        line.SetLineColor(ROOT.kBlack)
        line.Draw("SAME")

    #outname = f"{HOME}/{GlobalSettings['Save']}/{same1D['Name']}.{same1D['Ext']}"
    base_name = f"{GlobalSettings['Save']}/{same1D['Name']}"
    root_outname = f"{base_name}.root"
    image_outname = f"{base_name}.{same1D['Ext']}"
    
    # Always save the ROOT file.
    f_out = ROOT.TFile(root_outname, "RECREATE")
    if not f_out or f_out.IsZombie():
        raise RuntimeError(f"Could not create ROOT file: {root_outname}")


    # write the plotted hists (and ratio if you made one)
    for k, h in hist_dict.items():
        # make sure it survives file close / isn’t tied to a canvas
        h_out = h.Clone(f"h_{k}")
        h_out.SetDirectory(0)
        f_out.cd()
        h_out.Write()

    # optional: if you created a ratio hist named h_ratio, write it too
    if Add_Ratio:
        for ratio_key, ratio_hist in ratio_dict.items():
            ratio_name = f"h_ratio_{ratio_key}_over_{RatioNominal}"

            r_out = ratio_hist.Clone(ratio_name)
            r_out.SetDirectory(0)

            f_out.cd()
            r_out.Write(ratio_name)
        
    f_out.cd()
    c.Write("canvas")
    f_out.Close()

    c.SaveAs(image_outname)
    print(f"Saved {root_outname}")
    print(f"Saved {image_outname}") 
    

def MakeContour(Contour,GlobalSettings):
    reweight_cfg = GrabFluxReWeights(GlobalSettings)
    reweight_flag = reweight_cfg[0]
    areaB = reweight_cfg[5]
    userFolder = GlobalSettings["userFolder"]
    root_files = glob.glob( userFolder + f'/*{Contour["Gen"]}*{Contour["Description"]}*.root')
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
        if(GlobalSettings["EvisB"]):
            df = pp.DefineEvis(df)
            df = df.Filter("Evis_kin != -9999.9")
        if (GlobalSettings["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (GlobalSettings["TkiB"]):
            df = pp.DefineTKI(df)
        # if (GlobalSettings["ThresholdsB"]):
        #     df = pp.FlagParticleThresholds(df)
        # if Contour.get("Cut"):
        #     df = df.Filter(Contour["Cut"])

        if reweight_flag:
            df, bin_integral_unnorm = pp.defineWeightsSpline(df, reweight_cfg)
            weight_col = "weights"
        else:
            weight_col = ""

        # Calculate normalization before applying the contour selection
        if reweight_flag and not areaB:
            target_integral = bin_integral_unnorm
            current = df.Sum(weight_col).GetValue()

            if current <= 0:
                raise RuntimeError("Uncut weighted dataframe sum is non-positive")

            s = target_integral / current

            print("Contour normalization:")
            print(f"target integral = {target_integral:.6e}")
            print(f"current integral = {current:.6e}")
            print(f"scale factor = {s:.6e}")

            df = df.Redefine("weights", f"weights * {s}")

        elif reweight_flag and areaB:
            current = df.Sum(weight_col).GetValue()

            if current <= 0:
                raise RuntimeError("Uncut weighted dataframe sum is non-positive")

            df = df.Redefine("weights", f"weights / {current}")

        if GlobalSettings["ThresholdsB"]:
            df = pp.FlagParticleThresholds(df)
        if Contour.get("Cut"):
            df = df.Filter(Contour["Cut"])
    
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
                target_events = i * target_events_per_section
                # Find the first bin index where the cumulative event count exceeds the target
                bin_idx = min(range(len(cumulative_events)), key=lambda idx: abs(cumulative_events[idx] - target_events))
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
                save_L0 = GlobalSettings["Save"] + "/" + "INT" +Contour["Name"] + "." +Contour["Ext"]
                # c.SaveAs(save_L0)
                pp.SaveIntPlot(df,x,y,x_bins,save_L0)
        else:
            for cut,name in Contour["ConCuts"].items():
                cuts.append(cut)
                Legend.append(name)

        # for num in Contour["Colors"].split(","):
        #     colors.append(int(num))
        for color_spec in Contour["Colors"].split(","):
            colors.append(sf.parse_color(color_spec))
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
        print(AxisInfo)
        histlist = pp.PlotContEventCuts(df, Contour["Var1"], Contour["Var2"], histInfo, cuts, Contour["TotalPercents"])
        save_L = GlobalSettings["Save"]+ "/"+ Contour["Name"] + "." +Contour["Ext"]
        # if Contour["ContStyle"]:
        #     pp.SaveContHistStyles(histlist, AxisInfo, colors, Contour["styles"], Contour["Clabels"], Contour["Slabels"], save_L, Contour["logz"])
        # else:
        pp.SaveContHist(histlist, AxisInfo, Legend, colors, Contour["TotalPercents"], save_L, Contour["logz"])


def MakeContourStyle(ContourStyle,GlobalSettings):
    reweight_cfg = GrabFluxReWeights(GlobalSettings)
    reweight_flag = reweight_cfg[0]
    areaB = reweight_cfg[5]

    userFolder = GlobalSettings["userFolder"]
    root_files = glob.glob( userFolder + f'/*{ContourStyle["Gen"]}*{ContourStyle["Description"]}*.root')
    if root_files == []:
        print("NO such root files")

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        #df = pp.CreateDataFrame(file_path, Contour["Cut"])
        #df = pp.CreateDataFrame(file_path, cut="None")
        df = ROOT.RDataFrame(GlobalSettings["treeName"],file_path)
        BinL = ContourStyle["Bins"]
        AxisInfo = []
        cuts = []
        colors = []
        styles = []
        ColorLabels = {}
        StyleLabels = {}
        name1 = " "
        name2 = " "
        if(GlobalSettings["EvisB"]):
            df = pp.DefineEvis(df)
            df = df.Filter("Evis_kin != -9999.9")
        if (GlobalSettings["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (GlobalSettings["TkiB"]):
            df = pp.DefineTKI(df)
        if reweight_flag:
            df, bin_integral_unnorm = pp.defineWeightsSpline(df, reweight_cfg)
            weight_col = "weights"
        else:
            weight_col = ""

        if reweight_flag and not areaB:
            target_integral = bin_integral_unnorm
            current = df.Sum(weight_col).GetValue()

            if current <= 0:
                raise RuntimeError("Uncut weighted dataframe sum is non-positive")

            s = target_integral / current
            df = df.Redefine("weights", f"weights * {s}")

            print("ContourStyle normalization:")
            print(f"target integral = {target_integral:.6e}")
            print(f"current integral = {current:.6e}")
            print(f"scale factor = {s:.6e}")

        elif reweight_flag and areaB:
            current = df.Sum(weight_col).GetValue()

            if current <= 0:
                raise RuntimeError("Uncut weighted dataframe sum is non-positive")

            df = df.Redefine("weights", f"weights / {current}")

        if GlobalSettings["ThresholdsB"]:
            df = pp.FlagParticleThresholds(df)

        if ContourStyle.get("Cut"):
            df = df.Filter(ContourStyle["Cut"])
        for word in ContourStyle["AxisInfo"].split(','):
                AxisInfo.append(word)

        
        for cut1, info1 in ContourStyle["ColorCuts"].items():
            for cut2, info2 in ContourStyle["StyleCuts"].items():
                cuts.append(cut1+" && "+cut2)
                # name1, color = info1.split(",")
                # name2, style = info2.split(",")
                # colors.append(int(color))
                
                name1, color = [x.strip() for x in info1.split(",", 1)]
                name2, style = [x.strip() for x in info2.split(",", 1)]
                colors.append(sf.parse_color(color))
                styles.append(int(style))
    
        for cut1, info1 in ContourStyle["ColorCuts"].items():
                # name1, color = info1.split(",")
                # ColorLabels.update({name1:int(color)})
                name1, color = [x.strip() for x in info1.split(",", 1)]
                ColorLabels.update({name1: sf.parse_color(color)})
        for cut2, info2 in ContourStyle["StyleCuts"].items():
                # name2, style = info2.split(",")
                name2, style = [x.strip() for x in info2.split(",", 1)]
                StyleLabels.update({name2: int(style)})


        print(f"cuts {cuts}")
        print(f"colors {colors}")
        print(f"styles {styles}")
        print(f"Labels {ColorLabels} and { StyleLabels}") 

         

        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
        print(AxisInfo)
        histlist = pp.PlotContEventCuts(df, ContourStyle["Var1"], ContourStyle["Var2"], histInfo, cuts, ContourStyle["TotalPercents"])
        save_L = GlobalSettings["Save"]+ "/" + ContourStyle["Name"] + "." +ContourStyle["Ext"]
        pp.SaveContHistStyles(histlist, AxisInfo, colors, styles, ColorLabels, StyleLabels, save_L, ContourStyle["logz"])
