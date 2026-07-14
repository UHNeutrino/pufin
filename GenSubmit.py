import os
import argparse
import time
import GenMain
import subprocess
from multiprocessing import cpu_count

# This script runs GenMain->GenNeutCards to get a list of cards
# Then it runs GenMain->GenNeutMultiOnNode on multiple nodes with the nodeID and NChunks given


def NeutRunScript(Container, Tune, Events, TotalNodes, NChunks, Target=None, Mode=None, Flavor=None, CPUPercent=None):
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
        --wrap "apptainer exec --writable-tmpfs --bind {OutPath}:{OutPath} {Container} bash -c \\"source /opt/SetupAll.sh && export PUFIN_OUT={OutPath}  && python GenMain.py NeutXsec --tune {Tune} --target \\\\\\"{Targets}\\\\\\" \\" "
        """
    print(xseccmd)
    # xp = subprocess.Popen(xseccmd)

    processes = []
    FileNames = []
    FileNames = GenMain.CheckNeutFiles(CardNames,NChunks)
    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    NCores = max(1,int( cpu_count()*CPUPercent))
    NodeFiles = []
    # Sort NuMu to the front so it gets distributed equallyu
    print(f"Not Sorted {len(FileNames)}")
    FileNames = sorted(FileNames, key=lambda x: "_NuMu_" not in x)
    print(f"Total Files: {len(FileNames)}")


    for Node in range(0,TotalNodes):
        NodeFiles = FileNames[Node::TotalNodes] #split up card name based on number of nodes
        SlurmTime = NeutTimeEstimator(NodeFiles)
        print(f"Files on Node {Node}: {len(NodeFiles)}")
        cmd = f"""sbatch \\
        --nodes=1 \\
        --ntasks-per-node=1 \\
        --cpus-per-task={NCores} \\
        --time={SlurmTime} \\
        --wrap "apptainer exec --writable-tmpfs --bind {OutPath}:{OutPath} {Container} bash -c 'source /opt/SetupAll.sh && export PUFIN_OUT={OutPath} && python GenMain.py NeutMult --Files \\"{NodeFiles}\\" --CPUPercent {CPUPercent}'"
        """
        print(cmd)
        # p = subprocess.Popen(cmd)   # each cmd is a separate process
        # processes.append(p)
    
        
def GenieRunScript(Container, Tune, NChunks, TotalNodes, Target=None, Mode=None, Flavor=None, CPUPercent=None):
    OutPath = "/data/t2k-nova/PUfINOutputs/_MultiProcess"
    os.makedirs(OutPath, exist_ok=True)

    OldOutPath = os.environ.get("PUFIN_OUT")
    os.environ["PUFIN_OUT"] = OutPath

    Generator = "GENIE"

    FilePath, Targets = GenMain.DirectorySetup(Generator, SingleTarget=Target, Mode=Mode)
    GenMain.FlatFluxMaker()

    FileNames = GenMain.CheckGenieFiles(
        Tune=Tune,
        Targets=Targets,
        Events=NChunks,   # For multiprocessing, this means NuMu NChunks
        Modes=Mode,
        Flavors=Flavor,
    )

    if OldOutPath == None:
        del os.environ["PUFIN_OUT"]
    else:
        os.environ["PUFIN_OUT"] = OldOutPath

    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")

    NCores = max(1, int(cpu_count()*CPUPercent))

    print(f"Not Sorted {len(FileNames)}")
    FileNames = sorted(FileNames, key=lambda x: "_NuMu_" not in x)
    print(f"Total Files: {len(FileNames)}")

    processes = []

    for Node in range(0, TotalNodes):
        NodeFiles = FileNames[Node::TotalNodes]

        if len(NodeFiles) == 0:
            print(f"Files on Node {Node}: 0")
            continue

        SlurmTime = GenieTimeEstimator(NodeFiles)

        print(f"Files on Node {Node}: {len(NodeFiles)}")

        cmd = f"""
        sbatch \\
        --nodes=1 \\
        --ntasks-per-node=1  \\
        --cpus-per-task={NCores} \\
        --time={SlurmTime} \\
        --wrap "apptainer exec --writable-tmpfs --bind {OutPath}:/mnt {Container} bash -c 'source /opt/SetupAll.sh && export PUFIN_OUT={OutPath} && python GenMain.py GenieMult --Files "{NodeFiles}" --CPUPercent {CPUPercent} '"
        """

        print(cmd)
        # p = subprocess.Popen(cmd, shell=True)
        # processes.append(p)

    for p in processes:
        p.wait()

def NeutTimeEstimator(Files):
    # loop through all files and come up with a decent time estimation using linear regressions from trends found in initial testing
    EventsAndPart = Files[0].split("_")[7]
    print(EventsAndPart)
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
    GenieParser.add_argument("--tune", default=None)
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
        Tune=args.tune,
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
#   --container /path/to/container.sif \
#   --tune N24 \
#   --total_nodes 2 \
#   --cpu_percent 75 \
#   --nchunks 10 \
#   --target Carbon \
#   --mode CC \
#   --flavor NuMu



