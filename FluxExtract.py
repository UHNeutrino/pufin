import ROOT
import os
import PlotQuantiles as pq
import ParticlePlots as pp 
import SetupFunctions as sf
import glob

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import array as pyarray
import ROOT

HOME = os.getenv("HOME", "/home/lboe")
# ---- output directory ----
experiment = "NOvA"
outdir = f"{HOME}/t2k-nova/test"
outfile = "ratio_ExtractedProd5_Travis_flux"

userFolder1 = f"/data/t2k-nova/FlatTrees"
userFolder2 = f"/data/t2k-nova/Histograms"
userFolder3 = f"/home/kdobbs/t2k-nova/test"
userFolder4 = f"/data/t2k-nova/fluxes"

# rw_file = "/data/t2k-nova/fluxes/NOvAFlux.root"
# rw_flux = "cafanauniq0"
#Fscale = 1.0
AxisInfo = ['True E_{#nu}', 'GeV', 'Events', '', "title"]

ratio_min = 0.8
ratio_max = 1.4

#### file1 should be the full MC from which we want to extract the flux
file1 = f"{userFolder2}/CAFAnAprod5_AllFiles_skewfix.root"
hist_name_1 = "hEnu_Numu"
scale1 = 1/200
WF = 1.55701627557e-12 # (26.6e20/5.54e21)*(3.89137e31/12)*1e-42
#WF=1
hist1_label = "Extracted Flux from CAFAnA"

#### file2 is the flux to which we will compare the extracted flux
file2 = f"{userFolder4}/NOvAFlux50MeVTravis.root"
hist_name_2 ="cafanauniq0"
hist2_label = "Travis Flux 50 MeV"
# file3 = f"{userFolder3}/CC_tot.root"
# file4 = f"{userFolder3}/CC_npCohMecD12.root"

# Genie xsec paths
pathx = "/data/t2k-nova/xsec-splines/genie_xsec/v3_06_00/NULL/G1810a0211b-k250-e1000/data/xsec_graphs.root"
#pathx = "/data/t2k-nova/xsec-splines/genie_xsec/v3_06_00/NULL/N2420i0211b-k250-e1000/data/xsec_graphs.root"
CCpath = "nu_mu_C12/tot_cc"
NCpath = "nu_mu_C12/tot_nc"

def rebin_hist_to_match(hsrc, href, name="h2_rebinned"):
    # build target bin edges from href
    nb = href.GetNbinsX()
    edges = [href.GetXaxis().GetBinLowEdge(1)]
    for i in range(1, nb + 1):
        edges.append(href.GetXaxis().GetBinUpEdge(i))
    edges_arr = pyarray.array('d', edges)

    # create destination hist with exact binning
    hnew = ROOT.TH1D(name, hsrc.GetTitle(), nb, edges_arr)
    hnew.Sumw2()

    # integrate source bins into each target bin
    for i in range(1, nb + 1):
        lo = hnew.GetXaxis().GetBinLowEdge(i)
        hi = hnew.GetXaxis().GetBinUpEdge(i)

        # clamp to source range
        src_lo = max(lo, hsrc.GetXaxis().GetXmin())
        src_hi = min(hi, hsrc.GetXaxis().GetXmax())
        if src_hi <= src_lo:
            continue

        b1 = hsrc.GetXaxis().FindBin(src_lo + 1e-12)
        b2 = hsrc.GetXaxis().FindBin(src_hi - 1e-12)

        val = hsrc.Integral(b1, b2)

        # error propagation (bin-sum approximation)
        err2 = 0.0
        for b in range(b1, b2 + 1):
            err2 += hsrc.GetBinError(b) ** 2

        hnew.SetBinContent(i, val)
        hnew.SetBinError(i, err2 ** 0.5)

    hnew.SetDirectory(0)
    return hnew



if not os.path.exists(file1):
    raise RuntimeError(f"Missing file1: {file1}")
if not os.path.exists(file2):
    raise RuntimeError(f"Missing file2: {file2}")
# if not os.path.exists(file3):
#     raise RuntimeError(f"Missing file2: {file3}")
# if not os.path.exists(file4):
#     raise RuntimeError(f"Missing file2: {file4}")

# ---- load hist2 from ROOT file ----
f1 = ROOT.TFile.Open(file1, "READ")
if not f1 or f1.IsZombie():
    raise RuntimeError(f"Could not open {file1}")

hist1 = f1.Get(f"{hist_name_1}")
if not hist1:
    f1.ls()
    raise RuntimeError(f"Could not find histogram {hist_name_1} in file1")
