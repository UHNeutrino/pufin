import ROOT
import os
import PlotQuantiles as pq
import ParticlePlots as pp 
import SetupFunctions as sf
import glob



# file_path = '/data/t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6v2.root'
HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"
montecarlo = input("Enter the name of your montecarlo: NEUT, NOvA, or AR23. If you want to generate plots for all Flat Trees in the directory hit 'enter' ")

#root_files = glob.glob(userFolder + '/*NOvA*.root')
root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')
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

    # Evis vs Etrue - add minium thresholds for all of these?
    
    # Version 1: Evis = EvAlt (q0 - KE neutrons - mass pions) + ELep  
    # plottitle = f"{generator}: E_{{vis1}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{vis} = q0 - KE_{neutrons} - Mass_{pions} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Evis_1',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V1)vE_{flux}_{generator}")

    # Version 2 (from Erecoil in Nuiance github): Evis2 = KE (protons & charged pions) + E (pi0, e+/-, photons, muon) 
    # plottitle = f"{generator}: E_{{vis2}} vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','           E_{vis} = KE_{pr; pi+/-} + E_{pi0; e-/+; photons} + E_{#mu}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Evis_2',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(V2)vE_{flux}_{generator}")
    
    # Version 3 (Eavail from NOvA): Evis = Evis2 + skip bindinos & nucleons 
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



    # Minoo sections
    totalE = df1Pi.Count().GetValue()
    with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write(f"For {generator} at Enu = {flux} \n")
                f.write(f"Total Events: {totalE} \n \n")
    Wevo = {"1st Resonance Region": [0,1.4], "2nd Resonance Region": [1.4,1.6], "3rd Resonance Region": [1.6,2.0],"DIS": [2.0,2.4]}
    Q2evo = {"non-preterbative region": [0,1.0], "Transition Region": [1.0,5]}
    regionnum = 0

    for reigon in Wevo:
        plottitle = reigon + " " + "W vs Q^{2} for 1Pi events at #nu_{E} = " + flux
        AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]
        # print(Wevo[reigon][0])
        # print(Wevo[reigon][1])
        
        histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5)
        Wdf = df1Pi.Filter(f"W >= {Wevo[reigon][0]} && W < {Wevo[reigon][1]}")
        # Qdf1 = Wdf.Filter("Q2 <= 1.0")
        # Qdf2 = Wdf.Filter("Q2 > 1")
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
        totalN = Wdf.Count().GetValue()                
        for mode in Pimodes:
            modedf = Wdf.Filter(f"Mode == {mode}")
            filteredN = modedf.Count().GetValue()

            
            percent = filteredN/totalN

            printstring = str(modeDic.get(mode)) + " Events in " + str(reigon) + ": "+ str(filteredN) + " out of " + str(totalN) +  f" ({percent} %)"
            #File Writing
            with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write(f"{printstring}\n")
        #adding specific values that Dan wants:
        sum1df = Wdf.Filter("Mode == 11 || Mode == 13")
        printstring2 = f"Sum of mode 11 and 13: {sum1df.Count().GetValue()}\n "

        sum2df = sum1df.Filter("Q2<=1.0")
        printstring2 += f"Sum less than Q2 = 1: {sum2df.Count().GetValue()} ({sum2df.Count().GetValue()/sum1df.Count().GetValue()} % of 11 and 13) \n"

        sum3df = sum1df.Filter("Q2>1.0")
        printstring2 += f"Sum greater than Q2 = 1: {sum3df.Count().GetValue()} ({sum3df.Count().GetValue()/sum1df.Count().GetValue()} % of 11 and 13) \n"

        percTotal = totalN/df1Pi.Count().GetValue()
        printstring2 += f"Percent of total 1pi events: {percTotal}\n"


        # Stacked Event Plotting
        # colors = [ROOT.kRed ,ROOT.kViolet, ROOT.kYellow, ROOT.kBlue, ROOT.kGreen, ROOT.kOrange]
        # histinfo1D = ("name",f"plop1",40,0.5,2.5)
        # stack, histlist, Legend = pp.PlotStackedEventModes(Wdf, histinfo1D, Pimodes, colors)
        # AxisInfo = ["W (GeV)", "Events", reigon + " Stacked events vs W for #nu_{E} = " + flux]
        # pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,f"/home/lboe/t2k-nova/1PiPlots/{flux}stacked_eventsReigon{regionnum}.png")


        with open(f"{HOME}/t2k-nova/minooValues.txt", "a") as f:
                f.write(printstring2)
                f.write("\n \n")
        

    # E_kinQE vs E true (REC) - haven't checked
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",40,0.5,.9,40,0,0.85)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")


    # enu_QE vs enu_TRUE - this is working, needs formatting to move the stats box to the left edge
    # plottitle = f"{generator}: Enu_QE vs E_{{#nu true}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3.5,100,0,3.5)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','Enu_QE', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Enu_QE',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiE(QE)vE_{flux}_{generator}")

    # TKI variables - working
    
    # TKI (Including Neutrons)
    # plottitle = f"{generator}: TKI vs P_{{#mu}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3,100,-1.5,1.5)
    # AxisInfo2 = ['P_{#mu}', '(GeV/c)','TKI (Including Neutrons)', '(GeV/c)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'PLep','TKI_IN',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiTKI_INvp_{flux}_{generator}")
    
    # # TKI (Omitting Neutrons)
    # plottitle = f"{generator}: TKI vs P_{{#mu}} for 1Pi events at #nu_{{E}} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,3,100,-1.5,1.5)
    # AxisInfo2 = ['P_{#mu}', '(GeV/c)','TKI (Omitting Neutrons)', '(GeV/c)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'PLep','TKI_ON',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots",f"1PiTKI_ONvp_{flux}_{generator}")

    # Proton kinematics - haven't checked
    # plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
    # histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
    # AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
    # hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
    # pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")
