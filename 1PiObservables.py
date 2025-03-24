import ROOT
import os
import PlotQuantiles as pq
import ParticlePlots as pp 
import SetupFunctions as sf
import glob

#file_path = '/data/t2k-nova/FlatTrees/Flat_GenieNOvA_3.0GeV_1e7_v2.root'
#file_path = '/data/t2k-nova/FlatTrees/Flat_GenieNOvA_3.0GeV_1e7_v2.root'
HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"

# Use this option to run 1 file (change file name):
root_files = glob.glob(userFolder + '/*NEUT_2.0GeV*.root')

# Use this option to run all files, or all files for a specific generator:
# montecarlo = input("Enter the name of your montecarlo: NEUT, NOvA, or AR23. If you want to generate plots for all Flat Trees in the directory hit 'enter'")
# root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')

# Use this option to run all files for a specific flux:
# flux = input("Enter the flux of the root files you want to select: 0.5, 0.6, 0.7, 1.0, 1.5, 2.0, 3.0: ")
# root_files = glob.glob(userFolder + f'/*{flux}*.root')


print(f"Root Files: {root_files}")

modeDic = sf.modeDic()

print("Making File Plots: ")

# deleting text files to reset them
os.system(f"rm {HOME}/t2k-nova/minooValues.txt")

for file_path in root_files:
    file_name = file_path.split('/')[-1]
    generator = file_name.split('_')[1]
    flux = file_name.split('_')[2]
    # x_bins, total_events = pq.constant_event_binning(x, y, file_path, Mode = 
    # 1pi
    plottitle = "W vs Q^{2} for 1Pi events at #nu_{E} =" + flux
    histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5)
    AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
    df1Pi= pp.CreateDataFrame(file_path, "Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 ")
    hist2p_q = pp.Create2DHistogram(df1Pi,'W','Q2',histInfo)
    # pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots",f"{flux}1PiWvQ2V2")

    ##################################################################
    ##### Evis vs Etrue - add minium thresholds for all of these? ####
    ##################################################################
    
    ### Version 1: Evis = EvAlt (q0 - KE neutrons - mass pions) + ELep ###

    # plottitle = f"{generator}: E_{{vis1}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{vis} = q0 - KE_{neutrons} - Mass_{pions} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Evis_1',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V1)vE_{flux}_{generator}")

    ### Version 2 (from Erecoil in Nuiance github): Evis2 = KE (protons & charged pions) + E (pi0, e+/-, photons, muon) 

    # plottitle = f"{generator}: E_{{vis2}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','           E_{vis} = KE_{pr; pi+/-} + E_{pi0; e-/+; photons} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Evis_2',histInfo2)
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

    # pp.SaveHistSame(hist1, hist2, hist3,AxisInfo2,"t2k-nova/1PiPlots",f"1PiEvis_{flux}_{generator}")
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
    totalE = df1Pi.Count().GetValue()
    with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write(f"For {generator} at Enu = {flux} \n")
                f.write(f"Total Events: {totalE} \n \n")
    Wevo = {"1st Resonance Region": [1.1,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
    Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.4,1.6]}
    regionnum = 0

    for reigon in Wevo:
        plottitle = reigon + " " + "W vs Q^{2} for 1Pi events at #nu_{E} = " + flux
        AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
        # print(Wevo[reigon][0])
        # print(Wevo[reigon][1])
        
        histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5)
        Wdf = df1Pi.Filter(f"W >= {Wevo[reigon][0]} && W < {Wevo[reigon][1]}")
        if  Wdf.Count().GetValue() == 0:
            print("No events in reigon, break")
            with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write("No events in reigon, break \n")
            break
        Wevo[reigon] = Wdf
        hist2p_q = pp.Create2DHistogram(Wdf,'W','Q2',histInfo)
        regionnum += 1
        # pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots",f"{flux}1PiWvQ2V2Reigon{regionnum}")

        # Printing event numbers for each reigon (Make diagram in google slides)
        Pimodes = [11,12,13,15,16]
                
        for mode in Pimodes:
            modedf = Wdf.Filter(f"Mode == {mode}")
            totalN = Wdf.Count().GetValue()
            filteredN = modedf.Count().GetValue()

            
            percent = filteredN/totalN

            printstring = str(modeDic.get(mode)) + " Events in " + str(reigon) + ": "+ str(filteredN) + " out of " + str(totalN) +  f" ({percent} %)"
            print()
            print(printstring)
            print()
            #File Writing
            with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write(f"{printstring}\n")
        # Stacked Event Plotting
        # colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kYellow, ROOT.kBlue, ROOT.kGreen, ROOT.kOrange]
        # histinfo1D = ("name",f"plop1",40,0.5,2.5)
        # stack, histlist, Legend = pp.PlotStackedEventModes(Wdf, histinfo1D, Pimodes, colors)
        # AxisInfo = ["W (GeV)", "Events", reigon + " Stacked events vs W for #nu_{E} = " + flux]
        # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{flux}stacked_eventsReigon{regionnum}.png")
        with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write("\n \n")
        

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

    ############################################
    ### TKI variables: need to recalculate!! ###
    ############################################
    
    # TKI (Including Neutrons)
    # plottitle = f"{generator}: TKI vs P_{{#mu}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3,100,-1.5,1.5)
    # AxisInfo2 = ['P_{#mu}', '(GeV/c)','TKI (Including Neutrons)', '(GeV/c)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'PLep','TKI_IN',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiTKI_INvp_{flux}_{generator}", Normalize=2)
    
    # # TKI (Omitting Neutrons)
    # plottitle = f"{generator}: TKI vs P_{{#mu}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3,100,-1.5,1.5)
    # AxisInfo2 = ['P_{#mu}', '(GeV/c)','TKI (Omitting Neutrons)', '(GeV/c)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'PLep','TKI_ON',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiTKI_ONvp_{flux}_{generator}", Normalize=2)

    # Proton kinematics - haven't checked
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")
