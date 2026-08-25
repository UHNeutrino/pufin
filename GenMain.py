import os, argparse, ROOT, random, shutil, subprocess, pathlib, random, time, glob, sys
import concurrent.futures
import json5
import multiprocessing as mp
import src.GlobalV as GlobalV



OutPath = os.environ.get("PUFIN_OUT")
user = os.environ.get("USER")
tmpdir = f"{OutPath}/{user}_temp_dir"

def DirectorySetup(Generator, SingleTarget=None, Mode=None):
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
        
    if SingleTarget:
        #OnePath = OutPath + "/" + Generator.upper() + "/" + Target + "/"
        OnePath = OutPath + "/" + Generator.upper() + "/" + SingleTarget + "/"
        os.makedirs(OnePath, exist_ok=True)
        FilePaths = [OnePath]
        Targets = [SingleTarget]

    print(f"Outputting to {FilePaths}")
    return FilePaths, Targets

def FlatFluxMaker():
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

def CheckGenieFiles(Targets, Events, Modes=None, Flavors=None):
    # Checks all expected GENIE multiprocessing files and returns the Original_
    # filenames that still need to be generated or flattened.
    #
    # For multiprocessing, Events is interpreted as the desired NuMu NChunks.
    # Flavor chunk counts are scaled by GlobalV.GenFlavorScales.
    # Events per GENIE chunk are set by GlobalV.GenieEventsPerChunk.
    if OutPath == None:
        raise ValueError("PUFIN_OUT Needs to be defined!")

    if not os.environ.get("GENIE_VERSION"):
        raise ValueError("GENIE_VERSION Environment Variable Not Defined")
    GenieVersion = os.environ.get("GENIE_VERSION")

    GENIE_XSEC_TUNE = os.environ.get("GENIE_XSEC_TUNE", "")
    if not GENIE_XSEC_TUNE:
        raise ValueError("GENIE_XSEC_TUNE is not set")

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
        TargetLabel = None

        for _, info in GlobalV.NovaTargets.items():
            if info["name"] == Target:
                TargetLabel = info["label"]
                break

        if TargetLabel is None:
            raise ValueError(f"No target label found for {Target}")
        for Mode in Modes:
            if Mode not in GlobalV.GenModeScales:
                raise ValueError(f"No GENIE mode scale defined for {Mode}")
        
            for Flavor in Flavors:

                # Just like NEUT: no nue/nuebar NC generation
                if Mode == "NC" and (Flavor == "NuE" or Flavor == "NuEBar"):
                    continue

                if Flavor not in GlobalV.GenFlavorScales:
                    raise ValueError(f"No GENIE flavor scale defined for {Flavor}")

                # NChunks = int(NuMuNChunks * GlobalV.GenFlavorScales[Flavor])
                NChunks = int(NuMuNChunks* GlobalV.GenFlavorScales[Flavor]* GlobalV.GenModeScales[Mode])

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

                        GenName = f"Original_GENIE{GenieVersion}_{Tune}_{Mode}_{Flavor}_{Erange}_{TargetLabel}_{EventsPerChunk}P{i:03}.root"
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
    TargetLabel = GenInfo[6]
    EventsAndPart = GenInfo[7]

    TargetName = None
    TargetPDG = None

    for _, info in GlobalV.NovaTargets.items():
        if info["label"] == TargetLabel:
            TargetName = info["name"]
            TargetPDG = info["pdg"]
            break

    if TargetName is None or TargetPDG is None:
        raise ValueError(f"No target information found for label {TargetLabel}")

    Events = int(float(EventsAndPart.split("P")[0]))

    Emin = Erange.split("-")[0]
    Emax = Erange.split("-")[1].replace("GeV", "")

    GenDir = OutPath + f"/GENIE/{TargetName}"
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

    Flux = f"{OutPath}/FlatFluxes/flat_flux_{Emin}-{Emax}GeV.root,FlatHist_{Emin}"

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

        subprocess.run(exec_string, shell=True, executable="/bin/bash", check=True)
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

        subprocess.run(exec_string, shell=True, executable="/bin/bash", check=True)
        print(exec_string)

        exec_string = ""
        exec_string += f"nuisflat -i GENIE:{PrepPath} -o {FlatPath}"

        subprocess.run(exec_string, shell=True, executable="/bin/bash", check=True)
        print(exec_string)
        print(f"Generated {FlatName}")

        if os.path.exists(PrepPath):
            os.remove(PrepPath)
    else:
        print(f"GENIE FILE {FlatName} exists and works")

    return RunBool
            
