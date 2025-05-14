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


def DefineEvis(df):
    # Define Evis_1 where EavAlt = q0 - KE(neutrons) - mass(pions)
    df = df.Define("Evis_1", "EavAlt + ELep")
    
    # E_had = KE (protons & charged pions) + E (pi0, e+/-, photons)
    df = df.Define("E_had", """
        double e_had = 0;
        for (size_t i = 0; i < pdg.size(); ++i) {
            int pdg_val = pdg[i];
            double energy = E[i]; // E is a value in ttree

            if (pdg_val == 2212) { // Proton
                e_had += energy - 0.938; // KE of proton
            } else if (pdg_val == 211 || pdg_val == -211) { // Charged pion
                e_had += energy - 0.1396; // KE of charged pion
            } else if (pdg_val == 111 || pdg_val == 11 || pdg_val == -11 || pdg_val == 22) { // pi0, electron, positron, photon
                e_had += energy; // Total energy
            }
        }
        return e_had;
    """)

    # Add Evis_2 to dataframe (based on Erecoild from nuisance)
    df = df.Define("Evis_2", "E_had + ELep")
    
    # E_had3 = skip bindinos & nucleons + total energy minus proton mass of (Primarily) strange baryons
    # since decays will mostly contain protons 
    # + total energy plus proton mass of (primarily) anti-protons 
    # since anhillation is mostly the interaction mode
    # + if no neutrons or leptons (mostly kaons) just add all the energy
    df = df.Define("E_had3", """
        double e_had3 = 0;
        for (size_t i = 0; i < pdg.size(); ++i) {
            int pdg_val = pdg[i];
            double energy = E[i];
            double px_val = px[i];
            double py_val = py[i];
            double pz_val = pz[i];

            if (pdg_val == 2212 || abs(pdg_val) == 211) { // Proton or charged pion
                double mass_squared = energy * energy - px_val * px_val - py_val * py_val - pz_val * pz_val;
                if (mass_squared > 0) {
                    double mass = std::sqrt(mass_squared);
                    double gamma = energy / mass;
                    e_had3 += (gamma - 1) / gamma * energy;
                }
            } else if (pdg_val == 111 || pdg_val == 11 || pdg_val == -11 || pdg_val == 22) { // pi0, electron, positron, photon
                e_had3 += energy;
            }  else if (pdg_val >= 2000000000)
	        {
	        //skip the bindinos
	        }  else if (pdg_val >= 1000000000)
            {
	        //do nothing for nucleons
	        }  else if (pdg_val >= 2000 && pdg_val != 2212 && pdg_val !=2112){
	            e_had3 += energy - 0.9382;
	            //Primarily strange baryons add total energy minus proton mass since decays will mostly contain protons
	        }  else if (pdg_val <= -2000){
                e_had3 += energy + 0.9382;
	            //Primarily anti-protons add total energy plus proton mass since anhillation is mostly the interaction mode
	        }  else if (pdg_val != 2112 && (abs(pdg_val) < 11 || abs(pdg_val) > 16)){ // no neutrons or leptons
	            e_had3 += energy; //mostly kaons add all the energy
	        }

        }
        return e_had3;
    """)

    # Add Evis_3 to data frame (based on code from NOvA)
    df = df.Define("Evis_3", "E_had3 + ELep")

    # nabbed formula from https://indico.fnal.gov/event/53004/contributions/244614/attachments/158383/207801/interactionModelTalk.pdf
    # Assuming we're using Carbon 12, might be wrong on that!


    df = df.Define("Evis_kin", "(TMath::Power(.938272,2)-TMath::Power(.93956-0.09215,2)-TMath::Power(.105608,2)+2*(.93956-0.09215)*ELep)/(2*(0.93956-0.09215-ELep+PLep*CosLep))")

    
    # Define Neutrino Momentum as a Vector
    df = df.Define("PNu", """ 
        double px_nu = 0;
        double py_nu = 0;
        double pz_nu = 0;
        TVector3 pnu(px_nu, py_nu, pz_nu);
        
        for (size_t i = 0; i < pdg_init.size(); ++i) {
            if (pdg_init[i] == 14) { //neutrino 
                px_nu += px_init[i];
                py_nu += py_init[i];
                pz_nu += pz_init[i]; 
            }
        }
        pnu.SetXYZ(px_nu, py_nu, pz_nu);
        
        return pnu;

    """)
    
    # Define PTLep: Transverse Momemtum of Lepton (Cross Product with Neutrino Momentum)
    df = df.Define("PTLep", """
        double px_lep = 0;
        double py_lep = 0;
        double pz_lep = 0;
        TVector3 plep(0, 0, 0);
        for (size_t i = 0; i < pdg.size(); ++i) {
            if (pdg[i] == 13) {
                px_lep += px[i];
                py_lep += py[i];
                pz_lep += pz[i];
                
            }
        }
        plep.SetXYZ(px_lep, py_lep, pz_lep);
        return PNu.Cross(plep);
    """)
    
    # Transverse Momentum of Hadrons (Including Neutrons): Protons, +/-/0 Pions, Neutrons
    df = df.Define("PTHad_IN", """
        double px_had_in = 0;
        double py_had_in = 0;
        double pz_had_in = 0;
        TVector3 phad_in(0, 0, 0);
        for (size_t i = 0; i < pdg.size(); ++i) {
            int pdg_val = pdg[i];
            if (pdg_val == 2212 || pdg_val == 211 || pdg_val == -211 || pdg_val == 111 || pdg_val == 2112) {
                px_had_in += px[i];
                py_had_in += py[i];
                pz_had_in += pz[i];
                
            }
        }
        phad_in.SetXYZ(px_had_in, py_had_in, pz_had_in);
        return PNu.Cross(phad_in);
    """)
    
    # Transverse Momentum of Hadrons (Omitting Neutrons): Protons, +/-/0 Pions
    df = df.Define("PTHad_ON", """
    double px_had_on = 0;
    double py_had_on = 0;
    double pz_had_on = 0;
    TVector3 phad_on(0, 0, 0);
    for (size_t i = 0; i < pdg.size(); ++i) {
        int pdg_val = pdg[i];
        if (pdg_val == 2212 || pdg_val == 211 || pdg_val == -211 || pdg_val == 111) {
            px_had_on += px[i];
            py_had_on += py[i];
            pz_had_on += pz[i];
            
        }
    }
    phad_on.SetXYZ(px_had_on, py_had_on, pz_had_on);
    return PNu.Cross(phad_on);
    """)
    
    # Transverse Kinematic Imbalance (Including Neutrons)
    df = df.Define("TKI_IN", """
    TVector3 delta_p_T(PTLep.X(), PTLep.Y(), PTLep.Z());
    delta_p_T += PTHad_IN;
        
    return delta_p_T.Mag();
    """)
    
    # Transverse Kinematic Imbalance (Omitting Neutrons)
    df = df.Define("TKI_ON", """
    TVector3 delta_p_T(PTLep.X(), PTLep.Y(), PTLep.Z());
    delta_p_T += PTHad_ON;
        
    return delta_p_T.Mag();
    """)

    return df


