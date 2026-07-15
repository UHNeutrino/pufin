import os, argparse, ROOT, random, shutil, subprocess, pathlib
import GlobalV
import glob
import concurrent.futures
import json5
import time
from multiprocessing import cpu_count


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

def DirectorySetup(Generator, SingleTarget=None, Mode=None):
    OutPath = os.environ.get("PUFIN_OUT")
    Targets = []
    if Generator.lower() == "neut":
        Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium"]
    elif Generator.lower()=="genie":
        Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium", "Chlorine"]
    else:
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
        
    if SingleTarget:
        #OnePath = OutPath + "/" + Generator.upper() + "/" + Target + "/"
        OnePath = OutPath + "/" + Generator.upper() + "/" + SingleTarget + "/"
        os.makedirs(OnePath, exist_ok=True)
        FilePaths = [OnePath]
        Targets = [SingleTarget]

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
            hist = ROOT.TH1D(f"FlatHist_{low}", "Flat Flux; Energy (GeV); Neutrinos", N, low, high)
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
            
def GetGenieFlavorEvents(Events, Flavor):
    if Flavor not in GlobalV.GenFlavorScales:
        raise ValueError(f"No GENIE flavor scale defined for {Flavor}")

    FlavorEvents = int(Events * GlobalV.GenFlavorScales[Flavor])

    if FlavorEvents < 100:
        FlavorEvents = 100

    return FlavorEvents

def CheckGenieFiles(Tune, Targets, Events, Modes=None, Flavors=None):
    # Checks all expected GENIE multiprocessing files and returns the Original_
    # filenames that still need to be generated or flattened.
    #
    # For multiprocessing, Events is interpreted as the desired NuMu NChunks.
    # Flavor chunk counts are scaled by GlobalV.GenFlavorScales.
    # Each GENIE chunk is hard-coded to 100 events for now.

    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath == None:
        raise ValueError("PUFIN_OUT Needs to be defined!")

    if not os.environ.get("GENIE_VERSION"):
        raise ValueError("GENIE_VERSION Environment Variable Not Defined")
    GenieVersion = os.environ.get("GENIE_VERSION")

    if not Tune:
        GENIE_XSEC_TUNE = os.environ.get("GENIE_XSEC_TUNE", "")
        if not GENIE_XSEC_TUNE:
            raise ValueError("Tune not provided and GENIE_XSEC_TUNE is not set")
        Tune = GENIE_XSEC_TUNE.split("_", 1)[0]

    EventsPerChunk = GlobalV.GenieEventsPerChunk
    NuMuNChunks = Events
    FileNames = []

    if not Modes:
        Modes = ["NC", "CC"]
    elif isinstance(Modes, str):
        Modes = [Modes]

    if not Flavors:
        Flavors = GlobalV.Flavors
    elif isinstance(Flavors, str):
        Flavors = [Flavors]

    for Target in Targets:
        for Mode in Modes:
            for Flavor in Flavors:

                # Just like NEUT: no nue/nuebar NC generation
                if Mode == "NC" and (Flavor == "NuE" or Flavor == "NuEBar"):
                    continue

                if Flavor not in GlobalV.GenFlavorScales:
                    raise ValueError(f"No GENIE flavor scale defined for {Flavor}")

                NChunks = int(NuMuNChunks * GlobalV.GenFlavorScales[Flavor])

                if NChunks < 1:
                    NChunks = 1

                Eranges = ["0-8GeV"]
                if Mode == "NC":
                    Eranges = ["0-8GeV", "8-30GeV", "30-120GeV"]

                for Erange in Eranges:
                    print(
                        f"GENIE {Mode} {Flavor} {Target} {Erange}: "
                        f"{NChunks} chunks of {EventsPerChunk} events"
                    )

                    for i in range(NChunks):

                        GenName = f"Original_GENIE{GenieVersion}_{Tune}_{Mode}_{Flavor}_{Erange}_{Target}_{EventsPerChunk}P{i:03}.root"
                        GenName = GenName.replace("+", "")

                        FlatName = GenName.replace("Original", "Flat")

                        GenDir = OutPath + f"/GENIE/{Target}"
                        FlatPath = GenDir + f"/{FlatName}"

                        RunBool = not os.path.exists(FlatPath)

                        if RunBool == False:
                            try:
                                RFile = ROOT.TFile(FlatPath)
                                if RFile.IsZombie():
                                    os.remove(FlatPath)
                                    RunBool = True
                                elif not RFile.Get("FlatTree_VARS"):
                                    os.remove(FlatPath)
                                    RunBool = True
                                RFile.Close()
                            except:
                                os.remove(FlatPath)
                                RunBool = True

                        if RunBool == True:
                            FileNames.append(GenName)

    return FileNames

