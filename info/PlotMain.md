> Not what you're looking for? Click [here](https://github.com/UHNeutrino/pufin/blob/main/README.md) to return to the main PUfIN README

# PlotMain.py

PlotMain.py is a plotting function that uses interaction data in flattened root files as well as flux histograms to output organized files and figures with several extensions (.root, .png, and/or .pdf). This function can be used to reweight and plot data in a variety of forms (as outlined [here](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#functionality)) and also supports [custom variables](https://github.com/UHNeutrino/pufin/blob/main/info/VariablesAndModes.md#using-pufin-custom-variables) not included in standard root trees.


## Outline
+ [Setup](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#setup)
+ [Functionality](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#functionality)
  + [Reweighting with ```"FluxReweight":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#reweighting-with-fluxreweight)
  + [Plotting with ```"plots":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#plotting-with-plots)
  + [Plotting with ```"stacks":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#plotting-with-stacks)
  + [Plotting with ```"overlap":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#plotting-with-overlap)
  + [Plotting with ```"1DSame":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#plotting-with-1dsame)
  + [Plotting with ```"Contour":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#plotting-with-contour)
  + [Plotting with ```"ContourStyle":```](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#plotting-with-contourstyle)
+ [Using PlotMain.py](https://github.com/UHNeutrino/pufin/blob/main/info/PlotMain.md#using-plotmainpy)

## Setup
After installing PUfIN using:
```
git clone https://github.com/UHNeutrino/PUfIN/
```

+ Install ROOT (v6_30_02_cxx17) and Python (3.11)

+ Add paths by appending your ```.bash_profile``` (or other command-line shell script)
  + ROOT setup is currently the only pathing required for PlotMain
  <!--
    + Alternatively, copy over the bash script from 
    [PUfIN/setup/T2KRWsetup.sh](https://github.com/UHNeutrino/PUfIN/blob/main/setup/T2KRWsetup.sh). 
    This includes ROOT setup as well as pathing needed for functionality outside of plotting with ```main.py```
    (include when generalized shell script is made)
  -->

+ [Create a virtual environment in VSCode](https://code.visualstudio.com/docs/python/environments) that uses the Python version specified above and pip install dependencies within it using
  ```
  (.venv) [username@domain:~]$ pip install json5 numpy
  ```
  + To point the interpreter in VSCode to the venv you just created, navigate to the Command Palette using <kbd> Ctrl </kbd> + <kbd> Shift </kbd> + <kbd> P </kbd> , type and select ```Python: Select Interpreter```, and enter or select ```your_venv_folder/bin/python```


+ Change user specific file paths (optional)
  + In ```jsonreader.py``` and ```PlotMain.py``` change the home directory to 
    ```
    HOME = os.getenv("HOME", "/home/username")
    ```
  + In your config file, edit ```"global"``` to change the folder you want your plot(s) to be saved to
    ```
    "Save": "My_Folder",
    ```
    > If the folder you enter does not exist yet, it will not be created for you
    
    Leaving this field blank will save created files to your home directory.

## Functionality

### Reweighting with ```"FluxReweight":```

### Plotting with ```"plots":```

### Plotting with ```"stacks":```

### Plotting with ```"overlap":```

### Plotting with ```"1DSame":```

### Plotting with ```"Contour":```

### Plotting with ```"ContourStyle":```


## Using PlotMain.py

+ Create a ```.json5``` config file within the config folder, using
  [PUfIN/config/PlotMain.json5](https://github.com/UHNeutrino/pufin/blob/main/config/PlotMain.json5) as a template
  + Your config file (```config/MyConfig.json5```) should include ```"global"``` and one (or more) plotting modes
  + Alternatively, directly edit and run using the existing config file ```PlotMain.json5```

+ To create plots, include desired plotting modes within ```config/MyConfig.json5```, then run 
  ```
  (.venv) [username@domain PUfIN]$ python PlotMain.py MyConfig
  ```

     > DO NOT include the ```.json5``` extension when referencing your config file 

