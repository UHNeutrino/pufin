#include "nusystematics/utility/response_helper.hh"
#include <iostream>

void PrintAvailableSystematics(const nusyst::response_helper* resp) {
    std::cout << "==== Available systematics in response_helper ====" << std::endl;
    const auto& headers = resp->GetHeaders();
    for (const auto& header : headers) {
        std::cout << "ID: " << header.first     // paramId_t
                  << "   Name: " << header.second.name  // parameter name string
                  << std::endl;
    }
    std::cout << "=================================================" << std::endl;
}
