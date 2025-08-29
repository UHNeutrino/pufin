#include <TFile.h>
#include <TH1D.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TStyle.h>
#include <TH2D.h>
#include <TMatrixD.h>
#include <TLegend.h>
#include <TCut.h>
#include <TLine.h>
#include <TColor.h>

#include <vector>
#include <algorithm>
#include <memory>

#include "draw_struct/Covariance.hh"
#include "draw_struct/DrawAgainst.hh"
// #include "draw_struct/BinningStruct.hh"

#include "user_int/Get_User_stuff.hh"

void CreateErrorBand_ALL(std::string userdata,
                    //std::string Throw_file, 
                    std::string Errorband_output, 
                    // std::string Against, std::string against_file_path, 
                    // std::string event_prop, 
                    int num_of_throws){


// TH1::SetDirectory(kFALSE);
// TTree::SetDirectory(KFALSE);
 //Grab everything needed
 std::cout << "[MM]:   Initialize variables " << std::endl;
 const int num_of_events=Get_Num_Events(userdata);
 const std::vector<std::vector<std::variant<std::string, std::vector<std::string>>>> path_and_syst = Get_Path_and_Syst(userdata);
 const std::vector<std::vector<std::variant<std::string, std::vector<double>>>> event_prop_and_binning = Get_Event_Property(userdata);
 const std::vector<std::pair<std::string,std::string>> Comparisons = Get_Comparisons(userdata);
 const std::vector<std::vector<std::string>> labels = Get_Labels(userdata);
 const std::vector<std::vector<std::string>> Groups = Get_Groups(userdata);
 const std::string flag = Get_Flag(userdata);
 
 std::vector<std::string> Throw_Files;
 std::vector<std::vector<std::string>> Syst_for_throw_file_old;
 std::vector<std::vector<std::string>> Syst_for_throw_file;
 std::vector<std::string> Groups_for_throw_file;
 std::vector<std::string> event_prop;
 std::vector<std::vector<double>> binning_struct;

 //sort nicely
 //Organize throw path and systematics
 std::cout << "[MM]:  Setup File paths, systematics, and groups " << std::endl;
 TFile* TFile_Throws[path_and_syst.size()];
 //std::cout << path_and_syst.size() << std::endl;
 for(int i=0; i<path_and_syst.size(); i++){
   std::cout << i << std::endl;
  Throw_Files.push_back(std::get<std::string>(path_and_syst[i][0]));
  //std::cout << Throw_Files[i] << std::endl;
  Syst_for_throw_file_old.push_back(std::get<std::vector<std::string>>(path_and_syst[i][1]));
  std::vector<std::string> temp;
  for(int j=1; j<Syst_for_throw_file_old[i].size(); j++){
    std::cout << j << std::endl;
    temp.push_back(Syst_for_throw_file_old[i][j]);
  }
  Syst_for_throw_file.push_back(temp);
  Groups_for_throw_file.push_back(Syst_for_throw_file_old[i][0]);
  TFile_Throws[i] = new TFile(Throw_Files[i].c_str(), "READ");
 }
 std::cout << "[MM]:   Setup event_properties and binnings " << std::endl;
 //Organize Event prop and binning
 for(int i=0; i<event_prop_and_binning.size(); i++){
  event_prop.push_back(std::get<std::string>(event_prop_and_binning[i][0]));
  binning_struct.push_back(std::get<std::vector<double>>(event_prop_and_binning[i][1]));
 }
 //Split up flags and comparison paths
 std::vector<std::string> Against;
 std::vector<std::string> against_file_path;
 for(int i=0; i<Comparisons.size(); i++){
  Against.push_back(Comparisons[i].first);
  against_file_path.push_back(Comparisons[i].second);
 }

 //std::string flag = Comparisons[0];
 //std::string Against=Comparisons[1];
 //std::string against_file_path=Comparisons[2];

 //Set up variables that will allow for Experimental or Generator 
 //bool is_gen=false;
 bool is_gen=true;
 bool is_flag=false;
 //if(RemoveHeader(Against,"")=="NEUT"|| RemoveHeader(Against,"")=="NuWro"){
  //is_gen=true;
  //std::cout << "Comparing with alternate Generator --> " << Against << std::endl;  
 //}
 if(RemoveHeader(flag,"")!="NONE"){
  is_flag=true;
  std::cout << "[MM]: Using flagging parameter --> " << flag << std::endl;
 }

 //std::cout << "[MM]: Using " << Against << " located file path at " << against_file_path << std::endl;
 std::cout << "[MM]: Drawing fallowing Event Kinematics with applyed flag of " << flag <<std::endl;
 for(int i=0; i< event_prop.size(); i++){
  std::cout << "   "<< i+1 << ". " << event_prop[i] << " --> bin_num="<< binning_struct[i][0] <<", min=" << binning_struct[i][1] << ", max=" << binning_struct[i][2] << std::endl;
 }
 std::cout << "[MM]: Number of throws processing == " << num_of_throws << std::endl;
 std::cout << "[MM]: Number of Events == " << num_of_events << std::endl;
 std::cout << "[MM]: Using " << Against.size() <<  " MC Studies and associated event records:" << std::endl;
 TFile* Against_TFile[Against.size()];
 for(int i=0; i<Against.size(); i++){
   Against_TFile[i] = new TFile(against_file_path[i].c_str(), "READ");
   std:cout << "      " << Against[i] << ",  " << against_file_path[i] << std::endl;
 }
 //std::cout << "create color pallate" << std::endl;
 //Create Color Pallete for TH2D
 Double_t Red[3]={0.00, 1.00, 1.00};
 Double_t Green[3] = {0.00, 1.00, 0.00};
 Double_t Blue[3] = {1.00, 1.00, 0.00};
 Double_t Length[3] = {0.00, 0.50, 1.00}; 
 Int_t th2d_color_range = 100;

 int color_range[6] = {1, 880, 880+8, 860+10, 432-7, 616-3};
 int color_errorband[3] = {600-9, 432-10, 632-9};
 std::vector<int> color_errorband_range;
 for(int i=0; i<Groups.size()-1; i++){
   color_errorband_range.push_back(color_errorband[i]);
 }
 color_errorband_range.push_back(632-9);
 //std::cout << "create base tfile" << std::endl;
 //std::cout << Throw_Files[0] << std::endl;
 //All unweighted histograms are the same, so just use the first one for weightless
 //TFile base_TFile(Throw_Files[0].c_str(), "READ");
 //std::cout << "base TFile made" << std::endl;
 auto base_events = std::unique_ptr<TTree>(static_cast<TTree*>(TFile_Throws[0]->Get("GenericFlux_Vectors_VARS")));
 //std::cout << "base TTree made" << std::endl;
//  base_events->SetDirectory(0); 
 //std::cout << "create files" << std::endl;
 //TFile* Against_TFile[Against.size()];
 std::vector<double> fScaleFactor;
 for(int i=0; i<Against.size(); i++){
   //std::cout << i << std::endl;
   //Against_TFile[i] = new TFile(against_file_path[i].c_str(), "READ");
   fScaleFactor.push_back(GetfScaleFactor(TFile_Throws[0], Against_TFile[i]));
   std::cout << Against[i] << " has a fScaleFactor of " << fScaleFactor[i] <<  std::endl;
 }
 //TFile Against_TFile(against_file_path.c_str());
 //auto against_events = std::unique_ptr<TTree>(static_cast<TTree*>(Against_TFile.Get("GenericFlux_Vectors_VARS")));

 //Get a proper fScaleFactor that tunes for generator exposure
//  double fScaleFactor=1.;
//  if(is_gen==true){
//   fScaleFactor=GetfScaleFactor(base_TFile, Against_TFile);
//  }

 //Create output file
 TFile Error_file(Errorband_output.c_str(), "RECREATE");

 //Now for each event property
 for(int event_prop_index=0; event_prop_index<event_prop.size(); event_prop_index++){
   
  std::vector<int> atrocious_throws; //list any bad throw

  auto h_ev = std::make_unique<TH1D>("h_ev","h_ev",binning_struct[event_prop_index][0],binning_struct[event_prop_index][1], binning_struct[event_prop_index][2]); //base hist
  if(is_flag==true){
  //   Float_t event_val;
  //   bool some_bool;
  //   base_events->SetBranchAddress(event_prop[event_prop_index].c_str(), &event_val);
  //   base_events->SetBranchAddress(flag.c_str(), &some_bool);
  //   int nentries = base_events->GetEntries();
  //   for(int i=0; i<nentries; i++){
  //     base_events->GetEntry(i);
  //     h_ev->Fill(1-(event_val*some_bool),1);
  base_events->Draw(Form("%s>>h_ev", event_prop[event_prop_index].c_str()), flag.c_str());
  //   }
  }
  else{
   base_events->Draw(Form("%s>>h_ev",event_prop[event_prop_index].c_str()));
  }


  TH1D* h_vec[Groups.size()][num_of_throws];
  //Loop through throws
  for(int x=0; x<Groups.size(); x++){
    std::vector<int> group_index;
    for(int z=0; z<Groups[x].size(); z++){
      //std::cout << x << " ---> " << Groups[x][z] << std::endl;
      //std::cout << Groups[x][z] <<std::endl;
      //int index = find(Groups_for_throw_file.begin(), Groups_for_throw_file.end(), Groups[x][z])-Groups_for_throw_file.begin();
      auto it = find(Groups_for_throw_file.begin(), Groups_for_throw_file.end(), Groups[x][z]);
      group_index.push_back(it-Groups_for_throw_file.begin());
      int stop_index=1;
      while(it!=Groups_for_throw_file.end()){
        it = find(it+stop_index, Groups_for_throw_file.end(), Groups[x][z]);
        if(it != Groups_for_throw_file.end()){
          group_index.push_back(it-Groups_for_throw_file.begin());
        }
      }
      //std::cout << index << std::endl;
    }
    for(int i=0; i<num_of_throws; i++){
      if(i%10==0){
        std::cout << "Throw: " << i << std::endl;
      }
      std::string c_draw="";
      //Loop through files
      //for(int j=0; j<Throw_Files.size(); j++){
      for(int j=0; j<group_index.size(); j++){
        //TFile_Throws[j]->Open();
        //std::cout << "ADDING FRIND TREE IN LOCATION " << Throw_Files[group_index[j]] << std::endl;
        base_events->AddFriend(Form("h_%d",i), TFile_Throws[group_index[j]]);//Throw_Files[j].c_str());
        //Loop through systematics in the file
        for(int k=0; k<Syst_for_throw_file[group_index[j]].size()-1; k++){
        c_draw+=Form("h_%d.%s*", i, Syst_for_throw_file[group_index[j]][k].c_str());
        }
        c_draw+=Form("h_%d.%s*", i, Syst_for_throw_file[group_index[j]][Syst_for_throw_file[group_index[j]].size()-1].c_str());
      }

      h_vec[x][i] = new TH1D(Form("hdraw_%d_%d",x,i), Form("hdraw_%d_%d",x,i), binning_struct[event_prop_index][0], binning_struct[event_prop_index][1], binning_struct[event_prop_index][2]);
      if(is_flag==true){
        c_draw+=Form("%s",flag.c_str());
        //std::cout << c_draw << std::endl;
        //std::cout << event_prop[event_prop_index].c_str() << std::endl;
        base_events->Draw(Form("%s>>hdraw_%d_%d", event_prop[event_prop_index].c_str(),x,i), c_draw.c_str());
      }
      else{
        c_draw.pop_back();
        base_events->Draw(Form("%s>>hdraw_%d_%d", event_prop[event_prop_index].c_str(),x,i), c_draw.c_str());
      }

      if(abs(h_vec[x][i]->GetMaximum())>num_of_events){
        atrocious_throws.push_back(i);
      }
      //std::cout << h_vec[x][i]->GetBinContent(3) << std::endl;
      for(int j=0; j<group_index.size(); j++){
        TObject* fr = base_events->GetListOfFriends()->FindObject(Form("h_%d",i));
        base_events->GetListOfFriends()->Remove(fr);
      }
      //for(int j=0; j<Throw_Files.size(); j++){
      //  TObject* fr = base_events->GetListOfFriends()->FindObject(Form("h_%d",i));
      //  base_events->GetListOfFriends()->Remove(fr);
      //}
    }
  }
  //Calculate +/- sigma
  int plus_sig_index = int(num_of_throws*0.84);
  int minus_sig_index = int(num_of_throws*0.16);
  int central_val_index = int(num_of_throws*0.5);
  std::vector<int> white_groups={0};
  TH1D* error_band_EV[Groups.size()];
  TH1D* error_band_PS[Groups.size()];
  TH1D* error_band_MS[Groups.size()];
  TH1D* error_band_CV[Groups.size()];
  for(int gr=0; gr<Groups.size(); gr++){
    error_band_EV[gr]=new TH1D(Form("error_band_EV_%d",gr), Form("error_band_EV_%d", gr), binning_struct[event_prop_index][0],binning_struct[event_prop_index][1], binning_struct[event_prop_index][2]);
    error_band_PS[gr]=(TH1D*)error_band_EV[gr]->Clone();
    error_band_MS[gr]=(TH1D*)error_band_EV[gr]->Clone();
    error_band_CV[gr]=(TH1D*)error_band_EV[gr]->Clone();
  }
  // TH1D* error_band_EV= new TH1D("error_band_EV", "error_band_EV", binning_struct[event_prop_index][0],binning_struct[event_prop_index][1], binning_struct[event_prop_index][2]);
  // TH1D* error_band_PS = (TH1D*)error_band_EV->Clone();
  // TH1D* error_band_MS = (TH1D*)error_band_EV->Clone();
  // TH1D* error_band_CV = (TH1D*)error_band_EV->Clone(); 
  for(int gr=0; gr<Groups.size(); gr++){
    for(int bin=1; bin<binning_struct[event_prop_index][0]+1; bin++){ //+2 for overflow
    std::vector<double> bin_cont;
    //bool is_outragious=false;
    for(int hist_int=0; hist_int<num_of_throws; hist_int++){
        int cnt = std::count(atrocious_throws.begin(), atrocious_throws.end(), hist_int);
        if(cnt==0){
          bin_cont.push_back(h_vec[gr][hist_int]->GetBinContent(bin));
        }
    }
    std::sort(bin_cont.begin(), bin_cont.end());
    double plus_sigma = bin_cont[plus_sig_index];
    double minus_sigma = bin_cont[minus_sig_index];
    double central_val = bin_cont[central_val_index];
    error_band_EV[gr]->SetBinContent(bin, h_ev->GetBinContent(bin));
    error_band_PS[gr]->SetBinContent(bin, plus_sigma);
    error_band_MS[gr]->SetBinContent(bin, minus_sigma);
    error_band_CV[gr]->SetBinContent(bin, central_val);
    //std::cout << "PS [" << bin << "] --> " << plus_sigma << std::endl;
    //std::cout << "CV [" << gr << "][" << bin << "] --> " << error_band_CV[gr]->GetBinContent(bin) << std::endl;
    }
  }
  // for(int i=0; i<error_band_CV[Groups.size()-1]->GetNbinsX(); i++){
  //   std::cout << "CV[" << i << "][" <<i<<"] --> " << error_band_CV[Groups.size()-1]->GetBinContent(i) << std::endl;
  //   std::cout << "EV[" << i << "][" <<i<<"] --> " << error_band_EV[Groups.size()-1]->GetBinContent(i) << std::endl;
  // }
  // std::cout << "################### CVVVVVVV ###################" << std::endl;

  TH1D* Against_hist[Comparisons.size()];
  if(is_gen==true){
    for(int i=0; i<Against.size(); i++){
      Against_hist[i]=DrawAgainst(Against_TFile[i], event_prop[event_prop_index], binning_struct[event_prop_index], flag, fScaleFactor[i], Against[i]);
      //std::cout << Against[i] << std::endl;
    }
  }

  //TCanvas c_genie(Form("GENIE_Errorband_%s",event_prop[event_prop_index].c_str()), "Errorband");
  gStyle->SetOptStat(0);

  //////st
  auto legend = new TLegend(0.75, 0.75, 1.0, 1.0);
  for(int i=0; i<Groups.size(); i++){
    error_band_PS[i]->SetFillColor(color_errorband_range[i]);
    //error_band_PS[i]->SetFillStyle(4050);
    // if(i<Groups.size()-1){
    //   error_band_MS[i]->SetFillColorAlpha(10,0.9);
    // }
    // else{
    //   error_band_MS[i]->SetFillColor(10);
    // }
    if(i==Groups.size()-1){
      error_band_MS[i]->SetFillColor(10);
    }
    else{
      error_band_MS[i]->SetFillColor(color_errorband_range[Groups.size()-1-i]);
    }
    error_band_CV[i]->SetLineColor(2);
    error_band_EV[i]->SetLineColor(4);
    error_band_PS[i]->SetLineColor(color_errorband_range[i]);
    error_band_MS[i]->SetLineColor(color_errorband_range[i]);
    error_band_PS[i]->SetLineWidth(3);
    error_band_MS[i]->SetLineWidth(3);
    error_band_CV[i]->SetLineWidth(3);
    error_band_EV[i]->SetLineWidth(3);
    error_band_EV[i]->SetLineStyle(9);
    error_band_PS[i]->SetTitle(labels[event_prop_index][0].c_str());
    error_band_PS[i]->GetXaxis()->SetTitle(labels[event_prop_index][1].c_str());
    error_band_PS[i]->GetYaxis()->SetTitle(labels[event_prop_index][2].c_str());
    if(i==Groups.size()-1){
      legend->AddEntry(error_band_CV[i], "Central Value of all throws", "l");
      legend->AddEntry(error_band_EV[i], "Event Spectrum (unweighted events)", "l");
    }
    std::string legend_groups;
    for(int x=0; x<Groups[i].size(); x++){
      legend_groups+=Groups[i][x];
      legend_groups+=", ";
    }
    legend->AddEntry(error_band_PS[i], Form("%s1#sigma errorband", legend_groups.c_str()), "f");
  }

  // error_band_PS->Draw("hist");
  // error_band_CV->Draw("hist&same");
  // error_band_MS->Draw("hist&same");
  // error_band_EV->Draw("hist&same");
  // legend->Draw();
  // Error_file.cd();
  // c_genie.Write();
  // c_genie.Close();

  //gStyle->SetOptStat(0);    
  //TCanvas c3(Form("Covariance_Matrix_%s",event_prop[event_prop_index].c_str()), "Covariance_Matrix"); 
  Error_file.cd();
  TCanvas c1(Form("Covariance_and_correlation_%d", event_prop_index), Form("Covariance_and_correlation_%d", event_prop_index));
  TPad* pad_pre = new TPad("pad_pre", "pad_pre", 0.05, 0.53, 0.97, 0.97);
  TPad* pad_post= new TPad("pad_post", "pad_post", 0.05, 0.05, 0.97, 0.47);
  pad_pre->Draw();
  pad_post->Draw();

  pad_pre->cd();
  auto pad_pre_cov = new TPad("pad_pre_cov","pad_pre_cov",0.0, 0.0, 0.47, 1.0);
  auto pad_pre_cor = new TPad("pad_pre_cor","pad_pre_cor",0.53, 0.0, 1.0, 1.0);
  pad_pre_cov->Draw();
  pad_pre_cor->Draw();
  std::vector<std::vector<double>> Cov_vec = Covariance_vec(h_vec[Groups.size()-1], num_of_throws, atrocious_throws);
  TMatrixD TCOV = Covariance(Cov_vec);
  TH2D cov(TCOV);
  pad_pre_cov->cd();
  cov.SetName("COV_2D");
  cov.GetXaxis()->SetTitle("bin number");
  cov.GetYaxis()->SetTitle("bin number");
  cov.SetTitle(Form("GENIE Covariance matrix: %s",labels[event_prop_index][1].c_str()));
  double max_cont=0;
  for(int i=1; i<cov.GetNbinsX()+1; i++){
  for(int j=1; j<cov.GetNbinsY()+1; j++){
   if(abs(cov.GetBinContent(i,j))>max_cont){
    max_cont=cov.GetBinContent(i,j);
   }
  }
  }
  cov.GetZaxis()->SetRangeUser(-1*max_cont, max_cont);
  TColor::CreateGradientColorTable(3,Length, Red, Green, Blue, th2d_color_range);
  cov.SetContour(th2d_color_range);
  cov.Draw("colz");
  //cov.Write();
  //c3.Write();
  //c3.Close();

  gStyle->SetOptStat(0);
  //TCanvas c5(Form("Correlation_Matrix_%s",event_prop[event_prop_index].c_str()), "Correlation_Matrix");
  TMatrixD TCOR = Corelation(Cov_vec);
  TH2D cor(TCOR);
  pad_pre_cor->cd();
  cor.GetXaxis()->SetTitle("bin number");
  cor.GetYaxis()->SetTitle("bin number");
  cor.SetTitle(Form("GENIE Correlation Matrix: %s", labels[event_prop_index][1].c_str()));
  cor.GetZaxis()->SetRangeUser(-1.0,1.0);
  TColor::CreateGradientColorTable(3,Length, Red, Green, Blue, th2d_color_range);
  cor.SetContour(th2d_color_range);
  cor.Draw("colz");
  //Error_file.cd();
  //c5.Write();
  //c5.Close();

  //TH1D* h_cloned = (TH1D*)error_band_CV->Clone("h_cloned");
  pad_post->cd();
  auto pad_post_cov = new TPad("pad_post_cov","pad_post_cov", 0.0, 0.0, 0.47, 1.);
  auto pad_post_cor = new TPad("pad_post_cor","pad_post_cor",0.53, 0.0, 1.0, 1.0);
  pad_post_cov->Draw();
  pad_post_cor->Draw();

  std::vector<TH1D*> h_cloned;
  h_cloned.push_back(dynamic_cast<TH1D*>(error_band_CV[Groups.size()-1]->Clone("h_cloned")));
  std::vector<std::vector<double>> new_cov_vec;
  std::vector<double> bin_edges_for_chi;
  std::vector<TMatrixD> COR_VEC;
  COR_VEC.push_back(TCOR);
  int old_size=TCOR.GetNrows();
  int new_size=1;
  while(TCOR.GetNrows()>1){
    std::vector<double> bin_edges_chi = new_bin_edges(COR_VEC[COR_VEC.size()-1],binning_struct[event_prop_index][1], binning_struct[event_prop_index][2],h_cloned[h_cloned.size()-1]);
    //std::cout << "bin edges size is now --> " << bin_edges_chi.size() << std::endl;
    double bin_edges_arr[bin_edges_chi.size()];
    copy(bin_edges_chi.begin(), bin_edges_chi.end(), bin_edges_arr);
    TH1D* h_rebins[num_of_throws];
    //std::cout << "rebin in progress" << std::endl;
    for(int i=0; i<num_of_throws; i++){
        h_rebins[i]=(TH1D*)(h_vec[Groups.size()-1][i]->Rebin(bin_edges_chi.size()-1, Form("h_new_%i", i), bin_edges_arr));
    }
    h_cloned.push_back(dynamic_cast<TH1D*>(error_band_CV[Groups.size()-1]->Rebin(bin_edges_chi.size()-1, "h_cloned", bin_edges_arr)));
    //std::cout << "crecreate covariance" << std::endl;
    std::vector<std::vector<double>> cov_new = Covariance_vec(h_rebins, num_of_throws, atrocious_throws);
    //std::cout << "crecreate correlation" << std::endl;
    COR_VEC.push_back(Corelation(cov_new));
    old_size=COR_VEC[COR_VEC.size()-2].GetNrows();
    new_size=COR_VEC[COR_VEC.size()-1].GetNrows();
    //std::cout << "new size of TCOR is" << new_size << std::endl;
    if(old_size==new_size){
      new_cov_vec=cov_new;
      bin_edges_for_chi=bin_edges_chi;
      for(int i=0; i<num_of_throws; i++){
        delete h_rebins[i];
      }
      break;
    }
  }
  TMatrixD New_Cov=Covariance(new_cov_vec);
  //TCanvas new_cov_c1(Form("UpdatedCovarianceMatrix_%s", event_prop[event_prop_index].c_str()),Form("UpdatedCovarianceMatrix_%s", event_prop[event_prop_index].c_str()));
  TH2D NEWWEST_COV(New_Cov);
  pad_post_cov->cd();
  NEWWEST_COV.SetTitle(Form("Updated Covariance Matrix: %s", labels[event_prop_index][1].c_str()));
  NEWWEST_COV.GetXaxis()->SetTitle("Bin number");
  NEWWEST_COV.GetYaxis()->SetTitle("Bin number");
  double max_cont_new=0;
  for(int i=1; i<NEWWEST_COV.GetNbinsX()+1; i++){
   for(int j=1; j<NEWWEST_COV.GetNbinsY()+1; j++){
    if(abs(NEWWEST_COV.GetBinContent(i,j))>max_cont_new){
     max_cont_new=abs(NEWWEST_COV.GetBinContent(i,j));
    }
   }
  }
  NEWWEST_COV.GetZaxis()->SetRangeUser(-1*max_cont, max_cont);
  //TColor::CreateGradientColorTable(3,Length, Red, Green, Blue, th2d_color_range);
  NEWWEST_COV.SetContour(th2d_color_range);
  NEWWEST_COV.Draw("colz");
  //new_cov_c1.Write();

  //TCanvas new_cor_c1(Form("UpdatedCorrMatrix:%s", event_prop[event_prop_index].c_str()),Form("UpdatedCorrMatrix:%s", event_prop[event_prop_index].c_str()));
  TH2D NEWWEST_COR(COR_VEC[COR_VEC.size()-1]);
  pad_post_cor->cd();
  NEWWEST_COR.SetTitle(Form("Updated Correlation Matrix: %s", labels[event_prop_index][1].c_str()));
  NEWWEST_COR.GetXaxis()->SetTitle("Bin number");
  NEWWEST_COR.GetYaxis()->SetTitle("Bin number");
  NEWWEST_COR.GetZaxis()->SetRangeUser(-1.0,1.0);
  NEWWEST_COR.SetContour(th2d_color_range);
  NEWWEST_COR.Draw("colz");
  //new_cor_c1.Write();
  c1.Write();

  New_Cov.SetTol(0.0000000000000001*New_Cov.GetTol());
  New_Cov.Invert();


  gStyle->SetOptStat(0);
  TCanvas c4(Form("GENIE_V_MCSTUDIE_%s",event_prop[event_prop_index].c_str()),Form("GENIE_V_MCSTUDIE_%s",event_prop[event_prop_index].c_str()),800,600);//(Form("Genie_V_%s_%s", Against.c_str(),event_prop[event_prop_index].c_str()), Form("Genie_V_%s", Against.c_str()));
  TPad* pad1 = new TPad("pad1", "pad1", 0.05,0.32,0.95,0.97);
  TPad* pad2 = new TPad("pad2","pad2",0.05,0.02,0.95,0.30);
  pad1->Draw();
  pad2->Draw();
  //error_band_PS[Groups.size()-1]->SetTitle(Form("MC Study comparison with GENIE errorband: %s", event_prop[event_prop_index].c_str()));//(Form("%s and %s" ,Against.c_str(), event_prop[event_prop_index].c_str()));
  double hist_max_yval=0;
  for(int i=0; i<Against.size(); i++){
    double cur_val=SetHistRange(error_band_PS[0],Against_hist[i])*1.2;
    if(cur_val>hist_max_yval){
      error_band_PS[Groups.size()-1]->GetYaxis()->SetRangeUser(0,SetHistRange(error_band_PS[Groups.size()-1],Against_hist[i])*1.2);
      hist_max_yval=cur_val;
    }
  }
  pad1->cd();
  for(int i=0; i<Groups.size(); i++){
    if(i==0){
      error_band_PS[Groups.size()-1-i]->Draw("hist");
      //error_band_PS[i]->Draw("hist");
    }
    else{
      error_band_PS[Groups.size()-1-i]->Draw("hist&same");
      //error_band_PS[i]->Draw("hist&same");
    }
    error_band_MS[Groups.size()-1-i]->Draw("hist&same");
    //error_band_MS[i]->Draw("hist&same");
  }
  //error_band_CV[Groups.size()-1]->Draw("hist&same");
  //error_band_EV[Groups.size()-1]->Draw("hist&same");
  error_band_CV[Groups.size()-1]->Draw("hist&same");
  error_band_EV[Groups.size()-1]->Draw("hist&same");
  error_band_MS[Groups.size()-1]->Draw("hist&same");

  for(int i=0; i<Against.size(); i++){
    // std::vector<double> bin_edges_for_chi = new_bin_edges(TCOR,binning_struct[event_prop_index][1], binning_struct[event_prop_index][2], error_band_CV, Against_hist[i]);
    // TMatrixD INVERTED_COV = Invert_Covariance(bin_edges_for_chi, h_vec, num_of_throws, atrocious_throws);
    Against_hist[i]->SetLineWidth(3);
    Against_hist[i]->SetLineColor(color_range[i]);
    Against_hist[i]->Draw("e0&same");
    double chi = Chi_square(error_band_CV[Groups.size()-1], Against_hist[i], New_Cov, bin_edges_for_chi);//h_vec, num_of_throws, atrocious_throws);//TCOV, TCOR);
    //double chi = Chi_square(error_band_CV, Against_hist[i]);
    legend->AddEntry(Against_hist[i], Form("%s: #chi^{2} = %.3f",Against[i].c_str(), chi), "le");
    // legend->AddEntry((TObject*)0, Form("#chi^{2}/d.o.f = %.2f/%d", chi, num_of_bins));
  }
  // TLine* bin_lines[bin_edges_for_chi.size()];
  // for(int i=0; i<bin_edges_for_chi.size(); i++){
  //   bin_lines[i] = new TLine(bin_edges_for_chi[i],0,bin_edges_for_chi[i], hist_max_yval);
  //   bin_lines[i]->SetLineWidth(3);
  //   bin_lines[i]->SetLineColor(432);
  //   bin_lines[i]->Draw("same");
  // }
  
  legend->Draw();
  gPad->RedrawAxis();

  pad2->cd();
  TH1D* frac_diff_cv[Groups.size()];// = (TH1D*)error_band_CV[0]->Clone();
  //frac_diff_cv->Clear("MICES");
  TH1D* frac_diff_ms[Groups.size()];// = (TH1D*)frac_diff_cv[0]->Clone();
  TH1D* frac_diff_ps[Groups.size()];// = (TH1D*)frac_diff_cv[0]->Clone();
  TH1D* frac_diff_ev[Groups.size()];// = (TH1D*)frac_diff_cv[0]->Clone();
  TH1D* frac_diff_against[Groups.size()][Against.size()];
  for(int gr=0; gr<Groups.size(); gr++){
    frac_diff_cv[gr] = (TH1D*)error_band_CV[0]->Clone();
    frac_diff_cv[gr]->Clear("MICES");
    frac_diff_ms[gr]=(TH1D*)frac_diff_cv[gr]->Clone();
    frac_diff_ps[gr]=(TH1D*)frac_diff_cv[gr]->Clone();
    frac_diff_ev[gr]=(TH1D*)frac_diff_cv[gr]->Clone();
    for(int i=0; i<Against.size(); i++){
      frac_diff_against[gr][i] = (TH1D*)frac_diff_cv[gr]->Clone();
    }
  }
  for(int gr=0; gr<Groups.size(); gr++){
    for(int i=0; i<Against.size(); i++){
      frac_diff_against[gr][i]->SetName(Form("%s_frac_dff", Against[i].c_str()));
      frac_diff_against[gr][i]->SetLineWidth(3);
      frac_diff_against[gr][i]->SetLineColor(color_range[i]);
    }
    for(int i=1; i<frac_diff_cv[gr]->GetNbinsX()+1; i++){
      frac_diff_ms[gr]->SetBinContent(i, fractional_dif(error_band_CV[gr], error_band_MS[gr], i));
      frac_diff_ps[gr]->SetBinContent(i, fractional_dif(error_band_CV[gr], error_band_PS[gr], i));
      frac_diff_ev[gr]->SetBinContent(i, fractional_dif(error_band_CV[gr], error_band_EV[gr], i));
      for(int j=0; j<Against.size(); j++){
        frac_diff_against[gr][j]->SetBinContent(i, fractional_dif(error_band_CV[gr], Against_hist[j], i));
      }
    }
    frac_diff_ps[gr]->SetFillColor(color_errorband_range[gr]);
    //frac_diff_ps[gr]->SetFillStyle(4050);
    frac_diff_ms[gr]->SetFillColor(color_errorband_range[gr]);//10);
    //frac_diff_ms[gr]->SetFillStyle(4050);
    frac_diff_cv[gr]->SetLineColor(2);
    frac_diff_ev[gr]->SetLineColor(4);
    frac_diff_ps[gr]->SetLineColor(color_errorband_range[gr]);
    frac_diff_ms[gr]->SetLineColor(color_errorband_range[gr]);
    frac_diff_ps[gr]->SetLineWidth(3);
    frac_diff_ms[gr]->SetLineWidth(3);
    frac_diff_cv[gr]->SetLineWidth(3);
    frac_diff_ev[gr]->SetLineWidth(3);
    frac_diff_ev[gr]->SetLineStyle(9);
    frac_diff_ps[gr]->GetYaxis()->SetTitle("fractional Diff from CV");
    frac_diff_ps[gr]->GetXaxis()->SetTitle(labels[event_prop_index][1].c_str());
    frac_diff_ps[gr]->GetXaxis()->SetLabelSize(0.07);
    frac_diff_ps[gr]->GetYaxis()->SetLabelSize(0.07);
    frac_diff_ps[gr]->GetXaxis()->SetTitleSize(0.2);
    frac_diff_ps[gr]->GetYaxis()->SetTitleSize(0.2);
    frac_diff_ps[gr]->GetYaxis()->ChangeLabel(2,-1,0);
    frac_diff_ps[gr]->GetYaxis()->ChangeLabel(4,-1,0);
    frac_diff_ps[gr]->GetYaxis()->ChangeLabel(6,-1,0);
    frac_diff_ps[gr]->GetYaxis()->ChangeLabel(8,-1,0);  
    // if(gr==0){
    //   for(int i=0; i<Against.size(); i++){
    //    frac_diff_ps[gr]->GetYaxis()->SetRangeUser(SetHistRange(frac_diff_ps[gr],frac_diff_against[gr][i])*(-1.2),SetHistRange(frac_diff_ps[gr],frac_diff_against[gr][i])*(1.2));
    //   }
    //   frac_diff_ps[gr]->Draw("hist");
    // }
    // else{
    //   frac_diff_ps[gr]->Draw("hist&same");
    // }
    // frac_diff_ms[gr]->Draw("hist&same");
    if(gr==Groups.size()-1){
      for(int i=0; i<Against.size(); i++){
       frac_diff_ps[gr]->GetYaxis()->SetRangeUser(SetHistRange(frac_diff_ps[gr],frac_diff_against[gr][i])*(-1.2),SetHistRange(frac_diff_ps[gr],frac_diff_against[gr][i])*(1.2));
      }      
      // for(int i=0; i<Against.size(); i++){
      //   frac_diff_against[gr][i]->Draw("hist&same");
      // }
    }
  }
  for(int gr=0; gr<Groups.size(); gr++){
    if(gr==0){
      frac_diff_ps[Groups.size()-1-gr]->Draw("hist");
    }
    else{
      frac_diff_ps[Groups.size()-1-gr]->Draw("hist&same");
    }
    frac_diff_ms[Groups.size()-1-gr]->Draw("hist&same");
  }
  for(int i=0; i<Against.size(); i++){
    frac_diff_against[Groups.size()-1][i]->Draw("hist&same");
  }


  //for(int i=0; i<Against.size(); i++){
  //  frac_diff_ps->GetYaxis()->SetRangeUser(SetHistRange(frac_diff_ps,frac_diff_against[i])*(-1.2),SetHistRange(frac_diff_ps,frac_diff_against[i])*(1.2));
  //}
  // frac_diff_ps->SetFillColor(632-9);
  // frac_diff_ms->SetFillColor(632-9);//10);
  // frac_diff_cv->SetLineColor(2);
  // frac_diff_ev->SetLineColor(4);
  // frac_diff_ps->SetLineColor(632-9);
  // frac_diff_ms->SetLineColor(632-9);
  // frac_diff_ps->SetLineWidth(3);
  // frac_diff_ms->SetLineWidth(3);
  // frac_diff_cv->SetLineWidth(3);
  // frac_diff_ev->SetLineWidth(3);
  // frac_diff_ev->SetLineStyle(9);
  TLine* cv_line = new TLine(binning_struct[event_prop_index][1], 0, binning_struct[event_prop_index][2], 0);
  cv_line->SetLineColor(2);
  cv_line->SetLineWidth(3);
  // frac_diff_ps->GetYaxis()->SetTitle("fractional Diff from CV");
  // frac_diff_ps->GetXaxis()->SetTitle(labels[event_prop_index][1].c_str());
  // frac_diff_ps->GetXaxis()->SetLabelSize(0.07);
  // frac_diff_ps->GetYaxis()->SetLabelSize(0.07);
  // frac_diff_ps->GetXaxis()->SetTitleSize(0.2);
  // frac_diff_ps->GetYaxis()->SetTitleSize(0.2);
  // frac_diff_ps->GetYaxis()->ChangeLabel(2,-1,0);
  // frac_diff_ps->GetYaxis()->ChangeLabel(4,-1,0);
  // frac_diff_ps->GetYaxis()->ChangeLabel(6,-1,0);
  // frac_diff_ps->GetYaxis()->ChangeLabel(8,-1,0);
  //frac_diff_ps->Draw("hist");
  //frac_diff_ms->Draw("hist&same");
  cv_line->Draw("same");
  //frac_diff_cv->Draw("hist&same");
  //frac_diff_ev->Draw("hist&same");
  //for(int i=0; i<Against.size(); i++){
  //  frac_diff_against[i]->Draw("hist&same");
  //}
  gPad->RedrawAxis();
  c4.Update();
  //branch4->Fill();
  Error_file.cd();
  c4.Write();
  c4.Close();

  for(int i=0; i<Groups.size(); i++){
    delete error_band_PS[i];
    delete error_band_MS[i];
    delete error_band_CV[i];
    delete error_band_EV[i];
    for(int j=0; j<num_of_throws; j++){
      delete h_vec[i][j];
    }
  }
  for(int i=0; i<Against.size(); i++){
   delete Against_hist[i];
  }
  COR_VEC.clear();
  // delete frac_diff_ps;
  // delete frac_diff_ms;
  // delete frac_diff_cv;
  // delete frac_diff_ev;
  // for(int i=0; i<Against.size(); i++){
  //   delete frac_diff_against[i];
  // }
  //delete cv_line;
  //delete legend;
  //delete pad1;
  //delete pad2;

 }


}