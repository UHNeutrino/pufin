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
<<<<<<< HEAD
    
    # Generate normalized plot for 1PI and get the histogram object
    hist_1PI = ParticlePlots.Plot1PI(x, y, histInfo1, "1PI_hist_Normalized", file_path, Normalize=1)

    # Check the maximum frequency in the current histogram
    if hist_1PI is not None:
        current_max_1PI = hist_1PI.GetMaximum()
        if current_max_1PI > max_frequency_1PI:
            max_frequency_1PI = current_max_1PI
    
    ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist",file_path)
    ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist_Normalized",file_path, Normalize = 1)

    x = 'q3'
    y = 'q0' 
    
    hist_2P2H = ParticlePlots.Plot2P2H(x, y, histInfo1, "2P2H_hist_Normalized", file_path, Normalize=1)

    # Check the maximum frequency in the current histogram
    if hist_2P2H is not None:
        current_max_2P2H = hist_2P2H.GetMaximum()
        if current_max_2P2H > max_frequency_2P2H:
            max_frequency_2P2H = current_max_2P2H

    ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist",file_path)
    ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist_Normalized",file_path, Normalize = 1)
=======
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
>>>>>>> 1bdb1a5 (overhaul of PP and PM for future proofing)
    
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
    
    ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist_max",file_path, max = max_frequency_1PI, Normalize=1)
    
    x = 'q3'
    y = 'q0' 
    
    ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist_max",file_path, max = max_frequency_2P2H, Normalize=1)