def GenGenieFlatSingleFile(File):
    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath == None:
        raise ValueError("PUFIN_OUT Needs to be defined!")

    if not os.environ.get("GENIE_XSEC_TUNE"):
        raise ValueError("GENIE_XSEC_TUNE Environment Variable Not Defined")

    if not os.environ.get("GENIE_XSEC_FILE"):
        raise ValueError("GENIE_XSEC_FILE Environment Variable Not Defined")

    GenInfo = File.replace(".root", "").split("_")

    GeneratorVersion = GenInfo[1]   # GENIE3.06.00
    Tune = GenInfo[2]
    Mode = GenInfo[3]
    Flavor = GenInfo[4]
    Erange = GenInfo[5]
    Target = GenInfo[6]
    EventsAndPart = GenInfo[7]

    Events = int(float(EventsAndPart.split("P")[0]))

    Emin = Erange.split("-")[0]
    Emax = Erange.split("-")[1].replace("GeV", "")

    GenDir = OutPath + f"/GENIE/{Target}"
    os.makedirs(GenDir, exist_ok=True)

    GenName = File
    FlatName = GenName.replace("Original", "Flat")
    PrepName = GenName.replace("Original", "Prep")

    GenPath = GenDir + f"/{GenName}"
    FlatPath = GenDir + f"/{FlatName}"
    PrepPath = GenDir + f"/{PrepName}"

    FlavorPDG = None
    for pdg, label in GlobalV.NuPDGs.items():
        if label == Flavor:
            FlavorPDG = str(pdg)

    if FlavorPDG == None:
        raise ValueError(f"No Such Flavor {Flavor}")

    TargetPDG = None
    for _, info in GlobalV.NovaTargets.items():
        if info["name"] == Target:
            TargetPDG = info["pdg"]

    if TargetPDG == None:
        raise ValueError(f"No Such Target {Target}")

    Flux = f"/data/t2k-nova/fluxes/full_flat_flux_{Emin}-{Emax}GeV.root,h1"

    RunBool = not os.path.exists(GenPath)

    if RunBool == False:
        try:
            RFile = ROOT.TFile(GenPath)
            if RFile.IsZombie():
                os.remove(GenPath)
                RunBool = True
            elif not RFile.Get("gtree"):
                os.remove(GenPath)
                RunBool = True
            RFile.Close()
        except:
            os.remove(GenPath)
            RunBool = True

    if RunBool:
        seed = random.randint(10000, 999999)

        exec_string = ""
        exec_string += f"gevgen "
        exec_string += f"--tune $GENIE_XSEC_TUNE "
        exec_string += f"-t \"{TargetPDG}\" "
        exec_string += f"-n {Events} "
        exec_string += f"-e {Emin},{Emax} "
        exec_string += f"-f {Flux} "
        exec_string += f"-p {FlavorPDG} "
        exec_string += f"--event-generator-list {Mode} "
        exec_string += f"--seed {seed} "
        exec_string += f"-o {GenPath} "
        exec_string += f"--cross-sections $GENIE_XSEC_FILE"

        subprocess.run(exec_string, shell=True, executable="/bin/bash")
        print(exec_string)
        print(f"Generated {GenName}")
    else:
        print("Original GENIE File exists")

    FlatBool = not os.path.exists(FlatPath)

    if FlatBool == False:
        try:
            RFile = ROOT.TFile(FlatPath)
            if RFile.IsZombie():
                os.remove(FlatPath)
                FlatBool = True
            elif not RFile.Get("FlatTree_VARS"):
                os.remove(FlatPath)
                FlatBool = True
            RFile.Close()
        except:
            os.remove(FlatPath)
            FlatBool = True

    if FlatBool:
        try:
            Genf = ROOT.TFile(GenPath)
        except:
            raise RuntimeError("Cannot open GENIE file")

        if Genf.IsZombie() or not Genf.Get("gtree"):
            Genf.Close()
            raise RuntimeError("Generation of GENIE file failed, cannot flatten")
        Genf.Close()

        exec_string = ""
        exec_string += f"PrepareGENIE "
        exec_string += f"-i {GenPath} "
        exec_string += f"-t \"{TargetPDG}\" "
        exec_string += f"-o {PrepPath} "
        exec_string += f"-f {Flux}"

        subprocess.run(exec_string, shell=True, executable="/bin/bash")
        print(exec_string)

        exec_string = ""
        exec_string += f"nuisflat -i GENIE:{PrepPath} -o {FlatPath}"

        subprocess.run(exec_string, shell=True, executable="/bin/bash")
        print(exec_string)
        print(f"Generated {FlatName}")

        if os.path.exists(PrepPath):
            os.remove(PrepPath)
    else:
        print(f"GENIE FILE {FlatName} exists and works")

    return RunBool
            
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
    
    EventsPerJob = 100
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

