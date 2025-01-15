import ROOT
import os
import ParticlePlots




# v1 = 'q0'
# v2 = 'q3'
# histInfo = ("name",f"{v1} vs {v2} plot",40,0,2,40,0,2)
# ParticlePlots.Plot2P2H(v1,v2,histInfo, "q0_v_q3_hist")

v1 = 'W'
v2 = 'Q2'
histInfo = ("name",f"{v1} vs {v2} plot",50,0,1,50,0.8,1.6)
# print(histInfo)
ParticlePlots.Plot1PI(v1,v2,histInfo,"W_v_Q2_hist")