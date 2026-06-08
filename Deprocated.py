import ROOT
import SetupFunctions as SF
# This holds all deprocated functions:


####################
# Particle Plots####
####################

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


def Plot2P2H(x, y, histogramInfo, file_path = None, Mode = None, Normalize = 0, max = None):
    # First get the data into a dataframe
    if file_path is None:
        dir_location = input("Give Full Flat Tree Directory Location: ")
    else:
        dir_location = file_path
    
    
    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"
    print(fileName)

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    
    df = df.Define("PProton1", """
    double max_proton_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) { // Proton
            double p_magnitude = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
            if (p_magnitude > max_proton_p) {
                max_proton_p = p_magnitude;
            }
        }
    }
    return max_proton_p;
    """)

    df = df.Define("CosProton", """
    double cos_proton = -5.0; // Default value if no proton found
    double max_proton_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) { // Proton
        double p_magnitude = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
        if (p_magnitude > max_proton_p) {
            max_proton_p = p_magnitude;
        }
        }
        if (max_proton_p > 0) {
            cos_proton = pz[i] / max_proton_p; // Dot product with (0, 0, 1)
        }
    }
    return cos_proton;
    """)                    

    # Mode 2 is the 2P2H interaction
    if Mode is not None:
        cut1 = f'Mode == {Mode}'

    else:
        cut1 = 'Mode == 2'
    hist = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    if Normalize==1:
        scale = 1/(hist.Integral())
        hist.Scale(scale)
    
    # **Set Z-axis max value**
    # if max is not None:
    #     hist.SetMaximum(max)  # Ensures max value displayed is consistent
    
    return hist, file_path


def Plot1PI(x, y, histogramInfo, file_path = None):
    if file_path is None:
        dir_location = input("Give Full Flat Tree Directory Location: ")
    else:
        dir_location = file_path

    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    
    
    # Modes for single Pi are 11-16
    cut1 = 'Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 '
    hist = df.Filter(cut1).Histo2D(histogramInfo,x,y)

    return hist, file_path

def Create2DHistogram(df,x,y,histInfo):
    hist = df.Histo2D(histInfo,x,y)
    return hist

def Create1DHistogram(df,x,histInfo):
    hist = df.Histo1D(histInfo,x)
    return hist


def defineWeightsOld(df, rwRootFile, histName):
    flux_file = ROOT.TFile.Open(rwRootFile)
    hist = flux_file.Get(histName)  
    hist.SetDirectory(0)  
    flux_file.Close()

    # print(type(hist))

    # stupid hack to get the correct varible type TH1D or TH1F 
    a = str(type(hist)).split("TH1")[1][0]
    # print(a)
    ROOT.gROOT.ProcessLine(f"TH1{a}* fluxHist;")  # Declare a global variable in C++
    ROOT.fluxHist = hist  # Assign your Python-side TH1D to the C++ global

    ROOT.gInterpreter.Declare("""
    double getFluxWeight(double energy) {
        int bin = fluxHist->GetXaxis()->FindBin(energy);
        double weight = fluxHist->GetBinContent(bin);
        return weight;
    }
    """)
    df = df.Define("weights", "getFluxWeight(Enu_true)")

    return df



def defineWeightsOLD2(df, rwRootFile, histName):
    flux_file = ROOT.TFile.Open(rwRootFile)
    hist = flux_file.Get(histName)  
    hist.SetDirectory(0)  
    flux_file.Close()

    # print(type(hist))

    # stupid hack to get the correct varible type TH1D or TH1F 
    a = str(type(hist)).split("TH1")[1][0]
    # print(a)
    ROOT.gROOT.ProcessLine(f"TH1{a}* fluxHist;")  # Declare a global variable in C++
    ROOT.fluxHist = hist  # Assign your Python-side TH1D to the C++ global

    ROOT.gInterpreter.Declare("""
    double getFluxWeight(double energy) {
        int n = fluxHist->GetNbinsX();
        double x[n]{};
        double y[n]{};

        for (int i = 1; i <= n; i++) {
            x[i-1] = fluxHist->GetBinCenter(i);
            y[i-1] = fluxHist->GetBinContent(i);
        }

        TGraph* graph = new TGraph(n,x,y);                  
        TSPline* spline = new TSPline(*graph);
    
        double weight = spline->Eval(energy);
        delete spline;
        delete graph;                      
        return weight;
    }
    """)
    df = df.Define("weights", "getFluxWeight(Enu_true)")

    return df


