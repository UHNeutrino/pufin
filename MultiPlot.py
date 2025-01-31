import ROOT
import os
import ParticlePlots as pp

# lets me use other people's home directories
HOME = os.getenv("HOME", "/home/lboe")
dir_location = "t2k-nova/plots_quantiles/Hists_GenieNOvA_.7GeV_10E6.root"

NameParts = pp.formatName(dir_location)

# Open the ROOT file
fileName = f"{HOME}/{dir_location}"
root_file = ROOT.TFile.Open(fileName, "READ")

def LoadHistos(rf):
    histos = []
    for key in rf.GetListOfKeys():
        obj = key.ReadObj()
        
        # Check if the object is a histogram (TH1 or TH2)
        if isinstance(obj, ROOT.TH1) or isinstance(obj, ROOT.TH2):
            histos.append(obj)
    
    return histos


# Load histograms into list called histos
histos = LoadHistos(root_file)

# Print loaded histogram names for debugging
#print("Loaded histograms:", [h.GetName() for h in histos])

# Create a canvas
cFull = ROOT.TCanvas("cFull", "Canvas", 800, 600)

# Set margins
cFull.SetBottomMargin(0.25)
cFull.SetLeftMargin(0.25)
cFull.SetTopMargin(0.25)
cFull.SetRightMargin(0.25)

# Divide the canvas into a 4x1 grid
cFull.Divide(3, 2, 0, 0)

# Set a color-blind friendly palette
#ROOT.gStyle.SetPalette(112)  # kCividis (or use 111 for kViridis)
ROOT.gStyle.SetPalette(ROOT.kRainBow)    

# Loop over list of histograms 
for i in range(0, len(histos)):
    print(f"Drawing histogram {i} of {len(histos)}")  # Debug print
    cFull.cd(i+1)  # Move to the correct sub-pad because pad 1 for root = histo 0 for python
    histos[i].SetTitle(";;")  # Remove titles
    histos[i].SetMarkerStyle(8)  # Set marker style
    histos[i].Draw("colz")  # Draw histogram
    
# Go back to the main canvas to add a title and axis labels
cFull.cd()

# Add a global title
title = ROOT.TLatex()
title.SetTextSize(0.05)
title.SetTextAlign(22)  # Center alignment
title.DrawLatexNDC(0.5, 0.97, f"COS #theta vs. P_{{#mu}} ({NameParts[1]}: {NameParts[3]}#nu_{{#mu}} events at {NameParts[2]})")  # (x, y) in normalized device coordinates

# Add X-axis label (centered at the bottom)
xlabel = ROOT.TLatex()
xlabel.SetTextSize(0.04)
xlabel.SetTextAlign(22)
xlabel.DrawLatexNDC(0.5, 0.02, "P_{#mu} (GeV)")  # Adjust as needed

# Add Y-axis label (centered vertically on the left)
ylabel = ROOT.TLatex()
ylabel.SetTextSize(0.04)
ylabel.SetTextAngle(90)  # Rotate text vertically
ylabel.SetTextAlign(22)
ylabel.DrawLatexNDC(0.02, 0.5, "COS #theta")  # Adjust as needed

# Save the canvas
cFull.SaveAs("/home/kdobbs/t2k-nova/plots_quantiles/comparisons.png")

