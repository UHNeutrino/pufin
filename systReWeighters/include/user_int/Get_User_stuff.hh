// #ifndef User_int_H
// #define User_int_H

#include <fstream>
#include <vector>
#include <string>
#include <utility>

//  class User_int {
//   public:

const std::string RemoveHeader(std::string full_string, std::string removed){
    std::string::size_type st = full_string.find(removed);
    if(st != std::string::npos){
        full_string.erase(st, removed.length());
    }
    if(removed!="FLAG:"){
        for(int i=0; i<full_string.length(); i++){
            if(full_string[i] == ' '){
                full_string.erase(full_string.begin()+i);
                i--;
            }

            if(full_string[i] == ','){
                full_string.erase(full_string.begin()+i);
                i--;
            }
        }
    }
    return full_string;
}

const std::vector<std::string> Get_Syst_name(std::string file_path){
    std::fstream file;
    std::vector<std::string> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        while(getline(file, temp)){
            if(temp.find("DESIRED_SYSTEMATICS_FOR_GENERATION[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("DESIRED_SYSTEMATICS_FOR_GENERATION[") == std::string::npos){
                    std::cout << temp << std::endl;
                    vec.push_back(RemoveHeader(temp, ""));
                }
            }
            if(grabbed_first_brack==true && grabbed_last_brack==true){
                break;
            }
        }
    }
    return vec;
}

const std::vector<std::string> Get_Analysis_syst(std::string file_path){
    std::fstream file;
    std::vector<std::string> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        while(getline(file, temp)){
            if(temp.find("DESRIED_SYTEMATICS_FOR_TESTING[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("DESRIED_SYTEMATICS_FOR_TESTING[") == std::string::npos){
                    if(temp.find("all") == std::string::npos){
                        vec.push_back(RemoveHeader(temp, ""));
                    }
                    else{
                        vec=Get_Syst_name(file_path);
                    }
                }
            }
            if(grabbed_first_brack==true && grabbed_last_brack==true){
                break;
            }
        }
    }
    return vec;
}

const std::string Get_Central_Param(std::string file_path){
    std::fstream file;
    std::string CV;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_CV=false;
        while(getline(file, temp)){
            if(temp.find("centralParamValue:") != std::string::npos){
                CV = RemoveHeader(temp, "centralParamValue:");
                grabbed_CV=true;
            }
            if(grabbed_CV==true){
                break;
            }
        }
    }
    return CV;
}

const std::string Get_Engine_Type(std::string file_path){
    std::fstream file;
    std::string ENGINE;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_ENGINE=false;
        while(getline(file, temp)){
            if(temp.find("ENGINE_TYPE:") != std::string::npos){
                ENGINE = RemoveHeader(temp, "ENGINE_TYPE:");
                grabbed_ENGINE=true;
            }
            if(grabbed_ENGINE==true){
                break;
            }
        }
    }
    return ENGINE;
}

const std::vector<std::string> Get_GENIE_file_and_tune(std::string file_path){
    std::fstream file;
    std::string genie_path;
    std::string genie_tune;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_genie_file=false;
        bool grabbed_genie_tune=false;
        while(getline(file, temp)){
            if(temp.find("GENIE_FILE:") != std::string::npos){
                genie_path=RemoveHeader(temp, "GENIE_FILE:");
                grabbed_genie_file=true;
            }
            if(temp.find("GENIE_TUNE:") != std::string::npos){
                genie_tune=RemoveHeader(temp, "GENIE_TUNE:");
                grabbed_genie_tune=true;
            }
            if(grabbed_genie_file==true && grabbed_genie_tune==true){
                break;
            }
        }
    }
    std::vector<std::string> vec = {genie_path, genie_tune};
    return vec;
}

const int Get_Num_Events(std::string file_path){
    std::fstream file;
    int events=0;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_events=false;
        while(getline(file, temp)){
            if(temp.find("NUMBER_OF_EVENTS:") != std::string::npos){
                events=stoi(RemoveHeader(temp, "NUMBER_OF_EVENTS:"));
                grabbed_events=true;
            }
            if(grabbed_events==true){
                break;
            }
        }
    }
    return events;
}

const std::vector<std::string> Get_param_var(std::string file_path){
    std::fstream file;
    std::vector<std::string> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        while(getline(file, temp)){
            if(temp.find("PARAM_VARIATION[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("PARAM_VARIATION[") == std::string::npos){
                    vec.push_back(RemoveHeader(temp, ""));
                }
            }
            if(grabbed_first_brack==true && grabbed_last_brack==true){
                break;
            }
        }
    }
    return vec;
}

