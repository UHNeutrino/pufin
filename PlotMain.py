import json5
import os
import src.jsonreader as jsr
import src.SetupFunctions as sf

HOME = os.getenv("HOME", "/home/lboe")
sf.setupRoot
script_path = os.path.realpath(__file__)
script_dir = script_path.replace("PlotMain.py","")
f = open(f'{script_dir}/config/PlotMain.json5')
data = json5.load(f)

GlobalSettings = data.get("global")
if GlobalSettings["DebugMode"]:
    fD = open(f'{script_dir}/config/debug.json5')
    data = json5.load(fD)
    print("ACTIVATING DEBUG MODE")
    GlobalSettings["Save"] = script_dir + "DebugPlots"
    os.makedirs(GlobalSettings["Save"], exist_ok=True)

plots = data.get("plots")
stacks = data.get("stacks")
overlap = data.get("overlap")
same1D = data.get("1DSame")
Contour = data.get("Contour")
ContourStyle = data.get("ContourStyle")
quantiles = data.get("quantiles")

if GlobalSettings["DebugMode"]:
    print("Starting Plots")
    try:
        jsr.MakePlots(plots,GlobalSettings)
    except:
        print("Plots Failed")
    
    print("Starting Stacks")
    try:
        jsr.MakeStacks(stacks,GlobalSettings)
    except:
        print("Stacks Failed")

    print("Starting Overlap")
    try:
        jsr.MakeOverlap(overlap,GlobalSettings)
    except:
        print("Overlap Failed")
    
    print("Starting Same1D")
    try:
        jsr.MakeSame1D(same1D,GlobalSettings)
    except:
        print("Same1D Failed")
    
    print("Starting Contour")
    try:
        jsr.MakeContour(Contour,GlobalSettings)
    except:
        print("Contour Failed")
    
    print("Starting Contour Style")

    try:
        jsr.MakeContourStyle(ContourStyle,GlobalSettings)
    except:
        print("Contour Style Failed")

    print("Starting Quantiles")

    try:
        jsr.MakeQuantiles(same1D,GlobalSettings)
    except:
        print("Quantiles Failed")
    print("DEBUG OVER")
else:
    if plots["Bool"]:
        jsr.MakePlots(plots,GlobalSettings)
    if stacks["Bool"]:
        jsr.MakeStacks(stacks,GlobalSettings)
    if overlap["Bool"]:
        jsr.MakeOverlap(overlap,GlobalSettings)
    if same1D["Bool"]:
        jsr.MakeSame1D(same1D,GlobalSettings)
    if Contour["Bool"]:
        jsr.MakeContour(Contour,GlobalSettings)
    if ContourStyle["Bool"]:
        jsr.MakeContourStyle(ContourStyle,GlobalSettings)
    if quantiles["Bool"]:
        jsr.MakeQuantiles(same1D,GlobalSettings)
