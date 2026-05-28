import os
import argparse
import ROOT
import random
import os
import pathlib
import shutil
import subprocess
import GlobalV

# # Set PUfIN OUT location
# export PUFIN_OUT=/data/t2k-nova/PUfINOutputs
# # Check for Generator Variables


# # Setup Python Alisis 
# alias Gen-Main="python $(realpath ./Gen-Main.py)"

def DirectorySetup(Generator, Target=None, Mode=None):
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
            raise ValueError(f"Can't write to {OutPath}")
    FilePaths = []
    for target in Targets:
        OnePath = OutPath + "/" + Generator.upper() + "/" + target + "/"
        FilePaths.append(OnePath)
        os.makedirs(OnePath, exist_ok=True)
    if Target:
        FilePaths = [OutPath + "/" + Generator.upper() + "/" + Target + "/"]
        Targets = [Target]

    print(f"Outputting to {FilePaths}")
    return FilePaths, Targets

def FlatFluxMaker():
    OutPath = os.environ.get("PUFIN_OUT")
    FluxPath = OutPath+"/"+"FlatFluxes"
    os.makedirs(FluxPath, exist_ok=True)
    FlatFluxNames = ["flat_flux_0-8GeV.root","flat_flux_8-30GeV.root","flat_flux_30-120GeV.root"]

    for flux in FlatFluxNames:
        f = FluxPath + "/" + flux
        if not os.path.exists(f):
            print(f"Missing {f}")
            part = flux.split("_")[2]        # "x-YGeV.root"
            numbers = part.split("-")     # ["X", "YGeV.root"]
            low = int(numbers[0])           # "X"
            high = int(numbers[1].split("GeV")[0])  # "Y"
            N = (high-low)*125000
            hist = ROOT.TH1D("FlatHist", "Flat Flux; Energy (GeV); Neutrinos", N, low, high)
            hist.SetLineWidth(2)
            hist.SetLineColor(804)
            for i in range(N):
                hist.SetBinContent(i+1,1.0)
            OutFile = ROOT.TFile(f,"RECREATE")
            hist.Write()
            OutFile.Close()
            print(f"Made Flat Flux: {f}")
        else:
            print(f"Flat Flux {flux} exists")
            
def gev_gen_genie(events: int, i: int):
    """Run one GENIE job and return its output filename."""
    print(f"Running GENIE job {i} with {events} events...")

    seed = random.randint(10000, 999999)
    GENIE_XSEC_TUNE = os.environ.get("GENIE_XSEC_TUNE", "")
    if not GENIE_XSEC_TUNE:
        raise ValueError("GENIE_XSEC_TUNE is not set")
    Tune = GENIE_XSEC_TUNE.split("_", 1)[0]
    
    out_name = (
        f"{Generator}{Version}_{Tune}_{Mode}_{flavor_label}_"
        f"{Erange}_{target_label}_{events}_P{i}.root"
    )

    exec_gen = f"""
    gevgen \
      --tune $GENIE_XSEC_TUNE \
      -t "{Target}" \
      -n {events} \
      -e {Emin},{Emax} \
      -f {Flux_directory}/full_flat_flux_{Emin}-{Emax}GeV.root,h1 \
      -p {Flavor} \
      --event-generator-list {Mode} \
      --seed {seed} \
      -o {output_dir}/{out_name} \
      --cross-sections $GENIE_XSEC_FILE
    """
    subprocess.run(exec_gen, shell=True, executable="/bin/bash", check=True)

    return f"{output_dir}/{out_name}"