const std::vector<std::string> Get_Tool_options(std::string file_path){
    std::fstream file;
    std::vector<std::string> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        while(getline(file, temp)){
            if(temp.find("TOOL_OPTIONS[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("TOOL_OPTIONS[") == std::string::npos){
                    vec.push_back(RemoveHeader(temp, ""));
                }
            }
            if(grabbed_first_brack==true && grabbed_last_brack==true){
                break;
            }
        }
    }
    return vec;
}

const std::vector<std::vector<std::variant<std::string, std::vector<double>>>> Get_Event_Property(std::string file_path){
    std::fstream file;
    std::vector<std::vector<std::variant<std::string, std::vector<double>>>> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        while(getline(file, temp)){
            if(temp.find("DESIRED_EVENT_PROPERTY[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("DESIRED_EVENT_PROPERTY[") == std::string::npos){
                    std::string event_string;
                    std::string binning_string;
                    bool bin_left_brack=false;
                    bool bin_right_brack=false;
                    for(int i=0; i<temp.length(); i++){
                        if(temp[i]=='['){
                            bin_left_brack=true;
                        }
                        if(temp[i]==']'){
                            bin_right_brack=true;
                        }
                        if(temp[i]!=' ' && bin_left_brack==false && temp[i]!='['){
                            event_string+=temp[i];
                        }
                        if(bin_right_brack==false && bin_left_brack==true && temp[i]!='[' && temp[i]!=']'){
                            binning_string.push_back(temp[i]);
                        }
                    }
                    std::vector<double> binning_doubles;
                    std::string current_number_string="";
                    for(int i=0; i<binning_string.length(); i++){
                        double current_number;
                        if(binning_string[i]==','){
                            current_number=std::stod(current_number_string);
                            binning_doubles.push_back(current_number);
                            current_number_string="";
                        }
                        else{
                            current_number_string+=binning_string[i];
                            //std::cout << current_number_string << std::endl;
                        }
                    }
                    //std::cout << event_string << std::endl;
                    //for(int i=0; i< binning_doubles.size(); i++){
                        //std::cout << binning_doubles[i] << std::endl;
                    //}
                    std::vector<std::variant<std::string, std::vector<double>>> temp_vec = {event_string, binning_doubles};
                    vec.push_back(temp_vec);
                }
            }
            if(grabbed_first_brack==true && grabbed_last_brack==true){
                break;
            }
        }
    }
    return vec;
}

const std::vector<std::vector<std::variant<std::string, std::vector<std::string>>>> Get_Path_and_Syst(std::string file_path){
    std::fstream file;
    std::vector<std::vector<std::variant<std::string, std::vector<std::string>>>> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        bool syst_left_brack=false;
        bool syst_right_brack=false;
        std::string throw_path="";
        std::vector<std::string> vec_of_syst;
        while(getline(file, temp)){
            if(temp.find("DRAW_SYSTEMATICS[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("DRAW_SYSTEMATICS[") == std::string::npos){
                    if(RemoveHeader(temp,"")=="}"){
                        syst_right_brack=true;
                    }
                    if(syst_left_brack==true && syst_right_brack==false){
                        if(temp.find("Group_name:") != std::string::npos){
                            vec_of_syst.push_back(RemoveHeader(temp, "Group_name:"));
                        }
                        else{
                            if(RemoveHeader(temp,"") != "{" && RemoveHeader(temp,"") != "}"){
                                vec_of_syst.push_back(RemoveHeader(temp,""));
                            }
                        }
                        //std::cout << temp << std::endl;
                    }
                    if(syst_left_brack==false && syst_right_brack==false){
                        throw_path = RemoveHeader(temp,"{");
                        //std::cout << throw_path << std::endl;
                        syst_left_brack=true;
                    }
                    if(syst_left_brack==true && syst_right_brack==true){
                        std::vector<std::variant<std::string, std::vector<std::string>>> temp_vec = {throw_path, vec_of_syst};
                        //std::cout << vec_of_syst.size() << std::endl;
                        vec.push_back(temp_vec);
                        temp_vec.clear();
                        vec_of_syst.clear();
                        syst_left_brack=false;
                        syst_right_brack=false;
                    }
                }
            }
            if(grabbed_first_brack==true && grabbed_last_brack==true){
                break;
            }
        }
    }
    return vec;
}

const std::string Get_Flag(std::string file_path){
    std::fstream file;
    std::string flag;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_flag=false;
        while(getline(file, temp)){
            if(temp.find("FLAG:") != std::string::npos){
                flag = RemoveHeader(temp, "FLAG:");
                grabbed_flag=true;
            }
            if(grabbed_flag==true){
                break;
            }
        }
    }
    return flag;
}

