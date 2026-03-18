import json5
import jsonreader as jsr
import os
import SetupFunctions as sf

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
ContourStyle = data.get("ContourStyle")

if plots["Bool"]:
    jsr.MakePlots(plots)
