#include <vector>
#include <TH1D.h>
#include <TMatrixD.h>
#include <TArrayD.h>
#include <cmath>

std::vector<std::vector<Double32_t>> Covariance_vec (TH1D* hist_vec[], int num_throws, std::vector<int> bad_throws) {
    //std::cout << "Get Bin Cont" << std::endl;
    std::vector<std::vector<Double32_t>> Bin_cont_all_throws;
    //int num_throws=num_of_throws-bad_throws.size();
    //std::cout << num_of_throws << " MINUS " << bad_throws.size() << std::endl;
    for(int throw_num=0; throw_num<num_throws; throw_num++){
        int cnt=std::count(bad_throws.begin(), bad_throws.end(), throw_num);
        //std::cout << cnt << std::endl;
        if(cnt==0){
            int num_of_bins = hist_vec[throw_num]->GetXaxis()->GetNbins();
            std::vector<Double32_t> bin_cont_for_throw;
            for(int bin_num=1; bin_num<num_of_bins+1; bin_num++){//grabs opverflow
                bin_cont_for_throw.push_back(hist_vec[throw_num]->GetBinContent(bin_num));
            }
            Bin_cont_all_throws.push_back(bin_cont_for_throw);
        }
    }

    int num_bins = Bin_cont_all_throws[0].size();
    int new_num_throws = num_throws-bad_throws.size();

    //std::cout << "Zero the Cov Mat" << std::endl;
    std::vector<std::vector<Double32_t>> Cov_mat;
    for(int i=0; i<num_bins; i++){
        std::vector<Double32_t> zeros;
        for(int j=0; j<num_bins; j++){
            zeros.push_back(0.0);
        }
        Cov_mat.push_back(zeros);
    }

    std::vector<Double32_t> column_mean;
    //std::cout << "Gen Column mean" << std::endl;
    //std::cout << new_num_throws  << "----->"<< Bin_cont_all_throws.size() << std::endl;
    for(int i=0; i<num_bins; i++){
        Double32_t currrent_mean=0;
        //std::cout << i << std::endl;
        for(int j=0; j<new_num_throws; j++){
            //std::cout << j << std::endl;
            currrent_mean+=Bin_cont_all_throws[j][i];
        }
        currrent_mean/=new_num_throws;
        //std::cout << currrent_mean << std::endl;
        column_mean.push_back(currrent_mean);
    }
    
    //std::cout << "calculate covariance" << std::endl;
    for(int k=0; k<new_num_throws; k++){
        for(int i=0; i<num_bins; i++){
            for(int j=0; j<num_bins; j++){
                //echk if column means are 0, causes problems
                if(column_mean[i]!=0 && column_mean[j]!=0){
                    Cov_mat[i][j]+=((Bin_cont_all_throws[k][i]-column_mean[i])*(Bin_cont_all_throws[k][j]-column_mean[j]))/(column_mean[i]*column_mean[j]);
                    //std::cout << Cov_mat[i][j] << std::endl;
                }
                else{
                    if(column_mean[i]==0){
                        //  std::cout << "#####################################" << std::endl;
                        //  std::cout << "  [MM]: Bin content of 0 at bin " << i << std::endl;
                        //  std::cout << "#####################################" << std::endl;
                    }
                    //Cov_mat[i][j]+=(Bin_cont_all_throws[k][i]-column_mean[i])*(Bin_cont_all_throws[k][j]-column_mean[j]);
                }
            }
        }
    }
    for(int i=0; i<Cov_mat.size(); i++){
        for(int j=0; j<Cov_mat.size(); j++){
            //std::cout << Cov_mat[i][j] << std::endl;
            Cov_mat[i][j]/=new_num_throws;
            if(i==j){
                //std::cout << Cov_mat[i][j] << std::endl;
            }
        }
    }
    return Cov_mat;
}

TMatrixD Covariance(std::vector<std::vector<double>> cov_vec){
    TMatrixD TCov_matrix(cov_vec.size(), cov_vec[0].size());
    TArrayD cov_in_array(cov_vec.size()*cov_vec[0].size());
    //std::cout << "Set up done " << std::endl;
    int index=0;
    for(int i=0; i<cov_vec.size(); i++){
        for(int j=0; j<cov_vec[i].size(); j++){
            if(sqrt(cov_vec[i][i]*cov_vec[j][j])!=0){
                cov_in_array.AddAt(cov_vec[i][j], index);///sqrt(Cov_mat[i][i]*Cov_mat[j][j]), index);
            }
            else{
                cov_in_array.AddAt(0, index);
            }

            index++;
        }
    }
    //std::cout << "done" << std::endl;
    TCov_matrix.SetMatrixArray(cov_in_array.GetArray());
    return TCov_matrix;
}


