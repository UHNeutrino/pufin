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
f = open(f'{HOME}/t2k-nova/sysMain.json5')
data = json5.load(f)

plots = data.get("plots")
stacks = data.get("stacks")
same1D = data.get("1DSame")

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

        if (plots["sysRW"][0]) :
            f2 = ROOT.TFile(file_path)
            ft2 = f2.Get("FlatTree_VARS")
            ft2.AddFriend(plots["sysRW"][2],plots["sysRW"][1])
            print( type(ft2))
            df = ROOT.RDataFrame(ft2)
            df = df.Filter(plots["Cut"])
        else:
            df = pp.CreateDataFrame(file_path, plots["Cut"])
        if(plots["EvisB"]):
            df = pp.DefineEvis(df)  
        if (plots["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (plots["TkiB"]):
            df = pp.DefineTKI(df)
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)
        if(plots["reWeight"][0]):
            df = pp.defineWeightsSpline(df,plots["reWeight"][1],plots["reWeight"][2])
        if plots["Type"] == "1D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
            print(histInfo)
            if(plots["reWeight"][0]):
                hist = df.Histo1D(histInfo,plots["Var1"],"weights")
            elif(plots["sysRW"][0]):
                hist = df.Histo1D(histInfo,plots["Var1"],"FrAbs_pi")
            else:
                hist = df.Histo1D(histInfo,plots["Var1"])
        if plots["Type"] == "2D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
            if(plots["reWeight"][0]):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],"weights")
            elif(plots["sysRW"][0]):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],plots["sysRW"][3])
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

    weights = ""
    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        if (stacks["sysRW"][0]) :
            f2 = ROOT.TFile(file_path)
            ft2 = f2.Get("FlatTree_VARS")
            ft2.AddFriend(stacks["sysRW"][2],stacks["sysRW"][1])
            print( type(ft2))
            df = ROOT.RDataFrame(ft2)
            df = df.Filter(stacks["Cut"])
            weights = stacks["sysRW"][3]
        else:
            df = pp.CreateDataFrame(file_path, stacks["Cut"])
        BinL = stacks["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(stacks["EvisB"]):
            df = pp.DefineEvis(df)
        if(stacks["TkiB"]):
            df = pp.DefineTKI(df)
        for word in stacks["AxisInfo"].split(','):
                AxisInfo.append(word)
        print(AxisInfo)
        for cut,name in stacks["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for num in stacks["Colors"].split(","):
            colors.append(int(num))
        
        stack, histlist = pp.PlotStackedEventCuts(df, stacks["Var1"], histInfo, cuts, colors,weights = weights)
        save_L = stacks["Save"] + "/" + stacks["Name"] + "." +stacks["Ext"]
        pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,save_L, Normalize=stacks["Norm"])


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
    # legend = ROOT.TLegend(0.6, 0.6, 0.89, 0.79) ## most plots
    # legend = ROOT.TLegend(0.3, 0.6, 0.59, 0.79) ## better for cos theta plots
    legend = ROOT.TLegend(0.3, 0.2, 0.59, 0.39) ## plot in bottom middle

    
    norm = same1D.get("Norm")
    logy = same1D.get("logy")
    kin = same1D.get("KinematicsB", False)
    Evis = same1D.get("EvisB", False)
    Tki = same1D.get("TkiB", False)
    
    histCounter = 0
    hist_order = []
    top_histo = True # so the top histo (drawn first) will not have x-labels
    for plot in plots_list:
        file = plot["File"]
        key = plot["Key"]
        color_str = plot["Color"]
        label = plot["Label"]
        reweight_flag, rw_file, rw_flux = plot["reWeight"]
        Var = plot["Var"]
        sysRW_flag, sysRW_file, sysRW_tree, sysRW_branch = plot["sysRW"]
        hist_order.append(key)
        weight_col = ""

        # print(plot["sysRW"])
        # print(sysRW_flag, sysRW_file, sysRW_tree, sysRW_branch)

        # Find matching file
        matches = glob.glob(f"{userFolder}/*{file}*.root")
        if not matches:
            print(f"No file found for key: {file}")
            continue

        file_path = matches[0]
        print(f"Processing {file_path}")

        if (sysRW_flag) :
            f2 = ROOT.TFile(file_path)
            ft2 = f2.Get("FlatTree_VARS")
            ft2.AddFriend(sysRW_tree,sysRW_file)
            print( type(ft2))
            df = ROOT.RDataFrame(ft2)
            df = df.Filter(same1D["Cut"])
            weight_col = sysRW_branch
            print(f"Weight Col:{weight_col} sysrw: {sysRW_branch} ")

        else:
            df = pp.CreateDataFrame(file_path, same1D["Cut"])
        # df = pp.CreateDataFrame(file_path, same1D["Cut"])
        # unfiltered = df.Count().GetValue()
        # df = df.Filter("Enu_true < 8.0 ")
        # frakLost = 1.0 - df.Count().GetValue()/unfiltered
        # print(f"Fraction lost from E Nu cut: {frakLost}")
        # print(f"Events lost from E Nu cut: {unfiltered - df.Count().GetValue()}")
        # print(f'Total Events {df.Count().GetValue()}')

        if Evis:
            df = pp.DefineEvis(df)
        if kin:
            df = pp.DefineKinematics(df)
        if Tki:
            df = pp.DefineTKI(df)
        if reweight_flag:
            df = pp.defineWeightsSpline(df, rw_file, rw_flux)
            weight_col = "weights"

            

        bins = array.array('d',same1D["VBins"][1])

        histInfo = ("name", f"hist_{key}", BinL[0], BinL[1], BinL[2])
        # print("bins")
        # print(bins)
        # print("nbins")
        # print(len(bins) - 1)
        varBinInfo = ROOT.RDF.TH1DModel("h_varbins", f"hist_{key}", len(bins) - 1, bins)

        print("BOOL STATEMENT")
        
        print(weight_col != "")
        if same1D["VBins"][0]:
            histInfo = varBinInfo
        if (weight_col != ""):
            rdf_hist = df.Histo1D(histInfo, plot["Var"], weight_col)
            print("weights used")
        else:
            rdf_hist = df.Histo1D(histInfo, plot["Var"])
            print("WEIGHTS NOT USED")

        hist_rdfs.append(rdf_hist)  # Keep RDF object alive
        hist = rdf_hist.GetValue()
        
        pp.HistoErrorBars(hist)
        if norm and hist.Integral() != 0:
            hist.Scale(1.0 / hist.Integral())
        #hist = sf.formatHist(rdf_hist.GetValue(), xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PlotTitle)
        hist = sf.formatHist(hist, xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PlotTitle)
        print("Bug above^?")
        
        if Add_Ratio and top_histo:
            hist.GetXaxis().SetLabelSize(0)     # hide numbers
            hist.GetXaxis().SetTitleSize(0)     # hide title
            hist.GetXaxis().SetTickLength(0)    # hide ticks
            hist.GetXaxis().SetLabelOffset(999) # hide x axis labels
            top_histo = False
            
        color = getattr(ROOT, color_str.split("+")[0]) + int(color_str.split("+")[1]) if "+" in color_str else getattr(ROOT, color_str)
        hist.SetLineColor(color)
        print(f"color: {color}")
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