def gev_gen_genie(events: int, i: int, job: dict):
    """Run one GENIE job and return its output filename."""
    print(f"Running GENIE job {i} with {events} events...")

    seed = random.randint(10000, 999999)

    out_name = (
        f"{job['Generator']}{job['Version']}_{job['Tune']}_{job['Mode']}_"
        f"{job['flavor_label']}_{job['Erange']}_"
        f"{job['target_label']}_{events}_P{i}.root"
    )

    exec_gen = f"""
    gevgen \
      --tune $GENIE_XSEC_TUNE \
      -t "{job['TargetPDG']}" \
      -n {events} \
      -e {job['Emin']},{job['Emax']} \
      -f {job['Flux_directory']}/full_flat_flux_{job['Emin']}-{job['Emax']}GeV.root,FlatHist_{job['Emin']} \
      -p {job['FlavorPDG']} \
      --event-generator-list {job['Mode']} \
      --seed {seed} \
      -o {job['output_dir']}/{out_name} \
      --cross-sections $GENIE_XSEC_FILE
    """

    subprocess.run(
        exec_gen,
        shell=True,
        executable="/bin/bash",
        check=True,
    )

    return f"{job['output_dir']}/{out_name}"

def gen_series(Events: int, final_directory: str, job: dict):
    """Generate GENIE files serially and return list of filenames."""

    output_dir = job["output_dir"]
    output_path = pathlib.Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)

    output_path.mkdir(parents=True)

    out_files = []

    EventsPerJob = 100

    if Events % EventsPerJob != 0:
        raise ValueError(
            f"GENIE Events must be a multiple of {EventsPerJob}. "
            f"Got {Events}."
        )

    nJobs = Events // EventsPerJob

    for i in range(nJobs):
        out_file = gev_gen_genie(
            events=EventsPerJob,
            i=i,
            job=job,
        )
        out_files.append(out_file)

    EventsLabel = f"{Events:.0e}".replace("+0", "").replace("+", "")

    outFileName = (
        f"Original_{job['Generator']}{job['Version']}_{job['Tune']}_"
        f"{job['Mode']}_{job['flavor_label']}_{job['Erange']}_"
        f"{job['target_label']}_{EventsLabel}"
    )

    final_genie = f"{output_dir}/{outFileName}.root"

    hadd_cmd = (
        f'hadd -f -k "{final_genie}" '
        + " ".join(f'"{f}"' for f in out_files)
    )

    print(f"Running: {hadd_cmd}")
    subprocess.run(hadd_cmd, shell=True, check=True)

    final_copy = f"{final_directory}/{outFileName}.root"
    shutil.copy2(final_genie, final_copy)

    print(f"Copied final file to {final_copy}")

    return out_files, final_genie, final_copy

def gen_flatten(original_file: str, job: dict):
    """Prepare and flatten one specific GENIE file."""

    original_path = pathlib.Path(original_file)

    if not original_path.exists():
        raise FileNotFoundError(
            f"Missing original file: {original_file}"
        )

    final_dir = original_path.parent
    original_name = original_path.name

    prep_name = original_name.replace("Original_", "Prep_", 1)
    flat_name = original_name.replace("Original_", "Flat_", 1)

    prep_file = final_dir / prep_name
    flat_file = final_dir / flat_name

    prepare_cmd = f"""
    PrepareGENIE \
      -i "{original_path}" \
      -t "{job['TargetPDG']}" \
      -o "{prep_file}" \
      -f "{job['Flux_directory']}/full_flat_flux_{job['Emin']}-{job['Emax']}GeV.root,FlatHist_{job['Emin']}"
    """

    print("Preparing GENIE file...")

    subprocess.run(
        prepare_cmd,
        shell=True,
        executable="/bin/bash",
        check=True,
    )

    flatten_cmd = f"""
    nuisflat \
      -i "GENIE:{prep_file}" \
      -o "{flat_file}"
    """

    print("Flattening GENIE file...")

    subprocess.run(
        flatten_cmd,
        shell=True,
        executable="/bin/bash",
        check=True,
    )

    if prep_file.exists():
        prep_file.unlink()

    return str(flat_file)

