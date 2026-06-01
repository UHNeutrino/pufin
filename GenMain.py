import os
import argparse
import ROOT
import random
import pathlib
import shutil
import subprocess
import GlobalV
import glob


# PDGs = {
#     "1000010010[1.0]": "H1",
#     "1000060120[1.0]": "C12",
#     "1000080160[1.0]": "O16",
#     "1000170350[1.0]": "Cl35",
#     "1000220480[1.0]": "Ti48",
#     "12": "NuE",
#     "-12": "NuEBar",
#     "14": "NuMu",
#     "-14": "NuMuBar",
# }

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
    FlatFluxNames = ["flat_flux_0-8GeV.root","flat_flux_8-30GeV.root","flat_flux_30-120GeV.root"]
    Erange = "0-8GeV"

    if not Modes:
        Modes = ["NC", "CC"]
    if not Flavors:
        Flavors = ["NuMu","NuMuBar","NuE","NuEBar"]
    for Target in Targets:
        for Mode in Modes:
            for Flavor in Flavors:
                CNameList = []
                if (Mode == "NC"):
                    if (Flavor == "NuE" or Flavor == "NuEBar"):
                        continue
                    for Name in FlatFluxNames:
                        part = Name.split("_")[2]        # "x-YGeV.root"
                        ErangeNC = part.replace(".root","")
                        CName0 = f"NEUT{NeutVersion}_{Tune}_{Mode}_{Flavor}_{ErangeNC}_{Target}_{Events}.card"
                        CardNames.append(CName0) #one is to iterate over, one is to save at the end
                        CNameList.append(CName0)
                else:
                    CName0 = f"NEUT{NeutVersion}_{Tune}_{Mode}_{Flavor}_{Erange}_{Target}_{Events}.card"
                    CardNames.append(CName0)
                    CNameList.append(CName0)
                for CName in CNameList:
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
                            case "NuMuBar":
                                SpecialEvent = int(Events/20)
                                if SpecialEvent < 2000:
                                    SpecialEvent = 2000
                                CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                            case "NuE":
                                SpecialEvent = int(Events/200)
                                if SpecialEvent < 2000:
                                    SpecialEvent = 2000
                                CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                            case "NuEBar":
                                SpecialEvent = int(Events/2000)
                                if SpecialEvent < 2000:
                                    SpecialEvent = 2000
                                CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                            case _:
                                raise ValueError("UNKNOWN FLAVOR")
                        CardString = CardString + GlobalV.NeutCardModes.get(Mode)
                        CardString = CardString + GlobalV.NeutCardFlavors.get(Flavor)
                        CardString = CardString + GlobalV.NeutCardTargets.get(Target)
                        tempErange = CName.split("_")[-3]
                        if (tempErange != "0-8GeV"):
                            print("NOT 0-8GeV")
                            CardString = CardString.replace("EVCT-FILENM 'full_flat_flux_0-8.0GeV.root'",f"EVCT-FILENM 'full_flat_flux_{tempErange}.root'" )


                        if(NeutVersion == "5-6-4" or NeutVersion == "5-9-0") and Target == "Titanium" and Tune == "Prod7E":
                            # TI is dumb in 5-6-4
                            print("Special Ti Problem in 5.6.4. and 5.9.0")
                            CardString = CardString.replace("NEUT-MDL2P2H 2","NEUT-MDL2P2H 1")
                            CardString = CardString.replace("NEUT-MDLQE 402","NEUT-MDLQE 002")
                        # print(CardString)
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
    return CardNames

def GenNeutXsec(Tune, Targets, FullCardPath=None):
    #Grabs every neut card from FullCardPath or naming scheme and then checks for the corespondinig xsec histogram
    #If the histogram is missing, then it generates them with dumpmtotpauC
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"
    if not os.environ.get("NEUT_VERSION"):
        raise ValueError("NEUT_VERSION Environment Variable Not Defined")
    NeutVersion = str(os.environ.get("NEUT_VERSION")).replace(".","-")
    CardDir = OutPath + "/NEUT/Cards"
    XsecDir = OutPath + "/NEUT/Xsecs"
    os.makedirs(XsecDir, exist_ok=True)

    # delete temp dir if it exists from a previous run
    shutil.rmtree(tmpdir, ignore_errors=True)
    # create fresh temp dir
    os.makedirs(tmpdir)

    if FullCardPath:
        print("Using Single Card Name Given")
        XsecName = FullCardPath.split("/")[-1].replace("card","root")
        if "CC" in XsecName:
            XsecName = XsecName.replace("CC","")
        if "NC" in XsecName:
            XsecName = XsecName.replace("NC","")
        XsecName = XsecName.replace(".root","_XSECHIST.root")
        XsecPath = XsecDir+"/"+ XsecName
        # print(XsecName)  
        if not os.path.exists(XsecPath):
            # copy file to temp dir with same name
            shutil.copy(FullCardPath, os.path.join(tmpdir, os.path.basename("neut.card")))
            # run command in temp dir
            subprocess.run("dumptotpauC ", cwd=tmpdir, shell=True)
            shutil.move(f"{tmpdir}/neut_xsecs.root", os.path.join(XsecDir, XsecName))
        else:
            print(f"Xsec hists {XsecName} exists")

    else:
        for Target in Targets:
            for Flavor in GlobalV.Flavors:
                CName = f"NEUT{NeutVersion}_{Tune}_CC_{Flavor}_0-8GeV_{Target}_*.card"
                CardPaths = glob.glob(CardDir+"/"+CName)    #Grab any # of events for this card, then grab the first one
                CardPath = CardPaths[0]
                XsecName = f"NEUT{NeutVersion}_{Tune}_{Flavor}_{Target}_XSECHIST.root"
                XsecPath = XsecDir+"/"+ XsecName
                if not os.path.exists(XsecPath):
                    # copy file to temp dir with same name
                    shutil.copy(CardPath, os.path.join(tmpdir, os.path.basename("neut.card")))
                    # run command in temp dir
                    subprocess.run("dumptotpauC ", cwd=tmpdir, shell=True)
                    shutil.move(f"{tmpdir}/neut_xsecs.root", os.path.join(XsecDir, XsecName))
                else:
                    print(f"Xsec hists {XsecName} exists")




def Generate(Generator, Tune, Events, Target=None, Mode=None, Flavor=None, Multi=None):
    # Grab/Make paths for output generated files
    FilePath,Targets = DirectorySetup(Generator, Target=Target, Mode=Mode)
    FlatFluxMaker()

    match Generator.lower():
        case "genie":
            GenerateGenie(Generator, Events, Tune, Target, Mode, Flavor, Multi)
        case "neut":

            CardNames = MakeNeutCards(Tune, Targets, Events, Modes=Mode, Flavors=Flavor)
            GenNeutXsec(Tune, Targets)

            if Multi:
                raise NotImplementedError("GenerateNeut is not done yet")
            
            raise NotImplementedError("GenerateNeut is not done yet")
        case _:
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
    
   