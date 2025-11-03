import json5
import ROOT
import os
import ParticlePlots as pp 
import SetupFunctions as sf
import glob
import array


HOME = os.getenv("HOME", "/home/lboe")
sf.setupRoot
userFolder = f"/data/t2k-nova/FlatTrees"
f = open(f'{HOME}/t2k-nova/MinooTablePlotsConfig.json5')
data = json5.load(f)

plots = data.get("plots")
stacks = data.get("stacks")
same1D = data.get("1DSame")
Wevo = {"1st Resonance Region": [1.1,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.4,1.6]}




plots_list = same1D["Plots"]
hist_dict = {}
hist_rdfs = []  # Keep these alive to avoid ROOT segfaults
    
AxisInfo = same1D["AxisInfo"].split(",")
BinL = same1D["Bins"]
xvar, xunit, yvar, yunit, PlotTitle = AxisInfo
customL = True
Add_Ratio = same1D.get("Add_Ratio", False)
RatioOf = same1D.get("RatioOf", [])         
RatioRange = same1D.get("RatioRange", [0.5, 1.5])
for Wkey, value in Wevo.items():
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

    print(Wkey)
    print(value)
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
        df = df.Filter(f"W < {value[1]} && W >= {value[0]} ")
        df = df.Filter(plot["Cut2"])
        print(f"Events in {Wkey}: {df.Count().GetValue()} of {unfiltered}")

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

        histInfo = ("name", f"hist_{Wkey}", BinL[0], BinL[1], BinL[2])
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
        PT = "Pion Momentum distribution for " + str(Wkey) + " and Q^{2}>1"
        hist = sf.formatHist(hist, xvar, xunit, yvar, yunit, max=same1D["max"], PlotTitle=PT)
        
        if Add_Ratio and top_histo:
            hist.GetXaxis().SetLabelSize(0)     # hide numbers
            hist.GetXaxis().SetTitleSize(0)     # hide title
            hist.GetXaxis().SetTickLength(0)    # hide ticks
            hist.GetXaxis().SetLabelOffset(999) # hide x axis labels
            top_histo = False
            
        color = getattr(ROOT, color_str.split("+")[0]) + int(color_str.split("+")[1]) if "+" in color_str else getattr(ROOT, color_str)
        hist.SetLineColor(color)
        hist.SetLineStyle(plot["Style"])
        hist.SetLineWidth(1)
        # if (histCounter == 0):
        #     hist.SetLineWidth(2)
        # ^This could be better
        # if (histCounter == 0):
        #     Line = ROOT.TLine(1,0,1,hist.GetBinContent(hist.GetMaximumBin())) 
        # Line.Draw()
        
        if same1D["ErrorBars"]:
            draw_opt = "HIST E1" if len(hist_dict) == 0 else "HIST E1 SAME"
        else:
            draw_opt = "HIST" if len(hist_dict) == 0 else "HIST SAME"
        hist.Draw(draw_opt)
        
        # Line.Draw()
        legend.AddEntry(hist, label, "l")
        hist_dict[key] = hist
        histCounter += 1

    if customL:
        legend = ROOT.TLegend(0.6, 0.6, 0.89, 0.79) ## most plots
        fakeHist1 = ROOT.TH1D()
        fakeHist1.SetLineColor(ROOT.kRed)
        legend.AddEntry(fakeHist1, "NO#nuA Flux", "l")

        fakeHist2 = ROOT.TH1D()
        fakeHist2.SetLineColor(ROOT.kBlue)
        legend.AddEntry(fakeHist2, "T2K Flux", "l")
        
        fakeHist3 = ROOT.TH1D()
        fakeHist3.SetLineStyle(1)
        legend.AddEntry(fakeHist3, "#pi+", "l")

        fakeHist4 = ROOT.TH1D()
        fakeHist4.SetLineStyle(2)
        legend.AddEntry(fakeHist4, "#pi-", "l")

        fakeHist5 = ROOT.TH1D()
        fakeHist5.SetLineStyle(3)
        legend.AddEntry(fakeHist5, "#pi0", "l")


        





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

    # c = pp.DrawXLines(hist, [1.0], hist.GetMaximumBin())

    Nkey = Wkey.replace(" ", "")
    outname = f"{HOME}/{same1D['Save']}/{same1D['Name']}{Nkey}.{same1D['Ext']}"
    # print(outname)
    c.SaveAs(outname)