def defineWeightsNewBROKEN(df, rwRootFile, histName):
    flux_file = ROOT.TFile.Open(rwRootFile)
    hist = flux_file.Get(histName)  
    hist.SetDirectory(0)  
    flux_file.Close()

    # print(type(hist))

    # stupid hack to get the correct varible type TH1D or TH1F 
    a = str(type(hist)).split("TH1")[1][0]
    # print(a)
    ROOT.gROOT.ProcessLine(f"TH1{a}* fluxHist;")  # Declare a global variable in C++
    ROOT.fluxHist = hist  # Assign your Python-side TH1D to the C++ global

    # Create TSpline3 from histogram
    spline_name = f"spline_{histName}"
    spline = ROOT.TSpline3(spline_name, hist)

    # Register spline in C++ so it can be used inside the RDataFrame
    ROOT.gInterpreter.ProcessLine(f"TSpline3* fluxSpline = (TSpline3*){ROOT.AddressOf(spline)};")

    # Define function to evaluate spline and use it in DataFrame
    ROOT.gInterpreter.Declare("""
        extern TSpline3* fluxSpline;
        double get_flux_weight(double E) {
            return fluxSpline->Eval(E);
        }
    """)

    # Define new column in DataFrame
    df = df.Define("weights", f"get_flux_weight(Enu_true)")

    return df

#######################
# Particles Macro #####
#######################
import ParticlePlots as pp
import PlotQuantiles as pq
import glob
import os
import ROOT


HOME = os.getenv("HOME", "/home/lboe")


userFolder = f"/data/t2k-nova/FlatTrees"
root_files = glob.glob(userFolder + '/*NEUT*.root')

print(root_files)

max_frequency_1PI = -float('inf')  # Initialize with the smallest possible value
max_frequency_2P2H = -float('inf')

for file in root_files:
    # format correctly
    file_path = file.split('t2k-nova')[1]
    file_path = 't2k-nova' + file_path
  
    x = 'q3'
    y = 'q0' 
    
    AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
    histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    #hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    hist, path = Plot1PI(x,y,histInfo1,file_path)
    pp.SavePlot(hist,"1PI_W_vs_Q2", AxisInfo, path)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist, "1PI_hist_max", AxisInfo, path, max = .035, Normalize=1)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist,"1PI_hist_Normalized", AxisInfo,path, Normalize = 1)

    x = 'W'
    y = 'Q2'
    AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    pp.SavePlot(hist,"2P2H_q3_vs_q0", AxisInfo, path)
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist_max", AxisInfo, path, max = .016, Normalize = 1)
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist_Normalized", AxisInfo, path, Normalize = 1)


    # # Make q0 vs q3 histogram to find quantiles with equal events
    # x = 'q3'
    # y = 'q0'
    
    
    # x_bins, total_events = pq.constant_binning(x, y, file_path=file_path)
    
    # # Apply quantile_cutting to make a new dataframe for each quantile 
    # quantile_dfs = pq.quantile_cutting(x, y, x_bins, file_path=file_path)
    
    # # Check: Print the number of events in each quantile
    # for i, df in enumerate(quantile_dfs):
    #     print(f"Quantile {i+1}: {df.Count().GetValue()} events")
        
    # # Make plots for each dataframe
    # y = 'CosLep'
    # x = 'PLep'
    
    # #AxisInfo = ['cos{theta}', '', 'E Lep', '(GeV)'] not using this yet
    # histInfo = ("name", f"{y} vs {x} plot", 60, 0, 3.5,102, -1.02, 1.02)
    
    # # Create and save a plot for each quantile
    # for i, df in enumerate(quantile_dfs):
    #     # Define a title for the current quantile plot
    #     title = f"Quantile_{i+1}"
    #     pq.PlotQuantiles(x, y, histInfo, file_path=file_path, df = df, title = title)


    
# print(f"The highest frequency across all normalized 1PI plots is: {max_frequency_1PI}")
# print(f"The highest frequency across all normalized 2P2H plots is: {max_frequency_2P2H}")

# Now plot constant frequency (z axis) files using max_frequency_1PI and max_frequency_2P2H
# currently not fixed to reflect PP changes
fixed = False
if fixed:
    for file in root_files:
        # format correctly
        file_path = file.split('t2k-nova')[1]
        file_path = 't2k-nova' + file_path
        
        x = 'W'
        y = 'Q2'
        histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
        histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
        
        pp.Plot1PI(x,y,histInfo1,"1PI_hist_max",file_path, max = max_frequency_1PI, Normalize=1)
        
        x = 'q3'
        y = 'q0' 
        
        pp .Plot2P2H(x,y,histInfo2,"2P2H_hist_max",file_path, max = max_frequency_2P2H, Normalize=1)