def find_expected_file(directory: str, filename: str):
    file_path = pathlib.Path(directory) / filename
    if file_path.exists():
        return file_path
    return None
                    
def GenerateGenie(Generator, Events, Tune=None, Target=None, Mode=None, Flavor=None, Multi=None):
    FilePaths, Targets = DirectorySetup(Generator)

    if Target is not None:
        Targets = [Target]
        FilePaths, Targets = DirectorySetup(Generator, SingleTarget=Target)

    if Mode is None:
        Modes = ["CC", "NC"]
    else:
        Modes = [Mode]
    for Mode in Modes:
        if Flavor is None:
            if Mode == "NC":
                Flavors = ["14", "-14"]
            elif Mode == "CC":
                Flavors = ["12", "-12", "14", "-14"]
            else:
                Flavors = ["12", "-12", "14", "-14"]
        else:
            Flavors = [str(Flavor)]
    
        allowed_flavors = {"12", "-12", "14", "-14"}
        for flav in Flavors:
            if flav not in allowed_flavors:
                raise ValueError(
                    f"Flavor must be one of 12, -12, 14, -14. Got {flav}."
                )

        for Flavor in Flavors:
            flavor_label = GlobalV.NuPDGs[int(Flavor)]

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
                        
                    # EventsLabel = f"{Events:.0e}".replace("+0", "").replace("+", "")
                    # base_name = (
                    #     f"{Generator}{Version}_{TuneLabel}_{Mode}_{flavor_label}_{Erange}_{target_label}_{EventsLabel}"
                    # )
                    
                    FlavorEvents = GetGenieFlavorEvents(Events, flavor_label)
                    EventsLabel = f"{FlavorEvents:.0e}".replace("+0", "").replace("+", "")
                    base_name = (
                        f"{Generator}{Version}_{TuneLabel}_{Mode}_{flavor_label}_{Erange}_{target_label}_{EventsLabel}"
                    )
                    expected_original = f"Original_{base_name}.root"
                    expected_flat = f"Flat_{base_name}.root"

                    original_file = find_expected_file(final_dir, expected_original)
                    flat_file = find_expected_file(final_dir, expected_flat)

                    globals()["Target"] = TargetPDG
                    globals()["target_label"] = target_label
                    globals()["flavor_label"] = flavor_label
                    globals()["Mode"] = Mode
                    globals()["Flavor"] = Flavor
                    globals()["Emin"] = Emin
                    globals()["Emax"] = Emax
                    globals()["Erange"] = Erange
                    globals()["Generator"] = Generator
                    globals()["Version"] = Version
                    OutPath = os.environ.get("PUFIN_OUT")
                    user = os.environ.get("USER")
                    tmpdir = f"{OutPath}/{user}_temp_dir"
                    globals()["output_dir"] = tmpdir
                    globals()["Flux_directory"] = "/data/t2k-nova/fluxes"
                    globals()["FinaloutFileName"] = f"Original_{base_name}"

                    if flat_file is not None:
                        print(f"Skipping {target_name} {Mode} {Flavor} {Erange}: found {flat_file.name}")
                        continue

                    if original_file is not None:
                        print(f"Flattening existing file: {original_file.name}")
                        gen_flatten(str(original_file))
                        continue

                    # print(f"Generating {target_name} {Mode} {Flavor} {Erange}")
                    # genie_files, final_genie, final_copy = gen_series(Events, tmpdir, final_dir)
                    # gen_flatten(final_copy)
                    
                    FlavorEvents = GetGenieFlavorEvents(Events, flavor_label)

                    print(f"Generating {target_name} {Mode} {Flavor} {Erange} with {FlavorEvents} events")
                    genie_files, final_genie, final_copy = gen_series(FlavorEvents, tmpdir, final_dir)
                    gen_flatten(final_copy)
                    
