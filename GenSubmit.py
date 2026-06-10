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


def NeutRunScript(Generator, Tune, Events, TotalNodes, NChunks, Target=None, Mode=None, Flavor=None, CPUPercent=None):
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

    for Node in range(0,TotalNodes):
        cmd = f"""
        sbatch \
        --nodes=1 \
        --ntasks-per-node=1  \
        --cpus-per-task={NCores} \
        --wrap 'python GenMain.py NeutMult --Cards {CardNames} --NodeID {Node} --CPUPercent {CPUPercent} --NChunks {NChunks} '
        """
        print(cmd)
        # p = subprocess.Popen(cmd)   # each cmd is a separate process
        # processes.append(p)
    
    for p in processes:
        p.wait()
    
if __name__ =="__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)
    #If just regular Generating:
    GenParser = subparsers.add_parser("GenNeut")
    GenParser.add_argument("--generator", required=True)
    GenParser.add_argument("--events", required=True, type=int)
    GenParser.add_argument("--TotalNodes", required=True, type=int)
    GenParser.add_argument("--tune", default=None)
    GenParser.add_argument("--target", default=None)
    GenParser.add_argument("--mode", default=None)
    GenParser.add_argument("--flavor", default=None)
    GenParser.add_argument("--CPUPercent", default=None)
    GenParser.add_argument("--NChunks", default=None)
    args = parser.parse_args()
    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath==None:
        raise ValueError("PUFIN_OUT Needs to be defined!")
    NeutRunScript(
                Generator=args.generator,
                Events=args.events,
                Tune=args.tune,
                TotalNodes = args.TotalNodes,
                Target=args.target,
                Mode=args.mode,
                Flavor=args.flavor,
                CPUPercent=float(args.CPUPercent),
                NChunks=int(args.NChunks),
            )



