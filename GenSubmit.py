import os
import argparse
import math
import time
import GenMain
import subprocess
from multiprocessing import cpu_count

# This script runs GenMain->GenNeutCards to get a list of cards
# Then it runs GenMain->GenNeutMultiOnNode on multiple nodes with the nodeID and NChunks given


def NeutRunScript(Container, Tune, Events, TotalNodes, NChunks, Target=None, Mode=None, Flavor=None, CPUPercent=None):
    DateStr = time.strftime("%Y-%m-%d")
    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath==None:
        raise ValueError("PUFIN_OUT Needs to be defined!")
    Generator = "NEUT"

    FilePath,Targets = GenMain.DirectorySetup(Generator, SingleTarget=Target, Mode=Mode)
    GenMain.FlatFluxMaker()
    CardNames = GenMain.MakeNeutCards(Tune, Targets, Events, Modes=Mode, Flavors=Flavor)
    # making an xsec needs to be on a node in the container:
    xseccmd = f"""
        sbatch \\
        --nodes=1 \\
        --ntasks-per-node=1  \\
        --cpus-per-task=1 \\
        --time=00:05:00 \\
        --job-name=NeutXsecGeneration{DateStr}\\
        --output=NeutXsecGeneration{DateStr}.out\\
        --wrap "apptainer exec --writable-tmpfs --bind {OutPath}:{OutPath} {Container} bash -c \\"source /opt/SetupAll.sh && export PUFIN_OUT={OutPath}  && python GenMain.py NeutXsec --tune {Tune} --target \\\\\\"{Targets}\\\\\\" \\" "
        """
    print("Running xsec generation")
    result = subprocess.Popen(xseccmd, shell=True)

    processes = []
    FileNames = []
    FileNames = GenMain.CheckNeutFiles(CardNames,NChunks)

    if len(FileNames) == 0:
        print("Already done (─ ‿ ─)")
        exit() 

    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    NCores = max(1,int( cpu_count()*CPUPercent))
    NodeFiles = []
    # Sort NuMu to the front so it gets distributed equally
    FileNames = sorted(FileNames, key=lambda x: "_NuMu_" not in x)

    if len(FileNames) < TotalNodes:
        TotalNodes = len(FileNames)

    for Node in range(0,TotalNodes):
        NodeFiles = FileNames[Node::TotalNodes] #split up card name based on number of nodes
        SlurmTime = NeutTimeEstimator(NodeFiles, NCores)
        print(f"Files on Node {Node}: {len(NodeFiles)}")
        FilesFormated = ""
        for file in NodeFiles:
            FilesFormated += file + " "
        cmd = f"""sbatch \\
        --nodes=1 \\
        --ntasks-per-node=1 \\
        --cpus-per-task={NCores} \\
        --time={SlurmTime} \\
        --job-name=NEUT{Node+1}of{TotalNodes}\\
        --output=NEUTGeneration_{Node}of{TotalNodes}_{DateStr}.out\\
        --wrap "apptainer exec --writable-tmpfs --bind {OutPath}/:{OutPath}/ {Container} bash -c 'source /opt/SetupAll.sh && export PUFIN_OUT={OutPath} && echo {len(NodeFiles)} Files in {SlurmTime} && python GenMain.py NeutMult --Files {FilesFormated} --CPUNumber {NCores}' "
        """
        # print(cmd)
        print(f"Sending Job to Node {Node} of {TotalNodes}\n  Estimated time: {SlurmTime}")
        result = subprocess.Popen(cmd, shell=True)   # each cmd is a separate process
        time.sleep(2)
    
        
