#include "TFile.h"
#include "TTree.h"

#include "neutvtx.h"
#include "neutpart.h"
#include "neutvect.h"

#include "T2KReWeight/Interface/T2KSyst.h"
#include "T2KReWeight/Interface/T2KWeightEngineI.h"
#include "T2KReWeight/WeightEngines/T2KReWeightEvent.h"
#include "T2KReWeight/WeightEngines/T2KReWeightFactory.h"
#include "T2KReWeight/WeightEngines/NEUT/T2KNEUTReWeight.h"
#include "T2KReWeight/WeightEngines/NEUT/T2KNEUTUtils.h"
#include "T2KReWeight/Interface/T2KReWeight.h"
#include <memory>


void t2krwSave(){
    // auto T2Krw = t2krew::MakeT2KReWeightInstance();
    std::string card_file = "/data/t2k-nova/LarsGen/neutsysMed.card";
    const char* infile = "/data/t2k-nova/LarsGen/neutSysTest1e5.root";
    const char* outfile = "/data/t2k-nova/LarsGen/NEUTSYS/nuisSysTestMed_with_NEUTweights.root";
    TFile *fin = TFile::Open(infile, "READ");
    if (!fin || fin->IsZombie()) {
        std::cerr << "Error: cannot open input file " << infile << std::endl;
        return;
    }

    TTree *intree = (TTree*)fin->Get("neuttree");
    if (!intree) {
        std::cerr << "Error: cannot find tree 'neuttree' in " << infile << std::endl;
        return;
    }
    // intree->Print();
    NeutVect *nvect = nullptr;
    intree->SetBranchAddress("vectorbranch", &nvect);

    // NeutVtx *nvtx = nullptr;
    // intree->SetBranchAddress("vertexbranch", &nvtx);

    std::cout << "hi1." << std::endl;
    // -------------------------------
    // Create output file and tree
    // -------------------------------
    TFile *fout = new TFile(outfile, "RECREATE");
    TTree *outtree = new TTree("weighttree", "Tree with syst weights");

    // Example systematic dials (replace with the ones you need!)
    std::vector<std::string> syst_names = {
        "MaCCQE",
        "MaRES",
        "CA5RES",
        "BgSclRES",
        "NucleonFSI_Double",
        "NucleonFSI_Elastic",
        "NucleonFSI_Single",
        "NucleonFSI_Total",
        "PionFSI_AbsProb",
        "PionFSI_QELowMomProb",
        "PionFSI_QEHighMomProb",
        "PionFSI_CExLowMomProb",
        "PionFSI_CExHighMomProb",
        "PionFSI_InelProb",
        "SRCFrac_C",
        "SRCFrac_O",
        "RadCorr_rate",
    };

    // Create a branch for each weight
    std::map<std::string, double> weight_branches;
    for (auto &name : syst_names) {
        weight_branches[name] = 1.0;
        outtree->Branch(name.c_str(), &weight_branches[name]);
    }

    std::cout << "hi2" << std::endl;

    // -------------------------------
    // Set the NEUT card file
    // -------------------------------
    t2krew::T2KNEUTUtils::SetCardFile(card_file);

    // -------------------------------
    // Create the ReWeight instance
    // -------------------------------
    std::cout << "Creating ReWeight instance" << std::endl;
    auto rw = t2krew::MakeT2KReWeightInstance(t2krew::Event::kNEUT);

    // -------------------------------
    // Event loop
    // -------------------------------
    Long64_t nentries = intree->GetEntries();
    for (Long64_t i = 0; i < nentries; ++i) {
        intree->GetEntry(i);
        if(i%10000==0){
            std::cout << i << std::endl;
        }
        // Create a t2krew::Event from NeutVect*
        auto neut_event = t2krew::Event::Make(nvect);
        // auto type = neut_event.GetEventType();

        for (auto &name : syst_names) {
            rw->Reset();
            auto dial_id = rw->DialFromString(name);
            rw->SetDial_NumberOfSigmas(dial_id, 1.0);
            rw->Reconfigure();
            // std::cout << "get Dial from String" << std::endl;
            // std::cout << "Event Type:" << << std::endl;
            // if (nvect->Mode == 11 && nvect->NnucFsiVert() == 1){
            //     if (rw->CalcWeight(neut_event) == 0){
            //         std::cout << "XXXXXXXXXBADXXXXXXXXXXX" << `std::endl;
            //     }
            //     int NPart = nvect->Npart();
            //     std::cout << "Event " << i << " weight = " << rw->CalcWeight(neut_event) << std::endl;
            //     std::cout << "\tNpart = " << nvect->Npart() << std::endl;
            //     std::cout << "\tNfsi = " << nvect->NfsiPart() << std::endl;
            //     std::cout << "\tNucFSI = " << nvect->NnucFsiVert() << std::endl;
            //     std::cout << "\tMode = " << nvect->Mode << std::endl;
            //     std::cout << "\tTarget A = " << nvect->TargetA << " Z = " << nvect->TargetZ << std::endl;
            //     for(int j=0; j<NPart;j++){
            //         auto Part = nvect->PartInfo(j);
            //         std::cout << "\t Particle " << j << std::endl;
            //         std::cout << "\t\tPID = " << Part->fPID << std::endl;
            //         std::cout << "\t\tStatus = " << Part->fStatus  << std::endl;

            //     }
            // }

            // CalcWeight now takes the Event reference
            weight_branches[name] = rw->CalcWeight(neut_event);
        }

        outtree->Fill();
    }


    // -------------------------------
    // Save output
    // -------------------------------
    fout->cd();
    outtree->Write();
    fout->Close();
    fin->Close();

    std::cout << "Wrote " << outfile << " with "
            << syst_names.size() << " systematic weight branches.\n";
    std::cout << "Done." << std::endl;
    
}