hist1 = hist1.Clone("hist1")   # detach from file
hist1.SetDirectory(0)
f1.Close()

tot = hist1.Integral()
print (f"hist1 integral = {tot}")
s = scale1
hist1.Scale(s)
scaled = hist1.Integral()
print(f"scaled integral = {scaled}")

##### divide by cross sections #################

fx = ROOT.TFile.Open(pathx, "READ")
if not fx or fx.IsZombie():
    raise RuntimeError(f"Could not open xsec file: {pathx}")

g_cc = fx.Get(CCpath)
g_nc = fx.Get(NCpath)
if not g_cc or not g_nc:
    fx.ls()
    raise RuntimeError(f"Missing graph(s): CC={CCpath} NC={NCpath}")

g_cc = g_cc.Clone("g_cc")
g_nc = g_nc.Clone("g_nc")
fx.Close()

# Make a new hist with identical binning
hist1Ex = hist1.Clone("hist1Ex")
hist1Ex.SetTitle("hist1Ex")          # optional
hist1Ex.SetDirectory(0)              # detach from any file
hist1Ex.Reset("ICES")                # clear contents/errors (keeps binning)

# (Optional but recommended) ensure errors exist
hist1.Sumw2()
hist1Ex.Sumw2()
  
for i in range(1, hist1.GetNbinsX() + 1):
    x = hist1.GetBinCenter(i)
    y = hist1.GetBinContent(i)
    w = hist1.GetBinWidth(i)
    #print(w)
    
    # evaluate CC/NC xsecs at this energy
    CCxsec = float(g_cc.Eval(x))
    NCxsec = float(g_nc.Eval(x))

    # clip negatives to 0
    if CCxsec < 0: CCxsec = 0.0
    if NCxsec < 0: NCxsec = 0.0

    xsec = (CCxsec) + (NCxsec)
    #xsec = 1
    ynew = y/(xsec*WF) 
    hist1Ex.SetBinContent(i, ynew)
    
total = hist1Ex.Integral()    

print(f"bin integral after extraction = {total}")

f2 = ROOT.TFile.Open(file2, "READ")
if not f2 or f2.IsZombie():
    raise RuntimeError(f"Could not open {file2}")

hist2 = f2.Get(f"{hist_name_2}")
if not hist2:
    f2.ls()
    raise RuntimeError(f"Could not find histogram '{hist_name_2}' in file2")

totalOrig = hist2.Integral()
print(f"total original flux bin integral = {totalOrig}")
xmax = 8.0
b2 = hist2.GetXaxis().FindFixBin(xmax)  # bin that contains 8.0
# if that bin extends past 8, step back one bin
if hist2.GetXaxis().GetBinUpEdge(b2) > xmax + 1e-12:
    b2 -= 1

totalOrig_up_to_8 = hist2.Integral(1, b2)
print("Integral (bins ending at/below 8 GeV) =", totalOrig_up_to_8)
# totalOrigW = hist2.Integral("width")
# print(f"total original flux width integral = {totalOrigW}")
s = totalOrig_up_to_8/total

print(s)

# detach from file so it survives after close
hist2 = hist2.Clone("h2")
hist2.SetDirectory(0)
f2.Close()

for i in range(1, hist2.GetNbinsX() + 1):
    y = hist2.GetBinContent(i)
    e = hist2.GetBinError(i)
    w = hist2.GetBinWidth(i)

# ---- put hist2 into same shape/binning as hist1 ----
# If they already match, great. If not, rebin hist2 into hist1's binning.
same_binning = (
    hist1Ex.GetNbinsX() == hist2.GetNbinsX()
    and abs(hist1Ex.GetXaxis().GetXmin() - hist2.GetXaxis().GetXmin()) < 1e-9
    and abs(hist1Ex.GetXaxis().GetXmax() - hist2.GetXaxis().GetXmax()) < 1e-9
)

if not same_binning:
    hist2 = rebin_hist_to_match(hist2, hist1Ex, name="h2_rebinned_to_hist1Ex")

# ---- ratio ----
ratio = hist1Ex.Clone("hRatio")
ratio.SetDirectory(0)
ratio.SetTitle("")
ratio.Sumw2()
hist1Ex.Sumw2()
hist2.Sumw2()
ratio.Divide(hist2)

# ---- save outputs ----
outroot = f"{outdir}/{outfile}.root"
out = ROOT.TFile.Open(outroot, "RECREATE")
hist1Ex.Write("h1")
hist2.Write("h2")
ratio.Write("hRatio")
out.Close()

c = ROOT.TCanvas("c", "c", 800, 800)

