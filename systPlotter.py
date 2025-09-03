import json5
import ROOT
import os
import datetime
import ParticlePlots as pp 
import SetupFunctions as sf
import PlotQuantiles as pq
import glob
import array


HOME = os.getenv("HOME", "/home/lboe")
sf.setupRoot
userFolder = f"/data/t2k-nova/FlatTrees"
f = open(f'{HOME}/t2k-nova/sysMain.json5')
data = json5.load(f)

plots = data.get("plots")
stacks = data.get("stacks")

if (plots["Bool"]):
    root_files = glob.glob(userFolder + f'/*{plots["Gen"]}*{plots["Flux"]}*.root')
    if root_files == []:
        print("NO such root files")

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        BinL = plots["Bins"]
        AxisInfo = []

        if (plots["sysRW"][0]) :
            f2 = ROOT.TFile(file_path)
            ft2 = f2.Get("FlatTree_VARS")
            ft2.AddFriend(plots["sysRW"][2],plots["sysRW"][1])
            print( type(ft2))
            df = ROOT.RDataFrame(ft2)
            df = df.Filter(plots["Cut"])
        else:
            df = pp.CreateDataFrame(file_path, plots["Cut"])
        if(plots["EvisB"]):
            df = pp.DefineEvis(df)  
        if (plots["KinematicsB"]):
            df = pp.DefineKinematics(df)
        if (plots["TkiB"]):
            df = pp.DefineTKI(df)
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)
        if(plots["reWeight"][0]):
            df = pp.defineWeightsSpline(df,plots["reWeight"][1],plots["reWeight"][2])
        if plots["Type"] == "1D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
            print(histInfo)
            if(plots["reWeight"][0]):
                hist = df.Histo1D(histInfo,plots["Var1"],"weights")
            elif(plots["sysRW"][0]):
                hist = df.Histo1D(histInfo,plots["Var1"],"FrAbs_pi")
            else:
                hist = df.Histo1D(histInfo,plots["Var1"])
        if plots["Type"] == "2D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
            if(plots["reWeight"][0]):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],"weights")
            elif(plots["sysRW"][0]):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],plots["sysRW"][3])
            else:
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"])
        if plots["Ext"] == "root":
            rootTitle = plots["Cut"]
            rootTitle = rootTitle.replace(" ","")
            out_file = ROOT.TFile(f"/data/t2k-nova/Histograms/{rootTitle}.root", "UPDATE")
            hist.Write()  # Write the histogram to the file
            out_file.Close()  # Close to finalize writing
        else:
            nx = datetime.datetime.now()
            x = str(nx)
            fileN = generator+flux+plots["Name"]+x
            fileN = fileN.replace(" ", "-")
            pp.Savehist(hist,AxisInfo,plots["Save"],fileN,plots["Ext"],max = plots["max"], Normalize=plots["Norm"], logz = plots["logz"])

if (stacks["Bool"]):
    root_files = glob.glob(userFolder + f'/*{stacks["Gen"]}*{stacks["Flux"]}*.root')
    if root_files == []:
        print("NO such root files")

    weights = ""
    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        if (stacks["sysRW"][0]) :
            f2 = ROOT.TFile(file_path)
            ft2 = f2.Get("FlatTree_VARS")
            ft2.AddFriend(stacks["sysRW"][2],stacks["sysRW"][1])
            print( type(ft2))
            df = ROOT.RDataFrame(ft2)
            df = df.Filter(stacks["Cut"])
            weights = stacks["sysRW"][3]
        else:
            df = pp.CreateDataFrame(file_path, stacks["Cut"])
        BinL = stacks["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(stacks["EvisB"]):
            df = pp.DefineEvis(df)
        if(stacks["TkiB"]):
            df = pp.DefineTKI(df)
        for word in stacks["AxisInfo"].split(','):
                AxisInfo.append(word)
        print(AxisInfo)
        for cut,name in stacks["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for num in stacks["Colors"].split(","):
            colors.append(int(num))
        
        stack, histlist = pp.PlotStackedEventCuts(df, stacks["Var1"], histInfo, cuts, colors,weights = weights)
        save_L = stacks["Save"] + "/" + generator + '-' + flux + stacks["Name"] + "." +stacks["Ext"]
        pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,save_L, Normalize=stacks["Norm"])
