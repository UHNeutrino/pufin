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

def DefineKinematics(df):
    #df = df.Define("PLep","TMath::Power(TMath::Power(ELep, 2)-TMath::Power(.1056, 2), 0.5)")
    
    # Momentum of the highest momentum proton in the final state (scalar)
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
    
    df = df.Define("PProton", """
    double proton_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) { // Proton
            proton_p = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
            
        }
    }
    return proton_p;
    """)
    
    # Momentum of the highest momentum proton after the neutrino interaction, but BEFORE FSI (scalar)
    df = df.Define("PProton1_PFSI", """
    double max_proton_p_pfsi = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg_vert.size(); ++i) {
        if (pdg_vert[i] == 2212) { // Proton
            double p_magnitude = std::sqrt(px_vert[i] * px_vert[i] + py_vert[i] * py_vert[i] + pz_vert[i] * pz_vert[i]);
            if (p_magnitude > max_proton_p_pfsi) {
                max_proton_p_pfsi = p_magnitude;
            }
        }
    }
    return max_proton_p_pfsi;
    """)
    
    # Momentum of the highest momentum pion(+) in the final state (scalar)
    df = df.Define("PPionPlus", """
    double max_pi_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 211) { // Pi+
            double p_magnitude = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
            if (p_magnitude > max_pi_p) {
                max_pi_p = p_magnitude;
            }
        }
    }
    return max_pi_p;
    """)

    df = df.Define("PPionMax", """
    double max_pi_p = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 211 || pdg[i] == -211 || pdg[i] == 111) { // Any Pion
            double p_magnitude = std::sqrt(px[i] * px[i] + py[i] * py[i] + pz[i] * pz[i]);
            if (p_magnitude > max_pi_p) {
                max_pi_p = p_magnitude;
            }
        }
    }
    return max_pi_p;
    """)
    
    # Momentum of the highest momentum pion(+) after the neutrino interaction, but BEFORE FSI (scalar)
    df = df.Define("PPionPlus_PFSI", """
    double max_pi_p_pfsi = -1.0; // Initialize to a negative value
    for (size_t i = 0; i < pdg_vert.size(); ++i) {
        if (pdg_vert[i] == 211) { // Pi+
            double p_magnitude = std::sqrt(px_vert[i] * px_vert[i] + py_vert[i] * py_vert[i] + pz_vert[i] * pz_vert[i]);
            if (p_magnitude > max_pi_p_pfsi) {
                max_pi_p_pfsi = p_magnitude;
            }
        }
    }
    return max_pi_p_pfsi;
    """)

    # Cosine of the angle the highest momentum proton (in the final state) makes with the initial neutrino direction
    df = df.Define("CosProton", """
    double cos_proton = -5.0;
    double max_proton_p = -1.0;
    int max_index = -1;

    for (size_t i = 0; i < pdg.size(); ++i) {
        if (pdg[i] == 2212) {
            double p = std::sqrt(px[i]*px[i] + py[i]*py[i] + pz[i]*pz[i]);
            if (p > max_proton_p) {
                max_proton_p = p;
                max_index = i;
            }
        }
    }

    if (max_index >= 0 && max_proton_p > 0) {
        cos_proton = pz[max_index] / max_proton_p;
    }

    return cos_proton;
    """)
    
    # Cosine of the angle the highest momentum proton (BEFORE FSI) makes with the initial neutrino direction
    df = df.Define("CosProton_PFSI", """
    double cos_proton_pfsi = -5.0;
    double max_proton_ppfsi = -1.0;
    int max_index = -1;

    for (size_t i = 0; i < pdg_vert.size(); ++i) {
        if (pdg_vert[i] == 2212) {
            double p = std::sqrt(px_vert[i]*px_vert[i] + py_vert[i]*py_vert[i] + pz_vert[i]*pz_vert[i]);
            if (p > max_proton_ppfsi) {
                max_proton_ppfsi = p;
                max_index = i;
            }
        }
    }

    if (max_index >= 0 && max_proton_ppfsi > 0) {
        cos_proton_pfsi = pz_vert[max_index] / max_proton_ppfsi;
    }

    return cos_proton_pfsi;
    """)
    
    #df = df.Filter("PProton1 >= 0")
    df = df.Define("initNeucMag", """
    std::vector<float> mags;
    for (size_t i = 0; i < px_init.size(); ++i) {
        int pdg = pdg_init[i];
        if (pdg == 2212 || pdg == 2112){ 
            float px = px_init[i];
            float py = py_init[i];
            float pz = pz_init[i];
            mags.push_back(std::sqrt(px*px + py*py + pz*pz));
        }
    }
    return mags;
    """)


    return df

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
    # E_had after the neutrino interaction, but before FSI
    df = df.Define("E_had_PFSI", """
        double e_had_pfsi = 0;
        for (size_t i = 0; i < pdg_vert.size(); ++i) {
            int pdg_val = pdg_vert[i];
            double energy = E_vert[i]; // E_vert is a value in ttree

            if (pdg_val == 2212) { // Proton
                e_had_pfsi += energy - 0.938; // KE of proton
            } else if (pdg_val == 211 || pdg_val == -211) { // Charged pion
                e_had_pfsi += energy - 0.1396; // KE of charged pion
            } else if (pdg_val == 111 || pdg_val == 11 || pdg_val == -11 || pdg_val == 22) { // pi0, electron, positron, photon
                e_had_pfsi += energy; // Total energy
            }
        }
        return e_had_pfsi;
    """)

    # Add Evis_2 to dataframe (based on Erecoil from nuisance)
    df = df.Define("Evis_2", "E_had + ELep")
    
    # Evis_2 after the neutrino interaction but BEFORE FSI
    df = df.Define("Evis_2_PFSI", "E_had_PFSI + ELep")
    
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

    # Eb from Bodek paper for neutron in C+O
    df = df.Define("Evis_kin", """
                double Energy = -9999.9;
                double Mp = .938272;
                double Mn = .93956;
                double Mu = .105608;
                double Eb = .0301 ;
                if (ELep > 0.0 && std::abs(CosLep) <= 1)
                {
                    Energy = (TMath::Power(Mp,2)-TMath::Power(Mn-Eb,2)-TMath::Power(Mu,2)+2*(Mn-Eb)*ELep)/(2*(Mn-Eb-ELep+PLep*CosLep)) ;
                }
                return Energy;
                   """)
    
    df = df.Define("Eres_kin","""
                double EnergyResKin = ((Evis_kin-Enu_true)/Enu_true);
                if (EnergyResKin > 10.0)
                {
                    EnergyResKin = 10.0;
                }
                if (EnergyResKin < -10.0)
                {
                    EnergyResKin = -10.0;
                }
                return EnergyResKin;
                   """)
    df = df.Define("Eres_kin2","""
                double EnergyResKin2 = ((Evis_kin-Enu_true)/Enu_true);
        
                return EnergyResKin2;
                   """)

    df = df.Define("Eres_cal","""
                double EnergyResCal = (Evis_3-Enu_true) / Enu_true;
              
                return EnergyResCal;
                   """)

    return df