def GenieRunScript(Container, Events, NChunks, TotalNodes, Target=None, Mode=None, Flavor=None, CPUPercent=None):
    OutPath = os.environ.get("PUFIN_OUT")

    if OutPath is None:
        raise ValueError("PUFIN_OUT Needs to be defined!")

    if Events <= 0:
        raise ValueError("Events must be greater than zero")

    if NChunks <= 0:
        raise ValueError("NChunks must be greater than zero")

    if TotalNodes <= 0:
        raise ValueError("TotalNodes must be greater than zero")

    Generator = "GENIE"
    CORES_PER_NODE = 48
    MAX_GENIE_CORES = 20
    MEMORY_PER_CORE_GB = 4

    FilePath, Targets = GenMain.DirectorySetup(Generator, SingleTarget=Target, Mode=Mode)
    GenMain.FlatFluxMaker()
    GenMain.GlobalV.GenieEventsPerChunk = Events

    FileNames = GenMain.CheckGenieFiles(
        Targets=Targets,
        Events=NChunks,
        Modes=Mode,
        Flavors=Flavor,
    )
    
    if len(FileNames) == 0:
        print("Already done (─ ‿ ─)")
        return

    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent <= 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    
    NCores = max(1, int(CORES_PER_NODE * CPUPercent))
    NCores = min(NCores,MAX_GENIE_CORES)
    # MemoryGB = NCores * MEMORY_PER_CORE_GB
    
    FileNames = sorted(FileNames, key=lambda x: "_NuMu_" not in x)
    if len(FileNames) < TotalNodes:
        TotalNodes = len(FileNames)
        
    print(f"Events per chunk: {Events}")
    print(f"Requested NuMu chunks: {NChunks}")
    print(f"Missing GENIE chunks: {len(FileNames)}")
    print(f"Number of node jobs: {TotalNodes}")
    print(f"Maximum simultaneous chunks per node: {NCores}")

    # print(f"Not Sorted {len(FileNames)}")
    # print(f"Total Files: {len(FileNames)}")

    for Node in range(TotalNodes):
        NodeFiles = FileNames[Node::TotalNodes]

        if len(NodeFiles) == 0:
            print(f"Files on Node {Node}: 0")
            continue
        
        CoresForNode = min(NCores,len(NodeFiles))

        MemoryGB = CoresForNode * MEMORY_PER_CORE_GB

        # SlurmTime = GenieTimeEstimator(NodeFiles)
        SlurmTime = GenieTimeEstimator(NodeFiles, CoresForNode)
        # SlurmTime = "00:30:00"
        FilesFormatted = " ".join(NodeFiles)
        print(f"Cores on Node {Node}: {CoresForNode}")
        print(f"Memory request: {MemoryGB} GB")
        print(f"Estimated time: {SlurmTime}")

        print(f"Files on Node {Node}: {len(NodeFiles)}")

        cmd = f"""sbatch \\
        --nodes=1 \\
        --ntasks-per-node=1 \\
        --cpus-per-task={CoresForNode} \\
        --time={SlurmTime} \\
        --mem={MemoryGB}G \\
        --exclude=compute-6-9,compute-6-10,compute-6-36 \\
        --job-name=GENIE{Node+1}of{TotalNodes} \\
        --output=GENIEGeneration_{Node+1}of{TotalNodes}_%j.out \\
        --wrap "apptainer exec --writable-tmpfs --bind {OutPath}:{OutPath} {Container} bash -c 'source /opt/SetupAll.sh && export PUFIN_OUT={OutPath} && python GenMain.py GenieMult --Files {FilesFormatted} --CPUPercent {CPUPercent}'"
        """
        print(f"Sending GENIE job to Node {Node} of {TotalNodes}")
        print(f"  Files: {len(NodeFiles)}")
        print(f"  Cores: {CoresForNode}")
        print(f"  Memory: {MemoryGB} GB")
        print(f"  Estimated time: {SlurmTime}")

        subprocess.run(cmd, shell=True, check=True)
        time.sleep(2)
        
