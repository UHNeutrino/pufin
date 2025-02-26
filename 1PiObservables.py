import ROOT
import PlotQuantiles as pq
import ParticlePlots as pp 
import SetupFunctions as sf







file_path = 't2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e7.root'

file_name = file_path.split('/')[2]
generator = file_name.split('_')[1]
flux = file_name.split('_')[2]


# x_bins, total_events = pq.constant_event_binning(x, y, file_path, Mode = 2)
histInfo = ("name",f"plop1",40,1.1,1.8,42,-0.1,2)



plottitle = "W vs Q^{2} for 1Pi events at #nu_{E} =" + flux


AxisInfo1 = ['Q^{2}', '(GeV)^{2}','W', '(GeV)', plottitle]
df1Pi= pp.CreateDataFrame(file_path, "Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 ")
# hist2p_q = pp.Create2DHistogram(df1Pi,'W','Q2',histInfo)
# pp.Savehist(hist2p_q,AxisInfo1,"t2k-nova/1PiPlots","1PiWvQ2")





# Evis vs Etrue (REC)

plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")

# E_kinQE vs E true (REC) 
plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
histInfo2 = ("name",f"plop1",40,0.5,.9,40,0,0.85)
AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")


# enu_QE vs enu_TRUE
# plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
# histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
# AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
# hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
# pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")

# TKI variables (look at talks or something)
# plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
# histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
# AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
# hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
# pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")

# Proton kinematics
# plottitle = "E_{#nu true} vs E_{av} for 1Pi events at #nu_{E} =" + flux
# histInfo2 = ("name",f"plop1",100,0,1,100,0,1)
# AxisInfo2 = ['E_{#nu true}', '(GeV)','E_{av}', '(GeV)', plottitle]
# hist2p_q = pp.Create2DHistogram(df1Pi,'Enu_true','Eav',histInfo2)
# pp.Savehist(hist2p_q,AxisInfo2,"t2k-nova/1PiPlots","1PiEvE")