def DefineTKI(df):
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
    
    # Define PTLep: Transverse Momemtum of Lepton (x and y projections of lepton momentum vector). Returns a vector.
    df = df.Define("PTLep", """
        double px_lep = 0;
        double py_lep = 0;
        double pz_lep = 0;
        TVector3 ptlep(0, 0, 0);
        for (size_t i = 0; i < pdg.size(); ++i) {
            if (pdg[i] == 13) {
                px_lep += px[i];
                py_lep += py[i];
                pz_lep += pz[i];
                
            }
        }
        ptlep.SetXYZ(px_lep, py_lep, 0);
        return ptlep;
    """)
    
    # Transverse Momentum of Hadrons in the final state (Including Neutrons): Protons, +/-/0 Pions, Neutrons
    df = df.Define("PTHad", """
        double px_had = 0;
        double py_had = 0;
        double pz_had = 0;
        TVector3 pthad(0, 0, 0);
        for (size_t i = 0; i < pdg.size(); ++i) {
            int pdg_val = pdg[i];
            if (pdg_val == 2212 || pdg_val == 211 || pdg_val == -211 || pdg_val == 111 || pdg_val == 2112) {
                px_had += px[i];
                py_had += py[i];
                pz_had += pz[i];
                
            }
        }
        pthad.SetXYZ(px_had, py_had, 0);
        return pthad;
    """)
    
    # Transverse Momentum of Hadrons after the neutrino interaction, BEFORE FSI (Including Neutrons): Protons, +/-/0 Pions, Neutrons
    df = df.Define("PTHad_PFSI", """
        double px_had_pfsi = 0;
        double py_had_pfsi = 0;
        double pz_had_pfsi = 0;
        TVector3 pthad_pfsi(0, 0, 0);
        for (size_t i = 0; i < pdg_vert.size(); ++i) {
            int pdg_val = pdg_vert[i];
            if (pdg_val == 2212 || pdg_val == 211 || pdg_val == -211 || pdg_val == 111 || pdg_val == 2112) {
                px_had_pfsi += px_vert[i];
                py_had_pfsi += py_vert[i];
                pz_had_pfsi += pz_vert[i];
                
            }
        }
        pthad_pfsi.SetXYZ(px_had_pfsi, py_had_pfsi, 0);
        return pthad_pfsi;
    """)
    
    # Transverse momentum of the highest momentum proton in the final state. Returns a vector.
    df = df.Define("PTProton1", """
        TVector3 pproton(0, 0, 0);
        TVector3 Best(0, 0, 0);
        double Best_mag = -5.0;
        for (size_t i = 0; i < pdg.size(); ++i) {
            if (pdg[i] == 2212) { // Proton
                pproton.SetXYZ(px[i], py[i], pz[i]);
                double p_mag = pproton.Mag();
                if (p_mag > Best_mag) {
                    Best_mag = p_mag;
                    Best.SetXYZ(px[i], py[i], pz[i]);
                    
                }
            }
        }
        return TVector3(Best.X(), Best.Y(), 0);
    """)
    
    # Transverse momentum of the highest momentum pion in the final state. Returns a vector.
    df = df.Define("PTPion1", """
        TVector3 ppion(0, 0, 0);
        TVector3 Best(0, 0, 0);
        double Best_mag = -5.0;
        double pion_mag = -5.0;
        for (size_t i = 0; i < pdg.size(); ++i) {
            int pdg_val = pdg[i];
            if (pdg_val == 211 || pdg_val == -211 || pdg_val == 111) { // All pions
                ppion.SetXYZ(px[i], py[i], pz[i]);
                pion_mag = ppion.Mag();
                if (pion_mag > Best_mag) {
                    Best_mag = pion_mag;
                    Best.SetXYZ(px[i], py[i], pz[i]);
                    
                }
            }
        }
        return TVector3(Best.X(), Best.Y(), 0);
    """)
    
    # Transverse momentum of the highest momentum pion after the neutrino interaction and before FSI. Returns a vector.
    df = df.Define("PTPion1_PFSI", """
        TVector3 ppion_pfsi(0, 0, 0);
        TVector3 Best_pfsi(0, 0, 0);
        double Best_mag = -5.0;
        double pion_mag = -5.0;
        for (size_t i = 0; i < pdg_vert.size(); ++i) {
            int pdg_val = pdg_vert[i];
            if (pdg_val == 211 || pdg_val == -211 || pdg_val == 111) { // All pions
                ppion_pfsi.SetXYZ(px_vert[i], py_vert[i], pz_vert[i]);
                pion_mag = ppion_pfsi.Mag();
                if (pion_mag > Best_mag) {
                    Best_mag = pion_mag;
                    Best_pfsi.SetXYZ(px_vert[i], py_vert[i], pz_vert[i]);
                    
                }
            }
        }
        return TVector3(Best_pfsi.X(), Best_pfsi.Y(), 0);
    """)
    
    # Transverse momentum of the highest momentum proton after the neutrino interaction and before FSI. Returns a vector.
    df = df.Define("PTProton1_PFSI", """
        TVector3 pproton_pfsi(0, 0, 0);
        TVector3 Best_pfsi(0, 0, 0);
        double Best_mag = -5.0;
        double p_mag = -5.0;
        for (size_t i = 0; i < pdg_vert.size(); ++i) {
            if (pdg_vert[i] == 2212) { // Proton
                pproton_pfsi.SetXYZ(px_vert[i], py_vert[i], pz_vert[i]);
                double p_mag = pproton_pfsi.Mag();
                if (p_mag > Best_mag) {
                    Best_mag = p_mag;
                    Best_pfsi.SetXYZ(px_vert[i], py_vert[i], pz_vert[i]);
                    
                }
            }
        }
        return TVector3(Best_pfsi.X(), Best_pfsi.Y(), 0);
    """)
    
    # Delta alpha-T using the lepton and entire hadronic system in the final state to calculate delta PT.
    df = df.Define("DeltaAlphaT_Had", """
        TVector3 delta_p_T = PTLep + PTHad;

        double dot = -(PTLep.Dot(delta_p_T));
        double magLep = PTLep.Mag();
        double magDelta = delta_p_T.Mag();

        double denom = magLep * magDelta;
        double delta_alpha_t;

        if ((dot == 0 || dot != dot) || (denom == 0 || denom != denom) || (fabs(dot) > fabs(denom))) {
            delta_alpha_t = -5.0;
        } else {
            delta_alpha_t = acos(dot / denom) * 180. / M_PI;
            if (delta_alpha_t != delta_alpha_t && fabs(dot - denom) < 1e-10) {
                delta_alpha_t = 0.0;
            }
        }

        return delta_alpha_t;
    """)
    
    # Delta alpha-T using just the lepton and the highest momentum proton in the final state to calculate delta PT. 
    df = df.Define("DeltaAlphaT", """
        TVector3 delta_p_T = PTLep + PTProton1;

        double dot = -(PTLep.Dot(delta_p_T));
        double magLep = PTLep.Mag();
        double magDelta = delta_p_T.Mag();

        double denom = magLep * magDelta;
        double delta_alpha_t;

        if ((dot == 0 || dot != dot) || (denom == 0 || denom != denom) || (fabs(dot) > fabs(denom))) {
            delta_alpha_t = -5.0;
        } else {
            delta_alpha_t = acos(dot / denom) * 180. / M_PI;
            if (delta_alpha_t != delta_alpha_t && fabs(dot - denom) < 1e-10) {
                delta_alpha_t = 0.0;
            }
        }

        return delta_alpha_t;
    """)
    
    # Delta alpha-T using the lepton, highest momentum proton and highest momentum pion in the final state to calculate delta PT.
    df = df.Define("DeltaAlphaT_pion", """
        TVector3 delta_p_T_pion = PTLep + PTProton1 + PTPion1;

        double dot = -(PTLep.Dot(delta_p_T_pion));
        double magLep = PTLep.Mag();
        double magDelta = delta_p_T_pion.Mag();

        double denom = magLep * magDelta;
        double delta_alpha_t_pion;

        if ((dot == 0 || dot != dot) || (denom == 0 || denom != denom) || (fabs(dot) > fabs(denom))) {
            delta_alpha_t_pion = -5.0;
        } else {
            delta_alpha_t_pion = acos(dot / denom) * 180. / M_PI;
            if (delta_alpha_t_pion != delta_alpha_t_pion && fabs(dot - denom) < 1e-10) {
                delta_alpha_t_pion = 0.0;
            }
        }

        return delta_alpha_t_pion;
    """)
    
    # Delta alpha-T using just the lepton and the highest momentum proton before FSI to calculate delta PT.
    df = df.Define("DeltaAlphaT_PFSI", """
        TVector3 delta_p_T_pfsi = PTLep + PTProton1_PFSI;

        double dot = -(PTLep.Dot(delta_p_T_pfsi));
        double magLep = PTLep.Mag();
        double magDelta = delta_p_T_pfsi.Mag();

        double denom = magLep * magDelta;
        double delta_alpha_t_pfsi;

        if ((dot == 0 || dot != dot) || (denom == 0 || denom != denom) || (fabs(dot) > fabs(denom))) {
            delta_alpha_t_pfsi = -5.0;
        } else {
            delta_alpha_t_pfsi = acos(dot / denom) * 180. / M_PI;
            if (delta_alpha_t_pfsi != delta_alpha_t_pfsi && fabs(dot - denom) < 1e-10) {
                delta_alpha_t_pfsi = 0.0;
            }
        }

        return delta_alpha_t_pfsi;
    """)

    ### All Delta PT variables return a scalar ###
    
    # Delta PT using the lepton and entire hadronic system in the final state.
    df = df.Define("DeltaPT_Had", """
        TVector3 delta_p_T(PTLep.X(), PTLep.Y(), PTLep.Z());
        delta_p_T += PTHad;
            
        return delta_p_T.Mag();
    """)
    
    # Delta PT using the lepton and the highest momentum proton in the final state.
    df = df.Define("DeltaPT", """
        TVector3 delta_p_T(PTLep.X(), PTLep.Y(), PTLep.Z());
        delta_p_T += PTProton1;
            
        return delta_p_T.Mag();
    """)
    
    # Delta PT using the lepton, the highest momentum proton and the highest momentum pion in the final state.
    df = df.Define("DeltaPT_pion", """
        TVector3 delta_p_T_pion = PTLep + PTProton1 + PTPion1;
            
        return delta_p_T_pion.Mag();
    """)
    
    # Delta PT using the lepton and the highest momentum proton before FSI.
    df = df.Define("DeltaPT_PFSI", """
        TVector3 delta_p_T_pfsi(PTLep.X(), PTLep.Y(), PTLep.Z());
        delta_p_T_pfsi += PTProton1_PFSI;
            
        return delta_p_T_pfsi.Mag();
    """)
    
    # Componet of delta pt that is parallel to the transverse momentum transfer vector q_T 
    # (using the entire hadronic system to calculate delta pt)
    df = df.Define("DeltaPT_y_Had", """
        TVector3 delta_pt_had = PTLep + PTHad;        
        double pTlep = PTLep.Mag();
        if (pTlep == 0 || pTlep != pTlep) return -5.0;   
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep;        
        return delta_pt_had.Dot(qT_hat);
    """)
    
    # Componet of delta pt that is parallel to the transverse momentum transfer vector q_T 
    # using the lepton and entire hadronic system to calculate delta pt
    # calculated BEFORE FSI
    df = df.Define("DeltaPT_y_Had_PFSI", """
        TVector3 delta_pt_had_pfsi = PTLep + PTHad_PFSI;        
        double pTlep = PTLep.Mag();
        if (pTlep == 0 || pTlep != pTlep) return -5.0;   
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep;        
        return delta_pt_had_pfsi.Dot(qT_hat);
    """)
    
    # Componet of delta pt that is parallel to the transverse momentum transfer vector q_T 
    # using just the letpton and the highest momentum proton to calculate delta pt
    df = df.Define("DeltaPT_y", """
        TVector3 delta_pt = PTLep + PTProton1;        
        double pTlep = PTLep.Mag();
        if (pTlep == 0 || pTlep != pTlep) return -5.0;   
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep;        
        return delta_pt.Dot(qT_hat);
    """)
    
    # Componet of delta pt that is parallel to the transverse momentum transfer vector q_T 
    # using just the letpton and the highest momentum proton to calculate delta pt
    # calculated BEFORE FSI
    df = df.Define("DeltaPT_y_PFSI", """
        TVector3 delta_pt_pfsi = PTLep + PTProton1_PFSI;        
        double pTlep = PTLep.Mag();
        if (pTlep == 0 || pTlep != pTlep) return -5.0;   
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep;        
        return delta_pt_pfsi.Dot(qT_hat);
    """)
    
    # Componet of delta pt that is parallel to the transverse momentum transfer vector q_T 
    # using just the letpton, the highest momentum proton and the highest momentum pion to calculate delta pt
    df = df.Define("DeltaPT_y_pion", """
        TVector3 delta_pt_pp = PTLep + PTProton1 + PTPion1;        
        double pTlep = PTLep.Mag();
        if (pTlep == 0 || pTlep != pTlep) return -5.0;   
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep;        
        return delta_pt_pp.Dot(qT_hat);
    """)
    
    # Componet of delta pt that is parallel to the transverse momentum transfer vector q_T 
    # using just the letpton, the highest momentum proton and the highest momentum pion to calculate delta pt
    # calculated BEFORE FSI
    df = df.Define("DeltaPT_y_pion_PFSI", """
        TVector3 delta_pt_pfsi_pp = PTLep + PTProton1_PFSI + PTPion1_PFSI;        
        double pTlep = PTLep.Mag();
        if (pTlep == 0 || pTlep != pTlep) return -5.0;   
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep;        
        return delta_pt_pfsi_pp.Dot(qT_hat);
    """)
    
    # Componet of delta pt that is perpendicular to the transverse momentum transfer vector q_T
    # using the lepton and entire hadronic system to calculate delta pt
    df = df.Define("DeltaPT_x_Had", """
        TVector3 delta_pt = PTLep + PTHad;
        double pnu = PNu.Mag();
        double pTlep = PTLep.Mag();
        if (pnu == 0 || pTlep == 0) return -5.0;
        
        TVector3 z_hat = (1.0 / pnu) * PNu;
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep; 
        TVector3 x_hat = z_hat.Cross(qT_hat);
        double xmag = x_hat.Mag();
        if (xmag == 0 || xmag != xmag) return -5.0;
        x_hat *= (1.0 / xmag); 
        
        return delta_pt.Dot(x_hat);
    """)
    
    # Componet of delta pt that is perpendicular to the transverse momentum transfer vector q_T
    # using the lepton and entire hadronic system to calculate delta pt
    # calculated BEFORE FSI
    df = df.Define("DeltaPT_x_Had_PFSI", """
        TVector3 delta_pt_had_pfsi = PTLep + PTHad_PFSI;
        double pnu = PNu.Mag();
        double pTlep = PTLep.Mag();
        if (pnu == 0 || pTlep == 0) return -5.0;
        
        TVector3 z_hat = (1.0 / pnu) * PNu;
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep; 
        TVector3 x_hat = z_hat.Cross(qT_hat);
        double xmag = x_hat.Mag();
        if (xmag == 0 || xmag != xmag) return -5.0;
        x_hat *= (1.0 / xmag); 
        
        return delta_pt_had_pfsi.Dot(x_hat);
    """)
    # Componet of delta pt that is perpendicular to the transverse momentum transfer vector q_T
    # using the just the lepton and the highest momentum proton to calculate delta pt
    df = df.Define("DeltaPT_x", """
        TVector3 delta_pt = PTLep + PTProton1;
        double pnu = PNu.Mag();
        double pTlep = PTLep.Mag();
        if (pnu == 0 || pTlep == 0) return -5.0;
        
        TVector3 z_hat = (1.0 / pnu) * PNu;
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep; 
        TVector3 x_hat = z_hat.Cross(qT_hat);
        double xmag = x_hat.Mag();
        if (xmag == 0 || xmag != xmag) return -5.0;
        x_hat *= (1.0 / xmag); 
        
        return delta_pt.Dot(x_hat);
    """)
    
    # Componet of delta pt that is perpendicular to the transverse momentum transfer vector q_T
    # using the just the lepton and the highest momentum proton to calculate delta pt
    # calculated BEFORE FSI
    df = df.Define("DeltaPT_x_PFSI", """
        TVector3 delta_pt_pfsi = PTLep + PTProton1_PFSI;
        double pnu = PNu.Mag();
        double pTlep = PTLep.Mag();
        if (pnu == 0 || pTlep == 0) return -5.0;
        
        TVector3 z_hat = (1.0 / pnu) * PNu;
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep; 
        TVector3 x_hat = z_hat.Cross(qT_hat);
        double xmag = x_hat.Mag();
        if (xmag == 0 || xmag != xmag) return -5.0;
        x_hat *= (1.0 / xmag); 
        
        return delta_pt_pfsi.Dot(x_hat);
    """)
    
    # Componet of delta pt that is perpendicular to the transverse momentum transfer vector q_T
    # using the just the lepton, the highest momentum proton and the highest momentum pion to calculate delta pt
    df = df.Define("DeltaPT_x_pion", """
        TVector3 delta_pt_pp = PTLep + PTProton1 + PTPion1;
        double pnu = PNu.Mag();
        double pTlep = PTLep.Mag();
        if (pnu == 0 || pTlep == 0) return -5.0;
        
        TVector3 z_hat = (1.0 / pnu) * PNu;
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep; 
        TVector3 x_hat = z_hat.Cross(qT_hat);
        double xmag = x_hat.Mag();
        if (xmag == 0 || xmag != xmag) return -5.0;
        x_hat *= (1.0 / xmag); 
        
        return delta_pt_pp.Dot(x_hat);
    """)
    
    # Componet of delta pt that is perpendicular to the transverse momentum transfer vector q_T
    # using the just the lepton, the highest momentum proton and the highest momentum pion to calculate delta pt
    # calculated BEFORE FSI
    df = df.Define("DeltaPT_x_pion_PFSI", """
        TVector3 delta_pt_pp_pfsi = PTLep + PTProton1_PFSI + PTPion1_PFSI;
        double pnu = PNu.Mag();
        double pTlep = PTLep.Mag();
        if (pnu == 0 || pTlep == 0) return -5.0;
        
        TVector3 z_hat = (1.0 / pnu) * PNu;
        TVector3 qT_hat = (-1.0 / pTlep) * PTLep; 
        TVector3 x_hat = z_hat.Cross(qT_hat);
        double xmag = x_hat.Mag();
        if (xmag == 0 || xmag != xmag) return -5.0;
        x_hat *= (1.0 / xmag); 
        
        return delta_pt_pp_pfsi.Dot(x_hat);
    """)
    
    # # Transverse Kinematic Imbalance (Omitting Neutrons)
    # df = df.Define("TKI_ON", """
    # TVector3 delta_p_T(PTLep.X(), PTLep.Y(), PTLep.Z());
    # delta_p_T += PTHad_ON;
        
    # return delta_p_T.Mag();
    # """)
    
    # # Transverse Momentum of Hadrons (Omitting Neutrons): Protons, +/-/0 Pions
    # df = df.Define("PTHad_ON", """
    # double px_had_on = 0;
    # double py_had_on = 0;
    # double pz_had_on = 0;
    # TVector3 phad_on(0, 0, 0);
    # for (size_t i = 0; i < pdg.size(); ++i) {
    #     int pdg_val = pdg[i];
    #     if (pdg_val == 2212 || pdg_val == 211 || pdg_val == -211 || pdg_val == 111) {
    #         px_had_on += px[i];
    #         py_had_on += py[i];
    #         pz_had_on += pz[i];
            
    #     }
    # }
    # phad_on.SetXYZ(px_had_on, py_had_on, pz_had_on);
    # return PNu.Cross(phad_on);
    # """)
    
    # Delta PT that includes protons, neutrons, and all pions in final state

    return df

