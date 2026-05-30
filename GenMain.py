import os
import argparse
import ROOT
import random
import pathlib
import shutil
import subprocess
import GlobalV
import glob

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
    # if Target:
    #     FilePaths = [OutPath + "/" + Generator.upper() + "/" + Target + "/"]
    #     Targets = [Target]
        
    if Target:
        OnePath = OutPath + "/" + Generator.upper() + "/" + Target + "/"
        os.makedirs(OnePath, exist_ok=True)
        FilePaths = [OnePath]
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


def gen_series(Events: int, output_dir: str, final_directory: str):
    """Generate GENIE files serially and return list of filenames."""
    output_path = pathlib.Path(output_dir)
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True)

    out_files = []
    
    GENIE_XSEC_TUNE = os.environ.get("GENIE_XSEC_TUNE", "")
    if not GENIE_XSEC_TUNE:
        raise ValueError("GENIE_XSEC_TUNE is not set")
    TuneLabel = GENIE_XSEC_TUNE.split("_", 1)[0]
    
    EventsPerJob = 50000
    if Events % EventsPerJob != 0:
        raise ValueError(
            f"GENIE Events must be a multiple of {EventsPerJob}. Got {Events}."
        )
    nJobs = Events//EventsPerJob

    for i in range(nJobs):
        out_file = gev_gen_genie(EventsPerJob, i)
        out_files.append(out_file)
        

    EventsLabel = f"{Events:.0e}".replace("+0", "").replace("+", "")    
    outFileName = f"Original_{Generator}{Version}_{TuneLabel}_{Mode}_{flavor_label}_{Erange}_{target_label}"
    FinaloutFileName = f"{outFileName}_{EventsLabel}"

    final_genie = f"{output_dir}/{FinaloutFileName}.root"

    hadd_cmd = f'hadd -f -k "{final_genie}" ' + " ".join(f'"{f}"' for f in out_files)
    print(f"Running: {hadd_cmd}")
    subprocess.run(hadd_cmd, shell=True, check=True)
    
    final_copy = f"{final_directory}/{FinaloutFileName}.root"
    shutil.copy2(final_genie, final_copy)
    print(f"Copied final file to {final_copy}")
    
    return out_files, final_genie, final_copy

