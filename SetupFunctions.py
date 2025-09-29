import ROOT
import os
from array import array

def setupRoot():
    ROOT.gStyle.SetStatX(0.85)  # Closer to the left edge
    ROOT.gStyle.SetStatY(0.9)  # Slightly below the top edge
    ROOT.gStyle.SetOptStat(10)  # Only show the number of entries (N)
    # Apply a modern color palette
    ROOT.gStyle.SetPalette(ROOT.kRainBow)  # Choose a visually pleasing palette
    #ROOT.gStyle.SetPalette(ROOT.kViridis)
    # ROOT.gStyle.SetPalette(ROOT.kBird)
    ROOT.gStyle.SetNumberContours(50)     # Increase the number of colors in the gradient

def formatName(dir_location):
    # HOME = os.getenv("HOME", "/home/lboe")
    fileName = dir_location
    parts = fileName.split('/')
    NameRoot = parts[4]
    NameParts = NameRoot.split('_')
    NameParts[3] = NameParts[3].split('.root')[0]
    return NameParts

def formatHist(hist, xvar, xunit, yvar, yunit, max = -1, PlotTitle = None, NameParts = None):
    hist.SetStats(1) #1 for a legend 0 for no legend
    hist.GetXaxis().SetTitle(f"{xvar} {xunit}")
    hist.GetYaxis().SetTitle(f"{yvar} {yunit}")
    if max != -1:
        hist.SetMaximum(max)

    if NameParts is not None:
        hist.SetTitle(f"{yvar} vs. {xvar} ({NameParts[1]}: {NameParts[3]} #nu_{{#mu}} events at {NameParts[2]})")
    if PlotTitle is not None and not "":
        hist.SetTitle(f"{PlotTitle}")
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)
    return hist

def formatTcanvas(hist, c):
    # Adjust margins; Default is 0.1; increase as needed
    c.SetLeftMargin(0.15)  # Adjust the left margin to avoid cutting off the y-axis label
    c.SetRightMargin(0.15) #Adjust the right margin to make space for the legend
    c.SetBottomMargin(0.15) #Adjust the bottom margin to avoid cutting off the x-axis label
    hist.Draw("COLZ") 
    # c.SetCanvasSize(600,500)
    c.SetCanvasSize(c.GetWw()+200,c.GetWh())
    
def formatTcanvasSame(c):
# """Formats a TCanvas for a 1D histogram."""
    # Adjust margins for 1D histograms
    c.SetLeftMargin(0.12)  # Adjust as needed
    c.SetRightMargin(0.05) # Adjust as needed
    c.SetBottomMargin(0.12) # Adjust as needed
    #hist.Draw("HIST")  # Draw the histogram as a standard histogram
    c.SetCanvasSize(c.GetWw(), c.GetWh())

def formatComparisonHist(hist, Compare_type, zmin=None, zmax=None):
    """
    Set a blue-white-red color palette for TH2 histograms and center the color scale.
    
    Parameters:
        hist (ROOT.TH2): The 2D histogram to format.
        Compare_type (str): Either "Difference" (center at 0) or "Ratio" (center at 1).
    """
    from array import array
    n_color_contours = 999

    # Get max and min bin contents
    max_val = hist.GetBinContent(hist.GetMaximumBin())
    min_val = hist.GetBinContent(hist.GetMinimumBin())

    if not hasattr(formatComparisonHist, "initialized"):
        formatComparisonHist.initialized = True
        ROOT.gStyle.SetNumberContours(n_color_contours)

        NRGBs = 3

        stops = array('d', [0.00, 0.5, 1.00])
        red   = array('d', [0.00, 1.00, 1.00])
        green = array('d', [0.00, 1.00, 0.00])
        blue  = array('d', [1.00, 1.00, 0.00])

        colmin = ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, n_color_contours)
        formatComparisonHist.colors = [colmin + i for i in range(n_color_contours)]

    # Set Z-axis range to center color palette
    if zmin != "None" and zmax != "None":
        hist.SetMinimum(zmin)
        hist.SetMaximum(zmax)

    elif Compare_type == "Difference":
        max_abs = max(abs(max_val), abs(min_val))
        hist.SetMinimum(-max_abs)
        hist.SetMaximum(+max_abs)
    # elif Compare_type == "Ratio":
    #     # Set custom palette: blue → black → red
    #     NRGBs = 3
    #     stops = array('d', [0.00, 0.5, 1.00])
    #     red   = array('d', [0.00, 0.00, 1.00])  # red on the right
    #     green = array('d', [0.00, 0.00, 0.00])  # black in the center
    #     blue  = array('d', [1.00, 0.00, 0.00])  # blue on the left

    #     colmin = ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, n_color_contours)
    #     formatComparisonHist.colors = [colmin + i for i in range(n_color_contours)]
        
    #     delta = max(abs(1 - max_val), abs(1 - min_val))
    #     hist.SetMinimum(1 - delta)
    #     hist.SetMaximum(1 + delta)
    #     print("formatComparisonHist does not currently work for Ratio plots.")

    return hist


def modeDic():
    CCmodes={1 : "NEU,N --> LEPTON-,P",
             2 : "NEU,N+X --> LEPTON-,P+X  (X=(N or P))" ,
             11 : "NEU,P --> LEPTON-,P,PI+",
             12 : "NEU,N --> LEPTON-,P,PI0",
             13 : "NEU,N --> LEPTON-,N,PI+",
             15 : "NEU,P --> LEPTON-,P,PI+  ( diffractive )",
             16 : "NEU,O(16) --> LEPTON-,O(16),PI+",
             17 : "NEU,N --> LEPTON-,P,GAMMA",
             26 : "NEU,(N OR P) --> LEPTON-,(N OR P),MESONS"}

    return CCmodes