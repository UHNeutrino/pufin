import json5
import subprocess
import sys
import os

###########################################################
############ Use MultiPlotter.py within PUfIN #############
# with TemplateConfig and MultiPlt config in PUfIN/config #
## To run in terminal: "python MultiPlotter.py MultiPlt" ##
###########################################################

##### Functions #####
# Calls PlotMain.py with given config file as arg[1]
def CallPlotMain(file):
    result = subprocess.run(
        ["python", "PlotMain.py", file], 
        capture_output=True, 
        text=True
        )
    print(f"Plotting using {file}.json config")
    print("Output:", result.stdout)
    print("Errors:", result.stderr)

# replaces {{VAR}} in TemplateConfig with its value
def ReplaceVariable(config, variable, value):
    # to replace booleans (keeps all json's lowercase form)
    if isinstance(value, bool):
        replacement = "true" if value else "false"
    else:
        replacement = str(value)
    return config.replace("{{" + variable + "}}", replacement)

# makes config name from level tags and positions (When making configs)
def CreateConfigName(ConfigTag, LevelTags, LevelPositions):
    # if len(LevelTags) != 4 or len(LevelPositions) != 4:
    #     raise ValueError("LevelTags and LevelPositions must each contain 4 items")
    # # --> Tag ValueErrors in prelude *should* make this error code obsolete

    ordered_tags = ["", "", "", ""]
    for tag, position in zip(LevelTags, LevelPositions):
        if not isinstance(position, int) or not 0 <= position < 4:
            raise ValueError("Level positions must be integers from 0 through 3")
        if ordered_tags[position]:
            raise ValueError("Level positions must be unique")
        ordered_tags[position] = tag

    return ConfigTag + "".join(
        "_" + str(tag) for tag in ordered_tags if str(tag)
    )

def ConfigNameForIndices(indices): # indices = (i,j,k,l)
    levels = [
        (Level_1, Tag_1),
        (Level_2 if Level_2 else {}, Tag_2 if Level_2 else ["", 1]),
        (Level_3 if Level_3 else {}, Tag_3 if Level_3 else ["", 2]),
        (Level_4 if Level_4 else {}, Tag_4 if Level_4 else ["", 3]),
    ]
    tags = [
        GetLevelTag(level, tag_definition, index) if level else ""
        for (level, tag_definition), index in zip(levels, indices)
    ]
    positions = [tag_definition[1] for _, tag_definition in levels]
    return CreateConfigName(MultiConfigTag, tags, positions)

def GetLevelTag(level, tag_definition, index):
    return level[tag_definition[0]][index]

# raise error if value lengths within a level don't match
def CheckLengths(dictionary):
    lengths = [len(value) for value in dictionary.values()]
    if lengths and len(set(lengths)) != 1:
        raise ValueError(
            f"Lengths of value lists assigned to:\n{dictionary.keys()} \nmust match")

# stashes config file without deleting (copy into stash directory)
def StashConfigFiles(directory, config_name, config_text):
    os.makedirs(directory, exist_ok=True)
    stash_path = os.path.join(directory, f"{config_name}.json5")
    with open(stash_path, "w") as f:
        f.write(config_text)
    print(f"Stashed {config_name} in {directory}")

