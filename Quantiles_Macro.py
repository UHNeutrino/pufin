import PlotQuantiles as pq
import ParticlePlots as pp
import SetupFunctions as sf
import os 
import glob

HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"
montecarlo = input("Enter the name of your montecarlo: NEUT, NOvA, or ICARUS. If you want to generate plots for all Flat Trees in the directory hit 'enter' ")

#root_files = glob.glob(userFolder + '/*NOvA*.root')
root_files = glob.glob(userFolder + f'/*{montecarlo}*.root')
print(f"Root Files: {root_files}")

modeDic = sf.modeDic()

print("Making File Plots: ")

for file_path in root_files :

    pq.PlotSegments(file_path=file_path)
    pq.PlotGrid(file_path=file_path)
