import ROOT
import os

def setupRoot():
    ROOT.gStyle.SetStatX(0.85)  # Closer to the left edge
    ROOT.gStyle.SetStatY(0.9)  # Slightly below the top edge
    ROOT.gStyle.SetOptStat(10)  # Only show the number of entries (N)
    # Apply a modern color palette
    ROOT.gStyle.SetPalette(ROOT.kRainBow)  # Choose a visually pleasing palette
    ROOT.gStyle.SetNumberContours(50)     # Increase the number of colors in the gradient

def formatName(dir_location):
    # HOME = os.getenv("HOME", "/home/lboe")
    HOME = "/data"
    fileName = f"{HOME}/{dir_location}"
    treeName = "FlatTree_VARS"
    parts = fileName.split('/')
    NameRoot = parts[4]
    NameParts = NameRoot.split('_')
    NameParts[3] = NameParts[3].split('.root')[0]
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    return NameParts

def formatHist(NameParts, hist, xvar, xunit, yvar, yunit, max = -1):
    hist.SetStats(1) #1 for a legend 0 for no legend
    hist.GetXaxis().SetTitle(f"{xvar} {xunit}")
    hist.GetYaxis().SetTitle(f"{yvar} {yunit}")
    if max != -1:
        hist.SetMaximum(max)
    hist.SetTitle(f"{yvar} vs. {xvar} ({NameParts[1]}: {NameParts[3]} #nu_{{#mu}} events at {NameParts[2]})")
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)
    return hist.Clone()

def formatTcanvas(hist, c):
    # Adjust margins; Default is 0.1; increase as needed
    c.SetLeftMargin(0.15)  # Adjust the left margin to avoid cutting off the y-axis label
    c.SetRightMargin(0.15) #Adjust the right margin to make space for the legend
    c.SetBottomMargin(0.15) #Adjust the bottom margin to avoid cutting off the x-axis label
    hist.Draw("COLZ")
    # c.SetCanvasSize(600,500)
    c.SetCanvasSize(c.GetWw()+200,c.GetWh())