# moves existing files 
def MoveConfigFiles(start_directory, end_directory, file):
    os.makedirs(end_directory, exist_ok=True)
    result = subprocess.run(
        [
            "mv",
            os.path.join(start_directory, file),
            os.path.join(end_directory, file),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    # print(f"Moved {file} to directory {end_directory}")


def MakeConfigFiles(): 
    # Makes and stores config files in PUfIN for all levels
    # in MultiPlt config (and/or calls StashConfigFiles).
    # !!!!!!! Should be refactored for brevity/readability !!!!!!!
    num_level_1 = len(next(iter(Level_1.values())))
    # len(next(iter(Level_n.values()))) gives the length of the values (lists) in Level_n
    if Level_2:
        num_level_2 = len(next(iter(Level_2.values())))

        if Level_3:
            num_level_3 = len(next(iter(Level_3.values())))

            if Level_4:
                num_level_4 = len(next(iter(Level_4.values())))
                # Make one config for every combination of ALL 4 levels

                for i in range(num_level_1):
                    for j in range(num_level_2):
                        for k in range(num_level_3):
                            for l in range(num_level_4):
                                with open(f"{script_dir}config/{TemplateConfig}", "r") as f:
                                    config_text = f.read()

                                for variable, values, in Level_1.items():
                                    config_text = ReplaceVariable(config_text, variable, values[i])

                                for variable, values, in Level_2.items():
                                    config_text = ReplaceVariable(config_text, variable, values[j])

                                for variable, values, in Level_3.items():
                                    config_text = ReplaceVariable(config_text, variable, values[k])

                                for variable, values, in Level_4.items():
                                    config_text = ReplaceVariable(config_text, variable, values[l])

                                LevelTags = [
                                    GetLevelTag(Level_1, Tag_1, i),
                                    GetLevelTag(Level_2, Tag_2, j),
                                    GetLevelTag(Level_3, Tag_3, k),
                                    GetLevelTag(Level_4, Tag_4, l),
                                ]
                                LevelPositions = [
                                    Tag_1[1], Tag_2[1], Tag_3[1], Tag_4[1]
                                ]

                                config_name = CreateConfigName(MultiConfigTag, LevelTags, LevelPositions)
                                config_path = f"{script_dir}config/{config_name}.json5"
                                ConfigList.append(config_name)

                                with open(config_path, "w") as f:
                                    f.write(config_text)

                                print(f"Created {config_path}") 

                                if StashConfigs:
                                    StashConfigFiles(StashConfigs, config_name, config_text)                              
            else: 
                # Make one config for every Level_1/Level_2/Level_3 combination
                for i in range(num_level_1):
                    for j in range(num_level_2):
                        for k in range(num_level_3):
                            with open(f"{script_dir}config/{TemplateConfig}", "r") as f:
                                config_text = f.read()

                                for variable, values, in Level_1.items():
                                    config_text = ReplaceVariable(config_text, variable, values[i])

                                for variable, values, in Level_2.items():
                                    config_text = ReplaceVariable(config_text, variable, values[j])

                                for variable, values, in Level_3.items():
                                    config_text = ReplaceVariable(config_text, variable, values[k])

                                LevelTags = [
                                    GetLevelTag(Level_1, Tag_1, i),
                                    GetLevelTag(Level_2, Tag_2, j),
                                    GetLevelTag(Level_3, Tag_3, k),
                                    "",
                                ]
                                LevelPositions = [
                                    Tag_1[1], Tag_2[1], Tag_3[1], 3
                                ]
                                config_name = CreateConfigName(
                                    MultiConfigTag, LevelTags, LevelPositions
                                )
                                config_path = f"{script_dir}config/{config_name}.json5"
                                ConfigList.append(config_name)

                                with open(config_path, "w") as f:
                                    f.write(config_text)

                                print(f"Created {config_path}")

                                if StashConfigs:
                                    StashConfigFiles(StashConfigs, config_name, config_text)                               
        else:
            # Make one config for every Level_1/Level_2 combination
            for i in range(num_level_1):
                for j in range(num_level_2):
                    with open(f"{script_dir}config/{TemplateConfig}", "r") as f:
                        config_text = f.read()

                    for variable, values in Level_1.items():
                        config_text = ReplaceVariable(config_text, variable, values[i])

                    for variable, values in Level_2.items():
                        config_text = ReplaceVariable(config_text, variable, values[j])

                    LevelTags = [
                        GetLevelTag(Level_1, Tag_1, i),
                        GetLevelTag(Level_2, Tag_2, j),
                        "",
                        "",
                    ]
                    LevelPositions = [Tag_1[1], Tag_2[1], 2, 3]
                    config_name = CreateConfigName(
                        MultiConfigTag, LevelTags, LevelPositions
                    )
                    config_path = f"{script_dir}config/{config_name}.json5"
                    ConfigList.append(config_name)

                    with open(config_path, "w") as f:
                        f.write(config_text)

                    print(f"Created {config_path}")

                    if StashConfigs:
                        StashConfigFiles(StashConfigs, config_name, config_text)

    else:
        # Make one config for each Level_1 entry when no other levels exist
        for i in range(num_level_1):
            with open(f"{script_dir}config/{TemplateConfig}", "r") as f:
                config_text = f.read()

            for variable, values in Level_1.items():
                config_text = ReplaceVariable(config_text, variable, values[i])

            LevelTags = [GetLevelTag(Level_1, Tag_1, i), "", "", ""]
            LevelPositions = [Tag_1[1], 1, 2, 3]
            config_name = CreateConfigName(
                MultiConfigTag, LevelTags, LevelPositions
            )
            config_path = f"{script_dir}config/{config_name}.json5"
            ConfigList.append(config_name)

            with open(config_path, "w") as f:
                f.write(config_text)

            print(f"Created {config_path} config")

            if StashConfigs:
                StashConfigFiles(StashConfigs, config_name, config_text)

# Makes Config Names only and add to ConfigList
def MakeConfigNames():
    # !!! Very repetetive, will try to refactor using sub-functions !!!
    # Raises ValueError: Level positions must be unique
    num_level_1 = len(next(iter(Level_1.values())))

    if Level_2:
        num_level_2 = len(next(iter(Level_2.values())))

        if Level_3:
            num_level_3 = len(next(iter(Level_3.values())))

            if Level_4: # Levels 1-4 (ALL)
                num_level_4 = len(next(iter(Level_4.values())))

                for i in range(num_level_1):
                    for j in range(num_level_2):
                        for k in range(num_level_3):
                            for l in range(num_level_4):
                                config_name = ConfigNameForIndices((i, j, k, l))
                                ConfigList.append(config_name)
            else: # Levels 1-3
                for i in range(num_level_1):
                    for j in range(num_level_2):
                        for k in range(num_level_3):
                            config_name = ConfigNameForIndices((i, j, k, 0))
                            ConfigList.append(config_name)
        else: # Levels 1&2
            for i in range(num_level_1):
                for j in range(num_level_2):
                    config_name = ConfigNameForIndices((i, j, 0, 0))
                    ConfigList.append(config_name)
    else: # Level 1 only
        for i in range(num_level_1):
            config_name = ConfigNameForIndices((i, 0, 0, 0))
            ConfigList.append(config_name)

############################################################################

## MultiPlottter ##

script_path = os.path.realpath(__file__)

if len(sys.argv) < 2:
    raise ValueError("Please specify which config file to use in /config")

Jsonfile = sys.argv[1].removesuffix(".json5")

script_dir = script_path.replace("MultiPlotter.py","")

# Opens MultiPlt config file and loads the MultiPlotter dictionary
with open(f"{script_dir}config/{Jsonfile}.json5") as f:
    cfg = json5.load(f)

if not (mp := cfg.get("MultiPlotter")):
    raise ValueError(f"MultiPlotter dictionary not present in config/{Jsonfile}")

Funct = False # intitialize functionality check

# get Retrieve/Stash directories if they exist
if RetrieveConfigs := mp.get("RetrieveConfigs"): # directory
    Funct = True
if StashConfigs := mp.get("StashConfigs"): # directory
    Funct = True

# Read required information from MultiPlt config file
if MakePlots := mp.get("MakePlots"): # bool
    Funct = True
if MakeConfigs := mp.get("MakeConfigs"): # bool
    Funct = True

if not (Funct):
    print("All functionality = false...")
    print("Task failed successfully")
    sys.exit(0)

if not (TemplateConfig := mp.get("TemplateConfig")):
    raise ValueError(f"TemplateConfig not present in config/{Jsonfile}")

if not (MultiConfigTag := mp.get("MultiConfigTag")):
    raise ValueError(f"MultiConfigTag not present in config/{Jsonfile}")

# assign levels to variables and check presence of required level
if Tag_1 := mp.get("Tag_1"):
    if not (Level_1 := mp.get("Levels").get("Level_1")):
        raise ValueError(f"Level_1 dictionary must be present in config/{Jsonfile}")
else:
    raise ValueError(f"Tag_1 must be present in config/{Jsonfile}")
CheckLengths(Level_1)


# Get optional levels & tags
Level_2 = None # initializing nrqd tags (reduces NameErrors later)
Level_3 = None
Level_4 = None

if Level_2 := mp.get("Levels").get("Level_2"):
    if not (Tag_2 := mp.get("Tag_2")):
        raise ValueError(f'Tag_2 must be present in config/{Jsonfile} if using Level_2')
    CheckLengths(Level_2)
    
if Level_3 := mp.get("Levels").get("Level_3"):
    if not (Tag_3 := mp.get("Tag_3")):
        raise ValueError(f'Tag_3 must be present in config/{Jsonfile} if using Level_3')
    CheckLengths(Level_3)
    
if Level_4 := mp.get("Levels").get("Level_4"):
    if not (Tag_4 := mp.get("Tag_4")):
        raise ValueError(f'Tag_4 must be present in config/{Jsonfile} if using Level_4')
    CheckLengths(Level_4)


ConfigList = [] # Initialize config list (used for most functionality)

# Retrieve Configs

## Moves configs out of retreival directory and into PUfIN/config
if RetrieveConfigs:
    if MakeConfigs:
        # overwrite waring
        print("MakeConfigs is in MultiPlt config")
        print("Running MakeConfigs will overwrite these configs after they are pulled from")
        print(f"retrieval directory {RetrieveConfigs}")
        while True:
                answer = input(
                    "Are you sure you wish to proceed? (Y/N): "
                    ).strip().upper()
                if answer == "Y":
                    break
                elif answer == "N":
                    while True:
                        answer = input(
                            "Continue running MultiPlotter.py with MakeConfigs = False? (Y/N): "
                            ).strip().upper()
                        if answer == "N":
                            sys.exit(0)
                        if answer == "Y":
                            print("Setting StashConfigs = False...")
                            StashConfigs = False
                            break
                        print("Please enter Y or N.")
                    break 
                else:
                    print("Please enter Y or N.")
    else:
        # make config NAMES ONLY and add to ConfigList
        print("Collecting config names... ")
        MakeConfigNames()

        # move config files from old directory into PUfIN/config 
        for config_name in ConfigList:
            new_directory = os.path.join(script_dir, "config")
            MoveConfigFiles(RetrieveConfigs, new_directory, f"{config_name}.json5")


# Make Configs  

if MakeConfigs: 
    MakeConfigFiles()


# Make Plots (references configs constructed with config/level tags in MultiPlt config)

if MakePlots:
    if not MakeConfigs:
        MakeConfigNames()

    # plots configs in ConfigList using PlotMain.py
    for config in ConfigList:
        CallPlotMain(config)


# Stash Configs

## Move configs out of PUfIN/config and into a Stash directory 
if StashConfigs:
    # if StashConfigs and MakeConfigs, configs were already 
    # added to Stash directory when MakeConfigs ran
    if MakeConfigs:
        print(f"Configs stashed in {StashConfigs}")
        print("are being removed from PUfIN/configs...")
        # Checks if the file exists before attempting to delete it
        # Deletes configs from PUfIN/config:
        for config_file in ConfigList:
            file_path = f"{script_dir}config/{config_file}.json5"
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        if not RetrieveConfigs:
            # make config NAMES ONLY and add to ConfigList
            print("Collecting config names... ")
            MakeConfigNames()

        # move config files from PUfIN/config into stash directory (StashConfigs)
        for config_name in ConfigList:
            old_directory = os.path.join(script_dir, "config")
            MoveConfigFiles(old_directory, StashConfigs, f"{config_name}.json5")


# Exit message
print("-------------------------------")
print("Task(s) completed successfully:")
print("-------------------------------")
if RetrieveConfigs:
    print("Retrieve Configs")
if MakeConfigs:
    print("Make Configs")
if MakePlots:
    print("Make Plots")
if StashConfigs:
    print("Stash Configs")