def find_expected_file(directory: str, filename: str):
    file_path = pathlib.Path(directory) / filename
    if file_path.exists():
        return file_path
    return None
                    
def GenerateGenie(Generator, Events, Target=None, Mode=None, Flavor=None, Multi=None):
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
                    if not GENIE_XSEC_TUNE:
                        raise ValueError("GENIE_XSEC_TUNE is not set")

                    TuneLabel = GENIE_XSEC_TUNE.split("_", 1)[0]
                    FlavorEvents = GetGenieFlavorEvents(Events, flavor_label)
                    EventsLabel = f"{FlavorEvents:.0e}".replace("+0", "").replace("+", "")
                    base_name = (
                        f"{Generator}{Version}_{TuneLabel}_{Mode}_{flavor_label}_{Erange}_{target_label}_{EventsLabel}"
                    )
                    expected_original = f"Original_{base_name}.root"
                    expected_flat = f"Flat_{base_name}.root"

                    original_file = find_expected_file(final_dir, expected_original)
                    flat_file = find_expected_file(final_dir, expected_flat)

                    job = {
                        "Generator": Generator,
                        "Version": Version,
                        "Tune": TuneLabel,
                        "Mode": Mode,
                        "FlavorPDG": Flavor,
                        "flavor_label": flavor_label,
                        "TargetPDG": TargetPDG,
                        "target_label": target_label,
                        "Emin": Emin,
                        "Emax": Emax,
                        "Erange": Erange,
                        "output_dir": tmpdir,
                        "Flux_directory": "/data/t2k-nova/fluxes",
                    }
                    if flat_file is not None:
                        print(f"Skipping {target_name} {Mode} {Flavor} {Erange}: found {flat_file.name}")
                        continue

                    if original_file is not None:
                        print(f"Flattening existing file: {original_file.name}")
                        gen_flatten(
                            original_file=str(original_file),
                            job=job,
                        )
                        continue
                
                    print(f"Generating {target_name} {Mode} {Flavor} {Erange} with {FlavorEvents} events")
                    genie_files, final_genie, final_copy = gen_series(
                        Events=FlavorEvents,
                        final_directory=final_dir,
                        job=job,
                    )

                    gen_flatten(
                        original_file=final_copy,
                        job=job,
                    )
                    
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
                    
def MakeNeutCards(Tune, Targets, Events, Modes=None, Flavors=None):
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
                TargetLabel = GlobalV.NeutTargetLabels.get(Target)
                CNameList = []
                if (Mode == "NC"):
                    if (Flavor == "NuE" or Flavor == "NuEBar"):
                        continue
                    for Name in FlatFluxNames:
                        part = Name.split("_")[2]        # "x-YGeV.root"
                        ErangeNC = part.replace(".root","")
                        CName0 = f"NEUT{NeutVersion}_{Tune}_{Mode}_{Flavor}_{ErangeNC}_{TargetLabel}_{Events:.0e}.card".replace("+", "")
                        CardNames.append(CName0) #one is to iterate over, one is to save at the end
                        CNameList.append(CName0)
                elif (Mode == "CC"):
                    CName0 = f"NEUT{NeutVersion}_{Tune}_{Mode}_{Flavor}_{Erange}_{TargetLabel}_{Events:.0e}.card".replace("+", "")
                    CardNames.append(CName0)
                    CNameList.append(CName0)
                else:
                    raise ValueError(f"Mode {Mode} Does Not Exist!!")
                for CName in CNameList:
                    f = CardPath + "/" + CName
                    if os.path.exists(f):
                        print(f"Remaking Card {CName}")
                        os.remove(f)
                    else:
                        print(f"Missing {CName}")
                    CardString = ""
                    if not GlobalV.NeutCardTunes.get(Tune):
                        raise ValueError(f"Tune {Tune} Does Not Exist")
                    CardString = CardString + GlobalV.NeutCardTunes.get(Tune)
                    CardString = CardString + f"\nEVCT-NEVT {Events}\n"
                    if "Bar" in Flavor:
                        CardString = CardString + GlobalV.AntiNeutCardModes.get(Mode)
                    else:
                        CardString = CardString + GlobalV.NeutCardModes.get(Mode)
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
                        # This is here because Neut can't generate titanium with certain QE models
                        if "NEUT-MDLQE 402" in CardString:
                            CardString = CardString.replace("NEUT-MDLQE 402","NEUT-MDLQE 002")
                        else:
                            CardString = CardString + "NEUT-MDLQE 002 \n"

                        if "NEUT-MDL2P2H 2" in CardString:
                            CardString = CardString.replace("NEUT-MDL2P2H 2","NEUT-MDL2P2H 1")
                        else:
                            CardString = CardString + "NEUT-MDL2P2H 1 \n"

                    with open(f, "w") as file:
                        file.write(CardString)
                    print(f"Made Neut Card: {f}")

    return CardNames