def GenGenieMultiOnNodeFiles(FileNames, CPUPercent):
    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent <= 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")

    MaxCores = os.cpu_count()
    NCores = max(1, int(os.environ.get("SLURM_CPUS_PER_TASK", MaxCores*CPUPercent)))
    
    if len(FileNames) == 0:
        print("No GENIE files need to be generated.")
        return []

    if NCores > len(FileNames):
        NCores = len(FileNames)

    print(f"Number of Cores: {NCores}")

    RunList = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=NCores) as exe:
        for result in exe.map(GenGenieFlatSingleFile, FileNames):
            RunList.append(result)

    return RunList
                    
def MakeNeutCards(Tune, Targets, Events, Modes=None, Flavors=None, MultiNodeB=None):
    OutPath = os.environ.get("PUFIN_OUT")
    if not os.environ.get("NEUT_VERSION"):
        raise ValueError("NEUT_VERSION Environment Variable Not Defined")
    NeutVersion = str(os.environ.get("NEUT_VERSION")).replace(".","-")
    CardPath = OutPath+"/"+"NEUT"+"/"+"Cards"
    os.makedirs(CardPath, exist_ok=True)
    CardNames = []
    FlatFluxNames = ["flat_flux_0-8GeV.root","flat_flux_8-30GeV.root"]
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
                        CName0 = f"NEUT{NeutVersion}_{Tune}_{Mode}_{Flavor}_{ErangeNC}_{Target}_{Events:.0e}.card".replace("+", "")
                        CardNames.append(CName0) #one is to iterate over, one is to save at the end
                        CNameList.append(CName0)
                elif (Mode == "CC"):
                    CName0 = f"NEUT{NeutVersion}_{Tune}_{Mode}_{Flavor}_{Erange}_{Target}_{Events:.0e}.card".replace("+", "")
                    CardNames.append(CName0)
                    CNameList.append(CName0)
                else:
                    raise ValueError(f"Mode {Mode} Does Not Exist!!")
                for CName in CNameList:
                    f = CardPath + "/" + CName
                    if not os.path.exists(f):
                        print(f"Missing {f}")
                        CardString = ""
                        if not GlobalV.NeutCardTunes.get(Tune):
                            raise ValueError(f"Tune {Tune} Does Not Exist")
                        CardString = CardString + GlobalV.NeutCardTunes.get(Tune)
                        if Flavor=="NuMu":
                            CardString = CardString + f"\nEVCT-NEVT {Events}\n"
                            CardString = CardString + GlobalV.NeutCardModes.get(Mode)
                        elif Flavor=="NuMuBar":
                            SpecialEvent = int(Events/10)
                            if SpecialEvent < 1000:
                                SpecialEvent = 1000
                            CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                            CName = CName.replace(f"{Events:.0e}",f"{SpecialEvent:.0e}").replace("+", "")
                            CardString = CardString + GlobalV.AntiNeutCardModes.get(Mode)
                        elif Flavor=="NuE":
                            SpecialEvent = int(Events/100)
                            if SpecialEvent < 1000:
                                SpecialEvent = 1000
                            CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                            CName = CName.replace(f"{Events:.0e}",f"{SpecialEvent:.0e}").replace("+", "")
                            CardString = CardString + GlobalV.NeutCardModes.get(Mode)
                        elif Flavor=="NuEBar":
                            SpecialEvent = int(Events/100)
                            if SpecialEvent < 1000:
                                SpecialEvent = 1000
                            CardString = CardString + f"\nEVCT-NEVT {SpecialEvent}\n"
                            CName = CName.replace(f"{Events:.0e}",f"{SpecialEvent:.0e}").replace("+", "")
                            CardString = CardString + GlobalV.AntiNeutCardModes.get(Mode)
                        else:
                            raise ValueError("UNKNOWN FLAVOR")
                        
                        CardString = CardString + GlobalV.NeutCardFlavors.get(Flavor)
                        CardString = CardString + GlobalV.NeutCardTargets.get(Target)
                        tempErange = CName.split("_")[-3]
                        low = tempErange.split("-")[0]
                        if (tempErange != "0-8GeV"):
                            print("NOT 0-8GeV")
                            CardString = CardString.replace("EVCT-FILENM 'flat_flux_0-8GeV.root'",f"EVCT-FILENM 'flat_flux_{tempErange}.root'" )
                            CardString = CardString.replace("EVCT-HISTNM 'FlatHist'",f"EVCT-HISTNM 'FlatHist_{low}''" )
                        else:
                            CardString = CardString.replace("EVCT-HISTNM 'FlatHist'",f"EVCT-HISTNM 'FlatHist_{low}''" )

                            

                        if Target == "Titanium":
                            # TI is dumb in 5-6-4
                            # print("Special Ti Problem in 5.6.4. and 5.9.0")
                            if "NEUT-MDLQE 402" in CardString:
                                CardString = CardString.replace("NEUT-MDLQE 402","NEUT-MDLQE 002")
                            else:
                                CardString = CardString + "NEUT-MDLQE 002 \n"

                            if "NEUT-MDL2P2H 2" in CardString:
                                CardString = CardString.replace("NEUT-MDL2P2H 2","NEUT-MDL2P2H 1")
                            else:
                                CardString = CardString + "NEUT-MDL2P2H 1 \n"

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
                if Flavor != "NuMu":
                    continue
                CName = f"NEUT{NeutVersion}_{Tune}_CC_{Flavor}_0-8GeV_{Target}_*.card"
                CardPaths = glob.glob(CardDir+"/"+CName)    #Grab any # of events for this card, then grab the first one
                CardPath = CardPaths[0]
                XsecName = f"NEUT{NeutVersion}_{Tune}_{Target}_XSECHIST.root"
                XsecPath = XsecDir+"/"+ XsecName
                if not os.path.exists(XsecPath):
                    # copy file to temp dir with same name
                    shutil.copy(CardPath, os.path.join(tmpdir, os.path.basename("neut.card")))
                    # run command in temp dir
                    subprocess.run("dumptotpauC ", cwd=tmpdir, shell=True)
                    shutil.move(f"{tmpdir}/neut_xsecs.root", os.path.join(XsecDir, XsecName))
                else:
                    print(f"Xsec hists {XsecName} exists")

