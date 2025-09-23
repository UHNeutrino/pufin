#include <string>
#include <TFile.h>
#include <TH1D.h>
#include <TTree.h>
#include <TMatrixD.h>
#include <cmath>
#include <TArrayD.h>
#include <memory>

// double GetfScaleFactor(TH1D* h_exposure_GENIE, TH1D* h_flux_GENIE, TH1D* h_exposure_comp, TH1D* h_flux_comp){
//     Double_t factor = 1.;
//     h_exposure_comp->Scale(factor, "width");
//     h_exposure_GENIE->Scale(factor, "width");
//     h_flux_comp->Scale(factor,"width");
//     h_flux_GENIE->Scale(factor, "width");
//     double fCompFactor = h_exposure_comp->GetEntries()*h_exposure_comp->Integral("width")/h_flux_comp->Integral("width");
//     double fGenieFactor = h_exposure_GENIE->GetEntries()*h_exposure_GENIE->Integral("width")/h_flux_GENIE->Integral("width");
//     double fScaleFactor = fCompFactor/fGenieFactor;
//     return fScaleFactor;

// }

double GetfScaleFactor(TFile* genie, TFile* Comparison){

    auto h_exposure_GENIE = std::unique_ptr<TH1D>(static_cast<TH1D*>(genie->Get("GenericFlux_Vectors_EVT")));
    auto h_flux_GENIE = std::unique_ptr<TH1D>(static_cast<TH1D*>(genie->Get("GenericFlux_Vectors_FLUX")));
    auto h_exposure_COMP = std::unique_ptr<TH1D>(static_cast<TH1D*>(Comparison->Get("GenericFlux_Vectors_EVT")));
    auto h_flux_COMP = std::unique_ptr<TH1D>(static_cast<TH1D*>(Comparison->Get("GenericFlux_Vectors_FLUX")));

    Double_t factor = 1.;
    h_exposure_COMP->Scale(factor, "width");
    h_exposure_GENIE->Scale(factor, "width");
    h_flux_COMP->Scale(factor,"width");
    h_flux_GENIE->Scale(factor, "width");

    double fCompFactor = h_exposure_COMP->GetEntries()*h_exposure_COMP->Integral("width")/h_flux_COMP->Integral("width");
    double fGenieFactor = h_exposure_GENIE->GetEntries()*h_exposure_GENIE->Integral("width")/h_flux_GENIE->Integral("width");
    double fScaleFactor = fCompFactor/fGenieFactor;
    
    return fScaleFactor;
}

TH1D* DrawAgainst(TFile* Comp, std::string event_property, std::vector<double> bin_struct, std::string flag, double fScaleFactor, std::string MCSTUD){
    TH1D* against_hist= new TH1D(MCSTUD.c_str(), MCSTUD.c_str(), bin_struct[0], bin_struct[1], bin_struct[2]);
    auto tree_ag = std::unique_ptr<TTree>(static_cast<TTree*>(Comp->Get("GenericFlux_Vectors_VARS")));
    if(flag!="" && flag!=" "&& flag!="NONE"){
        tree_ag->Draw(Form("%s>>%s", event_property.c_str(), MCSTUD.c_str()), flag.c_str());
    }
    else{
        tree_ag->Draw(Form("%s>>%s", event_property.c_str(), MCSTUD.c_str()));
    }
    for(int i=1; i<against_hist->GetNbinsX()+1; i++){
        against_hist->SetBinContent(i, against_hist->GetBinContent(i)*fScaleFactor);
    }

    return against_hist;
    // Float_t event_val;
    // bool some_bool;
    // tree_ag->SetBranchAddress(event_property.c_str(), &event_val);
    // if(flag!="" && flag!=" "&& flag!="NONE"){
    //     tree_ag->SetBranchAddress(flag.c_str(), &some_bool);
    // }
    // int nentries = tree_ag->GetEntries();
    // for(int i=0; i<nentries; i++){
    //     tree_ag->GetEntry(i);
    //     if(flag!="" && flag!=" " && flag!="NONE"){
    //         if(some_bool==true){
    //             against_hist->Fill(event_val*some_bool, fScaleFactor);
    //         }
    //     }
    //     else{
    //         against_hist->Fill(event_val*fScaleFactor);
    //     }
    // }
    // return against_hist;
}

