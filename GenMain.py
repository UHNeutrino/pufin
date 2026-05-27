import os
import argparse

def directorySetup(Generator, Tune, Events, Target=None, Mode=None):
    OutPath = os.environ.get("PUFIN_OUT")
    Targets = []
    match Generator.lower():
        case "neut":
            Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium"]
        case "genie":
            Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium", "Chlorine"]
        case _:
            raise ValueError("Generator has to be NEUT or GENIE")

    try:
        open(OutPath+"/"+"test", 'a').close()  # equivalent to touch
        os.remove(OutPath+"/"+"test")
    except OSError as e:
            print(f"Error: {e}")
    FilePaths = []
    for target in Targets:
        OnePath = OutPath + "/" + Generator.upper() + "/" + target + "/"
        FilePaths.append(OnePath)
        os.makedirs(OnePath, exist_ok=True)
    

    print(f"Outputting to {FilePaths}")
    return FilePaths

def Generate():
    print("! UNDER CONSTRUCTION !")


if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", required=True)
    parser.add_argument("-b", required=True)
    args = parser.parse_args()
    Generate()