def gen_series(EventsPerJob: int, nJobs: int, output_dir: str, final_directory: str):
    """Generate GENIE files serially and return list of filenames."""
    output_path = pathlib.Path(output_dir)
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True)

    out_files = []
    
    GENIE_XSEC_TUNE = os.environ.get("GENIE_XSEC_TUNE", "")
    if not GENIE_XSEC_TUNE:
        raise ValueError("GENIE_XSEC_TUNE is not set")
    Tune = GENIE_XSEC_TUNE.split("_", 1)[0]

    for i in range(nJobs):
        out_file = gev_gen_genie(EventsPerJob, i)
        out_files.append(out_file)
        

        
    outFileName = f"Original_{Generator}{Version}_{Tune}_{Mode}_{flavor_label}_{Erange}_{target_label}"
    FinaloutFileName = f"{outFileName}_{Events}"

    final_genie = f"{output_dir}/{FinaloutFileName}.root"

    hadd_cmd = f'hadd -f -k "{final_genie}" ' + " ".join(f'"{f}"' for f in out_files)
    print(f"Running: {hadd_cmd}")
    subprocess.run(hadd_cmd, shell=True, check=True)
    
    final_copy = f"{final_dir}/{FinaloutFileName}.root"
    shutil.copy2(final_genie, final_copy)
    print(f"Copied final file to {final_copy}")
    
    return out_files, final_genie, final_copy

def gen_flatten(final_dir: str):
    """Prepare and flatten the final GENIE file in final_dir."""
    final_path = pathlib.Path(final_dir)

    original_files = sorted(final_path.glob("Original_*.root"))
    if len(original_files) == 0:
        raise FileNotFoundError(f"No Original_*.root file found in {final_dir}")
    if len(original_files) > 1:
        raise ValueError(f"Multiple Original_*.root files found in {final_dir}: {[f.name for f in original_files]}")

    original_file = original_files[0]
    original_name = original_file.name

    prep_name = original_name.replace("Original_", "Prep_", 1)
    flat_name = original_name.replace("Original_", "Flat_", 1)

    prep_file = final_path / prep_name
    flat_file = final_path / flat_name

    prepare_cmd = f"""
    PrepareGENIE \
      -i "{original_file}" \
      -t "{Target}" \
      -o "{prep_file}" \
      -f "{Flux_directory}/full_flat_flux_{Emin}-{Emax}GeV.root,h1"
    """
    print("Preparing GENIE file...")
    subprocess.run(prepare_cmd, shell=True, executable="/bin/bash", check=True)

    flatten_cmd = f"""
    nuisflat \
      -i "GENIE:{prep_file}" \
      -o "{flat_file}"
    """
    print("Flattening GENIE file...")
    subprocess.run(flatten_cmd, shell=True, executable="/bin/bash", check=True)

    if prep_file.exists():
        prep_file.unlink()
    print(f"Deleted {prep_file}")
    
    return str(flat_file)

def find_file_with_prefix(directory: str, prefix: str):
    matches = sorted(pathlib.Path(directory).glob(f"{prefix}*.root"))
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f"Multiple {prefix}*.root files found in {directory}: {[m.name for m in matches]}")
    return matches[0]