def GenNeutXsec(Tune, Targets, FullCardPath=None):
    #Grabs every neut card from FullCardPath or naming scheme and then checks for the corespondinig xsec histogram
    #If the histogram is missing, then it generates them with dumpmtotpauC
    if not os.environ.get("NEUT_VERSION"):
        raise ValueError("NEUT_VERSION Environment Variable Not Defined")
    NeutVersion = str(os.environ.get("NEUT_VERSION")).replace(".","-")
    CardDir = OutPath + "/NEUT/Cards"
    XsecDir = OutPath + "/NEUT/Xsecs"
    os.makedirs(XsecDir, exist_ok=True)

    # delete temp dir if it exists from a previous run
    # shutil.rmtree(tmpdir, ignore_errors=True)
    # create fresh temp dir
    if not os.path.exists(tmpdir):
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
                TargetLabel = GlobalV.NeutTargetLabels.get(Target)
                if Flavor != "NuMu":
                    continue
                CName = f"NEUT{NeutVersion}_{Tune}_CC_{Flavor}_0-8GeV_{TargetLabel}_*.card"
                CardPaths = glob.glob(CardDir+"/"+CName)    #Grab any # of events for this card, then grab the first one
                CardPath = CardPaths[0]
                XsecName = f"NEUT{NeutVersion}_{Tune}_{TargetLabel}_XSECHIST.root"
                XsecPath = XsecDir+"/"+ XsecName
                if not os.path.exists(XsecPath):
                    # copy file to temp dir with same name
                    shutil.copy(CardPath, os.path.join(tmpdir, os.path.basename("neut.card")))
                    # run command in temp dir
                    subprocess.run("dumptotpauC ", cwd=tmpdir, shell=True)
                    shutil.move(f"{tmpdir}/neut_xsecs.root", os.path.join(XsecDir, XsecName))
                else:
                    print(f"Xsec hists {XsecName} exists")
    
    print("Finished making/finding Neut Xsecs")

def FluxToTemp():
    FluxDir= OutPath+"/"+"FlatFluxes"
    for flux in os.listdir(FluxDir):
        FluxPath = os.path.join(FluxDir, flux)
        if os.path.isfile(FluxPath) and not os.path.exists(tmpdir+"/"+flux):  # skip subdirectories and doesn't double copy
            shutil.copy(FluxPath, tmpdir)
       
