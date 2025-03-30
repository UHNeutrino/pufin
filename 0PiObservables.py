import ROOT
import os
import ParticlePlots as pp 
import SetupFunctions as sf
import glob


HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"

montecarlo = input("Specify flux or generator: ")
root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')


print(f"Root Files: {root_files}")
modeDic = sf.modeDic()
Wevo = {"1st Resonance Region": [0,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.0,5]}
ZPimodes = [1,2]
print("Making File Plots: ")


for file_path in root_files:
    file_name = file_path.split('/')[-1]
    generator = file_name.split('_')[1]
    flux = file_name.split('_')[2]
    # 0pi data frame
    df0Pi= pp.CreateDataFrame(file_path, "Mode == 1 || Mode == 2")

    # momentum/energy tranfer plot
    # plottitle = "0Pi  q0 vs q3 at E_{#nu} = " + flux
    # histInfo = ("name",f"plop1",60,0,3,60,0,3)
    # AxisInfo1 = ['q3', '(GeV)','q0', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df0Pi,'q3','q0',histInfo)
    # pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/0PiPlots",f"{generator}{flux}0Piq0vsq3")

    #######################
    ### Evis breakdown: ###
    #######################

    # mode breakdown
    # fluxfloat = float(flux.split("GeV")[0])
    # nbins =int(fluxfloat/.1)
    Legend1 = ["QE", "2P2H"]
    colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen, ROOT.kOrange]
    histinfo1D = ("name",f"plop1",60,0,3)


    stack, histlist, Legend = pp.PlotStackedEventModes(df0Pi ,"Evis_1", histinfo1D, ZPimodes, colors)
    AxisInfo = ["E_{vis1} (GeV)", "Events", generator + " Stacked events vs E_{vis1} for #nu_{E} = " + flux]
    pp.SaveStackedHist(stack, histlist, AxisInfo, Legend1,f"/home/lboe/t2k-nova/0PiPlots/{generator}{flux}ModeStacked_Evis1.png")

    stack, histlist, Legend = pp.PlotStackedEventModes(df0Pi ,"Evis_2", histinfo1D, ZPimodes, colors)
    AxisInfo = ["E_{vis2} (GeV)", "Events", generator +  " Stacked events vs E_{vis2} for #nu_{E} = " + flux]
    pp.SaveStackedHist(stack, histlist, AxisInfo, Legend1,f"/home/lboe/t2k-nova/0PiPlots/{generator}{flux}ModeStacked_Evis2.png")

    # stack, histlist, Legend = pp.PlotStackedEventModes(df1Pi ,"Evis_3", histinfo1D, Pimodes, colors)
    # AxisInfo = ["E_{vis3} (GeV)", "Events", generator + " Stacked events vs E_{vis3} for #nu_{E} = " + flux]
    # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{generator}{flux}Modestacked_Evis3.png")