def FluxToTemp():
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"
    FluxDir= OutPath+"/"+"FlatFluxes"
    for flux in os.listdir(FluxDir):
        FluxPath = os.path.join(FluxDir, flux)
        if os.path.isfile(FluxPath) and not os.path.exists(tmpdir+"/"+flux):  # skip subdirectories and doesn't double copy
            shutil.copy(FluxPath, tmpdir)
       
def GenNeut(CardNames):
    # Generates for every card given, 
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"
    CardDir = OutPath+"/"+"NEUT"+"/"+"Cards"
    FluxDir= OutPath+"/"+"FlatFluxes"
    GenList = []
    #Copy all Fluxes to tmp dir
    FluxToTemp()

    for Card in CardNames:
        Target = Card.split("_")[5]
        GenDir = OutPath + f"/NEUT/{Target}"
        # print(Target)
        GenName = Card.replace("NEUT", "Original_NEUT")
        GenName = GenName.replace(".card",".root")
        GenList.append(GenName)
        f = GenDir + f"/{GenName}"
        RunBool = not os.path.exists(f)
        if RunBool == False:
            RFile = ROOT.TFile(f)
            if RFile.IsZombie():
                os.remove(f) #if it failed previously, delete the zombie and regenerate 
                RunBool = True
            elif not RFile.Get("fluxhisto"):
                os.remove(f) #same thing if it is empty
                RunBool = True
            RFile.Close()
        if RunBool:
            exec_string=""
            exec_string += f"neutroot2 {Card} {GenName}"
            # copy card to temp dir with same name
            shutil.copy(CardDir+"/"+Card, os.path.join(tmpdir, os.path.basename(Card)))
            # run command in temp dir
            subprocess.run(exec_string, cwd=tmpdir, shell=True)
            shutil.move(f"{tmpdir}/{GenName}", os.path.join(GenDir, GenName))
            os.remove(tmpdir+"/"+Card)
            print(exec_string)
            print(f"Generated {GenName}")
        else:
            print(f"NEUT FILE {GenName} exists and works")
    return GenList