def GenNeut(CardNames):
    # Generates for every card given, 
    CardDir = OutPath+"/"+"NEUT"+"/"+"Cards"
    GenList = []
    #Copy all Fluxes to tmp dir
    FluxToTemp()

    for Card in CardNames:
        TargetLabel = Card.split("_")[5]
        Target = GlobalV.NeutLabelTargets.get(TargetLabel)
        GenDir = OutPath + f"/NEUT/{Target}"
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
    FileNames = []
    FinishedFiles = []
    #Copy all Fluxes to tmp dir

    for Card in CardNames:
        TempChunks = NChunks
        TargetLabel = Card.split("_")[5]
        Target = GlobalV.NeutLabelTargets.get(TargetLabel)
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
        
        if TempChunks < 1:
            TempChunks = 1
        
        for i in range(TempChunks):
            GenName = Card.replace("NEUT", "Flat_NEUT")
            GenName = GenName.replace(".card",f"P{i+1:03}.root")
            OriginName = GenName.replace("Flat","Original")
            f = GenDir + f"/{GenName}"
            RunBool = not os.path.exists(f)
            if not RunBool:
                try:
                    RFile = ROOT.TFile.Open(f)
                except OSError:
                    os.remove(f)
                    print("file messed up, deleted")
                    RunBool = True
                if not RunBool and ((not RFile) or RFile.IsZombie()):
                    os.remove(f) #if it failed previously, delete the zombie and regenerate 
                    RunBool = True
                elif not RFile.Get("FlatTree_VARS") and not RunBool:
                    os.remove(f) #same thing if it is empty
                    RunBool = True
                else:
                    FinishedFiles.append(OriginName)
                RFile.Close()
            if RunBool == True:
                FileNames.append(OriginName)

    print(f"{len(FinishedFiles)} files done, {len(FileNames)} to go")
    inputWait = True
    while inputWait:
        In = input("Continue? (y/n)")
        if In.lower() == "n":
            exit()
        elif In.lower() == "y":
            inputWait = False
        elif In.lower() == "p":
            print(FileNames)
        else:
            print("unknown response, y to continue, n to stop, p to print files")
    
    
    return FileNames

def GenNeutSingleFile(File,Card):
    TargetLabel = Card.split("_")[5]
    Target = GlobalV.NeutLabelTargets.get(TargetLabel)
    GenDir = OutPath + f"/NEUT/{Target}"
    GenName = File
    f = GenDir + f"/{GenName}"
    # wait time to hopefully not overload the memeory in a node
    waitTime = random.randrange(0,5)
    time.sleep(waitTime)
    
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
        #print(f">>>>>>>>>>>>>>>>>>>>Running Genertation of {GenName} now")
        subprocess.run(exec_string, shell=True, cwd=tmpdir)
        shutil.move(f"{tmpdir}/{GenName}", os.path.join(GenDir, GenName))   
        #print(f"Generated {GenName}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    else:
        print("Original File exists")
    return RunBool


def GenNeutFlatSingleFile(File, Card):
    TargetLabel = Card.split("_")[5]
    Target = GlobalV.NeutLabelTargets.get(TargetLabel)
    GenDir = OutPath + f"/NEUT/{Target}"

    GenName = File
    f = GenDir + f"/{GenName}"
    # wait time to hopefully not overload the I/O in a node
    waitTime = random.randrange(0,30)
    time.sleep(waitTime)
    

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
    output_text = open(f"{tmpdir}/{GenName}.text", "w")
    if RunBool:
        exec_string=""
        exec_string += f"neutroot2 {Card} {GenName}"
        #print(f">>>>>>>>>>>>>>>>>>>>Running Genertation of {GenName} now")
        output_text.write(f">>>>>>>Running Generation of {GenName} now...\n")
        output_text.flush()
        subprocess.run(exec_string, shell=True, cwd=tmpdir)
        output_text.write(f"Generate {GenName}<<<<<<<<<<<<<\n")
        output_text.flush()
        shutil.move(f"{tmpdir}/{GenName}", os.path.join(GenDir, GenName))   
        #print(f"Generated {GenName}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    else:
        print("Original File exists")
    GenList = [GenName]
    CardList = [Card]
    FlatNeut(GenList,CardList)
    output_text.write(f">>>>>>>{GenName} Flattened<<<<<<<<<<<\n")
    output_text.close()
    return RunBool