TMatrixD Corelation(std::vector<std::vector<double>> cov_vec){
    TMatrixD TCov_matrix(cov_vec.size(), cov_vec[0].size());
    TArrayD cov_in_array((cov_vec.size())*(cov_vec[0].size()));
    //std::cout << "Set up done " << std::endl;
    int index=0;
    for(int i=0; i<cov_vec.size(); i++){
        for(int j=0; j<cov_vec[i].size(); j++){
            if(sqrt(cov_vec[i][i]*cov_vec[j][j])!=0){
                cov_in_array.AddAt(cov_vec[i][j]/sqrt(cov_vec[i][i]*cov_vec[j][j]), index);
            }
            else{
                cov_in_array.AddAt(0, index);
            }
            if(i==j){
                //std::cout << cov_vec[i][j]/sqrt(cov_vec[i][i]*cov_vec[j][j]) << std::endl;
            }
            index++;
        }
    }
    //std::cout << "done" << std::endl;
    TCov_matrix.SetMatrixArray(cov_in_array.GetArray());
    return TCov_matrix;

}

std::vector<double> new_bin_edges(TMatrixD& cor, double bin_min, double bin_max, TH1D* h_1){
    
    std::vector<double> bin_edges = {bin_min};
    for(int j=1; j<cor.GetNrows(); j++){
        TMatrixDRow row(cor,j);
        bool merge = false;
        if(row(j-1)>0.99 && row(j)>0.99){
            merge = true;
        }
        if(merge==true){
            if(j+1<h_1->GetNbinsX()){
                bin_edges.push_back(h_1->GetBinLowEdge(j+1+1));
                j++;
            }
        }
        else{
            bin_edges.push_back(h_1->GetBinLowEdge(j+1));
        }
    }
    bin_edges.push_back(bin_max);

    return bin_edges;
}

//     double bin_edges_arr[bin_edges.size()];
//     copy(bin_edges.begin(), bin_edges.end(), bin_edges_arr);

//     h_cloned->Rebin(bin_edges.size()-1, Form("h_clone_rebin"), bin_edges_arr);
//     TH1D* h_rebins[num_of_throws];
//     for(int i=0; i<num_of_throws; i++){
//         //std::cout << i << std::endl;
//         //std::cout << "x" < std::endl;
//         h_rebins[i]=(TH1D*)(h_vec[i]->Rebin(bin_edges.size()-1, Form("h_new_%i", i), bin_edge_arr));
//         //std::cout << i << std::endl;
//     }

//     std::vector<std::vector<double>> cov_new = Covariance_vec(h_rebins, num_of_throws, bad_throws);
//     return cov_new;
// }

// std::vector<double> new_bin_edges(TMatrixD& cor, double bin_min, double bin_max, TH1D* h1, TH1D* h2){
        
//     std::vector<std::vector<int>> bin_num_cor_all;
//     for(int j=0; j<cor.GetNrows(); j++){    
//         TMatrixDRow row(cor,j);
//         std::vector<int> bin_num_cor;
//         bin_num_cor.push_back(1);
//         bool below_99=false;
//         bool above_99=false;
//         for(int i=1; i<cor.GetNrows()-1; i++){
//             //std::cout << "The correlation at i is -->" << row(i) << std::endl;
//             if(row(i)>0.999 && row(i+1)>0.999){
//                 above_99=true;
//                 below_99=false;
//             }
//             if(row(i+1)<0.999 && above_99==true){
//                 bin_num_cor.push_back(i+1);
//                 //std::cout << "bin added --> " << i+1 << std::endl;
//                 above_99=false;
//             }
//             if(row(i)<0.999 && row(i+1)<0.999){
//                 below_99=true;
//                 above_99=false;
//             }
//             if(row(i+1)>0.999 && below_99==true){
//                 bin_num_cor.push_back(i+1);
//                 //std::cout << "bin added --> " << i+1 << std::endl;
//                 below_99=false;
//             }
//             // if(row(i)>0.98 && row(i+1)>0.98){
//             //     above_99=true;
//             // }
//             // else{
//             //     bin_num_cor.push_back(i+1);
//             // }
//         }
//         bin_num_cor_all.push_back(bin_num_cor);
//     }

//     // std::vector<int> bin_num_frac;
//     // bin_num_frac.push_back(1);
//     // bool swtich=false;
//     // double current_value;
//     // double next_value;
//     // for(int i=1; i<h1->GetBinContent(i); i++){
//     //     current_value = (h2->GetBinContent(i)-h1->GetBinContent(i))/(h1->GetBinContent(i));
//     //     next_value = (h2->GetBinContent(i+1)-h1->GetBinContent(i+1))/(h1->GetBinContent(i));
    
//     //     if(current_value>0.1 && next_value>0.1){
//     //         bin_num_frac.push_back(i+1);
//     //     }
//     //     // if((current_value<0 && next_value>0) || (current_value>0 && next_value<0)){
//     //     //     bin_num_frac.push_back(i+1);
//     //     // }
//     // }
//     std::vector<int> bin_num;
//     int bin_with_most_indep=0;
//     int size_of_idep_bins=bin_num_cor_all[0].size();
//     for(int i=1; i<bin_num_cor_all.size(); i++){
//         if(size_of_idep_bins>bin_num_cor_all[i].size()){
//             size_of_idep_bins=bin_num_cor_all[i].size();
//             bin_with_most_indep=i;
//         }        
//     }
//     bin_num=bin_num_cor_all[bin_with_most_indep];
//     //if(bin_num_cor.size()>bin_num_frac.size()){
//         //bin_num=bin_num_cor;
//     //}
//     // else{
//     //     bin_num=bin_num_frac;
//     // }

