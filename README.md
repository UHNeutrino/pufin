# PUfIN

This repo is for all code related to the Plotting Utility for Interacting Neutrinos (PUfIN) made by Lars Bøe and Kristen Dobbs.

## Functionality
<!-- what can PUfIN do? -->
PUfIN consists of 4 independent functions, each of which serves a distinct purpose. These functions are described briefly below:

 + **PlotMain** \
   PlotMain.py is a plotting function that uses interaction data in flattened root files as well as flux histograms to output organized files and figures with several extensions (.root, .png, and/or .pdf). This function can be used to reweight and plot data in a variety of forms and also supports [custom variables](info/VariablesAndModes.md#using-pufin-custom-variables) not included in standard root trees.
    > For setup instructions and more detailed information on this function, see
  [PlotMain](info/PlotMain.md)

 + **GenMain** 
    > For setup instructions and more detailed information on this function, see
  [GenMain](info/GenMain.md)

 + **WeightMain**
    > For setup instructions and more detailed information on this function, see
  [WeightMain](info/WeightMain.md)

 + **GenSubmit**
    > For setup instructions and more detailed information on this function, see
  [GenSubmit](info/GenSubmit.md)

## Structure
<!-- include which files each function references, expanded file tree as list with embedded links, 
and where to modify or check functionality for each of the 4 primary PUfIN functions -->