def FlagParticleThresholds(df): 
    """
    Add boolean flags for particle momentum thresholds. 
    True if PLep > Threshold, False otherwise.
    """
    # NOvA muon momentum threshold > 490 MeV/c 
    #df = df.Define("flagNovaMuonP", f"(bool)(PLep > 0.490)") 
    cols = [str(c) for c in df.GetColumnNames()]
    if "flagNovaMuonP" in cols:
        df = df.Redefine("flagNovaMuonP", f"(PLep > 0.490)")
    else:
        df = df.Define("flagNovaMuonP", f"(PLep > 0.490)")
    if "flagNovaProtonP" in cols:
        df = df.Redefine("flagNovaProtonP", f"(PProton > .600)")
    else:
        df = df.Define("flagNovaProtonP", f"(PProton > .600)")
    df = df.Define("flagNovaPionPlusP", f"(PPionPlus > .390)")
    df = df.Define("flagT2KMuonP", f"(PLep > 0.225)")
    df = df.Define("flagT2KProtonP", f"(PProton > 0.400)") # value from T2K technote
    df = df.Define("flagT2KPionPlusP", f"(PPionPlus > 0.05)")
    df = df.Define("flagT2KALL", f"(flagT2KMuonP && flagT2KProtonP && flagT2KPionPlusP)")


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

    if cut == "None":
        return df
    else:
        df = df.Filter(cut)
        return df


