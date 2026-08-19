> Not what you're looking for? Click [here](../README.md) to return to the main PUfIN README

# PlotMain.py

PlotMain.py is a plotting function that uses interaction data in flattened root files as well as flux histograms to output organized files and figures with several extensions (.root, .png, and/or .pdf). This function can be used to reweight and plot data in a variety of forms (as outlined [here](#functionality)) and also supports [custom variables](VariablesAndModes.md#using-pufin-custom-variables) not included in standard root trees.


<details>
<summary><h2> Outline </h2></summary>
  
+ [Setup](#setup)
+ [Functionality](#functionality)
  + [Reweighting with ```"FluxReweight":```](#reweighting-with-fluxreweight)
  + [Plotting with ```"plots":```](#plotting-with-plots)
  + [Plotting with ```"stacks":```](#plotting-with-stacks)
  + [Plotting with ```"overlap":```](#plotting-with-overlap)
  + [Plotting with ```"1DSame":```](#plotting-with-1dsame)
  + [Plotting with ```"Contour":```](#plotting-with-contour)
  + [Plotting with ```"ContourStyle":```](#plotting-with-contourstyle)
+ [Using PlotMain.py](#using-plotmainpy)

</details>

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

+ See [Using PlotMain.py](#using-plotmainpy) to begin plotting

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
  [PUfIN/config/PlotMain.json5](../config/PlotMain.json5) as a template
  + Your config file (```config/MyConfig.json5```) should include ```"global"``` and one (or more) plotting modes
  + Alternatively, directly edit and run using the existing config file ```PlotMain.json5```

+ Change user specific save directory
  + In your config file, edit ```"global"``` to change the folder you want your plot(s) to be saved to. For example:
    ```
    "Save": "/home/username/My_Folder",
    ```
    > If the folder you enter does not exist yet, it will not be created for you
    
    Leaving this field blank or entering an invalid file path will result in the error: ```Can't save in "your/invalid/path"```.
    
+ To create plots, include desired plotting modes within ```config/MyConfig.json5```, then run 
  ```
  (.venv) [username@domain PUfIN]$ python PlotMain.py MyConfig
  ```

     > DO NOT include the ```.json5``` extension when referencing your config file 