const std::vector<std::pair<std::string, std::string>> Get_Comparisons(std::string file_path){
    std::fstream file;
    std::vector<std::pair<std::string, std::string>> vec;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_first_brack=false;
        bool grabbed_last_brack=false;
        std::pair<std::string, std::string> comp_path;
        while(getline(file, temp)){
            if(temp.find("DESIRED_DATA_DRAW_AGAINST[") != std::string::npos){
                grabbed_first_brack=true;
            }
            if(grabbed_first_brack==true && temp=="]"){
                grabbed_last_brack=true;
            }
            if(grabbed_first_brack==true && grabbed_last_brack==false){
                if(temp.find("DESIRED_DATA_DRAW_AGAINST[") == std::string::npos){
                    bool comp_complete=false;
                    std::string comp_model="";
                    std::string path_file="";
                    for(int i=0; i<temp.length(); i++){
                        if(temp[i]!=' ' && temp[i]!=',' && comp_complete==false){
                            comp_model+=temp[i];
                        }
                        if(temp[i]==','){
                            comp_complete=true;
                        }
                        if(temp[i]!=' ' && temp[i]!=',' && comp_complete==true){
                            path_file+=temp[i];
                        }
                    }
                    comp_path.first = comp_model;
                    comp_path.second = path_file;
                    vec.push_back(comp_path);
                }
            }
        }
    }
    return vec;
}

const std::vector<std::vector<std::string>> Get_Labels(std::string file_path){
    std::fstream file;
    std::vector<std::vector<std::string>> labels;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_tag=false;
        bool grabbed_bottom=false;
        while(getline(file,temp)){
            if(temp.find("TITLE_AND_AXIS_LABEL[") != std::string::npos){
                grabbed_tag=true;
            }
            if(grabbed_tag==true && temp=="]"){
                grabbed_bottom=true;
            }
            if(grabbed_tag==true && temp.find("TITLE_AND_AXIS_LABEL[") == std::string::npos && grabbed_bottom==false){
                std::cout << temp << std::endl;
                std::vector<std::string> grabbed_labels;
                std::stringstream this_label(temp);
                while(this_label.good()){
                    std::string substr;
                    getline(this_label, substr, ',');
                    grabbed_labels.push_back(substr);
                }
                labels.push_back(grabbed_labels);
            }
            if(grabbed_tag==true && grabbed_bottom==true){
                break;
            }
        }
    }
    return labels;
}

const std::vector<std::vector<std::string>> Get_Groups(std::string file_path){
    std::fstream file;
    std::vector<std::vector<std::string>> groups;
    file.open(file_path, std::ios::in);
    if(file.is_open()){
        std::string temp;
        bool grabbed_tag=false;
        bool grabbed_bottom=false;
        while(getline(file,temp)){
            if(temp.find("GROUPS[") != std::string::npos){
                grabbed_tag=true;
            }
            if(grabbed_tag==true && temp=="]"){
                grabbed_bottom=true;
            }
            if(grabbed_tag==true && temp.find("GROUPS[") == std::string::npos && grabbed_bottom==false){
                std::cout << temp << std::endl;
                std::vector<std::string> grabbed_groups;
                std::stringstream this_label(temp);
                while(this_label.good()){
                    std::string substr;
                    getline(this_label, substr, ',');
                    grabbed_groups.push_back(RemoveHeader(substr,""));
                }
                groups.push_back(grabbed_groups);
            }
            if(grabbed_tag==true && grabbed_bottom==true){
                break;
            }
        }
        
    }
    return groups;
}


// const std::vector<std::string> Get_Comparisons(std::string file_path){
//     std::fstream file;
//     std::string flag;
//     std::string Against;
//     std::string against_path;
//     file.open(file_path, std::ios::in);
//     if(file.is_open()){
//         std::string temp;
//         bool grabbed_Against=false;
//         bool grabbed_flag=false;
//         bool grabbed_against_path=false;
//         while(getline(file, temp)){
//             if(temp.find("FLAG:") != std::string::npos){
//                 flag = RemoveHeader(temp, "FLAG:");
//                 grabbed_flag=true;
//             }
//             if(temp.find("DESIRED_DATA_DRAW_AGAINST:") != std::string::npos){
//                 Against = RemoveHeader(temp, "DESIRED_DATA_DRAW_AGAINST:");
//                 grabbed_Against=true;
//             }
//             if(temp.find("DESIRED_EXPERIMENTAL_FLAG_OR_PATH:") != std::string::npos){
//                 against_path = RemoveHeader(temp, "DESIRED_EXPERIMENTAL_FLAG_OR_PATH:");
//                 grabbed_against_path=true;
//             }
//             if(grabbed_flag==true && grabbed_Against==true && grabbed_against_path==true){
//                 break;
//             }
//         }
//     }
//     std::vector<std::string> vec = {flag, Against, against_path};
//     return vec;

// }
//  };
// #endif /* User_int_H */