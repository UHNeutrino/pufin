import json
import ROOT
import os
import datetime
import ParticlePlots as pp 
import SetupFunctions as sf
import glob


userFolder = f"/data/t2k-nova/FlatTrees"
f = open('/home/lboe/t2k-nova/main.json')
data = json.load(f)

quantiles = data.get("quantiles")
plots = data.get("plots")








if (plots["Bool"]):
    globterms = ""
    root_files = glob.glob(userFolder + f'/*{plots["Gen"]}*{plots["Flux"]}*.root')

    for file_path in root_files:
        BinL = []
        AxisInfo = []
        df = pp.CreateDataFrame(file_path, plots["Cut"])
        if(plots["EvisB"]):
            df = pp.DefineEvis(df)
        
        i=0
        for num in plots["Bins"].split(','):
            if (i%3 == 0):
                BinL.append(int(num))
            else:
                BinL.append(float(num))
            i+=1
        
        for word in plots["AxisInfo"].split(','):
            AxisInfo.append(word)

        if plots["Type"] == "1D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2])
            hist = df.Histo1D(histInfo,plots["Var1"])
        if plots["Type"] == "2D":
            histInfo = (AxisInfo[-1],AxisInfo[-1],BinL[0],BinL[1],BinL[2],BinL[3],BinL[4],BinL[5])
            print(histInfo)
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
            fileN = plots["Gen"]+plots["Flux"]+AxisInfo[-1]+x
            fileN = fileN.replace(" ", "-")
            # pp.Savehist(hist,AxisInfo,plots["Save"],f"skibidi",plots["Ext"])
            pp.Savehist(hist,AxisInfo,plots["Save"],fileN,plots["Ext"])
            