def Savehist(hist, AxisInfo, save_location, filename, ext, max = 0, Normalize = False, logz = False):
    xvar = AxisInfo[0]
    xunit = AxisInfo[1]
    yvar = AxisInfo[2]
    yunit = AxisInfo[3]
    PlotTitle = AxisInfo[4]
    ROOT.gStyle.SetPalette(ROOT.kInvertedDarkBodyRadiator)
    #ROOT.gStyle.SetPalette(ROOT.kBird)
    if max != 0:
        hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, max = max, PlotTitle=PlotTitle)
    else:
        hist = SF.formatHist(hist ,xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)
    c = ROOT.TCanvas()

    if Normalize:
       scale = 1/(hist.Integral())
       hist.Scale(scale)
    SF.formatTcanvas(hist,c)
    if logz:
        c.SetLogz()

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
    
def Savehist2DWithProfile(hist1, prof1, AxisInfo, save_location, filename, ext,
                          max=0, Normalize=False, logz=False, diagonal=False, 
                          draw2d_opt="COLZ"):
    xvar, xunit, yvar, yunit, PlotTitle = AxisInfo[0], AxisInfo[1], AxisInfo[2], AxisInfo[3], AxisInfo[4]

    ROOT.gStyle.SetPalette(ROOT.kInvertedDarkBodyRadiator)

    # Format the TH2 (axes, titles, ranges, etc.)
    if max != 0:
        h1 = SF.formatHist(hist1, xvar, xunit, yvar, yunit, max=max, PlotTitle=PlotTitle)
    else:
        h1 = SF.formatHist(hist1, xvar, xunit, yvar, yunit, PlotTitle=PlotTitle)

    c = ROOT.TCanvas()

    if Normalize:
        integ = h1.Integral()
        if integ != 0:
            h1.Scale(1.0 / integ)

    # Make the canvas nice for 2D color palettes
    c.SetRightMargin(0.15)
    c.SetLeftMargin(0.14)
    c.SetBottomMargin(0.14)

    if logz:
        c.SetLogz()

    # 1) draw the 2D first
    h1.Draw(draw2d_opt)

    # 2) style + draw the profile on top
    if prof1:
        prof1.SetLineWidth(1)
        prof1.SetMarkerStyle(20)
        prof1.SetMarkerSize(0.5)
        prof1.Draw("SAME")
        
    if diagonal:
        diag = ROOT.TLine(0,0,5,5)
        diag.SetLineColor(ROOT.kGreen)
        diag.Draw("SAME")
        

    c.SaveAs(f"{HOME}/{save_location}/{filename}.{ext}")


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

