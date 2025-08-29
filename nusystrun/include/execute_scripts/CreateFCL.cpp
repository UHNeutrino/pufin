#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <TStopwatch.h>

#include "user_int/Get_User_stuff.hh"

void CreateFCL(std::string user_file, std::string Output_fcl){
    TStopwatch* sw = new TStopwatch();
    sw->Start();
    //Grab All Necessary Variables
    std::vector<std::string> syst_name = Get_Syst_name(user_file);
    std::vector<std::string> param_variation = Get_param_var(user_file);
    //std::vector<std::string> tool_option = Get_Tool_options(user_file);
    std::string CV = Get_Central_Param(user_file);
    std::string Engine_type = Get_Engine_Type(user_file);

    std::cout << "Creating .fcl file with systematics: " << std::endl;

    //Begin Writing FCL File
    std::ofstream FCL(Output_fcl);
    if(Engine_type=="ZExpPCAWeighter"){
        FCL <<"zexpansion_weighter_toolconfig: {" << std::endl;
        FCL <<"tool_type: \"ZExpPCAWeighter\""<< std::endl;
        FCL <<"instance_name: \"myreweighter\""<<std::endl;
        for(int j=1; j<5; j++){
            FCL <<  "b" << std::to_string(j)<<"_variation_descriptor: \"(";
            for(int i=0; i<param_variation.size()-1; i++){
                FCL << param_variation[i] <<",";
            }
            FCL<<param_variation[param_variation.size()-1]<<")\""<<std::endl;
        }
        FCL<<"}"<<std::endl;
        FCL<<"syst_providers: [zexpansion_weighter_toolconfig]"<<std::endl;
    }
    else if(Engine_type=="ResIso_toolconfig"){
        FCL<<"ResIso_toolconfig: {" << std::endl;
        FCL<<"  tool_type: \"ResIso" << std::endl;
        FCL<<"  instance_name: \"ResonanceIsolation\"" << std::endl;
        FCL<<"  alldial_variation_descriptor: \"(";
        for(int i=0; i<param_variation.size()-1; i++){
            FCL<<param_variation[i] <<",";
        }
        FCL<<param_variation[param_variation.size()-1]<<")\""<<std::endl;
        FCL<<"  verbosity_level: 5" << std::endl;
        FCL<<"}" << std::endl;
        FCL<<"syst_providers: [ResIso_toolconfig]" << std::endl;
    }
    else{
        FCL << "generated_systematic_provider_configuration: {" << std::endl;
        FCL << "    "<< Engine_type << ": {" << std::endl;
        for(int i=0; i<syst_name.size(); i++){
            FCL << "        "<< syst_name[i] << ": {" << std::endl;
            std::cout << syst_name[i] << std::endl;
            FCL << "            centralParamValue: " << CV << std::endl;
            FCL << "            paramVariations: [" << std::endl;
            for(int j=0; j<param_variation.size()-1; j++){
                FCL << "                " << param_variation[j] << "," << std::endl;
            }
            FCL << "                " << param_variation[param_variation.size()-1] << std::endl;
            FCL << "            ]" << std::endl;
            FCL << "            prettyName: \"" << syst_name[i] << "\"" << std::endl;
            FCL << "            systParamId: " << i << std::endl;
            FCL << "            isSplineable: true" << std::endl;
            FCL << "        }" << std::endl;
        }
        FCL << "        parameter_headers: [" << std::endl;
        for(int i=0; i<syst_name.size()-1; i++){
            FCL << "            " << syst_name[i] << "," << std::endl;
        }
        FCL << "            " << syst_name[syst_name.size()-1] << std::endl;
        FCL << "        ]" << std::endl;
        FCL << "        tool_options: {" << std::endl;
        // for(int i; i<tool_option.size(); i++){
        //     FCL << "            " << tool_option[i] << std::endl;
        // }
        if(Engine_type=="GENIEReWeight"){
            FCL << "            AxFFCCQEDipoleToZExp: false" << std::endl;
            FCL << "            CCRESIsShapeOnly: false" << std::endl;
            FCL << "            DISBYIsShapeOnly: false" << std::endl;
            FCL << "            MaCCQEIsShapeOnly: false" << std::endl;
            FCL << "            NCRESIsShapeOnly: false" << std::endl;
            FCL << "            UseFullHERG: true" << std::endl;
            FCL << "            evgen_list_name: \"\"" << std::endl;
            FCL << "            fill_valid_tree: false" << std::endl;
            FCL << "            genie_tune_name: \"${GENIE_XSEC_TUNE}\"" << std::endl;
            FCL << "            ignore_parameter_dependence: true" << std::endl;
            FCL << "        }" << std::endl;
            FCL << "        tool_type: \"GENIEReWeight\"" << std::endl;
            FCL << "    }" << std::endl;
            FCL << "    syst_providers: [" << std::endl;
            FCL << "        GENIEReWeight" << std::endl;
            FCL << "    ]" << std::endl;
        }
        if(Engine_type=="EmissRWEngine"){
            FCL <<"             OPT_STRING: \"option_test\"" << std::endl;
            FCL <<"             OPT_BOOL: true" << std::endl;
            FCL <<"             fill_valid_tree: false " << std::endl;
            FCL <<"         }" << std::endl;
            FCL <<"         tool_type: \"DIRT2_Emiss\"" << std::endl;
            FCL <<"     }"<< std::endl;
            FCL <<"     syst_providers: [" << std::endl;
            FCL <<"         EmissRWEngine" << std::endl;
            FCL <<"     ]"<<std::endl;
        }
        FCL << "}" << std::endl;
        FCL.close();
        sw->Stop();
        std::cout << "TIME!!!!! " << std::endl;
        std::cout << "TIME!!!!! " << std::endl;
        std::cout << "TIME!!!!! " << std::endl;
        std::cout << "TIME for FCL prod --->  " << sw->CpuTime() << std::endl;
    }
}