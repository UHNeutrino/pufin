import ParticlePlots as pp
import glob
import os


HOME = os.getenv("HOME", "/home/lboe")


userFolder = f"{HOME}/t2k-nova/FlatTrees"
root_files = glob.glob(userFolder + '/*.root')

# print(root_files)

max_frequency_1PI = -float('inf')  # Initialize with the smallest possible value
max_frequency_2P2H = -float('inf')

for file in root_files:
    # format correctly
    file_path = file.split('t2k-nova')[1]
    file_path = 't2k-nova' + file_path
  

    x = 'W'
    y = 'Q2'
    AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
    histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    pp.SavePlot(hist,"1PI_hist", AxisInfo, path)
    hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    pp.SavePlot(hist, "1PI_hist_max", AxisInfo, path, max = .035, Normalize=1)
    hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    pp.SavePlot(hist,"1PI_hist_Normalized", AxisInfo,path, Normalize = 1)

    x = 'q3'
    y = 'q0' 
    AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    pp.SavePlot(hist,"2P2H_hist", AxisInfo, path)
    hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    pp.SavePlot(hist,"2P2H_hist_max", AxisInfo, path, max = .016, Normalize = 1)
    hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    pp.SavePlot(hist,"2P2H_hist_Normalized", AxisInfo, path, Normalize = 1)
    
print(f"The highest frequency across all normalized 1PI plots is: {max_frequency_1PI}")
print(f"The highest frequency across all normalized 2P2H plots is: {max_frequency_2P2H}")

# Now plot constant frequency (z axis) files using max_frequency_1PI and max_frequency_2P2H
for file in root_files:
    # format correctly
    file_path = file.split('t2k-nova')[1]
    file_path = 't2k-nova' + file_path
    
    x = 'W'
    y = 'Q2'
    histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
    histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    
    pp.Plot1PI(x,y,histInfo1,"1PI_hist_max",file_path, max = max_frequency_1PI, Normalize=1)
    
    x = 'q3'
    y = 'q0' 
    
    pp .Plot2P2H(x,y,histInfo2,"2P2H_hist_max",file_path, max = max_frequency_2P2H, Normalize=1)
