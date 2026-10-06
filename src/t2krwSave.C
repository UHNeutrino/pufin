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
    std::string card_file = "/path/to/the/card/file.card";
    const char* infile = "/path/to/the/generated/file.root";
    const char* outfile = "/path/to/the/output/file.root";
    std::vector<float> DialValues = {-1.0, 0.0, 1.0};
    std::string BranchName = "";

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
    NeutVect *nvect = nullptr;
    intree->SetBranchAddress("vectorbranch", &nvect);

    // -------------------------------
    // Create output file and tree
    // -------------------------------
    TFile *fout = new TFile(outfile, "RECREATE");
    TTree *outtree = new TTree("weighttree", "Tree with syst weights");

    // Example systematic dials (replace with the ones you need!)
    std::vector<std::string> syst_names = {"Dial1","Dial2"};

    // Create a branch for each weight
    std::map<std::string, double> weight_branches;
    for (auto &value : DialValues) {
        for (auto &name : syst_names) {
            std::string key = name + "_" + std::to_string(value);
            weight_branches[key] = 0.0;              // initialize entry to zero to be filled later
            outtree->Branch(key.c_str(), &weight_branches[key]);
        }
    }

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

        for (auto &value: DialValues) {
            for (auto &name : syst_names) {
                rw->Reset();
                auto dial_id = rw->DialFromString(name);
                rw->SetDial_NumberOfSigmas(dial_id, value);
                rw->Reconfigure();
                std::string key = name + "_" + std::to_string(value);
                weight_branches[key] = rw->CalcWeight(neut_event);
            }
            outtree->Fill();
        }   

        
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
