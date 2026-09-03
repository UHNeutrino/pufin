> Not what you're looking for? Click [here](../README.md) to return to the main PUfIN README

# PlotMain.py

PlotMain.py is a plotting function that uses interaction data in flattened root files as well as flux histograms to output organized files and figures with several extensions (.root, .png, and/or .pdf). This function can be used to reweight and plot data in a variety of forms (as outlined [here](#functionality)) and also supports [custom variables](VariablesAndModes.md#using-pufin-custom-variables) not included in standard root trees.

<details>

<summary> <b>
  Useful Resources 
</b> </summary>

+ Identify Nuisance interaction mode codes with [Nuisance HEPForge](https://nuisance.hepforge.org/tutorials/interaction_modes.html)
  or this [internal document](info/VariablesAndModes.md)

+ Identify NEUT, GENIE, and PUfIN variables by referencing [VariablesAndModes.md](info/VariablesAndModes.md)
  
+ Format plot titles with subscripts, special characters, etc. using ROOT's [classTLatex](https://root.cern/doc/v606/classTLatex.html#L1)

+ Find or generate color schemes using ROOT's [TColor Class Reference](https://root.cern.ch/doc/v636/classTColor.html)
  
+ Set other line attributes by referencing ROOT's [TAttLine Class Reference](https://root.cern.ch/doc/v630/classTAttLine.html)
  > Check [src/jsonreader.py](src/jsonreader.py)
    for attribute support in each PlotMain plotting type

</details>

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

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>

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
 
</details>

<details>
<summary><b> Example </b></summary>
  
<!-- Example FluxReweight entry and link to config file with another example -->
  
</details>


### Plotting with ```"plots":```

```"plots":``` creates a simple plot using events from a single (flattened) root file (see [plotting with ```"1DSame":```](#plotting-with-1dsame) to plot multiple files on the same plot). To use ```"plots"```, the mode must be defined in the called config file and the following entries edited.


<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>

+ ```"File1":``` file (as a string)
+ ```"Type":``` plot dimensionality (```"1D"``` or ```"2D"```)
+ ```"Cut":``` see [making cuts](VariablesAndModes.md#making-cuts-with-variables-flags--modes) for more information
+ ```"Var1":``` x-axis variable
+ &dagger;```"Var2"``` y-axis variable (when ```"Type": "2D"```)
+ ```"AxisInfo":``` entered as a single string with entries separated by commas in the following form
  
  ```
    "x-axis variable, Var1 unit, y-axis variable, Var2 unit, plot title"
  ```
  > for 1D, leave unused fields blank: ``` "x-axis variable, Var1 unit, , , plot title" ```
+ ```"Bins":``` 
  + For ```"Type": 1D```: entered as a list in the following form
  
  ```
  [number of bins along x-axis, x-min, x-max]
  ```
  
  + For ```"Type": 2D```: entered as a list in the following form
  
  ```
  [number of bins along x-axis, x-min, x-max, number of bins along y-axis, y-min, y-max]
  ```
+ &dagger;```"VBins":```
+ ```"Name":``` name that created files will be saved as (entered as a string without extensions)
+ &dagger;```"max":``` manually maximum plot value (entered as a number, or omitted for automatic scaling)
+ ```"logz":``` sets z-axis (number of interactions) to a log scale (```true```/```false```)
+ &dagger;```"profileX":``` (?) activate by including ```"profileX": true```
+ &dagger;```"diagonal":``` (?) activate by including ```"diagonal": true```
+ &dagger;```"Style":``` line style (see ROOT's [TAttLine Class Reference](https://root.cern.ch/doc/v630/classTAttLine.html) for line style codes)

</details>

<details>
<summary><b> Examples </b></summary>
  
<!-- Example plots entry and link to config file with another example -->

> Note: In ```global```, raw file data was reweighted and area normalized using ```"FluxReweight":```
```
// 1D configuration
    "plots":
        {
            "File":"Flat_GenieAR23_onAr_flatf_0-5GeV_NumuCC_SuSAv2_ghep_1e7",
            "Type":"1D",
            "Cut": "flagCCINC == true",
            "Var1": "Enu_true",
            "AxisInfo":"E_{#nu}, GeV, Interactions,  , GENIEAr23 BNB CC-INC",
            "Bins": [160, 0, 8], // doesn't affect binning since VBins is activated
            "VBins":[true,[0.0, 0.1, 0.2, 0.34, 0.4, 0.5, 0.6, 0.70, 0.8, 0.9, 1.0, 1.1, 1.200, 1.3, 1.40, 1.5, 1.6, 1.7, 1.8, 1.91, 2.0, 2.1, 2.2, 2.3, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.5, 5.0] ],
            "Name": "GENIEAR23_Enu_true",
            "logz": false,
        }
```

```
2D example config
```


<table>
  <!-- <tr> <b> 1D Plot </b> </tr> -->
  <tr> 
  <td> 
  <img width="896" height="472" alt="image" src="https://github.com/user-attachments/assets/086a7631-712a-463f-900a-1c0f10184757" />
  </td> 
  <td> 
  <!-- To add 2D plot image, just copy/paste it here (GitHub automatically adds necessary tags & hosts image) -->
  </td>
  </tr> 
  
  <tr> 
  <td>
  A plot, made using the 1D configuration above, showing the number of events (predicted by GENIE on Ar23) for different values of E<sub>&nu;</sub> using variable bin widths.
  </td> 
  <td>
  <!-- type 2D plot description here -->
  </td> 
  </tr>
</table>

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"stacks":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>
  
+ ```"File":```
+ ```"Type":```
+ ```"Cut":```
+ ```"Var1"```
+ ```"StackCuts":```
+ ```"":``` ....not finished...

</details>

<details>
<summary><b> Example </b></summary>
  
<!-- Example stacks entry and link to config file with another example -->

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

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"overlap":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>
  
+ 

</details>

<details>
<summary><b> Example </b></summary>
  
<!-- Example overlap entry and link to config file with another example -->

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

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"1DSame":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>
  
+ 

</details>

<details>
<summary><b> Example </b></summary>
  
<!-- Example 1DSame entry and link to config file with another example -->

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

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"Contour":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>
  
+ 

</details>


<details>
<summary><b> Example </b></summary>
  
<!-- Example Contour entry and link to config file with another example -->

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

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"ContourStyle":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>
  
+ 

</details>

<details>
<summary><b> Example </b></summary>
  
<!-- Example ContourStyle entry and link to config file with another example -->

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

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"quantiles":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>
  
+ 

</details>

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

> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
</details>


### Plotting with ```"2DRatio":```

***...still needs general description...***

<details>
<summary><b> Required & Supported&dagger; Key/Value Pairs </b></summary>

+ ```"File1":``` file (as a string) that acts as the ratio numerator
+ ```"File2":``` file (as a string) that acts as the ratio denominator
+ ```"Cut":``` see [making cuts](VariablesAndModes.md#making-cuts-with-variables-flags--modes) for more information
+ ```"Var1":``` x-axis variable
+ ```"Var2":``` y-axis variable
+ ```"AxisInfo":``` entered as a single string with entries separated by commas in the following form
  
  ```
    "x-axis variable, Var1 unit, y-axis variable, Var2 unit, plot title"
  ```
+ ```"BinsX":``` entered as a list in the following form
  
  ```
  [number of bins along x-axis, x-min, x-max]
  ```
+ ```"BinsY":``` follows the same convention as ```"BinsX":```
+ ```"Name":``` name that created files will be saved as (entered as a string without extensions)
+ &dagger;```"max":``` individual histogram maxes when saved (entered as a number)
+ ```"RatioMax":``` and ```"RatioMin":``` are the minimum and maximum ratio values
+ ```"logz":``` is a boolean that sets the ratio to a logarithmic scale when ```true```

</details>

<details>
<summary><b> Example </b></summary>
  
<!-- Example 2DRatio entry and link to config file with another example -->

> Note: In ```global```, raw file data was reweighted and area normalized using ```"FluxReweight":```, the color palette was set by adding ```"Palette": "kRainBow"```, and [PUfIN custom variable](VariablesAndModes.md#using-pufin-custom-variables) CosLep was activated by setting ```"TkiB": true```
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


> See [```PlotMain.json5```](../config/PlotMain.json5) for more examples of ```PlotMain.py``` plotting config entries.
  
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