#####################
## Quantiles Macro ##
#####################
import PlotQuantiles as pq
import ParticlePlots as pp
import SetupFunctions as sf
import os 
import glob

HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"
montecarlo = input("Enter the name of your montecarlo: NEUT, NOvA, or ICARUS. If you want to generate plots for all Flat Trees in the directory hit 'enter' ")

#root_files = glob.glob(userFolder + '/*NOvA*.root')
root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')
print(f"Root Files: {root_files}")

modeDic = sf.modeDic()

print("Making File Plots: ")

for file_path in root_files :

    pq.PlotSegments(file_path=file_path)
    pq.PlotGrid(file_path=file_path)



###############################
## Units rework (abandoned) ##
##############################

import ROOT
import ParticlePlots as pp
import array
import SetupFunctions as SF

class FluxObject:
    Targets = {"T2K":5.9e29, "NOvA":5.6e31}
    xsecScale = {"NEUTAll":3.10e-37,"GENIECC":2.379e-37}
    Exposure = {"T2K":19.7e20, "NOvA":26.6e20}
    FluxPot = {"enu_nd5_23a_untuned_numu":1e21, "cafanauniq0":5e21}
    UnitsDir = {"enu_nd5_23a_untuned_numu":["50MeV","1e21POT","cm^{2}"], "cafanauniq0":["5e21POT","m^{2}"]}

    def __init__(self,Generator=None, h=None, histPathTuple=None):
        if h:
            self.Fhist = h.Clone()
            self.Fhist.SetDirectory(0)  # idk what this does
        elif histPathTuple:
            rootPath,hist_name = histPathTuple
            f = ROOT.TFile.Open(rootPath)
            h = f.Get(hist_name)
            if not h:
                raise ValueError(f"Histogram {hist_name} not found.")
            self.Fhist = h.Clone()
            self.Fhist.SetDirectory(0)
            f.Close()
        else:
            raise ValueError("Provide either hist or (root_file, hist_name)")
        

        n_points0 = self.Fhist.GetNbinsX()
        j = 1
        a = 0
        self.BinEdges = []
        while a<8:
            j+=1
            a = self.Fhist.GetBinLowEdge(j)
            self.BinEdges.append(a)
            # print(a)
            
        # print(self.BinEdges)
        # print(len(self.BinEdges))
        # print(j)
        n_points0 = j-1
        self.BinN = n_points0
        graph0 = ROOT.TGraph(n_points0)
        self.y = []
        for i in range(1, n_points0 + 1):
            x = self.Fhist.GetBinCenter(i)
            y = self.Fhist.GetBinContent(i) / self.Fhist.Integral("Width")
            graph0.SetPoint(i - 1, x, y)
            self.y.append(y)


        self.Spline = ROOT.TSpline3(f"g_fluxSpline_{hist_name}", graph0)
        self.Units = "#nu/"
        self.UnitsDen = []
        for u in self.UnitsDir[hist_name]:
            self.Units += u
            self.Units += " "
            self.UnitsDen.append(u)
        if ("MeV".casefold() in a.casefold for a in self.UnitsDen) or("GeV".casefold() in a.casefold for a in self.UnitsDen) :
            print("Bin Width Normed!~")
            self.bwNormed = True
        else:
            self.bwNormed = False
        self.Integral = self.Fhist.Integral("Width")
        self.BinEdgesA = array.array('d', self.BinEdges)
        self.Title = "Default Title"
        self.XTitle = "E_{#nu} GeV"
        print("Made Flux Object")

    def MakeHist(self):
        self.hist = ROOT.TH1D("h1", f"{self.Title}; {self.XTitle}; {self.Units}", self.BinN-1, self.BinEdgesA)
        for i in range(1, self.BinN+1):
            center = self.hist.GetBinCenter(i)
            Ncontent = self.Spline.Eval(center) * self.Integral
            self.hist.SetBinContent(i, Ncontent)
        self.hist.SetStats(0)
        print("Histogram Made")
    
    def ChangeBinning(self,bins=None, histPathTuple=None):
        if histPathTuple:
            rootPath,hist_name = histPathTuple
            f = ROOT.TFile.Open(rootPath)
            h = f.Get(hist_name)
            if not h:
                raise ValueError(f"Histogram {hist_name} not found.")
            Bhist = h.Clone()
            Bhist.SetDirectory(0)
            f.Close()
            nbins = []
            j = 1
            a = 0
            while a<8:
                j+=1
                a = Bhist.GetBinLowEdge(j)
                nbins.append(a)
            n_points = j-1
        elif bins:
            nbins = bins
            n_points = len(nbins)-1
        else:
            raise ValueError("Provide either bins or (root_file, hist_name)")
        if self.bwNormed:
            self.BinEdges = nbins
            self.BinN = n_points
        else:
            #if it's not bin width normalized than the integral changes and the shape could change
            total = 0
            Newtotal = 0
            variableBW = False
            newWidth = nbins[1] - nbins[0]
            for i in range(0,n_points):
                if(newWidth != nbins[i+1]-nbins[i]):
                    variableBW = True
                newWidth = nbins[i+1]-nbins[i]
                Newtotal += newWidth * self.y[i]
            widthFactor = total/n_points
            self.BinEdges = nbins
            self.BinN = n_points


    
    def SplineToFlatFlux(self,Generator=None):
        if Generator=="NEUT":
            self.df = ROOT.RDataFrame("FlatTree_VARS","/data/t2k-nova/FlatTrees/Flat_NEUT5.9_flatf_1e7.root")
        elif Generator=="GENIE":
            self.df = ROOT.RDataFrame("FlatTree_VARS","/data/t2k-nova/FlatTrees/Flat_GenieN24_flatf_1e7.root")

    def SaveHistroot(self, path, name):
        out_file = ROOT.TFile(f"{path}/{name}/.root","UPDATE")
        self.hist.Write()
        out_file.Close()
        print(f"Saved to {path}/{name}/.root")
    def SaveHistpng(self, path, name):
        c = ROOT.TCanvas()
        SF.formatTcanvas(self.hist,c)
        c.SaveAs(f"{path}/{name}.png")
        print(f"Histogram png saved to {path}/{name}.png")

        
        
