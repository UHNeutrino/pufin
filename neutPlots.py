import ParticlePlots




# x = 'q0'
# y = 'q3'
# histInfo = ("name",f"{x} vs {y} plot",40,0,2,40,0,2)
# ParticlePlots.Plot2P2H(x,y,histInfo, "q0_v_q3_hist")

x = 'W'
y = 'Q2'
histInfo1 = ("name",f"{x} vs {y} plot",60,0,3,124,-0.2,6)
histInfo2 = ("name",f"{x} vs {y} plot",60,0,1.2,60,0,1.2)
# print(histInfo)
ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6.root")
ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_1.0GeV_1e6.root")
ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_1.5GeV_1e6.root")
ParticlePlots.Plot1PI(x,y,histInfo1,"1PI_hist","t2k-nova/FlatTrees/Flat_NEUT_3GeV_1e6.root")

x = 'q3'
y = 'q0'

ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_0.7GeV_1e6.root")
ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_1.0GeV_1e6.root")
ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_1.5GeV_1e6.root")
ParticlePlots.Plot2P2H(x,y,histInfo2,"2P2H_hist","t2k-nova/FlatTrees/Flat_NEUT_3GeV_1e6.root")
