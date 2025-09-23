#include <fstream>
#include <iostream>
#include <string>

void CreateDrawFile(std::string desired_file){
 std::ofstream UD(desired_file);
 UD << "NUMBER_OF_EVENTS:" << std::endl;
 UD << "DRAW_SYSTEMATICS[" << std::endl;
 UD << "]" << std::endl;
 UD << "GROUPS[" << std::endl;
 UD << "]" << std::endl;
 UD << "DESIRED_EVENT_PROPERTY[" << std::endl;
 UD << "]" << std::endl;
 UD << "TITLE_AND_AXIS_LABEL[" << std::endl;
 UD << "]" << std::endl;
 UD << "DESIRED_DATA_DRAW_AGAINST[" << std::endl;
 UD << "]" << std::endl;
 UD << "FLAG: " << std::endl;
 // UD << "DESIRED_DATA_DRAW_AGAINST: " << std::endl;
 // UD << "DESIRED_EXPERIMENTAL_FLAG_OR_PATH: " << std::endl;
}