def CreateDataFrame(file_path, cut):    # First get the data into a dataframe
    if file_path is None:
        dir_location = input("Give Full Flat Tree Directory Location: ")
    else:
        dir_location = file_path
    
    
    fileName = f"{dir_location}"
    treeName = "FlatTree_VARS"
    print(fileName)

    df = ROOT.RDataFrame(treeName,fileName)
    df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")

    df = df.Filter(cut)
    return df


def Savehist(hist, AxisInfo, save_location, filename, ext, max = None, Normalize = 0):
    xvar = AxisInfo[0]
    xunit = AxisInfo[1]
    yvar = AxisInfo[2]
    yunit = AxisInfo[3]
    PlotTitle = AxisInfo[4]

    if max is not None:
        hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, max = max, PlotTitle=PlotTitle)
    else:
        hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)
    c = ROOT.TCanvas()

    if Normalize == 1:
       scale = 1/(hist.Integral())
       hist.Scale(scale)

    elif Normalize == 2:
        #hist.SetMinimum(1)
        hist.SetMaximum(3000)
        c.SetLogz()

    SF.formatTcanvas(hist,c)
    c.SaveAs(f"{HOME}/{save_location}/{filename}.{ext}")


    

def SaveHistSame(hist1, hist2, hist3, AxisInfo, save_location, filename, max=None, Normalize=0):
    """Saves multiple 1D histograms on the same canvas."""

    xvar = AxisInfo[0]
    xunit = AxisInfo[1]
    yvar = AxisInfo[2]
    yunit = AxisInfo[3]
    PlotTitle = AxisInfo[4]

    c = ROOT.TCanvas()
    legend = ROOT.TLegend(0.6, 0.6, 0.89, 0.79)  # Adjust legend position as needed

    hist1 = SF.formatHist(hist1, xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)
    hist2 = SF.formatHist(hist2, xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)
    hist3 = SF.formatHist(hist3, xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)
    
    # for i, hist in enumerate(hist_list): #iterate through the rresultptr objects
    #     if max is not None:
    #         hist = SF.formatHist(hist, xvar, xunit, yvar, yunit, max=max, PlotTitle=PlotTitle)
    #     else:
    #         hist = SF.formatHist(hist, xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)

        # if Normalize == 1:
        #     scale = 1 / (hist.Integral())
        #     hist.Scale(scale)

        # elif Normalize == 2:
        #     hist.SetMaximum(3000)
        #     c.SetLogz()

    # Manual color and style settings:
    hist1.SetLineColor(ROOT.kBlue)
    hist1.SetLineWidth(2)

    hist2.SetLineColor(ROOT.kBlack)
    hist2.SetLineWidth(2)

    hist3.SetLineColor(ROOT.kOrange+2)
    hist3.SetLineStyle(2)  # Dotted line
    hist3.SetLineWidth(2)

    hist2.Draw("HIST")
    hist3.Draw("HIST SAME")
    hist1.Draw("HIST SAME")

    legend.AddEntry(hist1, "Evis 1", "l")
    legend.AddEntry(hist2, "Evis 2", "l")
    legend.AddEntry(hist3, "Evis 3", "l")

    SF.formatTcanvasSame(c)  # Format the canvas based on the first histogram
    legend.Draw("SAME") #draw legend.
    c.SaveAs(f"{HOME}/{save_location}/{filename}.png")

