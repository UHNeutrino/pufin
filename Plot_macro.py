import ParticlePlots
import os
import glob


userFolder = "/home/lboe/t2k-nova/FlatTrees"
root_files = glob.glob(userFolder + '/*.root')

# print(root_files)



for file in root_files:
    # format correctly
    file_path = file.split('t2k-nova')[1]
    file_path = 't2k-nova' + file_path
    # print(file_path)

    x = 'W'
    y = 'Q2'
    histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
    histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist",file_path)
    ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist_max",file_path, max = 80000)
    ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist_Normalized",file_path, Normalize = 1)

    x = 'q3'
    y = 'q0' 

    ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist",file_path)
    ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist_max",file_path, max = 80000)
    ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist_Normalized",file_path, Normalize = 1)
    
