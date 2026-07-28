# PUfIN

This repo is for all code related to the Plotting Utility for Interacting Neutrinos (PUfIN) made by Lars Bøe and Kristen Dobbs.

## Useful Resources
+ Find or generate color schemes using ROOT's [TColor Class Reference](https://root.cern.ch/doc/v636/classTColor.html)
  
+ Set other line attributes by referencing ROOT's [TAttLine Class Reference](https://root.cern.ch/doc/v630/classTAttLine.html)
  > At the moment, only Line Style ("Style") and Line Color ("Color") are supported in PUfIN

+ Identify Nuisance interaction mode codes with [Nuisance HEPForge](https://nuisance.hepforge.org/tutorials/interaction_modes.html) or this [internal document](https://github.com/UHNeutrino/PUfIN/InteractionModes.md) 

+ Review git commands with this [cheat sheet](https://education.github.com/git-cheat-sheet-education.pdf)

## GenMain.py

Before running this script do: 
```
source /data/t2k-nova/MainSetup.sh
```
to set global variables

## Setup for plotting with ```main.py```
After installing PUfIN using:
```
git clone https://github.com/UHNeutrino/PUfIN/
```

+ Install ROOT (v6_30_02_cxx17) and Python (3.11)
  > If on UH SSH, these will already be installed

+ Add paths by appending your ```.bash_profile``` (located in your home directory)
  + ROOT setup 
    ```
    # Source ROOT setup
    source /project/ROOT/v6_30_02_cxx17/bin/thisroot.sh
    source /project/software/neut/build/Linux/setup.sh
    export ROOTSYS=/project/ROOT/v6_30_02_cxx17
    ```
  + Alternatively, copy over the bash script from
    [PUfIN/setup/T2KRWsetup.sh](https://github.com/UHNeutrino/PUfIN/blob/main/setup/T2KRWsetup.sh).
    This includes ROOT setup as well as pathing needed for functionality outside of plotting with ```main.py```
    
    > above bash scripts are for UH SSH

+ [Create a virtual environment in VSCode](https://code.visualstudio.com/docs/python/environments) that uses the Python version specified above and pip install dependencies within it using
  ```
  (.venv) [username@uhneutrino:~]$ pip install json5 numpy
  ```
  + To point the interpreter in VSCode to the venv you just created, navigate to the Command Palette using ```Ctrl + Shift + P```, type and select ```Python: Select Interpreter```, and enter or select ```your_venv_folder/bin/python```

+ Change user specific file paths (optional)
  + In ```jsonreader.py``` and ```main.py``` change the home directory to 
    ```
    HOME = os.getenv("HOME", "/home/username")
    ```
  + In ```main.json5```, edit ```"global"``` to change the folder you want your plot(s) to be saved to
    ```
    "Save": "My_Folder",
    ```
    > If the folder you enter does not exist yet, it will not be created for you
    
    Leaving this field blank will save plots to your home directory.
   

To create plots, edit and activate (by setting ```"Bool": true```) ONE of the plotting modes within ```config/PlotMain.json5```, then run ```PlotMain.py```