//     std::vector<double> bin_edges;
//     for(int i=1; i<h1->GetNbinsX()+1; i++){
//         if(std::count(bin_num.begin(), bin_num.end(), i)){
//             bin_edges.push_back(h1->GetBinLowEdge(i));
//         }
//     }
//     bin_edges.push_back(bin_max);
//     std::cout << bin_edges.size() << std::endl;
//     for(int i=0; i<bin_edges.size(); i++){
//         std::cout << "using bin edge --> " << bin_edges[i] << std::endl;
//     }

//     return bin_edges;
// }





// TMatrixD Invert_Covariance(std::vector<double> bin_edges, TH1D* h_vec[], int num_of_throws, std::vector<int> bad_throws){
//     std::cout << "Invert Matrix " << std::endl;
//     double bin_edge_arr[bin_edges.size()];
//     copy(bin_edges.begin(), bin_edges.end(), bin_edge_arr);

//     TH1D* h_rebins[num_of_throws];
//     for(int i=0; i<num_of_throws; i++){
//         //std::cout << i << std::endl;
//         //std::cout << "x" < std::endl;
//         h_rebins[i]=(TH1D*)(h_vec[i]->Rebin(bin_edges.size()-1, Form("h_new_%i", i), bin_edge_arr));
//         //std::cout << i << std::endl;
//     }
//     // for(int i=1; i<h_rebins[0]->GetNbinsX()+1; i++){
//     //     std::cout << "New bin "<< i << " has ===  " << h_rebins[0]->GetBinContent(i) << std::endl;
//     // }
//     std::cout << "create new TCov" << std::endl;
//     std::vector<std::vector<double>> cov_new = Covariance_vec(h_rebins, num_of_throws, bad_throws);
//     TMatrixD cov_TMD_noI = Covariance(cov_new);
//     cov_TMD_noI.SetTol(0.000000000000001*cov_TMD_noI.GetTol());
//     TMatrixD cov_TMD = cov_TMD_noI.Invert();

//     for(int i=0; i<num_of_throws; i++){
//         delete h_rebins[i];
//     }


//     return cov_TMD;
// }

Double32_t Chi_square(TH1D* h1, TH1D* h2, TMatrixD& cov, std::vector<double> bin_edges){
    std::vector<double> diff_arr;
    double h1_current_count=0.0;
    double h2_current_count=0.0;
    for(int i=1; i<h1->GetNbinsX()+1; i++){
        h1_current_count+=h1->GetBinContent(i);
        h2_current_count+=h2->GetBinContent(i);
        if(i>1){
            if(count(bin_edges.begin(), bin_edges.end(), h1->GetBinLowEdge(i))>0){
                diff_arr.push_back((h2_current_count-h1_current_count)/(h1_current_count));
                //std::cout << "diff arr value is " << diff_arr[diff_arr.size()-1] << std::endl;
                h1_current_count=0.0;
                h2_current_count=0.0;
            }
            if(i==h1->GetNbinsX()){
                if(h1_current_count!=0){
                    diff_arr.push_back((h2_current_count-h1_current_count)/(h1_current_count));
                    //td::cout << "diff arr value is " << diff_arr[diff_arr.size()-1] << std::endl;
                }
            }
        }
    }
    //std::cout << "SIZE OF COV IS " <<  cov.GetNrows() << " AND SIZE OF DIFF ARR " << diff_arr.size() << std::endl;
    std::vector<double> first_opp;
    for(int i=0; i<diff_arr.size(); i++){
        TMatrixDRow row(cov,i);
        double comp_sum=0;
        //std::cout << " new new new new new new " << std::endl;
        for(int j=0; j<diff_arr.size(); j++){
            comp_sum+=row(j)*diff_arr[j];
            //std::cout << row(j) << std::endl;
        }
        //std::cout << comp_sum/diff_arr.size() << std::endl;
        first_opp.push_back(comp_sum/diff_arr.size());
    }

    double chi=0;
    for(int i=0; i<diff_arr.size(); i++){
        chi+=first_opp[i]*diff_arr[i];
        std::cout << "CHI^2 AT i==" << i << " === "  << chi << std::endl;
    }
    chi/=first_opp.size();
    return chi;

}

