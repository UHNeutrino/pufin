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


def Plot2P2H(x, y, histogramInfo, file_path = None):
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
    cut1 = 'Mode == 2'
    hist = df.Filter(cut1).Histo2D(histogramInfo,x,y)
    
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


def SavePlot(hist, title, AxisInfo, dir_location, max = None, Normalize = 0):
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
        hist = SF.formatHist(NameParts, hist ,xvar, xunit, yvar, yunit)
    else:
        hist = SF.formatHist(NameParts, hist ,xvar, xunit, yvar, yunit, max = max)
    
    
    c = ROOT.TCanvas()


    SF.formatTcanvas(hist,c)
    # saves hist to a specific directory 
    if max is not None:
        c.SaveAs(f"{HOME}/t2k-nova/plots_constant_z_axis/{title}_{Name}.png")
    elif Normalize == 1:
        c.SaveAs(f"{HOME}/t2k-nova/plots_normalized/{title}_{Name}.png")
    else:
        c.SaveAs(f"{HOME}/t2k-nova/plots/{title}_{Name}.png")

if __name__=="__main__":
    # Test functions in this area
    # print("What are you testing?")
    x = 'q3'
    y = 'q0'
    AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    histInfo = ("name",f"{y} vs {x} plot",60,0,3,60,0,3)
    hist, file_path = Plot2P2H(x,y,histInfo,"t2k-nova/FlatTrees/FLAT_NEUT_1.0GeV_1e7.root")
    SavePlot(hist,"titlename1",AxisInfo, file_path)
    x = 'W'
    y = 'Q2'
    AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    histInfo = ("name",f"{y} vs {x} plot",60,0,3,120,0,6)
    hist, file_path = Plot1PI(x,y,histInfo,"t2k-nova/FlatTrees/FLAT_NEUT_1.0GeV_1e7.root")
    SavePlot(hist,"testname2",AxisInfo, file_path)