def PlotStackedEventCuts(df, x, histInfo, cuts, colors, weights=""):
    stack = ROOT.THStack("stack","")
    histlist = []
    for i in range(len(cuts)):
        modedf = df.Filter(f"{cuts[i]}")
        if (df.HasColumn(weights)):
            hist = modedf.Histo1D(histInfo,x,weights)
        else:
            hist = modedf.Histo1D(histInfo,x)
        # print(colors[i])
        hist.SetFillColor(colors[i])
        th1d = hist.GetPtr()
        stack.Add(th1d)
        histlist.append(th1d)
        print(f"Plotting mode {cuts[i]}")

    return stack, histlist

def SaveStackedHist(stack, histlist, AxisInfo, Legend, save_path, Normalize = 0):
    canvas = ROOT.TCanvas("canvas", "Canvas for Stacked Histograms", 1000, 600)

    stack.Draw("HIST")  # "HIST" option tells ROOT to draw the histograms
    stack.GetXaxis().SetTitle(AxisInfo[0]+ " " + AxisInfo[1])
    stack.GetYaxis().SetTitle(AxisInfo[2]+ " " +AxisInfo[3])
    stack.SetTitle(AxisInfo[4])

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

    canvas.SaveAs(f"{HOME}/{save_path}")

def PlotContEventCuts(df, x, y, histInfo, cuts, percents):
    histlist = []
    return_list = []
    if (df.HasColumn("weights")):
        hist = df.Histo2D(histInfo,x,y,"weights")
        # print("weights activated2")
    else:
        hist = df.Histo2D(histInfo,x,y)
    th2d = hist.GetPtr()
    histlist.append(th2d)
    return_list.append(th2d)

    for i in range(len(cuts)):
        modedf = df.Filter(f"{cuts[i]}")
        if (df.HasColumn("weights")):
            hist = modedf.Histo2D(histInfo,x,y,"weights")
            # print("weights activated3")
        else:
            hist = modedf.Histo2D(histInfo,x,y)
        th2d = hist.GetPtr()
        # stack.Add(th2d)
        histlist.append(th2d)
        # print(f"Plotting mode {cuts[i]}")
    for hist in histlist[1:]:
        # print("starting Hists")
        hmax = hist.GetMaximum()
        for percent in percents:
            POmax = .9 #percent of max
            POmaxStep = .1 #how much POmax decreases by
            TEvents = hist.Integral()
            if TEvents == 0:
                return_list.append(hist.Clone())
                continue
            CEvents = 0 
            NinteyB = True
            truePercent = percent
            if percent > 1:
                    percent /= 100
            FallBack = 0
            while(NinteyB):
                filtered_hist = hist.Clone()
                histCopy = hist.Clone()
                for y in range(1,filtered_hist.GetNbinsY()+1):
                    for x in range(1,filtered_hist.GetNbinsX()+1):
                        if (filtered_hist.GetBinContent(x,y) > hmax *POmax):
                            filtered_hist.SetBinContent(x,y,1)
                        else:
                            filtered_hist.SetBinContent(x,y,0)
                histCopy.Multiply(filtered_hist)
                CEvents = histCopy.Integral()
                # print(f'Percent of events: {CEvents/TEvents} Tolerance Percent of Max bin: {POmax} FallBack: {FallBack}')
                if (CEvents/TEvents < (percent + .005) and CEvents/TEvents > (percent - .005)):
                    NinteyB = False
                    print("Done Correctly!")
                elif (CEvents/TEvents >= (percent + .005)):
                    POmax += 2*POmaxStep
                    POmaxStep /= 10
                elif (FallBack >= 100):
                    NinteyB = False
                    print("Problem, try using finer binning, or higher percent")
                    print(f"Plotted with {CEvents/TEvents}% of events rather than {percent}%")
                    percents[percents.index(truePercent)] = CEvents/TEvents
                    print(percents)

                POmax -= POmaxStep
                FallBack += 1
            # print(f'Percent of events: {CEvents/TEvents} Tolerance Percent of Max bin: {POmax}')
            return_list.append(filtered_hist.Clone())

    return return_list

