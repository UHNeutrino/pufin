import json5
import ROOT
import os
import datetime
import ParticlePlots as pp 
import SetupFunctions as sf
import glob


sf.setupRoot
userFolder = f"/data/t2k-nova/FlatTrees"
f = open('/home/lboe/t2k-nova/main.json5')
data = json5.load(f)

quantiles = data.get("quantiles")
plots = data.get("plots")
stacks = data.get("stacks")

if (plots["Bool"]):
    root_files = glob.glob(userFolder + f'/*{plots["Gen"]}*{plots["Flux"]}*.root')

    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        BinL = plots["Bins"]
        AxisInfo = []
        df = pp.CreateDataFrame(file_path, plots["Cut"])
        if(plots["EvisB"]):
            df = pp.DefineEvis(df)  
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)
        if(plots["reWeight"][0]):
            df = pp.defineWeights(df,plots["reWeight"][1],plots["reWeight"][2])

        if plots["Type"] == "1D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
            if(plots["reWeight"][0]):
                hist = df.Histo1D(histInfo,plots["Var1"],"weights")
            else:
                hist = df.Histo1D(histInfo,plots["Var1"])
        if plots["Type"] == "2D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
            if(plots["reWeight"][0]):
                hist = df.Histo2D(histInfo,plots["Var1"],plots["Var2"],"weights")
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
            pp.Savehist(hist,AxisInfo,plots["Save"],fileN,plots["Ext"],max = plots["max"], Normalize=plots["Norm"])

if (stacks["Bool"]):
    root_files = glob.glob(userFolder + f'/*{stacks["Gen"]}*{stacks["Flux"]}*.root')
    for file_path in root_files:
        file_name = file_path.split('/')[-1]
        generator = file_name.split('_')[1]
        flux = file_name.split('_')[2]
        df = pp.CreateDataFrame(file_path, stacks["Cut"])
        BinL = stacks["Bins"]
        AxisInfo = []
        cuts = []
        Legend = []
        colors = []
        if(stacks["EvisB"]):
            df = pp.DefineEvis(df)
        for word in stacks["AxisInfo"].split(','):
                AxisInfo.append(word)
        for cut,name in stacks["StackCuts"].items():
            cuts.append(cut)
            Legend.append(name)
        histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
        for num in stacks["Colors"].split(","):
            colors.append(int(num))
        
        stack, histlist = pp.PlotStackedEventCuts(df, stacks["Var1"], histInfo, cuts, colors)
        save_L = stacks["Save"] + generator + '-' + flux + stacks["Name"] + "." +stacks["Ext"]
        pp.SaveStackedHist(stack, histlist, AxisInfo, Legend,save_L,max = stacks["max"], Normalize=stacks["Norm"])