###################### 0PI Observables:
# import ROOT
# import os
# import ParticlePlots as pp 
# import SetupFunctions as sf
# import glob


# HOME = os.getenv("HOME", "/home/lboe")
# userFolder = f"/data/t2k-nova/FlatTrees"

# montecarlo = input("Specify flux or generator: ")
# root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')


# print(f"Root Files: {root_files}")
# modeDic = sf.modeDic()
# Wevo = {"1st Resonance Region": [0,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
# Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.0,5]}
# ZPimodes = [1,2]
# print("Making File Plots: ")


# for file_path in root_files:
#     file_name = file_path.split('/')[-1]
#     generator = file_name.split('_')[1]
#     flux = file_name.split('_')[2]
#     # 0pi data frame
#     df0Pi= pp.CreateDataFrame(file_path, "Mode == 1 || Mode == 2")
#     df0Pi = pp.DefineEvis(df0Pi)

#     # momentum/energy tranfer plot
#     # plottitle = "0Pi  q0 vs q3 at E_{#nu} = " + flux
#     # histInfo = ("name",f"plop1",60,0,3,60,0,3)
#     # AxisInfo1 = ['q3', '(GeV)','q0', '(GeV)', plottitle]
#     # hist2p_q = pp.Create2DHistogram(df0Pi,'q3','q0',histInfo)
#     # pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/0PiPlots",f"{generator}{flux}0Piq0vsq3")

#     #######################
#     ### Evis breakdown: ###
#     #######################

#     # mode breakdown
#     # fluxfloat = float(flux.split("GeV")[0])
#     # nbins =int(fluxfloat/.1)
#     Legend1 = ["QE", "2P2H"]
#     colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen, ROOT.kOrange]
#     histinfo1D = ("name",f"plop1",60,0,3)


#     stack, histlist, Legend = pp.PlotStackedEventModes(df0Pi ,"Evis_1", histinfo1D, ZPimodes, colors)
#     AxisInfo = ["E_{vis1} (GeV)", "Events", generator + " Stacked events vs E_{vis1} for #nu_{E} = " + flux]
#     pp.SaveStackedHist(stack, histlist, AxisInfo, Legend1,f"/home/lboe/t2k-nova/0PiPlots/{generator}{flux}ModeStacked_Evis1.png")

#     stack, histlist, Legend = pp.PlotStackedEventModes(df0Pi ,"Evis_2", histinfo1D, ZPimodes, colors)
#     AxisInfo = ["E_{vis2} (GeV)", "Events", generator +  " Stacked events vs E_{vis2} for #nu_{E} = " + flux]
#     pp.SaveStackedHist(stack, histlist, AxisInfo, Legend1,f"/home/lboe/t2k-nova/0PiPlots/{generator}{flux}ModeStacked_Evis2.png")