def SaveContHist(histlist, AxisInfo, Legend, colors, percents, save_path, logz):
    # stupid crap at the begining to get a proper legend
    # legend = ROOT.TLegend(0.7, 0.1, 0.9, 0.3)  # Define legend position
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)  # Define legend position
    styletemp = [1,2,3,4,5]
    style = []
    for z in range(0,len(percents)):
        style.append(styletemp[len(percents) - z -1])
    if (len(percents) > 1):
        legend.SetNColumns(2)
        counter1 = 0
        counter2 = 0
        clonelist =[]
        for hist in histlist:
            clonelist.append(hist.Clone())
        LegIter =0
        if (len(Legend)==len(percents)):
            LegIter = len(Legend)+len(percents)
        else:
            LegIter = len(Legend)+len(percents) + abs(len(Legend)-len(percents))
        for i in range(0,LegIter):
            if ((i+1)%2):
                if (counter1 < len(percents)):
                    clonelist[i].SetLineColor(ROOT.kBlack)
                    clonelist[i].SetLineStyle(style[(counter1%len(percents))])
                    legend.AddEntry(clonelist[i], f"{str(percents[counter1])[0:4]}% of events", "l")
                else:
                    legend.AddEntry(0, " ", "")
                counter1 += 1
            else:
                if (counter2 < len(Legend)):
                    clonelist[i].SetLineColor(colors[counter2])
                    legend.AddEntry(clonelist[i], f"{Legend[counter2]}", "l")
                else:
                    legend.AddEntry(0, " ", "")
                counter2 += 1
        

    ROOT.gStyle.SetOptStat(0)
    # ROOT.gStyle.SetStatX(.9)
    # ROOT.gStyle.SetStatY(.4)
    # ROOT.gStyle.SetStatH(.1)
    # ROOT.gStyle.SetStatW(.2)
    ROOT.gStyle.SetPalette(52)
    ROOT.TColor.InvertPalette()
    canvas = ROOT.TCanvas("canvas", "Canvas for Contour Histograms", 1000, 600)
    # Add legend
    # legend = ROOT.TLegend(0.7, 0.1, 0.9, 0.3)  # Define legend position
    histlist[0].GetXaxis().SetTitle(AxisInfo[0]+ AxisInfo[1])
    histlist[0].GetYaxis().SetTitle(AxisInfo[2]+ AxisInfo[3])
    histlist[0].SetTitle(AxisInfo[4])
    histlist[0].Draw("COLZ")  # "HIST" option tells ROOT to draw the histograms
    if logz:
        canvas.SetLogz()
    # legend.AddEntry(histlist[0], f"{Legend[0]}", "f")
    j = 0


    for i in range(0, len(histlist)-1):
        histlist[i+1].SetLineColor(colors[j])
        histlist[i+1].SetFillStyle(0)
        # print(style[(i%len(percents))])
        histlist[i+1].SetLineStyle(style[(i%len(percents))])
        histlist[i+1].SetLineWidth(1)
        histlist[i+1].Draw("CONT3 SAME")  # "HIST" option tells ROOT to draw the histograms
        if (len(percents) == 1):
           legend.AddEntry(histlist[i+1], f"{Legend[i]}", "l")
        if (i%len(percents) + 1 == len(percents)):
            j += 1
    
    # if (len(percents) > 1):
    #     legend.SetNColumns(2)
    #     counter1 = 0
    #     counter2 = 0
    #     for i in range(0,len(histlist)):
    #         if ((i+1)%2):
    #             if (counter1 < len(percents)):
    #                 histlist[1].SetLineColor(ROOT.kBlack)
    #                 histlist[1].SetLineStyle(style[(counter1%len(percents))])
    #                 legend.AddEntry(histlist[1], f"{percents[counter1]}% of events", "l")
    #             else:
    #                 legend.AddEntry(0, " ", "")
    #             counter1 += 1
    #         else:
    #             if (counter2 < len(Legend)):
    #                 histlist[1].SetLineColor(colors[counter2])
    #                 legend.AddEntry(histlist[1], f"{Legend[counter2]}", "l")
    #             else:
    #                 legend.AddEntry(0, " ", "")
    #             counter2 += 1
           
    
    legend.Draw()
    pave = ROOT.TPaveText(0.7, 0.65, 0.9, 0.7, "NDC")  # (x1, y1, x2, y2)
    pave.AddText(f"Events: {histlist[0].Integral():.0f}")
    pave.SetFillColor(0)    # Transparent fill
    pave.SetBorderSize(1)   # Border thickness
    pave.SetTextSize(0.025)  # Optional
    pave.Draw()
    # latex.DrawLatex(0.9, 0.35, f"Events = {histlist[0].Integral():.1f}")

    canvas.SaveAs(f"{HOME}/{save_path}")

