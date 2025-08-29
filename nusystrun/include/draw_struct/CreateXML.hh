#include <string>
#include <iostream>
#include <fstream>

void CreateXML(std::string genie_file){
    std::ofstream GO("genie_comp.xml");
    GO << "<nuisance>" << std::endl;
    GO << " < sample name=\"GenericFlux_Vectors\" input=\"GENIE:";
    GO << genie_file;
    GO << "\" />" << std::endl;
    GO << "</nuisance>";
    GO.close();

    std::ofstream MSXML("MultiSig.xml");
    MSXML << "<nuisance>" << std::endl;
    MSXML << " < sample name=\"MultiSignal.so\" input=\"GENIE:";
    MSXML << genie_file;
    MSXML << "\" />" << std::endl;
    MSXML << "</nuisance>";
    MSXML.close();
}