#     stack, histlist, Legend = pp.PlotStackedEventModes(df0Pi ,"Evis_kin", histinfo1D, ZPimodes, colors)
#     AxisInfo = ["E_{visKin} (GeV)", "Events", generator + " Stacked events vs E_{visKin} for #nu_{E} = " + flux]
#     pp.SaveStackedHist(stack, histlist, AxisInfo, Legend1,f"/home/lboe/t2k-nova/0PiPlots/{generator}{flux}ModeStacked_EvisKin.png")

#     # stack, histlist, Legend = pp.PlotStackedEventModes(df1Pi ,"Evis_3", histinfo1D, Pimodes, colors)
#     # AxisInfo = ["E_{vis3} (GeV)", "Events", generator + " Stacked events vs E_{vis3} for #nu_{E} = " + flux]
#     # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/0PiPlots/{generator}{flux}Modestacked_Evis3.png")


# 1Pi Observables:
# import ROOT
# import os
# import ParticlePlots as pp 
# import SetupFunctions as sf
# import glob

# ROOT.EnableImplicitMT()

# #file_path = '/data/t2k-nova/FlatTrees/Flat_GenieNOvA_3.0GeV_1e7_v2.root'
# #file_path = '/data/t2k-nova/FlatTrees/Flat_GenieNOvA_3.0GeV_1e7_v2.root'
# HOME = os.getenv("HOME", "/home/lboe")
# userFolder = f"/data/t2k-nova/FlatTrees"

# ## Use this option to run 1 file (change file name):
# root_files = glob.glob(userFolder + '/*NOvAflux_1e6.root')

# ## Use this option to run all files, or all files for a specific generator:
# # montecarlo = input("Specify flux or generator: ")
# # root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')

# ## Use this option to run all files for a specific flux:
# # flux = input("Enter the flux of the root files you want to select: 0.5, 0.6, 0.7, 1.0, 1.5, 2.0, 3.0: ")
# # root_files = glob.glob(userFolder + f'/*{flux}*.root')


# print(f"Root Files: {root_files}")

# modeDic = sf.modeDic()
# Wevo = {"1st Resonance Region": [0,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
# Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.0,5]}
# Pimodes = [11,12,13,15,16]

# print("Making File Plots: ")

# deleting text files to reset them
# os.system(f"rm {HOME}/t2k-nova/minooValues.txt")