def CheckNeutFiles(CardNames, NChunks):
    # Checks all files
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    FileNames = []
    #Copy all Fluxes to tmp dir

    for Card in CardNames:
        TempChunks = NChunks
        Target = Card.split("_")[5]
        Flavor = Card.split("_")[3]
        GenDir = OutPath + f"/NEUT/{Target}"
        if Flavor=="NuMu":
            TempChunks = NChunks
        elif Flavor=="NuMuBar":
            TempChunks = int(NChunks/10)
        elif Flavor=="NuE":
            TempChunks = int(NChunks/100)
        elif Flavor=="NuEBar":
            TempChunks = int(NChunks/100)
        else:
            raise ValueError(f"No Such Flavor {Flavor}")
        # print(Target)
        for i in range(TempChunks):
            GenName = Card.replace("NEUT", "Original_NEUT")
            GenName = GenName.replace(".card",f"P{i:03}.root")
            f = GenDir + f"/{GenName}"
            RunBool = not os.path.exists(f)
            if not RunBool:
                RFile = ROOT.TFile(f)
                if RFile.IsZombie():
                    os.remove(f) #if it failed previously, delete the zombie and regenerate 
                    RunBool = True
                elif not RFile.Get("fluxhisto"):
                    os.remove(f) #same thing if it is empty
                    RunBool = True
                RFile.Close()
            if RunBool == True:
                FileNames.append(GenName)

    return FileNames


def GenNeutFlatSingle(Card, i:int):
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"
    Target = Card.split("_")[5]
    GenDir = OutPath + f"/NEUT/{Target}"
    

    GenName = Card.replace("NEUT", "Original_NEUT")
    GenName = GenName.replace(".card",f"P{i:03}.root") #removes .card, .root gets added later
    GenList = [GenName]
    f = GenDir + f"/{GenName}"

    RunBool = not os.path.exists(f)
    if RunBool == False:
        try:
            RFile = ROOT.TFile(f)
            if RFile.IsZombie():
                os.remove(f) #if it failed previously, delete the zombie and regenerate 
                RunBool = True
            elif not RFile.Get("fluxhisto"):
                os.remove(f) #same thing if it is empty
                RunBool = True
            RFile.Close()
        except:
            os.remove(f)
            RunBool = True
        

    if RunBool:
        exec_string=""
        exec_string += f"neutroot2 {Card} {GenName}"

        if i == 1:
            start = time.time()
        subprocess.run(exec_string, cwd=tmpdir, shell=True)
        shutil.move(f"{tmpdir}/{GenName}", os.path.join(GenDir, GenName))
        # os.remove(tmpdir+"/"+Card)
        # print(exec_string)
        if i == 1:
            elapsed = time.time() - start
            with open("CardTiming.txt", "a") as OutF:
                OutF.write(f"Card {Card} took {elapsed:.2f} seconds\n")
        print(f"Generated {GenName}")
    else:
        print("Original File exists")
    FlatNeut(GenList)
    return RunBool

def GenNeutFlatSingleFile(File, Card):
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"
    Target = Card.split("_")[5]
    GenDir = OutPath + f"/NEUT/{Target}"

    GenName = File
    f = GenDir + f"/{GenName}"
    

    #Move over fluxes for generation
    FluxToTemp()

    RunBool = not os.path.exists(f)
    if RunBool == False:
        try:
            RFile = ROOT.TFile(f)
            if RFile.IsZombie():
                os.remove(f) #if it failed previously, delete the zombie and regenerate 
                RunBool = True
            elif not RFile.Get("fluxhisto"):
                os.remove(f) #same thing if it is missing fluxhisto
                RunBool = True
            RFile.Close()
        except:
            os.remove(f)
            RunBool = True
    if RunBool:
        exec_string=""
        exec_string += f"neutroot2 {Card} {GenName}"
        subprocess.run(exec_string, cwd=tmpdir, shell=True)
        shutil.move(f"{tmpdir}/{GenName}", os.path.join(GenDir, GenName))
        # os.remove(tmpdir+"/"+Card)
        # print(exec_string)    
        print(f"Generated {GenName}")
    else:
        print("Original File exists")
    GenList = [GenName]
    FlatNeut(GenList)

    return RunBool

def GenNeutMultiOnNode(CardNames, CPUPercent, NChunks):
    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    
    
    NCores = max(1,int(os.environ.get("SLURM_CPUS_PER_TASK", cpu_count()*CPUPercent)))
    if NCores>NChunks:
        NCores = NChunks

    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"

    # if NCores >= 20:
    #     print(f"Too many cores {NCores}")
    #     exit()

    for Card in CardNames:
        TempChunk = NChunks
        if "NuMuBar" in Card:
            TempChunk = int(NChunks/10)
        elif "NuE" in Card:
            TempChunk = int(NChunks/100)
        if TempChunk<1:
            TempChunk = 1
        # Copy Card to temp dir 
        # Change number of events in card from N to 100,000
        i_list =[]
        CardList = []
        GenName = Card.replace("NEUT", "Original_NEUT")
        for i in range(0,TempChunk):
            i_list.append(i+1)
            CardList.append(Card) #List of the same card (Chunks) times
        # copy the card path for all cores to use
        CardDir = OutPath+"/"+"NEUT"+"/"+"Cards"
        shutil.copy(CardDir+"/"+Card, os.path.join(tmpdir, os.path.basename(Card)))
        # proccessed files list
        RunList = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=NCores) as exe: 
            for result in exe.map(GenNeutFlatSingle, CardList, i_list):
                RunList.append(result)
        
        os.remove(tmpdir+"/"+Card)

    return RunList