def PlotStackedEventModes(df, x, histInfo, modes, colors):
    modeDic = SF.modeDic()
    stack = ROOT.THStack("stack","")
    histlist = []
    Legend = []
    for i in range(len(modes)):
        modedf = df.Filter(f"Mode == {modes[i]}")
        hist = modedf.Histo1D(histInfo,x)
        # print(colors[i])
        hist.SetFillColor(colors[i])
        th1d = hist.GetPtr()
        stack.Add(th1d)
        histlist.append(th1d)
        Legend.append(modeDic.get(modes[i]))
        print(f"Plotting mode {modes[i]}")

    return stack, histlist, Legend

def SaveStackedHist(stack, histlist, AxisInfo, Legend, save_path, Normalize = 0):
    canvas = ROOT.TCanvas("canvas", "Canvas for Stacked Histograms", 1000, 600)

    stack.Draw("HIST")  # "HIST" option tells ROOT to draw the histograms
    stack.GetXaxis().SetTitle(AxisInfo[0])
    stack.GetYaxis().SetTitle(AxisInfo[1])
    stack.SetTitle(AxisInfo[2])

    # Add legend
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)  # Define legend position
    for i in range(len(Legend)):
        if Normalize==1:
            # scale = 1/(histlist[i].Integral())
            # print(scale)
            # histlist[i].Scale(scale)
            print("Normalize doesn't work")
        legend.AddEntry(histlist[i], f"{Legend[i]}", "f")
    legend.Draw()

    canvas.SaveAs(save_path)

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
    file_path = input("Full File Path: ")
    AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    histInfo = ("name",f"{y} vs {x} plot",60,0,3,60,0,3)
    df2p2h = CreateDataFrame(file_path, "Mode == 2")
    hist  = df2p2h.Histo2D(histInfo,'q3','q0')
    SavePlot(hist,"titlename1",AxisInfo, file_path)
    x = 'W'
    y = 'Q2'
    # AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    # histInfo = ("name",f"{y} vs {x} plot",60,0,3,120,0,6)
    # hist, file_path = Plot1PI(x,y,histInfo,"/data/t2k-nova/FlatTrees/FLAT_NEUT_0.7GeV_1e7.root")
    # SavePlot(hist,"testname2",AxisInfo, file_path)