# for file_path in root_files:
    # file_name = file_path.split('/')[-1]
    # generator = file_name.split('_')[1]
    # flux = file_name.split('_')[2]
    # x_bins, total_events = pq.constant_event_binning(x, y, file_path, Mode = 
    # 1pi
    # plottitle = "W vs Q^{2} for 1Pi events at #nu_{E} =" + flux
    # histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5) ('Test Title', 'Test Title', 60.0, 1.1, 2.4, 105.0, -0.1, 5.0)
    # AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
    # df1Pi= pp.CreateDataFrame(file_path, "Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 ")
    # # hist2p_q = df1Pi.Histo2D(histInfo,'W','Q2')
    # df1Pi.Snapshot("main", "/home/lboe/t2k-nova/1Pi.root", ("W","Q2"))
    # pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots",f"{generator}{flux}1PiWvQ2","pdf")
    

    ##################################################################
    ##### Evis vs Etrue - add minimum thresholds for all of these? ####
    ##################################################################
    
    ### Version 1: Evis = EvAlt (q0 - KE neutrons - mass pions) + ELep ###

    # plottitle = f"{generator}: E_{{vis1}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['W', '(GeV)','E_{vis} = q0 - KE_{neutrons} - Mass_{pions} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'W','Evis_1',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V1)vE_{flux}_{generator}")

    ### Version 2 (from Erecoil in Nuiance github): Evis2 = KE (protons & charged pions) + E (pi0, e+/-, photons, muon) 

    # plottitle = f"{generator}: E_{{vis2}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['W', '(GeV)','           E_{vis} = KE_{pr; pi+/-} + E_{pi0; e-/+; photons} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'W','Evis_2',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V2)vE_{flux}_{generator}")
    
    ### Version 3 (Eavail from NOvA): Evis = Evis2 + skip bindinos & nucleons 
    # + total energy minus proton mass of (Primarily) strange baryons
    # since decays will mostly contain protons 
    # + total energy plus proton mass of (primarily) anti-protons 
    # since anhillation is mostly the interaction mode
    # + if no neutrons or leptons (mostly kaons) just add all the energy
    
    # plottitle = f"{generator}: E_{{vis3}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{vis 3}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Evis_3',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V3)vE_{flux}_{generator}")

    # plottitle = f"{generator}: E_{{vis1}} vs W for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['W', '(GeV)','E_{vis} = q0 - KE_{neutrons} - Mass_{pions} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'W','Evis_1',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V1)vW_{flux}_{generator}")

    #########################################
    ### Evis 1D (all 3 versions together) ###
    #########################################

    # plottitle = f"{generator}: E_{{vis}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5)
    # AxisInfo2 = ['E_{vis}', '(GeV)', 'Frequency', '(# of Events)', plottitle]
    # hist1_result = pp.Create1DHistogram(df1Pi, 'Evis_1', histInfo2)
    # hist2_result = pp.Create1DHistogram(df1Pi, 'Evis_2', histInfo2)
    # hist3_result = pp.Create1DHistogram(df1Pi, 'Evis_3', histInfo2)

    # hist1 = hist1_result.GetValue()
    # hist2 = hist2_result.GetValue()
    # hist3 = hist3_result.GetValue()
    # hist_list = [hist1, hist2, hist3]

    # # pp.SaveHistSame(hist1, hist2, hist3,AxisInfo2,"t2k-nova/1PiPlots",f"1PiEvis_{flux}_{generator}")
    # pp.SaveHistSame(hist1, hist2, hist3,AxisInfo2,"t2k-nova",f"1PiEvis_{flux}_{generator}")

    ################################################################
    ### Ratio of Evis Variations - modify for different versions ###
    #################################################################
    # plottitle = f"{generator}: Ratio of E_{{vis1}} / E_{{vis2}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5)
    # AxisInfo2 = ['E_{vis}', '', 'Ratio', '', plottitle]
    # histEvis1_result = pp.Create1DHistogram(df1Pi,'Evis_1',histInfo2)
    # histEvis2_result = pp.Create1DHistogram(df1Pi,'Evis_2',histInfo2)

    # histEvis1 = histEvis1_result.GetValue() #get TH1D
    # histEvis2 = histEvis2_result.GetValue() #get TH1D

    # ratio_hist = histEvis1.Clone(plottitle)
    # ratio_hist.SetTitle(plottitle)

    # # Divide hist1 by hist2
    # ratio_hist.Divide(histEvis2)

    # pp.Savehist(ratio_hist,AxisInfo2,"t2k-nova/1PiPlots",f"1PiEvisRatio_1v2_{flux}_{generator}")
    #pp.Savehist(ratio_hist,AxisInfo2,"t2k-nova",f"1PiRatioE2vE3_{flux}_{generator}")

    ###############################################
    ### Evis vs W (Sub in Evis, Evis2 or Evis3) ###
    ###############################################

    #max = .12 # for 0.7 GeV
    # max = .05 # for 2.0 GeV
    # plottitle = f"{generator}: E_{{vis3}} vs W for 1Pi events at #nu_{{E}} = " + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['W', '(GeV)','E_{vis3}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'W','Evis_3',histInfo2)
    # #hist2p_q.SetMaximum(max)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V3)vW_{flux}_{generator}", max = None, Normalize=0)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova",f"1PiE(V1)vE_{flux}_{generator}")

    ######################
    ### Minoo sections ###
    #######################
    # totalE = df1Pi.Count().GetValue()
    # with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
    #             f.write(f"For {generator} at Enu = {flux} \n")
    #             f.write(f"Total Events: {totalE} \n \n")
    # Wevo = {"1st Resonance Region": [1.1,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
    # Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.4,1.6]}

    # regionnum = 0

    # for reigon in Wevo:
    #     plottitle = reigon + " " + "W vs Q^{2} for 1Pi events at #nu_{E} = " + flux
    #     AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
    #     # print(Wevo[reigon][0])
    #     # print(Wevo[reigon][1])
        
    #     histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5)
    #     Wdf = df1Pi.Filter(f"W >= {Wevo[reigon][0]} && W < {Wevo[reigon][1]}")
    #     # Qdf1 = Wdf.Filter("Q2 <= 1.0")
    #     # Qdf2 = Wdf.Filter("Q2 > 1")
    #     if  Wdf.Count().GetValue() == 0:
    #         print("No events in reigon, break")
    #         with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
    #             f.write("No events in reigon, break \n")
    #         break
    #     Wevo[reigon] = Wdf
    #     hist2p_q = pp.Create2DHistogram(Wdf,'W','Q2',histInfo)
    #     regionnum += 1
    #     # pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots",f"{flux}1PiWvQ2V2Reigon{regionnum}")

    #     # Printing event numbers for each reigon (Make diagram in google slides)
    #     totalN = Wdf.Count().GetValue()                
    #     for mode in Pimodes:
    #         modedf = Wdf.Filter(f"Mode == {mode}")
    #         filteredN = modedf.Count().GetValue()

            
    #         percent = filteredN/totalN

    #         printstring = str(modeDic.get(mode)) + " Events in " + str(reigon) + ": "+ str(filteredN) + " out of " + str(totalN) +  f" ({percent} %)"
    #         #File Writing
    #         with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
    #             f.write(f"{printstring}\n")
    #     #adding specific values that Dan wants:
    #     sum1df = Wdf.Filter("Mode == 11 || Mode == 13")
    #     printstring2 = f"Sum of mode 11 and 13: {sum1df.Count().GetValue()}\n "

    #     sum2df = sum1df.Filter("Q2<=1.0")
    #     printstring2 += f"Sum less than Q2 = 1: {sum2df.Count().GetValue()} ({sum2df.Count().GetValue()/sum1df.Count().GetValue()} % of 11 and 13) \n"

    #     sum3df = sum1df.Filter("Q2>1.0")
    #     printstring2 += f"Sum greater than Q2 = 1: {sum3df.Count().GetValue()} ({sum3df.Count().GetValue()/sum1df.Count().GetValue()} % of 11 and 13) \n"

    #     percTotal = totalN/df1Pi.Count().GetValue()
    #     printstring2 += f"Percent of total 1pi events: {percTotal}\n"


    #     # Stacked Event Plotting
    #     # colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kYellow, ROOT.kBlue, ROOT.kGreen, ROOT.kOrange]
    #     # histinfo1D = ("name",f"plop1",40,0.5,2.5)
    #     # stack, histlist, Legend = pp.PlotStackedEventModes(Wdf,"W", histinfo1D, Pimodes, colors)
    #     # AxisInfo = ["W (GeV)", "Events", reigon + " Stacked events vs W for #nu_{E} = " + flux]
    #     # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{flux}stacked_eventsReigon{regionnum}.png")


    #     with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
    #             f.write(printstring2)
    #             f.write("\n \n")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------        

    ### E_kinQE vs E true (REC) - haven't checked
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",40,0.5,.9,40,0,0.85)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")


    ### enu_QE vs enu_TRUE - this is working, needs formatting to move the stats box to the left edge
    # plottitle = f"{generator}: Enu_QE vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','Enu_QE', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Enu_QE',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(QE)vE_{flux}_{generator}")

    #####################
    ### TKI variables ###
    #####################
    
    # TKI 2D (Including Neutrons)
    # plottitle = f"{generator}: #delta_pT vs P_{{#mu}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3,100,0,2.5)
    # AxisInfo2 = ['P_{#mu}', '(GeV/c)','#delta_pt (Including Neutrons)', '(GeV/c)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'PLep','TKI_IN',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiTKI_INvp_{flux}_{generator}", Normalize=2)

    
    # TKI 1D (Including Neutrons)
    # plottitle = f"{generator}: #delta P_{{T}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,2.5)
    # AxisInfo2 = ['#delta P_{T}', '(GeV/c)', '# of Events', '', plottitle]
    # hist1_result = pp.Create1DHistogram(df1Pi, 'TKI_IN', histInfo2)
    # hist1 = hist1_result.GetValue()
    # pp.Savehist(hist1,AxisInfo2,"t2k-nova/1PiPlots",f"1Pi1DTKI_IN_{flux}_{generator}")
    
    # # TKI 2D (Omitting Neutrons)
    # plottitle = f"{generator}: #delta_pT vs P_{{#mu}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3,100,0,2.5)
    # AxisInfo2 = ['P_{#mu}', '(GeV/c)','#delta_pt (Omitting Neutrons)', '(GeV/c)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'PLep','TKI_ON',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiTKI_ONvp_{flux}_{generator}", Normalize=2)
    
    # TKI 1D (Omitting Neutrons)
    # plottitle = f"{generator}: #delta P_{{T}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,2.5)
    # AxisInfo2 = ['#delta P_{T}', '(GeV/c)', '# of Events', '', plottitle]
    # hist1_result = pp.Create1DHistogram(df1Pi, 'TKI_ON', histInfo2)
    # hist1 = hist1_result.GetValue()
    # pp.Savehist(hist1,AxisInfo2,"t2k-nova/1PiPlots",f"1Pi1DTKI_ON_{flux}_{generator}")

    # Proton kinematics - haven't checked - Do we need this here? We do this in PlotQuantiles I think
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ### Evis breakdown: ###
    #######################

    # mode breakdown
    # fluxfloat = float(flux.split("GeV")[0])
    # nbins =int(fluxfloat/.1)


    # colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen, ROOT.kOrange, ]
    # histinfo1D = ("name",f"plop1",60,0,3)

    # stack, histlist, Legend = pp.PlotStackedEventModes(df1Pi ,"Evis_1", histinfo1D, Pimodes, colors)
    # AxisInfo = ["E_{vis1} (GeV)", "Events", generator + " Stacked events vs E_{vis1} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}stacked_Evis1.png")

    # stack, histlist, Legend = pp.PlotStackedEventModes(df1Pi ,"Evis_2", histinfo1D, Pimodes, colors)
    # AxisInfo = ["E_{vis2} (GeV)", "Events", generator +  " Stacked events vs E_{vis2} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}stacked_Evis2.png")

    # stack, histlist, Legend = pp.PlotStackedEventModes(df1Pi ,"Evis_3", histinfo1D, Pimodes, colors)
    # AxisInfo = ["E_{vis3} (GeV)", "Events", generator + " Stacked events vs E_{vis3} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}Modestacked_Evis3.png")


    # Minoo reigon breakdown
    # print("starting Evis Minoo regions")
    # colors2 = [ROOT.kBlue, ROOT.kBlue +1,ROOT.kGreen, ROOT.kGreen +1,ROOT.kYellow +1, ROOT.kYellow +2, ROOT.kRed, ROOT.kRed +1 ]
    # Q2k = list(Q2evo.keys())
    # Wk = list(Wevo.keys())
    # minoodf = df1Pi.Filter("Mode == 11 || Mode == 13")
    # stack1 = ROOT.THStack("stack1","")
    # stack2 = ROOT.THStack("stack2","")
    # stack3 = ROOT.THStack("stack3","")
    # histlist1 = []
    # histlist2 = []
    # histlist3 = []
    # LegendM = ["1st Res Non-P", "1st Res Trans","2nd Res Non-P", "2nd Res Trans","3rd Res Non-P", "3rd Res Trans","DIS Non-P", "DIS Trans" ]
    # k = 0
    # for i in range(len(Wevo)):
    #     for j in range(len(Q2evo)):
    #         tempdf = minoodf.Filter(f" W > {Wevo[Wk[i]][0]}    &&  W <= {Wevo[Wk[i]][1]} ")
    #         regiondf = tempdf.Filter(f" Q2 > {Q2evo[Q2k[j]][0]}  &&  Q2 <= {Q2evo[Q2k[j]][1]}")
    #         hist1 = regiondf.Histo1D(histinfo1D,"Evis_1")
    #         hist2 = regiondf.Histo1D(histinfo1D,"Evis_2")
    #         hist3 = regiondf.Histo1D(histinfo1D,"Evis_3")
    #         # print(colors2[i])
    #         hist1.SetFillColor(colors2[k])
    #         th1d = hist1.GetPtr()
    #         stack1.Add(th1d)
    #         histlist1.append(th1d)

    #         hist2.SetFillColor(colors2[k])
    #         th1d2 = hist2.GetPtr()
    #         stack2.Add(th1d2)
    #         histlist2.append(th1d2)

    #         hist3.SetFillColor(colors2[k])
    #         th1d3 = hist3.GetPtr()
    #         stack3.Add(th1d3)
    #         histlist3.append(th1d3)

    #         k+=1
    #         # LegendM.append((Wk[i]) + " and " + Q2k[j])
    #         print(f"{LegendM[k]}")

    # AxisInfoMinoo = ["E_{vis1} (GeV)", "Events", " Stacked events vs E_{vis1} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack1, histlist1, AxisInfoMinoo, LegendM,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}stacked_MReigonsEvis1.png")
    # AxisInfoMinoo = ["E_{vis2} (GeV)", "Events", " Stacked events vs E_{vis2} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack2, histlist2, AxisInfoMinoo, LegendM,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}stacked_MReigonsEvis2.png")
    # AxisInfoMinoo = ["E_{vis3} (GeV)", "Events", " Stacked events vs E_{vis3} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack3, histlist3, AxisInfoMinoo, LegendM,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}stacked_MReigonsEvis3.png")




if __name__=="__main__":
    print("Don't run this")
    # a = FluxObject(histPathTuple= ("/data/t2k-nova/fluxes/23av1_nom/nd5_numode_23a_nominal_finebins.root","enu_nd5_23a_untuned_numu"))
    # a.MakeHist()
    # a.SaveHistpng("/home/lboe","test3")
    # print(a.Fhist.GetBinCenter(a.BinN))
