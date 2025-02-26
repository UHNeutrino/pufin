import ROOT
import os
import SetupFunctions as SF


SF.setupRoot()



# enables multiprocessing **currently has no multiprocessing***
# ROOT.EnableImplicitMT()

# Allows python to manage the memeory rather than ROOT ***might be causing seg faults***
# ROOT.TH1.AddDirectory(False)

# use Rdataframes to plot the q0 v q3 2DHisto and Q^2 vs W 2DHisto for 2P2H interacions, which have mode 2
# Plan is to get the q0, q3, Q^2 and W for all events where Mode = 2
HOME = os.getenv("HOME", "/home/lboe")


def Plot2P2H(x, y, histogramInfo, file_path = None, Mode = None):
    # First get the data into a dataframe
    if file_path is None:
        dir_location = input("Give Flat Tree Directory Location (not including /data): ")
    else:
        dir_location = file_path
    
    
    fileName = f"/data/{dir_location}"
    treeName = "FlatTree_VARS"
    print(fileName)

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
                         
    # Mode 2 is the 2P2H interaction
    if Mode is not None:
        cut1 = f'Mode == {Mode}'

    else:
        cut1 = 'Mode == 2'
    df = df.Filter(cut1).Histo2D(histogramInfo,x,y)
    
    return hist, file_path


def Plot1PI(x, y, histogramInfo, file_path = None):
    if file_path is None:
        dir_location = input("Give Flat Tree Directory Location (not including home): ")
    else:
        dir_location = file_path

    fileName = f"/data/{dir_location}"
    treeName = "FlatTree_VARS"

    df = ROOT.RDataFrame(treeName,fileName)

    # Modes for single Pi are 11-16
    cut1 = 'Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 '
    hist = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    return hist, file_path


def SavePlot(hist, title, AxisInfo, dir_location, max = None, Normalize = 0, PlotTitle  = None):
    NameParts = SF.formatName(dir_location)
    Name = NameParts[1] + "_" + NameParts[2] + "_" + NameParts[3]

    xvar = AxisInfo[0]
    xunit = AxisInfo[1]
    yvar = AxisInfo[2]
    yunit = AxisInfo[3]

    if Normalize == 1:
       scale = 1/(hist.Integral())
    #    print(scale)
       hist.Scale(scale)
    if max is None:
        max = -1
    if PlotTitle is None:
        PlotTitle = ""
  
    hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, max = max, PlotTitle=PlotTitle, NameParts = NameParts)
    
    c = ROOT.TCanvas()


    SF.formatTcanvas(hist,c)
    # saves hist to a specific directory 
    if max is not None:
        c.SaveAs(f"{HOME}/t2k-nova/plots_constant_z_axis/{title}_{Name}.png")
    elif Normalize == 1:
        c.SaveAs(f"{HOME}/t2k-nova/plots_normalized/{title}_{Name}.png")
    else:
        c.SaveAs(f"{HOME}/t2k-nova/plots/{title}_{Name}.png")


def CreateDataFrame(file_path, cut):    # First get the data into a dataframe
    if file_path is None:
        dir_location = input("Give Flat Tree Directory Location (not including /data): ")
    else:
        dir_location = file_path
    
    
    fileName = f"/data/{dir_location}"
    treeName = "FlatTree_VARS"
    print(fileName)

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")

    df = df.Filter(cut)
    return df

def Create2DHistogram(df,x,y,histInfo):
    hist = df.Histo2D(histInfo,x,y)
    return hist


def Savehist(hist,AxisInfo, save_location, filename, max = None, Normalize = 0):
    xvar = AxisInfo[0]
    xunit = AxisInfo[1]
    yvar = AxisInfo[2]
    yunit = AxisInfo[3]
    PlotTitle = AxisInfo[4]

    if Normalize == 1:
       scale = 1/(hist.Integral())
       hist.Scale(scale)

    if max is not None:
        hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, max = max, PlotTitle=PlotTitle)
    hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)
    c = ROOT.TCanvas()
    SF.formatTcanvas(hist,c)
    c.SaveAs(f"{HOME}/{save_location}/{filename}.png")

def DrawXLines(hist, x_bins, y_max):
    c = ROOT.TCanvas()
    SF.formatTcanvas(hist,c)
    line_list = ROOT.TList()
       
    for i in range(0,len(x_bins)):
        print(f"saving line {i} at {x_bins[i]}")
        myline = ROOT.TLine(x_bins[i],0,x_bins[i],y_max)
        line_list.Add(myline)
        line_list[-1].Draw()

    return c 
        

if __name__=="__main__":
    # Test functions in this area
    # print("What are you testing?")
    x = 'q3'
    y = 'q0'
    AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    histInfo = ("name",f"{y} vs {x} plot",60,0,3,60,0,3)
    hist, file_path = Plot2P2H(x,y,histInfo,"t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e7.root")
    df2p2h = CreateDataFrame(file_path, "Mode == 2")
    hist  = Create2DHistogram(df2p2h,'q3','q0',histInfo)
    SavePlot(hist,"titlename1",AxisInfo, file_path)
    x = 'W'
    y = 'Q2'
    # AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    # histInfo = ("name",f"{y} vs {x} plot",60,0,3,120,0,6)
    # hist, file_path = Plot1PI(x,y,histInfo,"t2k-nova/FlatTrees/FLAT_NEUT_0.7GeV_1e7.root")
    # SavePlot(hist,"testname2",AxisInfo, file_path)