// TH1D* DrawAgainst(std::string ag_file_path, std::string event_property, std::vector<double> bin_struct, std::string flag, TH1D* h_exposure_GENIE, TH1D* h_flux_GENIE, TH1D* h_xsec_GENIE){
//     TFile* file_path = new TFile(ag_file_path.c_str(), "READ");
//     TH1D* h_exposure_comp = (TH1D*)file_path->Get("GenericFlux_Vectors_EVT");
//     TH1D* h_flux_comp = (TH1D*)file_path->Get("GenericFlux_Vectors_FLUX");
//     TH1D* h_xsec_comp = (TH1D*)file_path->Get("GenericFlux_Vectors_XSEC");
//     int n_bins_comp = h_exposure_comp->GetNbinsX();
//     //int n_bins_GENIE = h_exposure_GENIE->GetNbinsX();
//     //double fScaleFactor=0;
//     // /if(n_bins_comp>n_bins_GENIE){ ///// RESIZE BIN CONTENT FOR COMP
//     std::cout << "REBING EVT OF NEUT" << std::endl;
    
    
//     // TH1D* h_new_comp = (TH1D*)h_exposure_comp->Clone();
//     // h_new_comp->Clear("MICES");
//     // for(int i=1; i<n_bins_comp+1; i++){
//     //     h_new_comp->SetBinContent(i, h_exposure_comp->GetBinContent(i)/h_exposure_comp->GetBinWidth(i));
//     // }
//     // double fScaleFactor=h_new_comp->Integral()/h_exposure_GENIE->Integral();
    
//     //double fScaleFactor = GetfScaleFactor(h_exposure_GENIE,h_flux_GENIE,h_exposure_comp,h_flux_comp);
    
//     //double fScaleFactor = h_xsec_comp->Integral("width")/h_xsec_GENIE->Integral("width");
    
    
    
//     //h_exposure_GENIE->Scale(factor, "width");
//     //double fScaleFactor = h_exposure_comp->Integral()/h_exposure_GENIE->Integral();
    
    
//     //fScaleFactor=1/fScaleFactor;
//    // }
//     // else{
//     //     std::cout << "REBING EVT OF GENIE" << std::endl;
//     //     TH1D* h_new_GENIE = (TH1D*)h_exposure_comp->Clone();
//     //     h_new_GENIE->Clear("MICES");
//     //     for(int i=1; i<n_bins_GENIE+1; i++){
//     //         h_new_GENIE->SetBinContent(i, h_exposure_GENIE->GetBinContent(i)/h_exposure_GENIE->GetBinWidth(i));
//     //         std::cout << "SETTING GENIE BIN " << i << " AS " << h_exposure_GENIE->GetBinContent(i)/h_exposure_GENIE->GetBinWidth(i) << std::endl;
//     //         std::cout << "GETTING NEUT BIN " << i << " --> " << h_exposure_comp->GetBinContent(i) << std::endl;
//     //     }
//     //     std::cout << "NEUT INTEGRAL --> " << h_exposure_comp->Integral("width") << std::endl;
//     //     std::cout << "GENIE INTEGRAL --> " << h_new_GENIE->Integral("width") << std::endl;
//     //     fScaleFactor=h_exposure_comp->Integral("width")/h_new_GENIE->Integral("width");
//     // }
//     // double comp_exposure = h_exposure_gen->Integral("width");
//     // double fScaleFactor = comp_exposure/genie_exposure;
//     TH1D* h1 = new TH1D("h1", "h1", bin_struct[0], bin_struct[1], bin_struct[2]);
//     auto tree_ag = std::unique_ptr<TTree>(static_cast<TTree*>(file_path->Get("GenericFlux_Vectors_VARS")));
//     std::cout << "FSCALE FACTOR IS ---->>>>> " << fScaleFactor << std::endl;
//     //tree_ag->Draw(Form("(%s)&&%s!=0>>h1", event_property.c_str(),flag.c_str()));
//     //TCut cut1 = Form("%s>0",flag.c_str());
//     //tree_ag->Draw(Form("%s>>h1",event_property.c_str()), cut1);
//     //return h1;
//     //if null -> try some other tree, maybe a flat tree
//     //if niether -> create a flattree for them
//     Float_t event_val;
//     bool some_bool;
//     tree_ag->SetBranchAddress(event_property.c_str(), &event_val);
//     if(flag!="" && flag!=" "&& flag!="NONE"){
//         tree_ag->SetBranchAddress(flag.c_str(), &some_bool);
//     }
//     int nentries = tree_ag->GetEntries();

//     for(int i=0; i<nentries; i++){
//         tree_ag->GetEntry(i);
//         if(flag!="" && flag!=" " && flag!="NONE"){
//             if(some_bool==true){
//                 h1->Fill(event_val*some_bool, fScaleFactor);
//             }
//         }
//         else{
//             h1->Fill(event_val*fScaleFactor);
//         }
//     }
//     // std::cout << "return" << std::endl;
//     return h1;
// }

