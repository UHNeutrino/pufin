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
  + [Plotting with ```"quantiles":```](#plotting-with-quantiles)
  + [Plotting with ```"2DRatio":```](#plotting-with-2dratio)
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

```"FluxReweight"``` can be used in any of the plotting modes supported by ```"PlotMain.py"``` to reweight using flux histograms and/or area normalize data. To set a flux, the following reweight dictionary entries can be modified in ```"global"``` or in an active plotting mode.

> Note: Reweighting in ```"global"``` overrides flux reweighting in all modes, with the exception of 1DSame. In this mode, the reweighting within individual plots in ```"1DSame"``` takes precedence over ```"global"```. To specify and use different fluxes in a plotting mode other than ```"1DSame"```, remove or comment out the ```"FluxReweight"``` entry in ```"global"```.

+ Required entries:
  + ```"FluxPath":```
  + ```"FluxHistogram":```
  + ```"AreaNormFlag":```
+ Only for ```"AreaNormFlag": false```:
  + ```"XsecType":```
  + ```"UndoFluxNormFlag":```
  + ```"TargetWeightsFile":```
  + ```"Detector":```
  + ```"Target":```
  + ```"XsecMode":```
  + ```"XsecPath":```
+ Only used by GENIE (without area normalization):
  + ```"Flavor":```
  + ```"NucleonsPerTarget":```

<details>
<summary><b> Example </b></summary>
  
<!-- Example FluxReweight entry and link to config file with another example -->
  
</details>


### Plotting with ```"plots":```

```"plots":``` creates a simple plot using events from a single (flattened) root file (see [plotting with ```"1DSame":```](#plotting-with-1dsame) to plot multiple files on the same plot). To use ```"plots"```, the mode must be defined in the called config file and the following entries edited.

+ Standard entries
  + ```"File":```
  + ```"Type":```
  + ```"Cut":```
  + ```"Var1"```
  + ```"Var2"```
  + ```"AxisInfo":```
  + ```"Bins":```
    + For ```"Type": 1D```:
    + For ```"Type": 2D```:
  + ```"VBins":```
  + ```"Name":```
  + ```"max":```
  + ```"logz":```
  + ```"profileX":```
  + ```"diagonal":```
+ Optional/additional plot customization
  + ```"Style":```

<details>
<summary><b> Examples </b></summary>
  
<!-- Example plots entry and link to config file with another example -->

```
1D example config
```

```
2D example config
```

<table><tr>

<td valign="top">
<table>
  <tr> <b> 1D Plot </b> </tr>
  <tr> <td> 
  <!-- To add a plot image, just copy/paste it here (GitHub automatically adds necessary tags & hosts image) -->
  </td> </tr> 
  <tr> <td>
  <!-- type plot description here -->
  </td> </tr>
</table>
</td>

<td valign="top">
<table>
  <tr> <b> 2D Plot </b> </tr>
  <tr> <td> 
  <!-- To add 2D plot image, just copy/paste it here (GitHub automatically adds necessary tags & hosts image) -->
  </td> </tr> 
  <tr> <td>
  <!-- type 2D plot description here -->
  </td> </tr>
</table>
</td>

</tr></table>

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"stacks":```

***...still needs general description...***

+ ```"File":```
+ ```"Type":```
+ ```"Cut":```
+ ```"Var1"```
+ ```"StackCuts":```
+ ```"":```

<details>
<summary><b> Example </b></summary>
  
<!-- Example stacks entry and link to config file with another example -->

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"overlap":```

***...still needs general description...***

<details>
<summary><b> Example </b></summary>
  
<!-- Example overlap entry and link to config file with another example -->

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"1DSame":```

***...still needs general description...***

<details>
<summary><b> Example </b></summary>
  
<!-- Example 1DSame entry and link to config file with another example -->

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"Contour":```

***...still needs general description...***

<details>
<summary><b> Example </b></summary>
  
<!-- Example Contour entry and link to config file with another example -->

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"ContourStyle":```

***...still needs general description...***

<details>
<summary><b> Example </b></summary>
  
<!-- Example ContourStyle entry and link to config file with another example -->

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"quantiles":```

***...still needs general description...***

<details>
<summary><b> Example </b></summary>
  
<!-- Example quantiles entry and link to config file with another example -->

```
Example config
```

<table>
<tr> <td> 
<!-- To add a plot image, just copy/paste it here (GitHub automatically adds necessary tags & hosts image) -->
</td> </tr> 
<tr> <td>
<!-- type plot description here -->
</td> </tr>
</table>

> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"2DRatio":```

***...still needs general description...***

<details>
<summary><b> Example </b></summary>
  
<!-- Example 2DRatio entry and link to config file with another example -->

> Note: ```In global```, the color palette was set by adding ```"Palette": "kRainBow"```, and the [PUfIN custom variable](/VariablesAndModes.md#using-pufin-custom-variables) CosLep was activated by setting ```"TkiB": true```
```
    "2DRatio":
        {
            "File1":"Flat_NEUT6.1.4_OxygenDCC",
            "File2":"Flat_NEUT6.1.4_OxygenRS",
            "Cut": "(Mode == 11 || Mode == 12 || Mode == 13) && CosLep > 0.92", 
            "Var1": "W",
            "Var2": "Q2",
            "AxisInfo":"W, GeV, Q^{2}, GeV^{2}, Oxygen DCC/RS (CosLep > 0.92)",
            "BinsX": [50, 0.5, 3], 
            "BinsY": [60, 0, 3], 
            "Name": "DCCRSRatio_CosLep_Oxygen_4of4",
            "RatioMax":2,
            "RatioMin":0,
            "logz": false,
        },
```

<table>
<tr> <td> 
<img width="896" height="472" alt="png rendered from 2DSame example" src="https://github.com/user-attachments/assets/d5e20538-385d-42e4-a7b9-76387dd7cced" /> 
</td> </tr> 
<tr> <td>
A 2D Ratio plot--generated using the configuration above--showing the differences (as a ratio) in the NEUT DCC (Dynamical Coupled-Channels) and RS (Rein-Sehgal) model predictions for resonant event occupation of Q<sup>2</sup>-W kinematic space when cos(&theta;<sub>&mu;</sub>) > 0.92. 
</td> </tr>
</table>


> See [```PlotMain.json5```](../config/PlotMain.json5) or [```DifferentConfigs.json5```](../config/DifferentConfigs.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


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