def GenNeutMultiOnNodeFiles(FileNames, CPUPercent=None, CPUNumber=None):
    if not CPUPercent and not CPUNumber:
        raise ValueError("NEED CPU PERCENT OR CPU NUMBER")
    if CPUNumber and not CPUPercent:
        CPUPercent = 100

    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    
    MaxCores     = os.cpu_count()
    NCores = max(1,int(os.environ.get("SLURM_CPUS_PER_TASK", MaxCores*CPUPercent))) #makes the number of core the max between 1, slurm cpu count, and cpupercent*cpu count
    if CPUNumber:
        NCores = CPUNumber

    JobID = os.environ.get("SLURM_JOB_ID","0")
    print(f"Number of Cores: {NCores}")
    CardList = []

    CardDir = f"{OutPath}/NEUT/Cards"
    for File in FileNames:
        # COPY THE CARDS HERE AND NAME THE CARDS PER NODE SO NODES WONT DELETE OTHER CARDS THAT ARE USED
        CardName = File[:-9] #removes PXXX.root
        CardName = CardName + ".card"
        CardName = CardName.replace("Original_NEUT", "NEUT")
        NodeCard = CardName.replace(".card",f"{JobID}.card")
        if not os.path.exists(f"{tmpdir}/{NodeCard}"):
            shutil.copy(f"{CardDir}/{CardName}", os.path.join(tmpdir, os.path.basename(NodeCard)))
        else:
            os.remove(f"{tmpdir}/{NodeCard}")
            shutil.copy(f"{CardDir}/{CardName}", os.path.join(tmpdir, os.path.basename(NodeCard)))
        CardList.append(NodeCard) 
    # proccessed files list
    RunList = []
    ctx = mp.get_context("spawn") #This should help with a slurm multiprocessing bug?
    if NCores > len(FileNames):
            NCores = len(FileNames)
    with concurrent.futures.ProcessPoolExecutor(max_workers=NCores, mp_context=ctx) as exe: 
        for result in exe.map(GenNeutFlatSingleFile, FileNames, CardList):
            RunList.append(result)


    
    for Card in CardList:
        if os.path.exists(f"{tmpdir}/{Card}"):
            os.remove(f"{tmpdir}/{Card}")

    print("---------------------------FILE GENERATION ON NODE FINISHED, BYE BYE----------------------------------")

    return RunList


def FlatNeut(GenList, CardList):
    #Flattens for every given generated file
    for Gen,Card in zip(GenList,CardList):
        TargetLabel = Gen.split("_")[6]
        Target = GlobalV.NeutLabelTargets.get(TargetLabel)
        GenDir = OutPath + f"/NEUT/{Target}"
        FlatName = Gen.replace("Original", "Flat")
        Flattenedf = GenDir + f"/{FlatName}"
        RunBool = not os.path.exists(Flattenedf)
        # if RunBool:
        #     raise RuntimeError(f"Flattening None exist {f}??")

        if RunBool == False:
            try:
                RFile = ROOT.TFile.Open(Flattenedf)
            except OSError:
                os.remove(Flattenedf)
                print("file messed up, deleted")
                RunBool = True
            if not RunBool and ((not RFile) or (not RFile.Get("FlatTree_VARS")) or  (RFile.IsZombie())):
                if RFile:
                    RFile.Close()
                os.remove(Flattenedf) #if it failed previously, delete the zombie and regenerate 
                RunBool = True
            else:
                print(f"Flat Tree exists and works {Flattenedf}")
        if RunBool:
            GenPath = f"{GenDir}/{Gen}"
            print(GenPath)
            try:
                Genf = ROOT.TFile(GenPath)
            except:
                raise RuntimeError("Cannot open file")
            
            if (Genf.IsZombie()) or (not Genf.Get("fluxhisto")):
                Genf.Close()
                os.remove(GenPath)
                GenNeutSingleFile(Gen,Card)  #Try to regenerate once if it failed before
                try:
                    Genf = ROOT.TFile(GenPath)
                except:
                    raise RuntimeError("Cannot open file")
                if (Genf.IsZombie()) or (not Genf.Get("fluxhisto")):
                    raise RuntimeError("Generation of file failed twice. Cannot Flatten")
                else:
                    print("Regenerated, ready to flatten now")
            Genf.Close()
            exec_string=""
            exec_string += f"nuisflat -i NEUT:{Gen} -o {FlatName}"
            # run command in Gen dir
            subprocess.run(exec_string, cwd=GenDir, shell=True)
            print(f"Generated {FlatName}")
        else:
            print(f"NEUT FILE {FlatName} exists and works")