TH1D* Experiment(std::string against, 
                std::vector<std::string> syst_name,
                TFile* throw_file, 
                std::string event_prop, 
                TTree* event_tree, 
                std::vector<double> rebins,
                int num_of_throws,
                int num_of_events){
    const char* file_path="ExperimentalFlags.root"; //Path to signal flags
    TFile* signal_file = new TFile(file_path, "READ");
    event_tree->AddFriend("MultiSignal_FLAGS", signal_file);

    TH1D* evt_hist = (TH1D*)signal_file->Get("MultiSignal_EVT");
    TH1D* flux_hist = (TH1D*)signal_file->Get("MultiSignal_FLUX");

    TFile* exp_flux = new TFile("MINER_FLUX.root","READ");
    TH1D* exp_flux_hist = (TH1D*)exp_flux->Get("MIN_FLUX");

    double fScaleFactor_base=flux_hist->Integral("width")/num_of_events;
    double fScaleFactor_exp = exp_flux_hist->Integral("width");         //*Event_ratio;
    double fScaleFactor=fScaleFactor_exp/fScaleFactor_base;
    std::cout << "base="<< fScaleFactor_base << "  exp=" << fScaleFactor_exp << "  Scaled=" << fScaleFactor << std::endl;


    std::vector<TH1D*> h_sig_vec;
    double rebin[rebins.size()];
    copy(rebins.begin(), rebins.end(), rebin);

    for(int i=0; i<num_of_throws; i++){
        event_tree->AddFriend(Form("h_%d",i), throw_file);
        std::string c_draw = Form("h_%d.%s*", i, syst_name[0].c_str());
        for(int syst=1; syst<syst_name.size()-1; syst++){
            c_draw+= Form("h_%d.%s*", i, syst_name[syst].c_str());
        }
        c_draw+=Form("h_%d.%s*", i, syst_name[syst_name.size()-1].c_str());
        //c_draw+=Form("MultiSignal_FLAGS.%s", against.c_str());
        c_draw+=Form("MultiSignal_FLAGS.%s*%f", against.c_str(),fScaleFactor);
        event_tree->Draw(Form("%s>>hnew", event_prop.c_str()), c_draw.c_str());
        TH1D* hnew = (TH1D*)gPad->GetPrimitive("hnew");
        TH1D* h_i = (TH1D*)hnew->Rebin(rebins.size()-1, "h_i", rebin);
        //h_i->Scale(fScaleFactor,"width");
        h_sig_vec.push_back(h_i);
        TObject* fr = event_tree->GetListOfFriends()->FindObject(Form("h_%d",i));
        event_tree->GetListOfFriends()->Remove(fr);
        hnew->Clear();
    }

    int plus_sig_index = int(num_of_throws*0.84);
    int minus_sig_index = int(num_of_throws*0.16);
    int central_val_index = int(num_of_throws*0.5);

    TH1D* error_band_SIGNAL=new TH1D("h1","h1", rebins.size()-1, rebin);
    int num_of_bins=error_band_SIGNAL->GetXaxis()->GetNbins();
    for(int bin=0; bin<num_of_bins; bin++){
        std::vector<double> bin_cont;
        for(int hist_int=1; hist_int<num_of_throws; hist_int++){
            bin_cont.push_back(h_sig_vec[hist_int]->GetBinContent(bin));
        }
        std::sort(bin_cont.begin(), bin_cont.end());
        double plus_sigma = bin_cont[plus_sig_index];
        double minus_sigma = bin_cont[minus_sig_index];
        double error = plus_sigma-minus_sigma;
        //double error_t[2] = {minus_sigma,plus_sigma};
        double central_val = bin_cont[central_val_index];
        error_band_SIGNAL->SetBinContent(bin, central_val);
        error_band_SIGNAL->SetBinError(bin, error);
        //error_band_SIGNAL->SetBinError(bin,plus_sigma);
        //error_band_SIGNAL->SetBinError(bin,minus_sigma);
    }
    return error_band_SIGNAL;
}


double SetHistRange(TH1D* Upper, TH1D* test_upper){
    double max_cont=0;
    for(int i=1; i<Upper->GetNbinsX()+1; i++){
        double upper_bin=Upper->GetBinContent(i);
        double test_bin=test_upper->GetBinContent(i);
        double current_largest;
        if(upper_bin>test_bin){
            current_largest=upper_bin;
        }
        else{
            current_largest=test_bin;
        }
        if(current_largest>max_cont){
            max_cont=current_largest;
        }
    }
    return max_cont;
}

double fractional_dif(TH1D* h_genie, TH1D* h_comp, int i){
    double frac_diff=(h_comp->GetBinContent(i)-h_genie->GetBinContent(i))/(h_genie->GetBinContent(i));
    if(h_genie->GetBinContent(i)==0){
        frac_diff=h_comp->GetBinContent(i)-h_genie->GetBinContent(i);
    }
    return frac_diff;
}