def MakeNeutCards(Tune, Targets, Events, Modes=None, Flavors=None):
    OutPath = os.environ.get("PUFIN_OUT")
    if not os.environ.get("NEUT_VERSION"):
        raise ValueError("NEUT_VERSION Environment Variable Not Defined")
    NeutVersion = str(os.environ.get("NEUT_VERSION")).replace(".","-")
    CardPath = OutPath+"/"+"NEUT"+"/"+"Cards"
    os.makedirs(CardPath, exist_ok=True)
    CardNames = []
    if not Modes:
        Modes = ["NC", "CC"]
    if not Flavors:
        Flavors = ["NuMu","NuMuBar","NuE","NuEBar"]
    for Target in Targets:
        for Mode in Modes:
            for Flavor in Flavors:
                CName = f"NEUT{NeutVersion}_{Tune}_{Mode}{Flavor}_{Target}.card"
                CardNames.append(CName)
                f = CardPath + "/" + CName
                
                if not os.path.exists(f):
                    print(f"Missing {f}")
                    CardString = ""
                    if not GlobalV.NeutCardTunes.get(Tune):
                        raise ValueError(f"Tune {Tune} Does Not Exist")
                    CardString = CardString + GlobalV.NeutCardTunes.get(Tune)
                    match Flavor:
                        case "NuMu":
                            CardString = CardString + f"\nEVCT-NEVT {Events}\n"
                        case "NuMuB":
                            SpecialEvent = int(Events/10)
                            if SpecialEvent < 2000:
                                SpecialEvent = 2000
                            CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                        case "NuE":
                            SpecialEvent = int(Events/100)
                            if SpecialEvent < 2000:
                                SpecialEvent = 2000
                            CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                        case "NuEB":
                            SpecialEvent = int(Events/100)
                            if SpecialEvent < 2000:
                                SpecialEvent = 2000
                            CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                        case _:
                            raise ValueError("UNKNOWN FLAVOR")
                    CardString = CardString + GlobalV.NeutCardModes.get(Mode)
                    CardString = CardString + GlobalV.NeutCardFlavors.get(Flavor)
                    CardString = CardString + GlobalV.NeutCardTargets.get(Target)
                    # print(CardString)
                    if NeutVersion == "5-6-4" and Target == "Titanium" and Tune == "Prod7E":
                        # TI is dumb in 5-6-4
                        print("Special Ti Problem in 5.6.4")
                        CardString.replace("NEUT-MDL2P2H 2","NEUT-MDL2P2H 1")
                        CardString.replace("NEUT-MDLQE 402","NEUT-MDLQE 002")
                    with open(f, "w") as file:
                        file.write(CardString)
                    # print("Mode")
                    # print(GlobalV.NeutCardModes.get(Mode))
                    # print("Nu Type")
                    # print(GlobalV.NeutCardFlavors.get(Flavor))
                    # print("Target")
                    # print(GlobalV.NeutCardTargets.get(Target))  
                    print(f"Made Neut Card: {f}")
                else:
                    print(f"Neut Card {CName} exists")



def Generate(Generator, Tune, Events, Target=None, Mode=None, Multi=None):
    # Grab/Make paths for output generated files
    FilePath,Targets = DirectorySetup(Generator)

    #Check if FF exist, make them if not
    FlatFluxMaker()


    print("! UNDER CONSTRUCTION !")


if __name__ =="__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-a", required=True)
    # parser.add_argument("-b", required=True)
    # args = parser.parse_args()
    # Generate()
    
    Mode = "NC"
    #Target = "1000060120[1.0]"
    Flavor = "12"
    # target_key = "C"
    # target_info = GlobalV.NovaTargets[target_key]
    # Target = target_info["pdg"]
    # target_label = target_info["label"]
    # target_name = target_info["name"]
    flavor_label = GlobalV.NuPDGs[int(Flavor)]
    Generator = "Genie"
    Emin = "0"
    Emax = "8"
    Erange = f"{Emin}-{Emax}"
    nJobs = 2
    Events = 200
    EventsPerJob = Events//nJobs
    Version = "3-6-0"
    Flux_directory = "/data/t2k-nova/fluxes"
    output_dir = "/data/t2k-nova/KristenGen/MultiGen"
    
    file_paths, targets = DirectorySetup(Generator, Mode=Mode)
    
    for target_name, final_dir in zip(targets, file_paths):
        for _, info in GlobalV.NovaTargets.items():
            if info["name"] == target_name:
                Target = info["pdg"]
                target_label = info["label"]
                break
        else:
            raise ValueError(f"No target info found for {target_name}")
        
        flat_file = find_file_with_prefix(final_dir, "Flat_")
        original_file = find_file_with_prefix(final_dir, "Original_")

        if flat_file is not None:
            print(f"Skipping {target_name}: found flat file {flat_file.name}")
            continue

        if original_file is not None:
            print(f"Found original file for {target_name}: {original_file.name}")
            print(f"Flattening only for {target_name}")
            gen_flatten(final_dir)
            continue

        print(f"No existing files found for {target_name}")
        print(f"Generating and flattening for {target_name}")
    
        genie_files, final_genie, final_copy = gen_series(EventsPerJob, nJobs, output_dir, final_dir)
        flat_file = gen_flatten(final_dir)

