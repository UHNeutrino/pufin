# file: WeightMain.py

import src.PufinClasses as pc
import os
import sys
import json5

def main():
    script_path = os.path.realpath(__file__)
    if sys.argv[1]:
        argString = sys.argv[1]
        if ".json5" in argString:
            argString = argString.replace(".json5","")
        Jsonfile = argString
    else:
        raise ValueError("Please specify which config file to use in /config")


    script_dir = script_path.replace("WeightMain.py","")
    f = open(f'{script_dir}config/{Jsonfile}.json5')
    config = json5.load(f)

    
    uhmc = pc.UHMC(config)
    uhmc.MakeDF()
    uhmc.MakeExpWeights()
    if config.get("saveDF") != None:
        print(f"Saving dataframe to {config['saveDF']}")
        uhmc.df.Snapshot("FlatTree_VARS",config["saveDF"])
    if config.get('saveEnu') != None:
        print(f"Saving Enu true Spectrum to {config['saveEnu']}")
        uhmc.PlotEnuTrue(config['saveEnu'])


if __name__ == "__main__":
    main()
    print("Finished Weight Main")
    
### For UH_1: export PUFIN_OUT=/data/t2k-nova/PUfINOutputs
### For carya: export PUFIN_OUT=/project/cherdack/t2k-nova/PUfINOutPuts
### python WeightMain.py KristenWeightMain