# PUfIN

This repo is for all code related to the Plotting Utility for Interacting Neutrinos (PUfIN) made by Lars Bøe and Kristen Dobbs.

<details>

<summary> <b>
  Useful Resources 
</b> </summary>

+ Find or generate color schemes using ROOT's [TColor Class Reference](https://root.cern.ch/doc/v636/classTColor.html)
  
+ Set other line attributes by referencing ROOT's [TAttLine Class Reference](https://root.cern.ch/doc/v630/classTAttLine.html)
  > Check [src/jsonreader.py](https://github.com/UHNeutrino/pufin/blob/main/src/jsonreader.py)
    for attribute support in each PlotMain plotting type

+ Identify Nuisance interaction mode codes with [Nuisance HEPForge](https://nuisance.hepforge.org/tutorials/interaction_modes.html)
  or this [internal document](https://github.com/UHNeutrino/pufin/blob/main/info/VariablesAndModes.md) 

+ Review git commands with this [cheat sheet](https://education.github.com/git-cheat-sheet-education.pdf)

</details>

## Functionality
<!-- what can PUfIN do? -->
PUfIN consists of 4 independent functions, each of which serves a distinct purpose. These functions are described briefly below:

 + **PlotMain**
    > For setup instructions and more detailed information on this function, see
  [PlotMain](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md)

 + **GenMain**
    > For setup instructions and more detailed information on this function, see
  [GenMain](https://github.com/UHNeutrino/pufin/blob/main/info/GenMain.md)

 + **WeightMain**
    > For setup instructions and more detailed information on this function, see
  [WeightMain](https://github.com/UHNeutrino/pufin/blob/main/info/WeightMain.md)

 + **GenSubmit**
    > For setup instructions and more detailed information on this function, see
  [GenSubmit](https://github.com/UHNeutrino/pufin/blob/main/info/GenSubmit.md)

## Structure
<!-- include which files each function references, expanded file tree as list with embedded links, 
and where to modify or check functionality for each of the 4 primary PUfIN functions -->
