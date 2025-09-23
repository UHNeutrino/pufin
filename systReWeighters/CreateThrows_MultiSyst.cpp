R__ADD_LIBRARY_PATH($LD_LIBRARY_PATH)
R__LOAD_LIBRARY(libGRwClc.so)

#include "nusystematics/utility/response_helper.hh"
#include "Framework/Ntuple/NtpMCEventRecord.h"
#include "Framework/EventGen/EventRecord.h"


#include "user_int/Get_User_stuff.hh"
#include "draw_struct/CreateXML.hh"

#include <vector>
#include <iostream>

#include <TRandom3.h>
#include <TFile.h>
#include <TTree.h>
#include <TBranch.h>
#include <TStopwatch.h>
#include <TH1D.h>
#include <ROOT/RDataFrame.hxx>

void CreateThrows_MultiSyst(std::string userdata, std::string fcl_file, std::string point_file, std::string hist_output, int num_of_throws){
    TStopwatch sw;
    sw.Start();
    TFile genie_file(Get_GENIE_file_and_tune(userdata)[0].c_str());
    std::cout << Get_GENIE_file_and_tune(userdata)[0] << std::endl;
    TTree* mytree = (TTree*)genie_file.Get("gtree");
    genie::NtpMCEventRecord* myEventRecord = new genie::NtpMCEventRecord();
    mytree->SetBranchAddress("gmcrec", &myEventRecord);
    //genie_file.Close();

    nusyst::response_helper* resp = new nusyst::response_helper(fcl_file.c_str());
    
    std::fstream syst_file;
    //std::vector<std::string> syst_name = Get_Analysis_syst(userdata);
    std::vector<string> syst_name = Get_Syst_name(userdata);
    std::vector<systtools::paramId_t> syst_id;
    std::cout << syst_name.size() << std::endl;
    for(int i=0; i<syst_name.size(); i++){
        std::cout << syst_name[i] << std::endl;
        syst_id.push_back(resp->GetHeaderId(syst_name[i]));
    }
    int num_of_events=Get_Num_Events(userdata);

    //std::vector<std::vector<std::unique_ptr<TSpline3>>> splines;
    //std::vector<std::vector<TSpline3*>> splines;
    std::vector<std::vector<TSpline3>> splines;

    std::fstream fcl_check; 
    fcl_check.open(fcl_file, std::ios::in);
    std::string string_temp;
    int string_index=0;  
    bool is_genie_set=false;
    while(getline(fcl_check, string_temp)){
        if(string_index==1){
            if(string_temp.find("    GENIEReWeight: {")  != std::string::npos){
                is_genie_set=true;
            }
            break;
        }
        string_index++;
    }
    if(is_genie_set==false){
        for(int event_num=0; event_num<num_of_events; event_num++){
            if(event_num%10000==0){
                std::cout << event_num << std::endl;
            }
            //std::cout << "Get Events" << std::endl;
            mytree->GetEntry(event_num);
            //std::cout << "Grab Nodes" << std::endl;
            const genie::EventRecord & event = *(myEventRecord->event);
            std::vector<TSpline3> temp_spline_vec;
            //std::cout << event_num << std::endl;
            for(int syst=0; syst<syst_name.size(); syst++){
                //std::cout << syst_name[syst] << std::endl;
                systtools::event_unit_response_t Events_stand = resp->GetEventResponses(event);
                temp_spline_vec.push_back(resp->GetSpline(syst_id[syst], Events_stand));
                std::cout << "at -1: " << temp_spline_vec[syst].Eval(-1.00) << " ---> and at 3.00: "<< temp_spline_vec[syst].Eval(3.00) << std::endl;
            }
            splines.push_back(temp_spline_vec);
        }
    }
    else{
        //Set up vectors needed for storing splines
        TFile tree_file(point_file.c_str(), "READ");

        for(int event_num=0; event_num<num_of_events; event_num++){
            auto tree = std::unique_ptr<TTree>(static_cast<TTree*>(tree_file.Get(Form("event_%d", event_num))));
            //TTree* tree = (TTree*)tree_file.Get(Form("event_%d", event_num));
            //std::vector<std::unique_ptr<TSpline3>> temp_spline_vec;
            //std::vector<TSpline3*> temp_spline_vec;
            std::vector<TSpline3> temp_spline_vec;
            std::vector<std::pair<double,double>>* event_pair=0;
            if(event_num%10000 == 0){
                std::cout << event_num << std::endl;
            }
            for(int syst=0; syst<syst_name.size(); syst++){
                auto branch = tree->GetBranch(syst_name[syst].c_str());
                branch->SetAddress(&event_pair);
                branch->SetAutoDelete(kTRUE);
                int nentries = branch->GetEntries();
                for(Int_t i=0; i<nentries; i++){
                    branch->GetEntry(i);
                }
                double nodes[branch->GetEntries()];
                double weights[branch->GetEntries()];
                int index=0;
                for(const auto &x : *event_pair){
                    nodes[index] = x.first;
                    weights[index] = x.second;
                    index++;
                }
                const char* opt=0;
                //TSpline3* temp_spline = new TSpline3("spline", nodes, weights, branch->GetEntries(),opt);
                TSpline3 temp_spline("spline", nodes, weights, branch->GetEntries(),opt);
                //auto temp_spline = std::make_unique<TSpline3>(TSpline3("spline", nodes, weights, branch->GetEntries(),opt));
                //std::unique_ptr<TSpline3> temp_spline(new TSpline3("spline", nodes, weights, branch->GetEntries(), opt));
                temp_spline_vec.push_back(temp_spline);
                event_pair->clear();
                delete opt;
            }
            splines.push_back(temp_spline_vec);
            temp_spline_vec.clear();
            delete event_pair;
        }
        tree_file.Close();
    }
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME FOR EVENTS -----> "  << sw.CpuTime() << std::endl;
    sw.Reset();
    sw.Continue();


    CreateXML(Get_GENIE_file_and_tune(userdata)[0]);
    std::system(Form("nuiscomp -c genie_comp.xml -o %s -n %d", hist_output.c_str(), num_of_events));
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME !!!!" << std::endl;
    std::cout << "TIME for events!!! ----> "<<sw.CpuTime() << std::endl;
    sw.Reset();
    sw.Continue();
    TFile f1(hist_output.c_str(), "UPDATE");
    f1.cd();
    TRandom3 throw_gen;
    for(int k=0; k<num_of_throws; k++){
        std::cout << "Throw: " << k << std::endl; 
        std::vector<double> random_param;
        throw_gen.SetSeed();
        for(int param_ind=0; param_ind<syst_name.size(); param_ind++){
            random_param.push_back(throw_gen.Gaus(0,1));
        }
        auto throw_tree = std::make_unique<TTree>(Form("h_%d",k), Form("h_%d", k));
        for(int isyst=0; isyst<syst_name.size(); isyst++){
            double RWWeight;
            TBranch* branch = throw_tree->Branch(syst_name[isyst].c_str(), &RWWeight);
            //auto branch = make_unique<TBranch>(throw_tree->Branch(syst_name[isyst].c_str(), &RWWeight));
            for(int event_num=0; event_num<splines.size(); event_num++){
                double param_value = random_param[isyst];
                double weight = splines[event_num][isyst].Eval(param_value);
                RWWeight=weight;
                if(RWWeight!=1.0){
                    std::cout << RWWeight << std::endl;
                }
                throw_tree->Fill();
            }
        }
        throw_tree->Write();
    }
    f1.Close();
    std::cout << "TIME!!!!" << std::endl;
    std::cout << "TIME!!!!" << std::endl;
    std::cout << "TIME!!!!" << std::endl;
    std::cout << "TIME!!!!" << std::endl;
    std::cout << "TIME!!!!" << std::endl;
    std::cout << "TIME FOR THROWS ---> " << sw.CpuTime() << std::endl;

    std::system(Form("nuiscomp -c MultiSig.xml -o ExperimentalFlags.root -n %d", num_of_events));
}