#include <fstream>
#include <iostream>
#include <string>

void CreateUserData(std::string desired_file){
    std::ofstream UD(desired_file);

    UD << "GENIE_FILE:" << std::endl;
    UD << "GENIE_TUNE:" << std::endl;
    UD << "NUMBER_OF_EVENTS:" << std::endl;
    UD << "ENGINE_TYPE: " << std::endl;
    UD << "DESIRED_SYSTEMATCS_FOR_GENERATION[:" << std::endl;
    UD << "" << std::endl;
    UD << "]" << std::endl;
    UD << "centralParamValue:" << std::endl;
    UD << "PARAM_VARIATION[" << std::endl;
    UD << "" << std::endl;
    UD << "]" << std::endl;
    UD << "TOOL_OPTIONS[" << std::endl;
    UD << "    AxFFCCQEDipoleToZExp: false" << std::endl;
    UD << "    CCRESIsShapeOnly: false" << std::endl;
    UD << "    DISBYIsShapeOnly: false" << std::endl;
    UD << "    MaCCQEIsShapeOnly: false" << std::endl;
    UD << "    NCRESIsShapeOnly: false" << std::endl;
    UD << "    UseFullHERG: true" << std::endl;
    UD << "    evgen_list_name: \"\"" << std::endl;
    UD << "    fill_valid_tree: false" << std::endl;
    UD << "    genie_tune_name: \"${GENIE_XSEC_TUNE}\"" << std::endl;
    UD << "    ignore_parameter_dependence: true" << std::endl;
    UD << "]" << std::endl;
    UD << "DESRIED_SYTEMATICS_FOR_TESTING[" << std::endl;
    UD << "" << std::endl;
    UD << "]" << std::endl;
    UD << "DESIRED_EVENT_PROPERTY[" << std::endl;
    UD << "]" << std::endl;
    UD << "FLAG: " << std::endl;
    UD << "DESIRED_DATA_DRAW_AGAINST: " << std::endl;
    UD << "DESIRED_EXPERIMENTAL_FLAG_OR_PATH: " << std::endl;
    UD.close();
}