def Generate(Generator, Events, Tune=None, Target=None, Mode=None, Flavor=None, CPUPercent=None, NChunks=None):
    # Grab/Make paths for output generated files

    if OutPath==None:
        raise ValueError("PUFIN_OUT Needs to be defined!")

    FilePath,Targets = DirectorySetup(Generator, SingleTarget=Target, Mode=Mode)
    FlatFluxMaker()
    if Generator.lower()=="genie":
        if CPUPercent and NChunks:
            FileNames = CheckGenieFiles(
                Targets=Targets,
                Events=NChunks,   # multiprocessing interpretation: NuMu NChunks
                Modes=Mode,
                Flavors=Flavor,
            )
            RunList = GenGenieMultiOnNodeFiles(FileNames, CPUPercent)
        elif CPUPercent or NChunks:
            raise ValueError("Need both CPUPercent and NChunk for multi processing")
        else:
            GenerateGenie(
                Generator=Generator,
                Events=Events,
                Target=Target,
                Mode=Mode,
                Flavor=Flavor,
            )
    elif Generator.lower()=="neut":
        subprocess.run("rm *.text ", cwd=tmpdir, shell=True) #remove previous text files

        if not Tune:
            raise ValueError("Neut requires a tune")
        CardNames = MakeNeutCards(Tune, Targets, Events, Modes=Mode, Flavors=Flavor)
        GenNeutXsec(Tune, Targets)

        if CPUPercent and NChunks:
            # If you want to multiprocess on one node, multiple cores
            # For Multiple Nodes use GenSubmit  
            FluxToTemp()
            FileNames = CheckNeutFiles(CardNames, NChunks)
            if len(FileNames) == 0:
                    print("Already done (─ ‿ ─)")
                    exit() 
            RunList = GenNeutMultiOnNodeFiles(FileNames, CPUPercent)
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


    print(f"{Generator.upper()} Generation Is Complete")

def CheckGeneratedFiles(Verbosity, UseRoot):
    if UseRoot:
        import ROOT
    FlatNeutFiles = glob.glob(f"{OutPath}/NEUT/*/Flat*.root")
    FlatGenieFiles = glob.glob(f"{OutPath}/GENIE/*/Flat*.root")
    if (len(FlatNeutFiles)> 0):
        print("----------------Neut----------------")
        print(f"Total Files: {len(FlatNeutFiles)}")
        VersionTuneLoop(FlatNeutFiles, UseRoot, Verbosity)

    if (len(FlatGenieFiles)> 0 ):
        print("----------------Genie----------------")
        print(f"Total Files: {len(FlatGenieFiles)}")
        VersionTuneLoop(FlatGenieFiles, UseRoot, Verbosity)
        

def VersionTuneLoop(FileList, UseRoot, Verbosity):
    
    VersionTuneList = []
    for file in FileList:
        FName = file.split("/")[-1]
        Version = FName.split("_")[1]
        Tune = FName.split("_")[2]
        VersionTune = Version.upper() + "_" + Tune.upper()
        if not (VersionTune.upper() in VersionTuneList):
            VersionTuneList.append(VersionTune)


    for VersionTune in VersionTuneList:
        TotalEvents = 0
        FlatFilesTemp = []
        for file in FileList:
            if VersionTune.upper() in file.upper():
                FlatFilesTemp.append(file)
        
        print(f"************For {VersionTune} ************")
        print(f"Total Files {len(FlatFilesTemp)}")
        for file in FlatFilesTemp:
            endStr = file.split("_")[-1]
            eventCount = endStr[:4]
            if "." in eventCount:
                # genie uses e:2 rather than e:3 so I need to remove the period
                eventCount = eventCount.replace(".", "")
            eventFloat = float(eventCount)
            TotalEvents += eventFloat
        
        if UseRoot:
            Ndf = ROOT.RDataFrame("FlatTree_VARS",FlatFilesTemp)
            print(f"Total Events in RDataFrame:{Ndf.Count().GetValue()}")
        else:
            print(f"Total Events: {int(TotalEvents):e}")
            print("Warning this number is based off of the file naming and may not reflect the actual number of events")





