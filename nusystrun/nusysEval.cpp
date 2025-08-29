// R__ADD_LIBRARY_PATH($LD_LIBRARY_PATH)
R__ADD_LIBRARY_PATH("/project/software/GENIE_v2_06_00/Generator/install/lib")
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
#include <ROOT/RDataFrame.hxx>

void nusysEval(){
    std::string fcl_file = "/home/mazen_malak/Thesis_results/all.fcl";
    const char* Genie_file = "/data/t2k-nova/LarsGen/GenieGen/N24TestGen.root"; // Genie file path
    std::string userdata = "/data/t2k-nova/LarsGen/GenieGen/N24Config.txt"; //Config file path??
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
    genie::NtpMCEventRecord* myEventRecord = new genie::NtpMCEventRecord();
    mytree->SetBranchAddress("gmcrec",&myEventRecord);
    // genie_file->Close();
    nusyst::response_helper* resp = new nusyst::response_helper(fcl_file.c_str());
    std::cout << "hi2" << std::endl;
    // // // ###########################################################################
    // // ^This block pulls the GENIE Event Record followed by setting up nusystematics reposnsehelper where you pass it a fcl file
    std::fstream syst_file;
    std::vector<string> syst_name = Get_Syst_name(userdata);
    std::vector<systtools::paramId_t > syst_id;
    std::cout << syst_name.size() << std::endl;

    for(int i = 0; i<syst_name.size(); i++ ){
        std::cout << syst_name[i] << std::endl;
        syst_id.push_back(resp->GetHeaderId(syst_name[i]));
    }
    systtools::paramId_t xxxx = resp->GetHeaderId("FrAbs_pi");
    int num_of_events = Get_Num_Events(userdata);
    std::cout <<  "Events:" << std::endl;
    std::cout << num_of_events << std::endl;


    // // The stuff before the temp spline is important
    for(int event_num =0; event_num<num_of_events; event_num++){
        if(event_num%1==0){
            std::cout << event_num << std::endl;
        }
        std::cout << "Get Events" << std::endl;
        mytree->GetEntry(event_num);
        std::cout << "Grab Nodes" << std::endl;
        const genie::EventRecord & event = *(myEventRecord->event);
        std::vector<TSpline3> temp_spline_vec;
        for(int syst=0;syst<syst_name.size();syst++){
            std::cout << "Get Events" << std::endl;
            systtools::event_unit_response_t Events_stand = resp->GetEventResponses(event); //resp->GetSpline() will create the spline and from there you .Eval()
            temp_spline_vec.push_back(resp->GetSpline(syst_id[syst], Events_stand));
            std::cout << resp->GetSpline(syst_id[0], Events_stand).Eval(1.5) << std::endl;

        }
        // rather than storing splines you can store evals these are doubles 
        // auto Events_stand = resp->GetEventResponses(event);
        // std::cout << resp->GetSpline(syst_id[0], Events_stand).Eval(1.5) << std::endl;
    }
    genie_file->Close();

    // // ^


}
