import ParticlePlots as pp
import PlotQuantiles as pq
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
  

    # x = 'W'
    # y = 'Q2'
    # AxisInfo = ['q_{3}', '(GeV)','q_{0}', '(GeV)']
    # histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
    # histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist,"1PI_hist", AxisInfo, path)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist, "1PI_hist_max", AxisInfo, path, max = .035, Normalize=1)
    # hist, path = pp.Plot1PI(x,y,histInfo1,file_path)
    # pp.SavePlot(hist,"1PI_hist_Normalized", AxisInfo,path, Normalize = 1)

    # x = 'q3'
    # y = 'q0' 
    # AxisInfo = ['W', '(GeV)','Q^{2}', '(GeV)^{2}']
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist", AxisInfo, path)
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist_max", AxisInfo, path, max = .016, Normalize = 1)
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path)
    # pp.SavePlot(hist,"2P2H_hist_Normalized", AxisInfo, path, Normalize = 1)


    # Make q0 vs q3 histogram to find quantiles with equal events
    x = 'q3'
    y = 'q0'
    
    
    x_bins, total_events = pq.constant_binning(x, y, file_path=file_path)
    
    # Apply quantile_cutting to make a new dataframe for each quantile 
    quantile_dfs = pq.quantile_cutting(x, y, x_bins, file_path=file_path)
    
    # Check: Print the number of events in each quantile
    for i, df in enumerate(quantile_dfs):
        print(f"Quantile {i+1}: {df.Count().GetValue()} events")
        
    # Make plots for each dataframe
    y = 'CosLep'
    x = 'PLep'
    
    #AxisInfo = ['cos{theta}', '', 'E Lep', '(GeV)'] not using this yet
    histInfo = ("name", f"{y} vs {x} plot", 60, 0, 3.5,102, -1.02, 1.02)
    
    # Create and save a plot for each quantile
    for i, df in enumerate(quantile_dfs):
        # Define a title for the current quantile plot
        title = f"Quantile_{i+1}"
        pq.PlotQuantiles(x, y, histInfo, file_path=file_path, df = df, title = title)


    
# print(f"The highest frequency across all normalized 1PI plots is: {max_frequency_1PI}")
# print(f"The highest frequency across all normalized 2P2H plots is: {max_frequency_2P2H}")

# Now plot constant frequency (z axis) files using max_frequency_1PI and max_frequency_2P2H
# currently not fixed to reflect PP changes
fixed = False
if fixed:
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