def SaveContHistStyles(histlist, AxisInfo, colors, styles, Clabels, Slabels, save_path, logz):
    # stupid crap at the begining to get a proper legend
    # legend = ROOT.TLegend(0.7, 0.1, 0.9, 0.3)  # Define legend position
    legend1 = ROOT.TLegend(0.7, 0.7, 0.8, 0.9)  # Define legend position
    legend2 = ROOT.TLegend(0.8, 0.7, 0.9, 0.9)


    fh1 = ROOT.TH1D()
    fh2 = ROOT.TH1D()
    fh3 = ROOT.TH1D()
    fh4 = ROOT.TH1D()
    fh5 = ROOT.TH1D()
    fh6 = ROOT.TH1D()
    fh7 = ROOT.TH1D()
    fh8 = ROOT.TH1D()
    fh9 = ROOT.TH1D()
    fh10 = ROOT.TH1D()
    fakehistList = [fh1,fh2,fh3,fh4,fh5,fh6,fh7,fh8,fh9,fh10]
    i = 0


    for cName, cValue  in Clabels.items():
        fakehistList[i].SetLineColor(cValue)
        legend1.AddEntry(fakehistList[i] , cName, "l")
        i+=1
    for sName, sValue in Slabels.items():
        fakehistList[i].SetLineStyle(sValue)
        legend2.AddEntry(fakehistList[i] , sName, "l")
        i+=1   

    ROOT.gStyle.SetOptStat(0)
    # ROOT.gStyle.SetStatX(.9)
    # ROOT.gStyle.SetStatY(.4)
    # ROOT.gStyle.SetStatH(.1)
    # ROOT.gStyle.SetStatW(.2)
    ROOT.gStyle.SetPalette(52)
    ROOT.TColor.InvertPalette()
    canvas = ROOT.TCanvas("canvas", "Canvas for Contour Histograms", 1000, 600)
    # Add legend
    # legend = ROOT.TLegend(0.7, 0.1, 0.9, 0.3)  # Define legend position
    histlist[0].GetXaxis().SetTitle(AxisInfo[0]+ AxisInfo[1])
    histlist[0].GetYaxis().SetTitle(AxisInfo[2]+ AxisInfo[3])
    histlist[0].SetTitle(AxisInfo[4])
    histlist[0].Draw("COLZ")  # "HIST" option tells ROOT to draw the histograms
    if logz:
        canvas.SetLogz()
    # legend.AddEntry(histlist[0], f"{Legend[0]}", "f")
    i=0


    for i in range(0, len(histlist)-1):
        histlist[i+1].SetLineColor(colors[i])
        histlist[i+1].SetFillStyle(0)
        # print(style[(i%len(percents))])
        histlist[i+1].SetLineStyle(styles[i])
        histlist[i+1].SetLineWidth(1)
        histlist[i+1].Draw("CONT3 SAME")  # "HIST" option tells ROOT to draw the histograms

    
    # if (len(percents) > 1):
    #     legend.SetNColumns(2)
    #     counter1 = 0
    #     counter2 = 0
    #     for i in range(0,len(histlist)):
    #         if ((i+1)%2):
    #             if (counter1 < len(percents)):
    #                 histlist[1].SetLineColor(ROOT.kBlack)
    #                 histlist[1].SetLineStyle(style[(counter1%len(percents))])
    #                 legend.AddEntry(histlist[1], f"{percents[counter1]}% of events", "l")
    #             else:
    #                 legend.AddEntry(0, " ", "")
    #             counter1 += 1
    #         else:
    #             if (counter2 < len(Legend)):
    #                 histlist[1].SetLineColor(colors[counter2])
    #                 legend.AddEntry(histlist[1], f"{Legend[counter2]}", "l")
    #             else:
    #                 legend.AddEntry(0, " ", "")
    #             counter2 += 1
           
    
    legend1.Draw()
    legend2.Draw()
    pave = ROOT.TPaveText(0.7, 0.65, 0.9, 0.7, "NDC")  # (x1, y1, x2, y2)
    pave.AddText(f"Events: {histlist[0].Integral():.0f}")
    pave.SetFillColor(0)    # Transparent fill
    pave.SetBorderSize(1)   # Border thickness
    pave.SetTextSize(0.025)  # Optional
    pave.Draw()
    # latex.DrawLatex(0.9, 0.35, f"Events = {histlist[0].Integral():.1f}")

    canvas.SaveAs(f"{HOME}/{save_path}")


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

def SaveIntPlot(df,x,y,x_bins,saveL):
    xmax = int((df.Max(x).GetValue()*1.2)*100)/100
    ymax = int((df.Max(y).GetValue()*1.2)*100)/100
    xmin = int((df.Min(x).GetValue()*1.2)*100)/100
    ymin = int((df.Min(y).GetValue()*1.2)*100)/100
    bin_width = 0.01
    nbins_x = int(xmax / bin_width)
    nbins_y = int(ymax / bin_width)
    interHistogramInfo = (
        "INTNAME",
        f"{y} vs {x} plot",
        nbins_x, xmin, xmax,   # X: nbins, min, max
        nbins_y, ymin, ymax    # Y: nbins, min, max
    )
    # print(interHistogramInfo)
    if (df.HasColumn("weights")):
        interhist = df.Histo2D(interHistogramInfo, x,y,"weights")
        # print("weights activated1")
    else:
        interhist = df.Histo2D(interHistogramInfo, x,y)
    c = DrawXLines(interhist, x_bins, df.Max(y).GetValue())
    c.SaveAs(saveL)

def defineWeights(df, rwRootFile, histName, Fscale = 1):
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

def defineWeightsSpline(df, rwRootFile, histName, label="", Fscale = 1, areaB = False, undoNormB = False):
    flux_file = ROOT.TFile.Open(rwRootFile)
    hist = flux_file.Get(histName)  
    print(histName)
    hist.SetDirectory(0)  
    flux_file.Close()

    if (areaB):
        integral1 = hist.Integral("width")  # Use "width" to integrate over bin widths (important for variable bins)
        if integral1 > 0:
            hist.Scale(1.0 / integral1)
        else:
            raise ValueError("Histogram has zero integral; cannot normalize.")
    print("original width integral")
    print(hist.Integral("width"))

    n_points0 = hist.GetNbinsX()
    graph0 = ROOT.TGraph(n_points0)

    for i in range(1, n_points0 + 1):
        x = hist.GetBinCenter(i)
        y = hist.GetBinContent(i)
        graph0.SetPoint(i - 1, x, y)
  
    # SHAPE (RELATIVE SCALE): First spline made from original histogram
    spline_name0 = f"g_fluxSpline_0{label}"
    spline0 = ROOT.TSpline3(spline_name0, graph0)
    func_name0 = f"get_flux_weight_0{label}"
    
    spline_width_integral0 = 0.0
    for i in range(1, hist.GetNbinsX() + 1):
        x = hist.GetBinCenter(i)
        w = hist.GetBinWidth(i)
        spline_width_integral0 += spline0.Eval(x) * w
    print("spline width-integral0 (hist-like) =", spline_width_integral0)
    
    # ABSOLUTE SCALE: Convert bin normalized histo to "per-bin" contents and apply Fscale
    bin_integral_unnorm = 0.0   
    for i in range(1, hist.GetNbinsX() + 1):
        y = hist.GetBinContent(i)
        w = hist.GetBinWidth(i)
        bin_integral_unnorm += y * w * Fscale   # multiply each bin by its width, then Fscale

    print("bin integral after (content*width*Fscale) =", bin_integral_unnorm)

    # Declare the global variable (no assignment yet)
    ROOT.gInterpreter.Declare(f"TSpline3* {spline_name0};")
    # Assign from Python side using setattr
    setattr(ROOT, spline_name0, spline0)

    ROOT.gInterpreter.Declare(f"""
        extern TSpline3* {spline_name0};
        double {func_name0}(double E) {{
            return {spline_name0}->Eval(E);
        }}
    """)
   
    # Define new column in DataFrame from spline0 to give the right shape
    df = df.Define("weights", f"{func_name0}(Enu_true)")

    # df with weights give flux shape, bin_integral_unnorm give absolute scale for give Fscale (xsec, target, exposure, unit conversion)
    return df, bin_integral_unnorm