topPad   = ROOT.TPad("topPad",   "top",   0.0, 0.30, 1.0, 1.0)
ratioPad = ROOT.TPad("ratioPad", "ratio", 0.0, 0.00, 1.0, 0.30)

topPad.SetBottomMargin(0.02)
topPad.SetLeftMargin(0.14)
topPad.SetRightMargin(0.05)

ratioPad.SetTopMargin(0.06)
ratioPad.SetBottomMargin(0.35)
ratioPad.SetLeftMargin(0.14)
ratioPad.SetRightMargin(0.05)
ratioPad.SetGridy()

topPad.Draw()
ratioPad.Draw()

# --- style + draw top ---
topPad.cd()

h1 = hist1Ex.Clone("h1")
h2 = hist2.Clone("h2")
h1.SetDirectory(0)
h2.SetDirectory(0)
h1.SetStats(0)
h2.SetStats(0)

h1.SetLineColor(ROOT.kRed)
h2.SetLineColor(ROOT.kBlack)
h1.SetLineWidth(2)
h2.SetLineWidth(2)

# Make y-range so both are visible
ymax = max(h1.GetMaximum(), h2.GetMaximum()) * 1.25
h1.SetMaximum(ymax)

h1.GetYaxis().SetTitle("Neutrinos")
h1.GetXaxis().SetLabelSize(0)  # hide x labels on top pad
h1.GetXaxis().SetTitleSize(0)

h1.Draw("HIST")
h2.Draw("HIST SAME")

leg = ROOT.TLegend(0.60, 0.70, 0.92, 0.88)
leg.SetBorderSize(0)
leg.AddEntry(h1, f"{hist1_label}", "l")
leg.AddEntry(h2, f"{hist2_label}", "l")
leg.Draw()

# --- draw ratio ---
ratioPad.cd()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

r = ratio.Clone("hRatio_draw")
r.SetDirectory(0)
r.SetStats(0)
r.SetTitle("")
r.SetLineColor(ROOT.kBlack)
r.SetLineWidth(1)

r.GetYaxis().SetTitle(f"Extracted / {experiment}")
r.GetYaxis().SetNdivisions(505)
r.GetYaxis().SetTitleSize(0.10)
r.GetYaxis().SetTitleOffset(0.70)
r.GetYaxis().SetLabelSize(0.10)
r.GetYaxis().SetTickLength(0.03)

r.GetXaxis().SetTitle("E_{#nu}^{true} (GeV)")
r.GetXaxis().SetTitleSize(0.12)
r.GetXaxis().SetLabelSize(0.10)
r.GetXaxis().SetTitleOffset(1.05)
r.GetXaxis().SetTickLength(0.08)

# range
xmin = r.GetXaxis().GetXmin()
xmax = r.GetXaxis().GetXmax()
ymin, ymax = ratio_min, ratio_max
r.SetMinimum(ymin)
r.SetMaximum(ymax)

# --- force a frame that definitely draws tick labels ---
frame = ratioPad.DrawFrame(xmin, ymin, xmax, ymax)
r.Draw("E1 SAME")
frame.GetYaxis().SetTitle(f"Extracted / {experiment}")
frame.GetYaxis().SetNdivisions(505)
frame.GetYaxis().SetTitleSize(0.10)
frame.GetYaxis().SetTitleOffset(0.70)
frame.GetYaxis().SetLabelSize(0.10)
frame.GetYaxis().SetTickLength(0.03)

frame.GetXaxis().SetTitle("E_{#nu}^{true} (GeV)")
frame.GetXaxis().SetTitleSize(0.12)
frame.GetXaxis().SetTitleOffset(1.05)
frame.GetXaxis().SetLabelSize(0.10)
frame.GetXaxis().SetTickLength(0.08)

r.Draw("E1")

# line at 1
line = ROOT.TLine(xmin, 1.0, xmax, 1.0)
line.SetLineStyle(2)
line.Draw("SAME")

ratioPad.Modified()
ratioPad.Update()

xmin = r.GetXaxis().GetXmin()
xmax = r.GetXaxis().GetXmax()
line = ROOT.TLine(xmin, 1.0, xmax, 1.0)
line.SetLineStyle(2)
line.Draw("SAME")

outpng = f"{outdir}/{outfile}.png"
c.SaveAs(outpng)

# Re-open ROOT file and store the canvas as a 4th object
out = ROOT.TFile.Open(outroot, "UPDATE")
c.Write("c_ratio_panel")   # 4th object: the combo view
out.Close()

print(f"Wrote {outroot} and {outpng}")