if __name__ =="__main__":
    
    parser = argparse.ArgumentParser("""
    Gen- Neut or Genie generation with multiprocessing available
    Neut/GenieMult- Multiprocessing that should only be called by GenSubmit
    NeutXsec- Generation of Neut Xsecs meant for GenSubmit
    """)

    subparsers = parser.add_subparsers(dest="command", required=True)
    #If just regular Generating:
    GenParser = subparsers.add_parser("Gen")
    GenParser.add_argument("--generator", required=True)
    GenParser.add_argument("--events", required=True, type=int)
    GenParser.add_argument("--tune", default=None)
    GenParser.add_argument("--target",  nargs="+", default=None)
    GenParser.add_argument("--mode",  nargs="+", default=None)
    GenParser.add_argument("--flavor",  nargs="+",default=None)
    GenParser.add_argument("--CPUPercent", default=None, type=float)
    GenParser.add_argument("--NChunks", default=None, type=int)
    #If Being called by GenSubmit on multiple Nodes:
    NeutMultParser = subparsers.add_parser("NeutMult")
    NeutMultParser.add_argument("--Files",  nargs="+", required=True)
    NeutMultParser.add_argument("--CPUPercent", required=False)
    NeutMultParser.add_argument("--CPUNumber", required=False)
    
    # For Making the Xsecs on a cluster:
    NeutXsecParser = subparsers.add_parser("NeutXsec")
    NeutXsecParser.add_argument("--tune", required=True)
    NeutXsecParser.add_argument("--targets", required=True)

    #Genie multiprocessing through GenSubmit
    GenieMultParser = subparsers.add_parser("GenieMult")
    GenieMultParser.add_argument("--Files", nargs="+", required=True)
    GenieMultParser.add_argument("--CPUPercent", required=True)

    #For checking files that have been downloaded
    GenCheckParser = subparsers.add_parser("Check")
    GenCheckParser.add_argument("--Verbosity")
    GenCheckParser.add_argument("--UseRoot", action="store_true")

    args = parser.parse_args()
    if args.command=="Gen":
        Generate(
            Generator=args.generator,
            Events=args.events,
            Tune=args.tune,
            Target=args.target,
            Mode=args.mode,
            Flavor=args.flavor,
            CPUPercent=args.CPUPercent,
            NChunks=args.NChunks,
        )
    elif args.command=="NeutMult":
        if args.CPUPercent:
            cpuPercent = float(args.CPUPercent)
        else:
            cpuPercent = None
        GenNeutMultiOnNodeFiles(
            FileNames= args.Files,
            CPUPercent=cpuPercent,
            CPUNumber=int(args.CPUNumber)
            )
    elif args.command=="NeutXsec":
        GenNeutXsec(
            Tune=args.tune,
            Targets=json5.loads(args.targets)
        )
    elif args.command=="GenieMult":
        GenGenieMultiOnNodeFiles(
            FileNames=args.Files,
            CPUPercent=float(args.CPUPercent),
        )
    elif args.command=="Check":
        CheckGeneratedFiles(Verbosity=args.Verbosity, UseRoot=args.UseRoot)

    
    # Tune = "Prod7E"
    # Targets = ["Carbon", "Hydrogen", "Oxygen", "Titanium"]
    # Events = 1000
    # MakeNeutCards(Tune, Targets,Events)
    # GenNeutXsec(Tune,Targets)
    


    # For Series:
    # python GenMain.py Gen \
    # --generator Genie \
    # --events 400 
        
    ## For Multi-core: (remember events = nChuncks for NuMu)
    # python GenMain.py Gen \
    #   --generator Genie \
    #   --events 50000 \
    #   --target Carbon \
    #   --mode CC \
    #   --flavor NuMu \
    #   --CPUPercent 50 \
    #   --NChunks 5
    
   