def defineSplineTest(df, rwRootFile, histName):
    flux_file = ROOT.TFile.Open(rwRootFile)
    hist = flux_file.Get(histName)  
    hist.SetDirectory(0)  
    flux_file.Close()

    n_points = hist.GetNbinsX()
    graph = ROOT.TGraph(n_points)

    for i in range(1, n_points + 1):
        x = hist.GetBinCenter(i)
        y = hist.GetBinContent(i)
        graph.SetPoint(i - 1, x, y)

   # Create TSpline3 from the graph
    spline = ROOT.TSpline3("flux_spline", graph)

    # Bind spline as a global C++ object
    # ROOT.gROOT.ProcessLine("TSpline3* g_fluxSpline = nullptr;")
    # ROOT.gROOT.ProcessLine("g_fluxSpline = new TSpline3();")  # placeholder
    # ROOT.g_fluxSpline = spline

    c1 = ROOT.TCanvas("c1", "Flux Histogram and Spline", 800, 600)

    hist.GetXaxis().SetRangeUser(0.0, 5.0)  # Set your desired range here

    # Draw the histogram first
    hist.SetLineColor(ROOT.kRed)
    hist.SetMarkerStyle(20)
    hist.Draw("HIST")  # E1 = error bars with markers

    # Draw the spline on top
    spline.SetLineColor(ROOT.kBlue)
    spline.SetLineWidth(2)
    spline.Draw("L SAME")  # L = line, SAME = overlay
    hist.GetXaxis().SetTitle("Neutrino Energy (GeV)")
    hist.GetYaxis().SetTitle("Flux Weight")

    c1.BuildLegend()
    hist.SetTitle("T2K Flux Spline vs Points")
    c1.Update()
    c1.SaveAs("/home/lboe/t2k-nova/6-23-25/flux_spline_comparison2.png")

def overlapPlots(df, x, histInfo, cuts, colors):
    histlist = []
    for i in range(len(cuts)):
        print(f"Plotting mode {cuts[i]}")
        modedf = df.Filter(f"{cuts[i]}")
        hist = modedf.Histo1D(histInfo,x)
        # print(colors[i])
        hist.SetLineColor(colors[i])
        hist.SetFillColor(0)
        # th1d = hist.GetPtr()
        histlist.append(hist)
    return histlist

def SaveOverlapPlot(histlist, AxisInfo, Legend, save_path, hist_max=None, Normalize = 0):
    xvar = AxisInfo[0]
    xunit = AxisInfo[1]
    yvar = AxisInfo[2]
    yunit = AxisInfo[3]
    PlotTitle = AxisInfo[4]
    if hist_max is None:
        hist_max = 0


    for i in range(len(histlist)):
        if Normalize == 1:
            scale = 1/(histlist[i].Integral())
        #    print(scale)
            histlist[i].Scale(scale)
        if Normalize == 2:
            for j in range(1, histlist[i].GetNbinsX()+1):
                histlist[i].SetBinContent(j,histlist[i].GetBinContent(j)/histlist[i].GetBinCenter(j))
        hist_max = max(hist_max, histlist[i].GetMaximum())
  
    histlist[0] = SF.formatHist(histlist[0],xvar, xunit, yvar, yunit, max = hist_max*1.1, PlotTitle=PlotTitle)

    
    c = ROOT.TCanvas()
    c.SetLeftMargin(0.15)  # Adjust the left margin to avoid cutting off the y-axis label
    c.SetRightMargin(0.15) #Adjust the right margin to make space for the legend
    c.SetBottomMargin(0.15) #Adjust the bottom margin to avoid cutting off the x-axis label
    legend = ROOT.TLegend(0.85, 0.7, 1.0, 0.9)  # Define legend position
    for i in range(len(histlist)):
        h = histlist[i].GetPtr()
        if i == 0:
            h.Draw("HIST")
            # print(f"first arg {histlist[i]} second :{Legend[i]}")
            legend.AddEntry(h, f"{Legend[i]}", "f")
        else:
            histlist[i].Draw("HIST SAME")
            legend.AddEntry(h, f"{Legend[i]}", "f")
    legend.Draw()

    # saves hist to a specific directory 
    c.SaveAs(f"{HOME}/{save_path}")
    
def HistoErrorBars(hist):
    """
    Ensures proper treatment of errors for a histogram.
    For weighted histograms, this will store sum of weights squared.
    """
    hist.Sumw2()  # Tells ROOT to store sum of weights^2 per bin
    return hist


if __name__=="__main__":
    # Test functions in this area
    # print("What are you testing?")
    x = 'Enu_true'
    y = 'q0'
    file_path = "/data/t2k-nova/FlatTrees/Flat_NEUT5.9_flatf_1e7.root"
    AxisInfo = ['E#nu_{true}', '(GeV)','counts', '',"test"]
    histInfo = ("name",f"{y} vs {x} plot",250,0,5)
    df = CreateDataFrame(file_path, "None")
    defineSplineTest(df, "/data/t2k-nova/fluxes/23av1_nom/nd5_numode_23a_nominal_10MeVbins.root","enu_nd5_23a_untuned_numu")
    # hist  = df.Histo1D(histInfo,x,"weights")
    # Savehist(hist,AxisInfo,"t2k-nova","Test2","png")
    # x = 'W'
    # y = 'Q2'
    # AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    # histInfo = ("name",f"{y} vs {x} plot",60,0,3,120,0,6)
    # hist, file_path = Plot1PI(x,y,histInfo,"/data/t2k-nova/FlatTrees/FLAT_NEUT_0.7GeV_1e7.root")
    # SavePlot(hist,"testname2",AxisInfo, file_path)








