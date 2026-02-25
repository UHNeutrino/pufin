import ROOT
import ParticlePlots as pp
import array
import SetupFunctions as SF

class FluxObject:
    Targets = {"T2K":5.9e29, "NOvA":5.6e31}
    xsecScale = {"NEUTAll":3.10e-37,"GENIECC":2.379e-37}
    Exposure = {"T2K":19.7e20, "NOvA":26.6e20}
    FluxPot = {"enu_nd5_23a_untuned_numu":1e21, "cafanauniq0":5e21}
    UnitsDir = {"enu_nd5_23a_untuned_numu":["50MeV","1e21POT","cm^{2}"], "cafanauniq0":["5e21POT","m^{2}"]}

    def __init__(self,Generator=None, h=None, histPathTuple=None):
        if h:
            self.Fhist = h.Clone()
            self.Fhist.SetDirectory(0)  # idk what this does
        elif histPathTuple:
            rootPath,hist_name = histPathTuple
            f = ROOT.TFile.Open(rootPath)
            h = f.Get(hist_name)
            if not h:
                raise ValueError(f"Histogram {hist_name} not found.")
            self.Fhist = h.Clone()
            self.Fhist.SetDirectory(0)
            f.Close()
        else:
            raise ValueError("Provide either hist or (root_file, hist_name)")
        

        n_points0 = self.Fhist.GetNbinsX()
        j = 1
        a = 0
        self.BinEdges = []
        while a<8:
            j+=1
            a = self.Fhist.GetBinLowEdge(j)
            self.BinEdges.append(a)
            # print(a)
            
        # print(self.BinEdges)
        # print(len(self.BinEdges))
        # print(j)
        n_points0 = j-1
        self.BinN = n_points0
        graph0 = ROOT.TGraph(n_points0)
        self.y = []
        for i in range(1, n_points0 + 1):
            x = self.Fhist.GetBinCenter(i)
            y = self.Fhist.GetBinContent(i) / self.Fhist.Integral("Width")
            graph0.SetPoint(i - 1, x, y)
            self.y.append(y)


        self.Spline = ROOT.TSpline3(f"g_fluxSpline_{hist_name}", graph0)
        self.Units = "#nu/"
        self.UnitsDen = []
        for u in self.UnitsDir[hist_name]:
            self.Units += u
            self.Units += " "
            self.UnitsDen.append(u)
        if ("MeV".casefold() in a.casefold for a in self.UnitsDen) or("GeV".casefold() in a.casefold for a in self.UnitsDen) :
            print("Bin Width Normed!~")
            self.bwNormed = True
        else:
            self.bwNormed = False
        self.Integral = self.Fhist.Integral("Width")
        self.BinEdgesA = array.array('d', self.BinEdges)
        self.Title = "Default Title"
        self.XTitle = "E_{#nu} GeV"
        print("Made Flux Object")

    def MakeHist(self):
        self.hist = ROOT.TH1D("h1", f"{self.Title}; {self.XTitle}; {self.Units}", self.BinN-1, self.BinEdgesA)
        for i in range(1, self.BinN+1):
            center = self.hist.GetBinCenter(i)
            Ncontent = self.Spline.Eval(center) * self.Integral
            self.hist.SetBinContent(i, Ncontent)
        self.hist.SetStats(0)
        print("Histogram Made")
    
    def ChangeBinning(self,bins=None, histPathTuple=None):
        if histPathTuple:
            rootPath,hist_name = histPathTuple
            f = ROOT.TFile.Open(rootPath)
            h = f.Get(hist_name)
            if not h:
                raise ValueError(f"Histogram {hist_name} not found.")
            Bhist = h.Clone()
            Bhist.SetDirectory(0)
            f.Close()
            nbins = []
            j = 1
            a = 0
            while a<8:
                j+=1
                a = Bhist.GetBinLowEdge(j)
                nbins.append(a)
            n_points = j-1
        elif bins:
            nbins = bins
            n_points = len(nbins)-1
        else:
            raise ValueError("Provide either bins or (root_file, hist_name)")
        if self.bwNormed:
            self.BinEdges = nbins
            self.BinN = n_points
        else:
            #if it's not bin width normalized than the integral changes and the shape could change
            total = 0
            Newtotal = 0
            variableBW = False
            newWidth = nbins[1] - nbins[0]
            for i in range(0,n_points):
                if(newWidth != nbins[i+1]-nbins[i]):
                    variableBW = True
                newWidth = nbins[i+1]-nbins[i]
                Newtotal += newWidth * self.y[i]
            widthFactor = total/n_points
            self.BinEdges = nbins
            self.BinN = n_points


    
    def SplineToFlatFlux(self,Generator=None):
        if Generator=="NEUT":
            self.df = ROOT.RDataFrame("FlatTree_VARS","/data/t2k-nova/FlatTrees/Flat_NEUT5.9_flatf_1e7.root")
        elif Generator=="GENIE":
            self.df = ROOT.RDataFrame("FlatTree_VARS","/data/t2k-nova/FlatTrees/Flat_GenieN24_flatf_1e7.root")

    def SaveHistroot(self, path, name):
        out_file = ROOT.TFile(f"{path}/{name}/.root","UPDATE")
        self.hist.Write()
        out_file.Close()
        print(f"Saved to {path}/{name}/.root")
    def SaveHistpng(self, path, name):
        c = ROOT.TCanvas()
        SF.formatTcanvas(self.hist,c)
        c.SaveAs(f"{path}/{name}.png")
        print(f"Histogram png saved to {path}/{name}.png")

        
        
if __name__=="__main__":
    a = FluxObject(histPathTuple= ("/data/t2k-nova/fluxes/23av1_nom/nd5_numode_23a_nominal_finebins.root","enu_nd5_23a_untuned_numu"))
    a.MakeHist()
    # a.SaveHistpng("/home/lboe","test3")
    # print(a.Fhist.GetBinCenter(a.BinN))