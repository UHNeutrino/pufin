import ROOT
import os
import ParticlePlots




# v1 = 'q0'
# v2 = 'q3'
# histInfo = ("name",f"{v1} vs {v2} plot",40,0,2,40,0,2)
# ParticlePlots.Plot2P2H(v1,v2,histInfo, "q0_v_q3_hist")

v1 = 'W'
v2 = 'Q2'
histInfo1 = ("name",f"{v1} vs {v2} plot",60,0,3,120,0,6)
histInfo2 = ("name",f"{v1} vs {v2} plot",60,0,3,60,0,3)
# print(histInfo)
ParticlePlots.Plot1PI(v1,v2,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6.root")
ParticlePlots.Plot1PI(v1,v2,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_1.0GeV_1e6.root")
ParticlePlots.Plot1PI(v1,v2,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_1.5GeV_1e6.root")
ParticlePlots.Plot1PI(v1,v2,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_3GeV_1e6.root")

v1 = 'q0'
v2 = 'q3'

ParticlePlots.Plot2P2H(v1,v2,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6.root")
ParticlePlots.Plot2P2H(v1,v2,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_1.0GeV_1e6.root")
ParticlePlots.Plot2P2H(v1,v2,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_1.5GeV_1e6.root")
ParticlePlots.Plot2P2H(v1,v2,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_3GeV_1e6.root")
