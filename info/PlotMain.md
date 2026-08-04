# PlotMain.py
> ...under construction...

## Setup
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
  (.venv) [username@domain:~]$ pip install json5 numpy
  ```
  + To point the interpreter in VSCode to the venv you just created, navigate to the Command Palette using <kbd> Ctrl </kbd> + <kbd> Shift </kbd> + <kbd> P </kbd> , type and select ```Python: Select Interpreter```, and enter or select ```your_venv_folder/bin/python```

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
> Above plotting method is outdated
<!-- Add new plotting method/config management instructions -->