def GenNeutMultiOnNodeFiles(FileNames, CPUPercent):
    #THIS SHOULD NOT BE RUN ON ITS OWN, ONLY CALLED BY GENSUBMIT.PY
    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    
    MaxCores     = os.cpu_count()
    NCores = max(1,int(os.environ.get("SLURM_CPUS_PER_TASK", MaxCores*CPUPercent))) #makes the number of core the max between 1, slurm cpu count, and cpupercent*cpu count
    JobID = os.environ.get("SLURM_JOB_ID","0")
    print(f"Number of Cores: {NCores}")
    CardList = []

    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"
    CardDir = f"{OutPath}/NEUT/Cards"
    for File in FileNames:
        # COPY THE CARDS HERE AND NAME THE CARDS PER NODE SO NODES WONT DELETE OTHER CARDS THAT ARE USED
        CardName = File[:-9] #removes PXXX.root
        CardName = CardName + ".card"
        CardName = CardName.replace("Original_NEUT", "NEUT")
        NodeCard = CardName.replace(".card",f"{JobID}.card")
        if not os.path.exists(f"{tmpdir}/{NodeCard}"):
            shutil.copy(f"{CardDir}/{CardName}", os.path.join(tmpdir, os.path.basename(NodeCard)))
        CardList.append(NodeCard) 
    # proccessed files list
    RunList = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=NCores) as exe: 
        for result in exe.map(GenNeutFlatSingleFile, FileNames, CardList):
            RunList.append(result)
    print(CardList)


    
    for Card in CardList:
        if os.path.exists(f"{tmpdir}/{Card}"):
            os.remove(f"{tmpdir}/{Card}")

    return RunList


def FlatNeut(GenList):
    #Flattens for every given generated file
    OutPath = os.environ.get("PUFIN_OUT")
    user = os.environ.get("USER")
    tmpdir = f"{OutPath}/{user}_temp_dir"

    for Gen in GenList:
        Target = Gen.split("_")[6]
        GenDir = OutPath + f"/NEUT/{Target}"
        print(Target)
        FlatName = Gen.replace("Original", "Flat")
        f = GenDir + f"/{FlatName}"
        RunBool = not os.path.exists(f)
        if RunBool == False:
            try:
                RFile = ROOT.TFile(f)
            except:
                os.remove(f)
                raise RuntimeError(f"File {f} failed to open, deleted")
            if (RFile.IsZombie()) or (not RFile.Get("FlatTree_VARS")):
                os.remove(f) #if it failed previously, delete the zombie and regenerate 
                RunBool = True
            RFile.Close()
        if RunBool:
            GenPath = f"{GenDir}/{Gen}"
            print(GenPath)
            try:
                Genf = ROOT.TFile(GenPath)
            except:
                raise RuntimeError("Cannot open file")
            
            if (Genf.IsZombie()) or (not Genf.Get("fluxhisto")):
                Genf.Close()
                raise RuntimeError("Generation of file failed, cannot flatten")
            Genf.Close()
            exec_string=""
            exec_string += f"nuisflat -i NEUT:{Gen} -o {FlatName}"
            # run command in Gen dir
            subprocess.run(exec_string, cwd=GenDir, shell=True)
            # print(exec_string)
            print(f"Generated {FlatName}")
        else:
            print(f"NEUT FILE {FlatName} exists and works")

