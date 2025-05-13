import ROOT
import os
import ParticlePlots as pp 
import SetupFunctions as sf




HOME = os.getenv("HOME", "/home/lboe")
userFolder = f"/data/t2k-nova/FlatTrees"
file_path = "/data/t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e7.root"

plottitle = "test"
histInfo = ("name",f"plop1",60,1.1,2.4,105,-0.1,5)
AxisInfo1 = ['W', '(GeV)','Q^{2}', '(GeV)^{2}', plottitle]

try:
    df= pp.CreateDataFrame(file_path, " ")
except:
    print("create df broke")

try:
    hist2p_q = df.Histo2D(histInfo,'W','Q2')
except:
    print("histogram broke")