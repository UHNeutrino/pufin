import ROOT
import os


print("test upload")

# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")

# enables multiprocessing
ROOT.EnableImplicitMT()

# Allows python to manage the memeory rather than ROOT
ROOT.TH1.AddDirectory(False)


# use Rdataframes to plot the q0 v q3 2DHisto and Q^2 vs W 2DHisto for 2P2H interacions, which have mode 2
# Plan is to get the q0, q3, Q^2 and W for all events where Mode = 2





# First get the data into a dataframe
fileName = f"{HOME}/generators/Flat_NEUT_1GeV_1e6.root"
treeName = "FlatTree_VARS"
parts = fileName.split('/')
NameRoot = parts[4]
NameParts = NameRoot.split('.')
Name = NameParts[0]



def formatHist(hist, xlabel, ylabel, max = -1):
    hist.GetXaxis().SetTitle(xlabel)
    hist.GetYaxis().SetTitle(ylabel)
    if max != -1:
        hist.SetMaximum(max)
    hist.SetTitle("")
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)

    # hist.GetXaxis().SetLabelSize(0);
    # hist.GetXaxis().SetTickLength(0);

    return hist.Clone()

def Plot2P2H(v1, v2, histogramInfo, title):
    df = ROOT.RDataFrame(treeName,fileName)

    # entries1 = D.Filter(cut1)\
    #             .Count()
    # f = ROOT.TFile(fileName)
    # ft = f.Get(treeName)
    # df = ROOT.RDataFrame(ft)


    # Mode 2 is the 2P2H interaction
    cut1 = 'Mode == 2'


    # entries1 = df.Filter(cut1)\
    #              .Count()
    # print('{} entries passed all filters'.format(entries1.GetValue()))

    hist1 = df.Filter(cut1).Histo2D(histogramInfo,v2,v1)

    hist = formatHist(hist1 ,'q_{3} (GeV)','q_{0} (GeV)', f'q_{3} vs q_{0} of {Name}')

    # Histo2D(("name","title",40,0,2,40,0,2),v1,v2),v2,v2)
    
    c = ROOT.TCanvas()
    # c.SetCanvasSize(1500, 1500)
    # c.SetWindowSize(500, 500)
    hist.Draw("COLZ")
    # c.SetCanvasSize(600,500)
    c.SetCanvasSize(c.GetWw()+200,c.GetWh())
    # print(f'{c.GetWindowHeight()}')

    # saves hist a specific directory I made in my home dir 
    c.SaveAs(f"{HOME}/generators/plots/{title}{Name}.png")
    # Change this ^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def Plot1PI(v1, v2, histogramInfo, title):
    df = ROOT.RDataFrame(treeName,fileName)

    # Modes for single Pi are 11-16
    cut1 = 'Mode == 11 || Mode ==  12 || Mode == 13 || Mode == 14 || Mode == 15 || Mode == 16 '

    hist1 = df.Filter(cut1).Histo2D(histogramInfo,v2,v1)
    hist = formatHist(hist1,'Q^{2} (GeV)','W (GeV)',"Q^{2} vs W of"+Name)
    c = ROOT.TCanvas()
    hist.Draw("COLZ")

    c.SetCanvasSize(c.GetWw()+200,c.GetWh())


    # saves hist to your home directory
    c.SaveAs(f"{HOME}/generators/plots/{title}{Name}.png")
    # Change this ^^^^^^^^^^^^^^^^^^^^^^^^^^^^







if __name__=="__main__":
    # print("hi")
    v1 = 'q0'
    v2 = 'q3'
    histInfo = ("name",f"{v1} vs {v2} plot",40,0,2,40,0,2)
    Plot2P2H(v1,v2,histInfo, "qvqhist")
    v1 = 'Q2'
    v2 = 'W'
    histInfo = ("name",f"{v1} vs {v2} plot",40,0,2,40,0,2)
    # print(histInfo)
    Plot1PI(v1,v2,histInfo,"Q2vWhist")








