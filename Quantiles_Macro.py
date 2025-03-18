import PlotQuantiles as pq
import ParticlePlots as pp
import SetupFunctions as SF



file_path = '/data/t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e7.root'
# file_path = ''
if file_path == '':
    file_name = input("Input Root file name: ")
    file_path = f"/data/t2k-nova/FlatTrees/{file_name}"

print(file_path)
lines = 0
if lines:
    print("no")
    # NameParts = SF.formatName(file_path)
    # x = 'q3'
    # y = 'q0' 
    # histInfo2 = ("name",f"{x} vs {y} plot",60,0,3,60,0,3)
    # AxisInfo = ['q_{0}', '(GeV)','q_{3}', '(GeV)']
    # hist, path = pp.Plot2P2H(x,y,histInfo2,file_path) 
    # x_bins, total = pq.constant_event_binning(x,y,file_path)
    # y_bins, total  = pq.constant_event_binning(y,x,file_path)
    # pq.visualize_segements(hist, file_path, x_bins=x_bins)
    # pq.visualize_segements(hist, file_path, y_bins=y_bins)
    # pq.visualize_segements(hist, file_path, x_bins=x_bins, y_bins=y_bins)

pq.PlotSegments(file_path=file_path)
pq.PlotGrid(file_path=file_path)