double Chi_square(TH1D* h1, TH1D* h2){
    std::vector<double> diff_arr;
    for(int i=1; i<h1->GetNbinsX()+1; i++){
        diff_arr.push_back((h2->GetBinContent(i)-h1->GetBinContent(i))/(h1->GetBinContent(i)));
    }
    std::vector<int> something={};
    int num_of_throws=1;
    TH1D* temp_vec[2] = {h1,h2};
    std::vector<std::vector<double>> cov_vec = Covariance_vec(temp_vec, num_of_throws, something);
    TMatrixD cov = Covariance(cov_vec);
    cov.Invert();

    std::vector<double> first_opp;
    for(int i=0; i<diff_arr.size(); i++){
        TMatrixDRow row(cov,i);
        double comp_sum=0;
        //std::cout << " new new new new new new " << std::endl;
        for(int j=0; j<diff_arr.size(); j++){
            comp_sum+=row(j)*diff_arr[j];
            std::cout << row(j) << std::endl;
        }
        //std::cout << comp_sum/diff_arr.size() << std::endl;
        first_opp.push_back(comp_sum);///diff_arr.size());
    }

    double chi=0;
    for(int i=0; i<diff_arr.size(); i++){
        chi+=first_opp[i]*diff_arr[i];
        std::cout << "CHI^2 AT i==" << i << " === "  << chi << std::endl;
    }
    return chi;

}
//, TMatrixD& cor_d){ //TH1D* h_vec[], int num_of_throws, std::vector<int> bad_throws){//TMatrixD& cov, TMatrixD& cor){
    
    // int size_of_stuff=h1->GetNbinsX()-1; //-0 if including overflow
    // double diff_arr[size_of_stuff];
    // for(int i=1; i<size_of_stuff+1; i++){
    //     double frac_diff=(h2->GetBinContent(i)-h1->GetBinContent(i))/h1->GetBinContent(i);
    //     double nieghbor_frac=(h2->GetBinContent(i+1)-h1->GetBinContent(i+1))/h1->GetBinContent(i+1);
    //     if(nieghbor_frac<0.1 && frac_diff<0.1){
    //         diff_arr[i-1]=(h2->GetBinContent(i)+h2->GetBinContent(i+1)-h1->GetBinContent(i)-h1->GetBinContent(i+1))/(h1->GetBinContent(i)+h1->GetBinContent(i+1));
    //     }
    //     else{
    //         diff_arr[i-1]=frac_diff;
    //     }
    // }

    // double cov_new[size_of_stuff][size_of_stuff];
    // for(int i=0; i<size_of_stuff; i++){
    //     TMatrixDRow cor_row(cor_d, i);
    //     TMatrixDRow cov_row(cov_d, i);
    //     for(int j=0; j<i+1; j++){//cov_d.GetNcols()-1; j++){
    //         if(cor_row(j)>0.99 && cor_row(j+1)>0.99){
    //             TMatrixDRow find_jj(cov_d, j+1);
    //             if(i==j){
    //                 cov_new[i][j]=cov_row(j)+find_jj(j+1)-cov_row(j+1)-find_jj(j);
    //             }
    //             else{
    //                 cov_new[i][j]=cov_row(j)+cov_row(j+1);
    //             }
    //             cov_new[j][i]=cov_new[i][j];
    //         }
    //         else{
    //             cov_new[i][j]=cov_row(j);
    //             cov_new[j][i]=cov_new[i][j];
    //         }
    //         std::cout << i << "," << j << "==" << cov_new[i][j] << " --> ";
    //     }
    //     std::cout << "" << std::endl;
    // }

    // std::vector<std::vector<double>> cov_vec;
    // for(int i=0; i<size_of_stuff; i++){
    //     std::vector<double> temp;
    //     for(int j=0; j<size_of_stuff; j++){
    //         temp.push_back(cov_new[i][j]);
    //         if(i==0 && j==11){
    //             std::cout << "Cov 1,11 === "<< cov_new[i][j] << std::endl;
    //         }
    //     }
    //     cov_vec.push_back(temp);
    // }
    // TMatrixD cov = Covariance(cov_vec);
    // cov.SetTol(0.0000000000000001*cov.GetTol());
    // cov.Invert();

    // double first_opp[size_of_stuff];
    // for(int i=0; i<size_of_stuff; i++){
    //     TMatrixDRow row(cov,i);
    //     double comp_sum=0;
    //     for(int j=0; j<size_of_stuff; j++){
    //         comp_sum+=row(j)*diff_arr[j];
    //         std::cout << "Cov_"<< i << ", "<< j << " = " << row(j) << " and diff is"<< diff_arr[j] << " --> Contributing :: " << row(j)*diff_arr[j] << std::endl;
    //     }
    //     first_opp[i]=comp_sum;
    // }
    // double chi=0;
    // for(int i=0; i<size_of_stuff; i++){
    //     chi+=first_opp[i]*diff_arr[i];
    //     std::cout << "first matrix calc == " << first_opp[i] << "; AND DIFF [ARR] <<" << diff_arr[i] << "::::: CHI^2 AT i==" << i << " === "  << chi << std::endl;
    // }
    // std::cout << "CHI IS =====" << chi << std::endl;
    // return chi;




    // double first_opp[h1->GetNbinsX()-1];
    // for(int i=0; h1->GetNbinsX()-1; i++){
    //     double comp_sum=0;
    //     for(int j=0; h1->GetNbinsX()-1; j++){
    //         comp_sum=
    //     }
    // }

     //     for(int j=0; j<diff_vec.size(); j++){
    //         comp_sum+=row(j)*diff_vec[j];
    //         std::cout << "Cov_"<< i << ", "<< j << " = " << row(j) << " and diff is"<< diff_vec[j] << " --> Contributing :: " << row(j)*diff_vec[j] << std::endl;
    //     }
    //     first_opp.push_back(comp_sum);
    // }
    // double chi=0;
    // for(int i=0; i<diff_vec.size(); i++){
    //     chi+=first_opp[i]*diff_vec[i];
    //     std::cout << "first matrix calc == " << first_opp[i] << "; AND DIFF [ARR] <<" << diff_vec[i] << "::::: CHI^2 AT i==" << i << " === "  << chi << std::endl;
    // }
    // std::cout << "CHI IS =====" << chi << std::endl;
    // return chi;

    // double chi=0;
    // return chi;


    //Invert Covaraiabce first, combined bins that are close to 1
    // std::vector<std::vector<double>> new_cov;
    // int rows=cov.GetNrows();
    // int cols=cov.GetNcols();
    // std::vector<double> temp_cov_row;
    // for(int i=0; i<rows-1; i++){
    //     TMatrixDRow row_cor(cor, i);
    //     //TMatrixDColumn col_cor(cor, i);
    //     TMatrixDRow row_cov(cov, i);
    //     for(int j=0; j<cols-1; j++){
    //         if(row_cor(j)>0.999 && row_cor(j+1)){
    //             TMatrixDRow find_jj(cov, j+1);
    //             temp_cov_row.push_back(row_cov(i)+find_jj(j)-2*row_cov(j));
    //         }
    //         else{
    //             temp_cov_row.push_back(row_cov(j));
    //         }
    //     }
    //     new_cov.push_back(temp_cov_row);
    // }
    // double new_cov[20][20];
    // int rows=cov.GetNrows();
    // int cols=cov.GetNcols();
    // // std::vector<double> temp_cov_row;
    // for(int i=0; i<rows-1; i++){
    //     TMatrixDRow row_cor(cor, i);
    //     TMatrixDColumn col_cor(cor, i);
    //     for(int j=0; j<i; j++){
    //         if(row_cor(j)>0.999 && row_cor(j+1)){
    //             TMatrixDRow find_jj(cov, j+1);
    //             TMatrixDRow find_ii(cov, j);
    //             new_cov[i][j]=find_ii(j)+find_jj(j+1)-2*row_cov(j);
    //             new_cov[j][i]=new_cov[i][j];
                
    //         }
    //         else{
    //             new_cov[i][j]=111111;
    //         }

    //     }
    // }
    //     //TMatrixDColumn col_cor(cor, i);
    //     TMatrixDRow row_cov(cov, i);
    //     for(int j=0; j<cols-1; j++){
    //         if(row_cor(j)>0.999 && row_cor(j+1)){
    //             TMatrixDRow find_jj(cov, j+1);
    //             temp_cov_row.push_back(row_cov(i)+find_jj(j)-2*row_cov(j));
    //         }
    //         else{
    //             temp_cov_row.push_back(row_cov(j));
    //         }
    //     }
    //     new_cov.push_back(temp_cov_row);
    // }

    // for(int i=0; i<cov.GetNrows(); i++){
    //     TMatrixDRow row_cor(cor, i);
    //     TMatrixDRow row_cov(cov, i);
    //     // double current_binning_cor_val=row_cor(0);
    //     // double current_cov_val=row_cov(0);
    //     bool nieghbor=false;
    //     std::vector<double> temp_cov_row;
    //     for(int j=0; j<cov.GetNcols(); j++){
    //         std::cout << row_cor(j) << std::endl;
    //         if(row_cor(j)>0.9990 && row_cor(j+1)>0.9990){
    //             TMatrixDRow find_j(cov, j+1);
    //             temp_cov_row.push_back(row_cov(i)+find_j(j)-2*row_cov(j));
    //             j++;
    //         }
    //         else{
    //             temp_cov_row.push_back(row_cov(j));
    //         }
    //         // if(row_cor(j)>0.99 && current_binning_cor_val>0.99){
    //         //     current_binning_cor_val+=row_cor(j);
    //         // }
    //         // else{
    //         //     temp_cov_row.push_back(current_cov_val);
    //         //     std::cout << current_cov_val << std::endl;
    //         //     current_cov_val=0;
    //         //     current_binning_cor_val=0;
    //     }
    //     new_cov.push_back(temp_cov_row);
    // }

    // for(int i=0; i<new_cov.size(); i++){
    //     std::cout <<"cov["<< i<< "].size()=" << new_cov[i].size() << std::endl;
    //     for(int j=0; j<new_cov.size(); j++){
    //         std::cout << new_cov[i][j] <<",   ";
    //     }
    //     std::cout << " "<< std::endl;
    // }

    // double chi=0;
    // return chi;

    // DOESNT WORK
    // std::vector<double> first_opp;
    // TMatrixD cov = cov_d.Invert();
    // for(int i=0; i<diff_arr.size(); i++){
    //     TMatrixDRow row(cov,i);
    //     double comp_sum=0;
    //     std::cout << " new new new new new new " << std::endl;
    //     for(int j=0; j<diff_arr.size(); j++){
    //         comp_sum+=row(j)*diff_arr[j];
    //         std::cout << row(j) << std::endl;
    //     }
    //     std::cout << comp_sum/diff_arr.size() << std::endl;
    //     first_opp.push_back(comp_sum/diff_arr.size());
    // }

    // double chi=0;
    // for(int i=0; i<diff_arr.size(); i++){
    //     chi+=first_opp[i]*diff_arr[i];
    //     std::cout << "CHI^2 AT i==" << i << " === "  << chi << std::endl;
    // }
    // return chi;


    // std::vector<double> diff_arr;
    // for(int i=1; i<h1->GetNbinsX()+1; i++){
    //     if(h2->GetBinContent(i)!=0){
    //         diff_arr.push_back((h2->GetBinContent(i)-h1->GetBinContent(i))/(h1->GetBinContent(i)));
    //         //std::cout << (h1->GetBinContent(i)-h2->GetBinContent(i))/(h2->GetBinContent(i)) << std::endl;
    //     }
    //     else{
    //         diff_arr.push_back(h2->GetBinContent(i)-h1->GetBinContent(i));
    //     }
    // }
    
    // std::vector<double> first_opp;
    // cov_d.SetTol(0.0000000000000001*cov_d.GetTol());
    // cout<<"cov det = "<<cov_d.Determinant()<<endl;
    // TMatrixD cov(cov_d.GetNrows(), cov_d.GetNcols());
    // if(cov_d.Determinant()>0.001){
    //   cov = cov_d.Invert();//cov_d.Determinant());
    // }
    // else{//use the pseduo inverse
    //     cout<<"Take SVD of cov_d"<<endl;
    //     TDecompSVD A(cov_d); // covMatrix is a TMatrixD or a TMatrixDSym
    //     cout<<"invert the SVD"<<endl;
    //     A.Decompose();
    //     cov = A.Invert();
    //     cout << "CONDITION ----> " << A.Condition() << std::endl;
    //     std::cout <<" NUM OF ROWS === " << cov.GetNrows() << " AND NUM OF COLUMNS " << cov.GetNcols() << std::endl;
    // }
    // // for(int i=0; i<diff_arr.size(); i++){
    //     TMatrixDRow row(cov,i);
    //     double comp_sum=0;
    //     for(int j=0; j<diff_arr.size(); j++){
    //         comp_sum+=row(j)*diff_arr[j];
    //         std::cout << "Cov_"<< i << ", "<< j << " = " << row(j) << " and diff is"<< diff_arr[j] << " --> Contributing :: " << row(j)*diff_arr[j] << std::endl;
    //     }
    //     first_opp.push_back(comp_sum);
    // }
    // double chi=0;
    // for(int i=0; i<diff_arr.size(); i++){
    //     chi+=first_opp[i]*diff_arr[i];
    //     std::cout << "first matrix calc == " << first_opp[i] << "; AND DIFF [ARR] <<" << diff_arr[i] << "::::: CHI^2 AT i==" << i << " === "  << chi << std::endl;
    // }
    //double chi=0;

    /////////////////////////////////////////
    // TVectorD diff_arr(h1->GetNbinsX());
    // for(int i=1; i<h1->GetNbinsX()+1; i++){
    //     if(h1->GetBinContent(i)!=0){
    //         diff_arr(i)=((h2->GetBinContent(i)-h1->GetBinContent(i))/(h1->GetBinContent(i)), i-1);
    //         //std::cout << (h1->GetBinContent(i)-h2->GetBinContent(i))/(h2->GetBinContent(i)) << std::endl;
    //     }
    //     else{
    //         diff_arr(i)=(h1->GetBinContent(i)-h2->GetBinContent(i), i-1);
    //     }
    // }

    // TVectorD diff_arrT = ROOT::Math::Transpose(diff_arr);
    // TVectorD chisq_interm = diff_arr * cov;
    // double chisq2 = cov * diff_arrT;
    // cout<<"chisq2 = "<<chisq2<<endl;

    // return chi;


    // USE ROOT FUNCTIONS
    // TArrayD diff_arr(h1->GetNbinsX());
    // for(int i=1; i<h1->GetNbinsX()+1; i++){
    //     if(h1->GetBinContent(i)!=0){
    //         diff_arr.AddAt((h2->GetBinContent(i)-h1->GetBinContent(i))/(h1->GetBinContent(i)), i-1);
    //         std::cout << (h1->GetBinContent(i)-h2->GetBinContent(i))/(h2->GetBinContent(i)) << std::endl;
    //     }
    //     else{
    //         diff_arr.AddAt(h1->GetBinContent(i)-h2->GetBinContent(i), i-1);
    //     }
    // }
    // double chi=0;
    // return chi;

    // TMatrixD diff_vec(1, h1->GetNbinsX());
    // diff_vec.SetMatrixArray(diff_arr.GetArray());
    // cov_d.SetTol(0.000000000000001*cov_d.GetTol());
    // TMatrixD cov = cov_d.Invert();  
    // TMatrixD first_opp(cov,TMatrixD::kMultTranspose,diff_vec);
    // // for(int i=0; i<40; i++){
    // //     TMatrixDRow row(first_opp, i);
    // //     //std::cout << row(0) << std::endl;
    // // }
    // TMatrixD second_opp(diff_vec,TMatrixD::kMult,first_opp);
    // //second_opp.Mult(diff_vec, first_opp); 
    // TMatrixDRow row(second_opp,0);
    // double chi = row(0);
    // std::cout << chi << std::endl;
    // std::cout << "Tolerance set too " << cov.GetTol() << std::endl;
    // return chi;

    //TArrayD diff_arr(h1->GetNbinsX());



    ///////// GEN BIN ARRAY FIRST //////////
    // std::vector<double> diff_vec;
    // //std::vector<std::vector<double>> new_bin_nums;
    // std::vector<double> bin_edges;
    // std::vector<double> temp_bin;
    // bool combine_bin=false;
    // for(int i=1; i<h1->GetNbinsX()+1; i++){
    //     double frac_diff=(h2->GetBinContent(i)-h1->GetBinContent(i))/h1->GetBinContent(i);
    //     if(abs(frac_diff)<0.1){
    //         temp_bin.push_back(i);
    //         //std::cout << "bin " << i << " has a frac diff of " << abs(frac_diff) << "<0.1 so move on" << std::endl; 
    //     }
    //     else{
    //         //std::cout << "bin " << i << " is greater than 0.1 --> " << abs(frac_diff) << std::endl;
    //         if(temp_bin.size()!=0){ 
    //             double numerator=0;
    //             double denominator=0;
    //             //new_bin_nums.push_back(temp_bin);
    //             bin_edges.push_back(h1->GetBinLowEdge(i-1));
    //             for(int j=0; j<temp_bin.size(); j++){
    //                 numerator+=h2->GetBinContent(j)-h1->GetBinContent(j);
    //                 denominator+=h1->GetBinContent(j);
    //             }
    //             diff_vec.push_back(numerator/denominator);
    //             temp_bin.clear();
    //         }
    //         diff_vec.push_back(frac_diff);
    //         bin_edges.push_back(h1->GetBinLowEdge(i));
    //         //temp_bin.push_back(i);
    //         //new_bin_nums.push_back(temp_bin);
    //         //temp_bin.clear();
    //     }
    //     if(i==h1->GetNbinsX() && abs(frac_diff)<0.1){
    //         double numerator=0;
    //         double denominator=0;
    //         //new_bin_nums.push_back(temp_bin);
    //         for(int j=0; j<temp_bin.size(); j++){
    //             numerator+=h2->GetBinContent(j)-h1->GetBinContent(j);
    //             denominator+=h1->GetBinContent(j);
    //         }
    //         diff_vec.push_back(numerator/denominator);
    //         bin_edges.push_back(h1->GetBinLowEdge(i));
    //         //temp_bin.clear();
    //     }
    // }
    // bin_edges.push_back(h1->GetXaxis()->GetXmax());
    // for(int i=0; i<bin_edges.size(); i++){
    //     std::cout << bin_edges[i] << std::endl;
    // }
    // Double_t bin_edge_arr[bin_edges.size()];
    // copy(bin_edges.begin(), bin_edges.end(), bin_edge_arr);
    // //std::cout << diff_vec.size() << std::endl;
    // //std::cout << bin_edges.size() << std::endl;
    // //Grab obverflow
    // //std::cout << "over flow h1--> " << h1->GetBinContent(h1->GetNbinsX()+1) << std::endl;
    // //std::cout << "over flow h2--> " << h2->GetBinContent(h2->GetNbinsX()+1) << std::endl;
    // //diff_vec.push_back((h2->GetBinContent(h2->GetNbinsX()+1)-h1->GetBinContent(h1->GetNbinsX()+1))/h1->GetBinContent(h1->GetNbinsX()+1));
    
    // TH1D* h_rebins[num_of_throws];
    // for(int i=0; i<num_of_throws; i++){
    //     //std::cout << "x" < std::endl;
    //     h_rebins[i]=dynamic_cast<TH1D*>(h_vec[i]->Rebin(bin_edges.size()-1, Form("h_new_%i", i), bin_edge_arr));
    //     //std::cout << i << std::endl;
    // }
    // for(int i=1; i<h_rebins[0]->GetNbinsX()+1; i++){
    //     //std::cout << "New bin "<< i << " has ===  " << h_rebins[0]->GetBinContent(i) << std::endl;
    // }
    // std::vector<std::vector<double>> cov_new = Covariance_vec(h_rebins, num_of_throws, bad_throws);
    // TMatrixD cov_TMD_noI = Covariance(cov_new);
    // cov_TMD_noI.SetTol(0.000000000000001*cov_TMD_noI.GetTol());
    // TMatrixD cov_TMD = cov_TMD_noI.Invert();

    // // // std::vector<double> first_opp;
    // // // for(int i=0; i<diff_vec.size(); i++){
    // // //     TMatrixDRow row(cov_TMD,i);
    // // //     double comp_sum=0;
    // // //     for(int j=0; j<diff_vec.size(); j++){
    // // //         comp_sum+=row(j)*diff_vec[j];
    // // //         std::cout << "Cov_"<< i << ", "<< j << " = " << row(j) << " and diff is"<< diff_vec[j] << " --> Contributing :: " << row(j)*diff_vec[j] << std::endl;
    // // //     }
    // // //     first_opp.push_back(comp_sum);
    // // // }
    // // // double chi=0;
    // // // for(int i=0; i<diff_vec.size(); i++){
    // // //     chi+=first_opp[i]*diff_vec[i];
    // // //     std::cout << "first matrix calc == " << first_opp[i] << "; AND DIFF [ARR] <<" << diff_vec[i] << "::::: CHI^2 AT i==" << i << " === "  << chi << std::endl;
    // // // }
    // // // std::cout << "CHI IS =====" << chi << std::endl;
    // // // return chi;

    // TMatrixD diff_tmd(1, diff_vec.size());
    // TArrayD diff_arr(diff_vec.size());
    // for(int i=0; i<diff_vec.size(); i++){
    //     diff_arr.AddAt(diff_vec[i], i);
    // }
    // diff_tmd.SetMatrixArray(diff_arr.GetArray());

    // TMatrixD first_opp(cov_TMD,TMatrixD::kMultTranspose,diff_tmd);
    // // for(int i=0; i<40; i++){
    // //     TMatrixDRow row(first_opp, i);
    // //     //std::cout << row(0) << std::endl;
    // // }
    // TMatrixD second_opp(diff_tmd,TMatrixD::kMult,first_opp);
    // //second_opp.Mult(diff_vec, first_opp); 
    // TMatrixDRow row(second_opp,0);
    // double chi = row(0);
    // std::cout << "CHI ====== " << chi << std::endl;
    // for(int i=0; i<num_of_throws; i++){
    //     delete h_rebins[i];
    // }
    // //std::cout << "Tolerance set too " << cov.GetTol() << std::endl;
    // return chi;







    /////////THIS PART WORKS /////////



    // std::vector<Double32_t> diff_arr;
    // // const int SIZE_ = 20;
    // // ROOT::Math::SVector<Double32_t, SIZE_> diff_svec;
    // for(int i=1; i<h1->GetNbinsX()+1; i++){
    //     if(h1->GetBinContent(i)!=0){
    //         diff_arr.push_back((h2->GetBinContent(i)-h1->GetBinContent(i))/h1->GetBinContent(i));//(h2->GetBinContent(i)));
    // //         //std::cout << (h1->GetBinContent(i)-h2->GetBinContent(i))/(h2->GetBinContent(i)) << std::endl;
    // //         diff_svec[i-1]=diff_arr[i-1];
    // //         std::cout << diff_svec[i-1] << std::endl;
    //     }
    //     else{
    //         diff_arr.push_back(h2->GetBinContent(i)-h1->GetBinContent(i));
    //     }
    // }

    // double chi;
    // for(int i=0; i<diff_arr.size(); i++){
    //     TMatrixDRow row(cov_d, i);
    //     double bin_chi;
    //     for(int j=0; j<diff_arr.size(); j++){
    //         bin_chi+=diff_arr[i]*diff_arr[j]/row(j);
    //         //std::cout << chi << std::endl;
    //     }
    //     bin_chi/=diff_arr.size();
    //     chi+=bin_chi;
    // }
    // std::cout << "CHI ===== " << chi << std::endl;
    // return chi;
    

    // TH1D* h_rebins[num_of_throws];
    // for(int i=0; i<num_of_throws; i++){
    //     //std::cout << "x" < std::endl;
    //     h_rebins[i]=dynamic_cast<TH1D*>(h_vec[i]->Rebin(bin_edges.size()-1, Form("h_new_%i", i), bin_edge_arr));
    //     //std::cout << i << std::endl;
    // }
    // for(int i=1; i<h_rebins[0]->GetNbinsX()+1; i++){
    //     //std::cout << "New bin "<< i << " has ===  " << h_rebins[0]->GetBinContent(i) << std::endl;
    // }
    // std::vector<std::vector<double>> cov_new = Covariance_vec(h_rebins, num_of_throws, bad_throws);
    // TMatrixD cov_TMD_noI = Covariance(cov_new);
    // cov_TMD_noI.SetTol(0.000000000000001*cov_TMD_noI.GetTol());
    // TMatrixD cov_TMD = cov_TMD_noI.Invert();