def GenieTimeEstimator(Files, NCores):
    """Estimate GENIE generation, preparation, and flattening wall time."""
    if not Files:
        raise ValueError("Files cannot be empty.")

    if NCores <= 0:
        raise ValueError("NCores must be positive.")

    SECONDS_PER_WAVE_AT_10K = 120
    SAFETY_FACTOR = 1.25
    MINIMUM_SECONDS = 300
    MAXIMUM_SECONDS = 86400

    events_per_chunk = int(Files[0].split("_")[7].split("P")[0])

    effective_cores = min(NCores, len(Files))
    waves = math.ceil(len(Files) / effective_cores)

    event_scale = events_per_chunk / 10000

    total_seconds = int(
        waves
        * SECONDS_PER_WAVE_AT_10K
        * event_scale
        * SAFETY_FACTOR
    )

    total_seconds = max(total_seconds, MINIMUM_SECONDS)

    if total_seconds >= MAXIMUM_SECONDS:
        raise ValueError(
            "GENIE allocation exceeds 24 hours; use more nodes "
            "or fewer chunks per node."
        )

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def NeutTimeEstimator(Files, NCores):
    # loop through all files and come up with a decent time estimation using linear regressions from trends found in initial testing
    EventsAndPart = Files[0].split("_")[7]
    Events = int(float(EventsAndPart[:-9]))
    TotalSeconds = 0
    for file in Files:
        if "8-30Gev" in file:
            TotalSeconds += int(Events*0.0135753 + 500)
        elif "NC" in file:
            TotalSeconds += int(0.0081201*Events + 120)
        elif "NuE_" in file:
            TotalSeconds += 70
        else:
            TotalSeconds += int(0.00591132*Events + 100)
    # add time for flattening ~3 min each:
    TotalSeconds += len(Files)*180
    
    TotalSeconds = int(TotalSeconds/(NCores/3))
    # add random wait time
    TotalSeconds += len(Files)*30
    
    if TotalSeconds>= 86400:
        raise ValueError("Allocation exceeding 24hrs, use more cores or less chunks")
    t = time.gmtime(TotalSeconds)
    SlurmTime = time.strftime("%H:%M:%S", t)
    return SlurmTime

    
if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    ## call to script GenNeut --events 1000 --tune Prod7E  --total_nodes 3 --cpu_percent 75 --nchunks 100 
    subparsers = parser.add_subparsers(dest="command", required=True)
    #If just regular Generating:
    GenParser = subparsers.add_parser("GenNeut")
    GenParser.add_argument("--container", required=True, type=str)
    GenParser.add_argument("--events", required=True, type=int)
    GenParser.add_argument("--tune", required=True)
    GenParser.add_argument("--total_nodes", required=True, type=int)
    GenParser.add_argument("--cpu_percent", required=True, type=float)
    GenParser.add_argument("--nchunks", required=True, type=int)    
    GenParser.add_argument("--target", default=None)
    GenParser.add_argument("--mode", default=None)
    GenParser.add_argument("--flavor", default=None)
    
    GenieParser = subparsers.add_parser("GenGenie")
    GenieParser.add_argument("--container", required=True, type=str)
    GenieParser.add_argument("--events",required=True,type=int,)
    GenieParser.add_argument("--total_nodes", required=True, type=int)
    GenieParser.add_argument("--cpu_percent", required=True, type=float)
    GenieParser.add_argument("--nchunks", required=True, type=int)
    GenieParser.add_argument("--target", default=None)
    GenieParser.add_argument("--mode", default=None)
    GenieParser.add_argument("--flavor", default=None)

    args = parser.parse_args()
    
    if args.command == "GenNeut":
        NeutRunScript(
                Container=args.container,
                Events=args.events,
                Tune=args.tune,
                TotalNodes = args.total_nodes,
                Target=args.target,
                Mode=args.mode,
                Flavor=args.flavor,
                CPUPercent= args.cpu_percent,
                NChunks= args.nchunks,
            )
    
    elif args.command == "GenGenie":
        GenieRunScript(
            Container=args.container,
            Events=args.events,
            NChunks=args.nchunks,
            TotalNodes=args.total_nodes,
            Target=args.target,
            Mode=args.mode,
            Flavor=args.flavor,
            CPUPercent=args.cpu_percent,
    )

# source /data/t2k-nova/MainSetup.sh
# export PUFIN_OUT=/data/t2k-nova/PUfINOutputs/_MultiProcess
# python GenSubmit.py GenGenie \
#     --container /project/cherdack/containers/Generators/t2k-nova-generator.sif \
#     --events 10000 \
#     --nchunks 1000 \
#     --total_nodes 20 \
#     --cpu_percent 100

# python GenSubmit.py GenGenie \
#     --container /project/cherdack/containers/Generators/t2k-nova-generator.sif \
#     --events 1000 \
#     --nchunks 80 \
#     --total_nodes 2 \
#     --cpu_percent 100