def Generate(Generator, Tune, Events, Target=None, Mode=None, Flavor=None, CPUPercent=None, NChunks=None):
    # Grab/Make paths for output generated files
    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath==None:
        raise ValueError("PUFIN_OUT Needs to be defined!")

    FilePath,Targets = DirectorySetup(Generator, SingleTarget=Target, Mode=Mode)
    FlatFluxMaker()

    # if Generator.lower()=="genie":
    #     #GenerateGenie(Generator, Events, Tune, Target, Mode, Flavor, Multi)
    #     GenerateGenie(Generator, Events, Tune, Target, Mode, Flavor)
    if Generator.lower()=="genie":
        if CPUPercent and NChunks:
            FileNames = CheckGenieFiles(
                Tune=Tune,
                Targets=Targets,
                Events=NChunks,   # multiprocessing interpretation: NuMu NChunks
                Modes=Mode,
                Flavors=Flavor,
            )
            RunList = GenGenieMultiOnNodeFiles(FileNames, CPUPercent)
        elif CPUPercent or NChunks:
            raise ValueError("Need both CPUPercent and NChunk for multi processing")
        else:
            GenerateGenie(Generator, Events, Tune, Target, Mode, Flavor)
    elif Generator.lower()=="neut":
        if not Tune:
            raise ValueError("Neut requires a tune")
        CardNames = MakeNeutCards(Tune, Targets, Events, Modes=Mode, Flavors=Flavor)
        GenNeutXsec(Tune, Targets)

        if CPUPercent and NChunks:
            # If you want to multiprocess on one node, multiple cores
            # For Multiple Nodes use GenSubmit  
            FluxToTemp()
            RunList = GenNeutMultiOnNode(CardNames, CPUPercent, NChunks)
        elif CPUPercent or NChunks:
            raise ValueError("Need both CPUPercent and NChunk for multi processing")
        else:
            # Regular processing, only using one core and one node
            GenList = GenNeut(CardNames)
            FlatNeut(GenList)
    else:
        raise ValueError("Generator must be 'Genie' or 'Neut'")

    #Check if FF exist, make them if not
    # FlatFluxMaker()


    print("NEUT Generation Is Complete")


if __name__ =="__main__":
    
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)
    #If just regular Generating:
    GenParser = subparsers.add_parser("Gen")
    GenParser.add_argument("--generator", required=True)
    GenParser.add_argument("--events", required=True, type=int)
    GenParser.add_argument("--tune", default=None)
    GenParser.add_argument("--target", default=None)
    GenParser.add_argument("--mode", default=None)
    GenParser.add_argument("--flavor", default=None)
    GenParser.add_argument("--CPUPercent", default=None, type=float)
    GenParser.add_argument("--NChunks", default=None, type=int)
    #If Being called by GenSubmit on multiple Nodes:
    NeutMultParser = subparsers.add_parser("NeutMult")
    NeutMultParser.add_argument("--Files",  nargs="+", required=True)
    NeutMultParser.add_argument("--CPUPercent", required=True)
    
    # For Making the Xsecs on a cluster:
    NeutXsecParser = subparsers.add_parser("NeutXsec")
    NeutXsecParser.add_argument("--tune", required=True)
    NeutXsecParser.add_argument("--targets", required=True)
    
    GenieMultParser = subparsers.add_parser("GenieMult")
    GenieMultParser.add_argument("--Files", nargs="+", required=True)
    GenieMultParser.add_argument("--CPUPercent", required=True)
    

    args = parser.parse_args()
    if args.command=="Gen":
        Generate(
            Generator=args.generator,
            Events=args.events,
            Tune=args.tune,
            Target=args.target,
            Mode=args.mode,
            Flavor=args.flavor,
            # CPUPercent=float(args.CPUPercent),
            # NChunks=int(args.NChunks),
            CPUPercent=args.CPUPercent,
            NChunks=args.NChunks,
        )
    elif args.command=="NeutMult":
        GenNeutMultiOnNodeFiles(
            FileNames= args.Files,
            CPUPercent=float(args.CPUPercent),
            )
    elif args.command=="NeutXsec":
        GenNeutXsec(
            Tune=args.tune,
            Targets=json5.loads(args.targets)
        )
    elif args.command=="GenieMult":
        GenGenieMultiOnNodeFiles(
            FileNames=json5.loads(args.Files),
            CPUPercent=float(args.CPUPercent),
        )

    
    # Tune = "Prod7E"
    # Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium"]
    # Events = 1000
    # MakeNeutCards(Tune, Targets,Events)
    # GenNeutXsec(Tune,Targets)
    
    # source /data/t2k-nova/MainSetup.sh
    # export PUFIN_OUT=/data/t2k-nova/PUfINOutputs/_MultiProcess
    # python GenMain.py Gen \

    ## For Series:
    # --generator Genie \
    # --events 200 
        
    ## For Multi-core: (remember events = nChuncks for NuMu)
    # python GenMain.py Gen \
    #   --generator Genie \
    #   --events 50000 \
    #   --target Carbon \
    #   --mode CC \
    #   --flavor NuMu \
    #   --CPUPercent 50 \
    #   --NChunks 5
    
   