import os
import argparse
import ROOT
import random
import shutil
import subprocess
import GlobalV
import glob
import GenMain
import json
import subprocess
from multiprocessing import cpu_count

# This script runs GenMain->GenNeutCards to get a list of cards
# Then it runs GenMain->GenNeutMultiOnNode on multiple nodes with the nodeID and NChunks given


def NeutRunScript( Tune, Events, TotalNodes, NChunks, Target=None, Mode=None, Flavor=None, CPUPercent=None):
    Generator = "NEUT"
    FilePath,Targets = GenMain.DirectorySetup(Generator, SingleTarget=Target, Mode=Mode)
    GenMain.FlatFluxMaker()
    CardNames = GenMain.MakeNeutCards(Tune, Targets, Events, Modes=Mode, Flavors=Flavor)
    GenMain.GenNeutXsec(Tune, Targets)
    processes = []
    CardNames = GenMain.CheckNeutFiles(CardNames,NChunks)
    if CPUPercent > 1 and CPUPercent <= 100:
        CPUPercent /= 100
    elif CPUPercent > 100 or CPUPercent < 0:
        raise ValueError("CorePercent must be 0<x leq 1 or 1<x<100")
    NCores = max(1,int( cpu_count()*CPUPercent))
    NodeCards = []
    # Sort NuMu to the front so it gets distributed equallyu
    print(f"Not Sorted {len(CardNames)}")
    CardNames = sorted(CardNames, key=lambda x: "_NuMu_" not in x)
    print(f"Total Cards: {CardNames}")
    for Node in range(0,TotalNodes):
        NodeCards = CardNames[Node::TotalNodes] #split up card name based on number of nodes
        print(f"Cards on each Node: {NodeCards}")
        cmd = f"""
        sbatch \
        --nodes=1 \
        --ntasks-per-node=1  \
        --cpus-per-task={NCores} \
        --wrap 'python GenMain.py NeutMult --Cards {NodeCards} --NodeID {Node} --CPUPercent {CPUPercent} --NChunks {NChunks} '
        """
        # print(cmd)
        # p = subprocess.Popen(cmd)   # each cmd is a separate process
        # processes.append(p)
    
    for p in processes:
        p.wait()
    
if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    ## call to script GenNeut --events 1000 --tune Prod7E  --total_nodes 3 --cpu_percent 75 --nchunks 100 
    subparsers = parser.add_subparsers(dest="command", required=True)
    #If just regular Generating:
    GenParser = subparsers.add_parser("GenNeut")
    GenParser.add_argument("--events", required=True, type=int)
    GenParser.add_argument("--tune", required=True)
    GenParser.add_argument("--total_nodes", required=True, type=int)
    GenParser.add_argument("--cpu_percent", required=True, type=float)
    GenParser.add_argument("--nchunks", required=True, type=int)    
    GenParser.add_argument("--target", default=None)
    GenParser.add_argument("--mode", default=None)
    GenParser.add_argument("--flavor", default=None)

    args = parser.parse_args()
    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath==None:
        raise ValueError("PUFIN_OUT Needs to be defined!")
    NeutRunScript(
                Events=args.events,
                Tune=args.tune,
                TotalNodes = args.total_nodes,
                Target=args.target,
                Mode=args.mode,
                Flavor=args.flavor,
                CPUPercent= args.cpu_percent,
                NChunks= args.nchunks,
            )



