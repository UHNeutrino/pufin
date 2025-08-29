#include <TH1D.h>
#include <vector>
#include <bits/stdc++.h>

std::vector<double> BinningStruct(TH1D* h1){
    //want atleast 1000 per bin
    int num_of_bins = h1->GetXaxis()->GetNbins();
    std::vector<double> bin_cont;
    double max_init_bin=0;
    for(int i=1; i<num_of_bins+1; i++){
        bin_cont.push_back(h1->GetBinContent(i));
        if(h1->GetBinContent(i)>max_init_bin){
            max_init_bin=h1->GetBinContent(i);
        }
        std::cout << h1->GetBinLowEdge(i) << std::endl;
        std::cout << h1->GetBinContent(i) << std::endl;
    }

    std::cout << "Start Rebinning" << std::endl;
    std::vector<double> rebins;

    double cutoff=max_init_bin/50;
    std::cout << cutoff << std::endl;
    bool last_index=false;
    for(int i=1; i<num_of_bins+1; i++){
        if(bin_cont[i-1]<cutoff){
            int m=1;
            double current_bin_cont=bin_cont[i-1];
            while(current_bin_cont<cutoff && i+m<num_of_bins && last_index==false){
                current_bin_cont+=bin_cont[i+m];
                m++;
            }
            if((i+m)==num_of_bins-1){
                last_index==true;
            }
            if(last_index==false){
                rebins.push_back(h1->GetXaxis()->GetBinLowEdge(i+m));
            }
            i+=m;
        }
        else{
            rebins.push_back(h1->GetXaxis()->GetBinLowEdge(i));
        }
    }
    //rebins.push_back(h1->GetXaxis()->GetBinLowEdge(num_of_bins));
    //rebins.push_back(h1->GetXaxis()->GetXmax());
    // rebins.push_back(max);
    for(int i=0; i<rebins.size(); i++){
        std::cout << "bin " << i << " --> " << rebins[i] << std::endl;
    }
    
    return rebins;
}


// std::vector<double> BinningStruct(std::vector<double> event_prop){
//     double max = event_prop[0];
//     double min = event_prop[0];
//     for(int i=1; i<event_prop.size(); i++){
//         if(event_prop[i]>max){
//             max=event_prop[i];
//         }
//         if(event_prop[i]<min){
//             min=event_prop[i];
//         }
//     }
//     std::cout << "max=" << max << " --> min=" << min << std::endl;
//     TH1D* h1 = new TH1D("h1","h1", 100, min, max);
//     for(int i=0; i<event_prop.size(); i++){
//         h1->Fill(event_prop[i]);
//     }
//     //want atleast 1000 per bin
//     int num_of_bins = h1->GetXaxis()->GetNbins();
//     std::vector<double> bin_cont;
//     for(int i=0; i<num_of_bins; i++){
//         bin_cont.push_back(h1->GetBinContent(i));
//         std::cout << bin_cont[i] << std::endl;
//     }

//     std::cout << "Start Rebinning" << std::endl;
//     std::vector<double> rebins;
//     rebins.push_back(min);
//     for(int i=1; i<num_of_bins; i++){
//         if(bin_cont[i]<1500){
//             int m=0;
//             double current_bin_cont=bin_cont[i];
//             while(current_bin_cont<1500 && i+m<num_of_bins-1){
//                 m++;
//                 current_bin_cont+=bin_cont[i+m];
//             }
//             rebins.push_back(h1->GetXaxis()->GetBinLowEdge(i+m));
//             i+=m;
//         }
//         else{
//             rebins.push_back(h1->GetXaxis()->GetBinLowEdge(i));
//         }
//     }
//     rebins.push_back(max);
//     for(int i=0; i<rebins.size(); i++){
//         std::cout << "bin " << i << " --> " << rebins[i] << std::endl;
//     }
    
//     return rebins;
// }

std::vector<double> Bin_cut_off(TH1D* h1) {
    //want atleast 1000 per bin
    std::cout << "Start Rebinning" << std::endl;
    std::vector<double> rebins;

    int bin_index=1;
    // if(h1->GetBinContent(bin_index)==0){
    //     bin_index++;
    // }
    
    while(h1->GetBinLowEdge(bin_index)<10000){
        if(h1->GetBinContent(bin_index)!=0){
            rebins.push_back(h1->GetBinLowEdge(bin_index));
        }
        bin_index++;
    }
    rebins.push_back(h1->GetBinLowEdge(bin_index));

    if(rebins.size()<4){
        rebins.clear();
        for(int i=1; i<h1->GetNbinsX(); i++){
            rebins.push_back(h1->GetBinLowEdge(i));
        }
    }
    return rebins;
}