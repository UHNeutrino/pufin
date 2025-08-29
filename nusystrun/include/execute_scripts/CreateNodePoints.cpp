R__ADD_LIBRARY_PATH($LD_LIBRARY_PATH)
R__LOAD_LIBRARY(libGRwClc.so)

#include "Framework/Ntuple/NtpMCEventRecord.h"
#include "Framework/EventGen/EventRecord.h"
#include "nusystematics/utility/response_helper.hh"

#include "user_int/Get_User_stuff.hh"

#include <vector>
#include <string>
#include <memory>

#include <TGraph.h>
#include <TFile.h>
#include <TTree.h>
#include <TInterpreter.h>
#include <TStopwatch.h>

void CreateNodePoints(std::string user_data, std::string fcl_file, std::string point_file){
    TStopwatch sw;
    sw.Start();
    TFile genie_file(Get_GENIE_file_and_tune(user_data)[0].c_str());
    std::cout << "GENIE FILE FOUND ---> " << Get_GENIE_file_and_tune(user_data)[0] << std::endl;
    TTree* mytree = (TTree*)genie_file.Get("gtree");
    genie::NtpMCEventRecord* myEventRecord = new genie::NtpMCEventRecord();
    mytree->SetBranchAddress("gmcrec", &myEventRecord);
    nusyst::response_helper* resp = new nusyst::response_helper(fcl_file.c_str());
    
    //Pull All Systematics by name;
    std::fstream syst_file;
    std::vector<string> syst_name = Get_Syst_name(user_data);
    std::vector<systtools::paramId_t> syst_id;
    std::cout << "Setting Node Point Config for " << syst_name.size()  << ": " << std::endl;
    for(int i=0; i<syst_name.size(); i++){
        syst_id.push_back(resp->GetHeaderId(syst_name[i]));
        std::cout << syst_name[i] << std::endl;
    }

    int num_of_events=Get_Num_Events(user_data);

    TFile spline_output_file(point_file.c_str(), "RECREATE");
    //bool filltree=false;


    ///Add a flag to check if this is a genie systematic or not 
    //std::fstream fcl_check; 
    //fcl_check.open(fcl_file, std::ios::in);
    //std::string string_temp;
    //int string_index=0;  
    bool is_genie_set=false;
    std::cout << "ENGINE USED --> " << Get_Engine_Type(user_data) << std::endl;
    if(Get_Engine_Type(user_data)=="GENIEReWeight"){
        is_genie_set=true;
    }
    //while(getline(fcl_check, string_temp)){
    //    if(string_index==1){
    //        if(string_temp.find("    GENIEReWeight: {")  != std::string::npos){
    //            is_genie_set=true;
    //        }
    //        break;
    //    }
    //    string_index++;
    //}
    if(is_genie_set==false){
        spline_output_file.Close();
    }
    else{
        for(int event_num=0; event_num<num_of_events; event_num++){
            auto event_tree = std::make_unique<TTree>(Form("event_%d", event_num), Form("event_%d", event_num));
            std::vector<std::pair<double, double>> my_pair;
            if(event_num%10==0){
                std::cout << event_num << std::endl;
            }
            mytree->GetEntry(event_num);
            const genie::EventRecord & event = *(myEventRecord->event);
            for(int syst=0; syst<syst_id.size(); syst++){
                my_pair.clear();
                auto branch = event_tree->Branch(syst_name[syst].c_str(), &my_pair);
                const std::vector<std::vector<double>>& Events_resp = resp->GetImprovedParameterResponse(syst_id[syst], event);
                for(int i=0; i<Events_resp[0].size(); i++){
                    my_pair.push_back(make_pair(Events_resp[0][i], Events_resp[1][i]));
                    branch->Fill();
                }
            }
            event_tree->Write();
        }
        spline_output_file.Close();
        std::cout << "TIME!!!!" << std::endl;
        std::cout << "TIME!!!!" << std::endl;
        std::cout << "TIME!!!!" << std::endl;
        std::cout << "TIME!!!!" << std::endl;
        std::cout << "TIME FOR NODES ----> " << sw.CpuTime() <<  std::endl;
    }
}
