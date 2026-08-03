import json5
import os
import sys
import src.jsonreader as jsr
import src.SetupFunctions as sf

HOME = os.getenv("HOME", "/home/lboe")
sf.setupRoot
script_path = os.path.realpath(__file__)

if sys.argv[1]:
    Jsonfile = sys.argv[1]
    Jsonfile = Jsonfile + ".json5"
else:
    Jsonfile = "PlotMain.json5"
    print("Defaulting to PlotMain.json5")


script_dir = script_path.replace("PlotMain.py","")
f = open(f'{script_dir}config/{Jsonfile}')
data = json5.load(f)

if not data.get("global"):
    raise ValueError(f"global dictionary not present in {script_dir}config/{Jsonfile}")

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
    print("DEBUG OVER")
else:
    if plots:
        jsr.MakePlots(plots,GlobalSettings)
    if stacks:
        jsr.MakeStacks(stacks,GlobalSettings)
    if overlap:
        jsr.MakeOverlap(overlap,GlobalSettings)
    if same1D:
        jsr.MakeSame1D(same1D,GlobalSettings)
    if Contour:
        jsr.MakeContour(Contour,GlobalSettings)
    if ContourStyle:
        jsr.MakeContourStyle(ContourStyle,GlobalSettings)
    if quantiles:
        jsr.MakeQuantiles(same1D,GlobalSettings)
