import ROOT
import os


ROOT.gStyle.SetStatX(0.85)  # Closer to the left edge
ROOT.gStyle.SetStatY(0.9)  # Slightly below the top edge

# Apply a modern color palette
ROOT.gStyle.SetPalette(ROOT.kRainBow)  # Choose a visually pleasing palette
ROOT.gStyle.SetNumberContours(50)     # Increase the number of colors in the gradient


# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")

# enables multiprocessing **currently has no multiprocessing***
# ROOT.EnableImplicitMT()

# Allows python to manage the memeory rather than ROOT ***might be causing seg faults***
# ROOT.TH1.AddDirectory(False)


# use Rdataframes to plot the q0 v q3 2DHisto and Q^2 vs W 2DHisto for 2P2H interacions, which have mode 2
# Plan is to get the q0, q3, Q^2 and W for all events where Mode = 2


def formatName(dir_location):
    fileName = f"{HOME}/{dir_location}"
    treeName = "FlatTree_VARS"
    parts = fileName.split('/')
    NameRoot = parts[5]
    NameParts = NameRoot.split('_')
    NameParts[3] = NameParts[3].split('.root')[0]
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]
    return fileName, treeName, NameParts, Name

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

    # hist.GetXaxis().SetLabelSize(0);
    # hist.GetXaxis().SetTickLength(0);

    return hist.Clone()

def formatTcanvas(hist, c):
    # Adjust margins; Default is 0.1; increase as needed
    c.SetLeftMargin(0.15)  # Adjust the left margin to avoid cutting off the y-axis label
    c.SetRightMargin(0.15) #Adjust the right margin to make space for the legend
    c.SetBottomMargin(0.15) #Adjust the bottom margin to avoid cutting off the x-axis label
    hist.Draw("COLZ")
    # c.SetCanvasSize(600,500)
    c.SetCanvasSize(c.GetWw()+200,c.GetWh())

def Plot2P2H(x, y, histogramInfo, title, file_path = None, max = None, Normalize = 0):
    # First get the data into a dataframe
    if file_path is None:
        dir_location = input("Give Flat Tree Directory Location (not including home): ")
    else:
        dir_location = file_path
    fileName, treeName, NameParts, Name = formatName(dir_location)

    df = ROOT.RDataFrame(treeName,fileName)
                         
    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'
    hist1 = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    if Normalize == 1:
       scale = 1/(hist1.Integral())
    #    print(scale)
       hist1.Scale(scale)


    if max is None:
        hist = formatHist(NameParts, hist1 ,'q_{3}', '(GeV)', 'q_{0}', '(GeV)')
    else:
        hist = formatHist(NameParts, hist1 ,'q_{3}', '(GeV)', 'q_{0}', '(GeV)', max = max)
    c = ROOT.TCanvas()

    formatTcanvas(hist,c)
    # saves hist to a specific directory 
    if max is not None:
        c.SaveAs(f"{HOME}/t2k-nova/plots_constant_z_axis/{title}_{Name}.png")
    elif Normalize == 1:
        c.SaveAs(f"{HOME}/t2k-nova/plots_normalized/{title}_{Name}.png")
    else:
        c.SaveAs(f"{HOME}/t2k-nova/plots/{title}_{Name}.png")


def Plot1PI(x, y, histogramInfo, title, file_path = None, max = None, Normalize = 0):
    if file_path is None:
        dir_location = input("Give Flat Tree Directory Location (not including home): ")
    else:
        dir_location = file_path

    fileName, treeName, NameParts, Name = formatName(dir_location)

    df = ROOT.RDataFrame(treeName,fileName)

    # Modes for single Pi are 11-16
    cut1 = 'Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 '
    hist1 = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    if Normalize == 1:
       scale = 1/(hist1.Integral())
    #    print(scale)
       hist1.Scale(scale)


    if max is None:
        hist = formatHist(NameParts, hist1,'W', '(GeV)', 'Q^{2}', '(GeV)^{2}')
    else:
        hist = formatHist(NameParts, hist1,'W', '(GeV)', 'Q^{2}', '(GeV)^{2}', max = max)
    c = ROOT.TCanvas()
    formatTcanvas(hist,c)
    # saves hist to a plots directory
    if max is not None:
        c.SaveAs(f"{HOME}/t2k-nova/plots_constant_z_axis/{title}_{Name}.png")
    elif Normalize == 1:
        c.SaveAs(f"{HOME}/t2k-nova/plots_normalized/{title}_{Name}.png")
    else:
        c.SaveAs(f"{HOME}/t2k-nova/plots/{title}_{Name}.png")


if __name__=="__main__":
    x = 'q3'
    y = 'q0'
    histInfo = ("name",f"{y} vs {x} plot",60,0,3,60,0,3)
    Plot2P2H(x,y,histInfo,"2P2H_hist","skibidi.com", Normalize = 1)
    # x = 'W'
    # y = 'Q2'
    # histInfo = ("name",f"{y} vs {x} plot",60,0,3,120,0,6)
    # Plot1PI(x,y,histInfo,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6.root")








