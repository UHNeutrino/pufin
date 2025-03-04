import ROOT
import PlotQuantiles as pq
import ParticlePlots as pp 
import SetupFunctions as sf
import glob






# file_path = '/data/t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6v2.root'
userFolder = f"/data/t2k-nova/FlatTrees"
root_files = glob.glob(userFolder + '/*NEUT*7.root')
print(f"Root Files: {root_files}")

for file_path in root_files:
    file_name = file_path.split('/')[-1]
    generator = file_name.split('_')[1]
    flux = file_name.split('_')[2]
    # x_bins, total_events = pq.constant_event_binning(x, y, file_path, Mode = 
    # 1pi
    plottitle = "W vs Q^{2} for 1Pi events at #nu_{E} =" + flux
    histInfo = ("name",f"plop1",40,1.1,1.8,42,-0.1,2)
    AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
    df1Pi= pp.CreateDataFrame(file_path, "Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 ")
    hist2p_q = pp.Create2DHistogram(df1Pi,'W','Q2',histInfo)
    pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots","1PiWvQ2V2")

    # Evis vs Etrue 
    plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvEV2")



    # Minoo sections

    Wevo = {"1st Resonance Region": [1.1,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
    Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.4,1.6]}
    
    for reigon in Wevo:
        plottitle = reigon + " " + "W vs Q^{2} for 1Pi events at #nu_{E} = " + flux
        AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
        print(Wevo[reigon][0])
        print(Wevo[reigon][1])
        
        histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5)
        Wdf = df1Pi.Filter(f"W >= {Wevo[reigon][0]} && W < {Wevo[reigon][1]}")
        Wevo[reigon] = Wdf
        hist2p_q = pp.Create2DHistogram(Wdf,'W','Q2',histInfo)
        pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots",f"{flux}1PiWvQ2V2{reigon}")
        Pimodes = [11,12,13,15,16]
        colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kYellow, ROOT.kBlue, ROOT.kGreen, ROOT.kOrange]
        
        histinfo1D = ("name",f"plop1",40,0.5,1.8)
        stack, histlist, Legend = pp.PlotStackedEventModes(Wdf, histinfo1D, Pimodes, colors)
        AxisInfo = ["W (GeV)", "Events", reigon + "Stacked events vs W for #nu_{E} = " + flux]
        pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{flux}stacked_events{reigon}.png")

    



    # E_kinQE vs E true (REC) 
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",40,0.5,.9,40,0,0.85)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")


    # enu_QE vs enu_TRUE
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")

    # TKI variables (look at talks or something)
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")

    # Proton kinematics
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")
