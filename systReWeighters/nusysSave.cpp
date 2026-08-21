// R__ADD_LIBRARY_PATH($LD_LIBRARY_PATH)
R__ADD_LIBRARY_PATH("/path/to/GENIE_v2_06_00/Generator/install/lib")
R__LOAD_LIBRARY(libGRwClc.so)
#include "nusystematics/utility/response_helper.hh"
#include "Framework/Ntuple/NtpMCEventRecord.h"
#include "Framework/EventGen/EventRecord.h"


#include "/home/lboe/nusystrun/include/user_int/Get_User_stuff.hh"
#include "/home/lboe/nusystrun/include/draw_struct/CreateXML.hh"

#include <vector>
#include <iostream>

#include <TRandom3.h>
#include <TFile.h>
#include <TTree.h>
#include <TBranch.h>
#include <TStopwatch.h>
#include <TH1D.h>
//#include <ROOT/RDataFrame.hxx>
// these are things we "include" later, but in case something changes, better to have them here
#include <string>
#include <fstream>
#include <algorithm>  // for std::min


void nusysSave(){
    std::string fcl_file = "/path/to/fcl/file/name.fcl";
    std::string Genie_path_name = "/path/to/genie/generated/file/name";  
    std::string Genie_file_str  = Genie_path_name + ".root";  
    std::string OutPath_str     = Genie_path_name + "_dialname.root";  
    const char* Genie_file = Genie_file_str.c_str(); // Genie file path
    const char* OutPath    = OutPath_str.c_str();

    std::string userdata = "/home/lboe/t2k-nova/systReWeighters/N24Config.txt"; //Config file path??
    // std::string userdata = "/home/kdobbs/t2k-nova/nusystrun/N24Config.txt"; //Config file path??
    std::cout << "hi" << std::endl;

    // ############################################################
    TFile* genie_file = TFile::Open(Genie_file, "READ"); //String for Genie event record preflattened gen

    if (!genie_file || genie_file->IsZombie()) {
        std::cerr << " Error: could not open file " << Genie_file << std::endl;
        delete genie_file; // cleanup
        return;
    }

    std::cout << "Successfully opened " << Genie_file << std::endl;
    std::cout << Get_GENIE_file_and_tune(userdata)[0] << std::endl;
    TTree* mytree = (TTree*)genie_file->Get("gtree");

    // Create tree to put weights in
    TFile* outfile = new TFile(OutPath, "RECREATE");
    TTree* outtree = new TTree("weighttree","weighttree"); // 0 = copy only structure (branches, leaves)
    std::cout << "Cloned Tree" << Genie_file << std::endl;

    genie::NtpMCEventRecord* myEventRecord = new genie::NtpMCEventRecord();
    mytree->SetBranchAddress("gmcrec",&myEventRecord);
    // // genie_file->Close();
    nusyst::response_helper* resp = new nusyst::response_helper(fcl_file.c_str());
    std::cout << "hi2" << std::endl;
    // ###########################################################################
    // ^This block pulls the GENIE Event Record followed by setting up nusystematics reposnsehelper where you pass it a fcl file
    std::fstream syst_file;
    std::vector<string> syst_name = Get_Syst_name(userdata);
    std::vector<systtools::paramId_t > syst_id;
    std::cout << syst_name.size() << std::endl;


    for(int i = 0; i<syst_name.size(); i++ ){
        std::cout << syst_name[i] << std::endl;
        syst_id.push_back(resp->GetHeaderId(syst_name[i]));
    }
    
    // defining branches for weights
    std::vector<double> syst_weights(syst_id.size(), 1.0); //create vector to hold all the weights
    std::vector<double*> syst_ptrs(syst_id.size(), nullptr);
    for (size_t i = 0; i < syst_name.size(); i++) {
        syst_ptrs[i] = &syst_weights[i];
        outtree->Branch(syst_name[i].c_str(), syst_ptrs[i]);
    }

    int num_of_events = Get_Num_Events(userdata);
    std::cout <<  "Events:" << std::endl;
    std::cout << num_of_events << std::endl;


    for(int event_num =0; event_num<num_of_events; event_num++){
        if(event_num%1000==0){
            std::cout << event_num << std::endl;
        }
        // std::cout << "Get Events" << std::endl;
        mytree->GetEntry(event_num);
        // std::cout << "Grab Nodes" << std::endl;
        const genie::EventRecord & event = *(myEventRecord->event);
        systtools::event_unit_response_t Events_stand = resp->GetEventResponses(event);
        for(int syst=0;syst<syst_name.size();syst++){
            // std::cout << "Get Events" << std::endl;
            // Evaluate spline at chosen dial (example: 1.5) and store in syst_weights
            syst_weights[syst] = resp->GetSpline(syst_id[syst], Events_stand).Eval(1);
        }
        outtree->Fill();
    }
    
    outfile->cd();
    outtree->Write();
    outfile->Close();
    genie_file->Close();

    // // ^


}