def gen_flatten(original_file: str):
    """Prepare and flatten one specific GENIE file."""
    original_path = pathlib.Path(original_file)
    if not original_path.exists():
        raise FileNotFoundError(f"Missing original file: {original_file}")

    final_dir = original_path.parent
    original_name = original_path.name

    prep_name = original_name.replace("Original_", "Prep_", 1)
    flat_name = original_name.replace("Original_", "Flat_", 1)

    prep_file = final_dir / prep_name
    flat_file = final_dir / flat_name

    prepare_cmd = f"""
    PrepareGENIE \
      -i "{original_path}" \
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
    return str(flat_file)

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
                    
def find_expected_file(directory: str, filename: str):
    file_path = pathlib.Path(directory) / filename
    if file_path.exists():
        return file_path
    return None
                    
def GenerateGenie(Generator, Events, Tune=None, Target=None, Mode=None, Flavor=None, Multi=None):
    FilePaths, Targets = DirectorySetup(Generator)

    if Target is not None:
        Targets = [Target]
        FilePaths, Targets = DirectorySetup(Generator, Target=Target)
        
    input_flavor = Flavor

    if Mode is None:
        Modes = ["CC", "NC"]
    else:
        Modes = [Mode]
    for Mode in Modes:
        if input_flavor is None:
            if Mode == "NC":
                Flavors = ["14", "-14"]
            elif Mode == "CC":
                Flavors = ["12", "-12", "14", "-14"]
            else:
                Flavors = ["12", "-12", "14", "-14"]
        else:
            Flavors = [str(input_flavor)]
    
        allowed_flavors = {"12", "-12", "14", "-14"}
        for flav in Flavors:
            if flav not in allowed_flavors:
                raise ValueError(
                    f"Flavor must be one of 12, -12, 14, -14. Got {flav}."
                )

        for flavor in Flavors:
            flavor_label = GlobalV.NuPDGs[int(flavor)]

            for target_name, final_dir in zip(Targets, FilePaths):
                for _, info in GlobalV.NovaTargets.items():
                    if info["name"] == target_name:
                        TargetPDG = info["pdg"]
                        target_label = info["label"]
                        break
                else:
                    raise ValueError(f"No target info found for {target_name}")

                if Mode == "CC":
                    energy_ranges = [("0", "8")]
                elif Mode == "NC":
                    energy_ranges = [("0", "8"), ("8", "30"), ("30", "120")]
                else:
                    raise ValueError(f"Unsupported GENIE mode: {Mode}")

                for Emin, Emax in energy_ranges:
                    Erange = f"{Emin}-{Emax}GeV"
                    #EventsPerJob = Events // nJobs ###############################################################
                    print(
                        f"CHECK: target={target_name}, Mode={Mode}, Flavor={Flavor}, "
                        f"flavor_label={flavor_label}, Erange={Erange}"
                    )
                    GENIE_VERSION = os.environ.get("GENIE_VERSION", "")
                    if not GENIE_VERSION:
                        raise ValueError("GENIE_VERSION is not set")
                    Version = GENIE_VERSION

                    GENIE_XSEC_TUNE = os.environ.get("GENIE_XSEC_TUNE", "")
                    if Tune is None:
                        if not GENIE_XSEC_TUNE:
                            raise ValueError("Tune not provided and GENIE_XSEC_TUNE is not set")
                        TuneLabel = GENIE_XSEC_TUNE.split("_", 1)[0]
                    else:
                        TuneLabel = Tune
                    EventsLabel = f"{Events:.0e}".replace("+0", "").replace("+", "")
                    base_name = (
                        f"{Generator}{Version}_{TuneLabel}_{Mode}_{flavor_label}_{Erange}_{target_label}_{EventsLabel}"
                    )
                    expected_original = f"Original_{base_name}.root"
                    expected_flat = f"Flat_{base_name}.root"

                    original_file = find_expected_file(final_dir, expected_original)
                    flat_file = find_expected_file(final_dir, expected_flat)

                    print(f"expected_original = {expected_original}")
                    print(f"expected_flat     = {expected_flat}")
                    print(f"found original?   = {original_file is not None}")
                    print(f"found flat?       = {flat_file is not None}")

                    globals()["Target"] = TargetPDG
                    globals()["target_label"] = target_label
                    globals()["flavor_label"] = flavor_label
                    globals()["Mode"] = Mode
                    globals()["Flavor"] = flavor
                    globals()["Emin"] = Emin
                    globals()["Emax"] = Emax
                    globals()["Erange"] = Erange
                    globals()["Generator"] = Generator
                    globals()["Version"] = Version
                    globals()["output_dir"] = "/data/t2k-nova/KristenGen/MultiGen"
                    globals()["Flux_directory"] = "/data/t2k-nova/fluxes"
                    globals()["FinaloutFileName"] = f"Original_{base_name}"

                    if flat_file is not None:
                        print(f"Skipping {target_name} {Mode} {Flavor} {Erange}: found {flat_file.name}")
                        continue

                    if original_file is not None:
                        print(f"Flattening existing file: {original_file.name}")
                        gen_flatten(str(original_file))
                        continue

                    print(f"Generating {target_name} {Mode} {Flavor} {Erange}")
                    genie_files, final_genie, final_copy = gen_series(Events, output_dir, final_dir)
                    gen_flatten(final_copy)
    
def Generate(Generator, Events, Tune=None, Target=None, Mode=None, Flavor=None, Multi=None):
    # Grab/Make paths for output generated files
    FilePath,Targets = DirectorySetup(Generator)
    if Generator.lower() == "genie":
        return GenerateGenie(Generator, Events, Tune, Target, Mode, Flavor, Multi)
    elif Generator.lower() == "neut":
        raise NotImplementedError("GenerateNeut is not implemented yet")
    else:
        raise ValueError("Generator must be 'Genie' or 'Neut'")

    #Check if FF exist, make them if not
    # FlatFluxMaker()


    print("! UNDER CONSTRUCTION !")


if __name__ =="__main__":
# screen 
# then leave it with ctrl+a+d
# and reattach it with screen -r <name of screen>

# # Set PUfIN OUT location
# export PUFIN_OUT=/data/t2k-nova/PUfINOutputs

#     python GenMain.py \
#   --generator Genie \
#   --events 100000 
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--generator", required=True)
    parser.add_argument("--events", required=True, type=int)
    parser.add_argument("--tune", default=None)
    parser.add_argument("--target", default=None)
    parser.add_argument("--mode", default=None)
    parser.add_argument("--flavor", default=None)
    parser.add_argument("--multi", default=None)

    args = parser.parse_args()

    Generate(
        Generator=args.generator,
        Events=args.events,
        Tune=args.tune,
        Target=args.target,
        Mode=args.mode,
        Flavor=args.flavor,
        Multi=args.multi,
    )
    
    # Tune = "Prod7E"
    # Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium"]
    # Events = 1000
    # MakeNeutCards(Tune, Targets,Events)
    # GenNeutXsec(Tune,Targets)
    
   