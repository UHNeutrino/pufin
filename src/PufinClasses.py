import os
import subprocess
import shutil
import numpy as np
import ROOT
import glob
import json5
from itertools import product
if __package__:
    import src.ParticlePlots as pp
else:
    import ParticlePlots as pp            


class UHMC:
    def __init__(self, Config):
        pp.CheckUHMCConfig(Config) #this will raise an error if something is missing from the config
        self.Config = Config
        TargetF = open(Config['targets_file'])
        TargetConfig = json5.load(TargetF)
        DetectorConfig = TargetConfig[Config['detector']]
        pp.CheckDetectorConfig(DetectorConfig,Config)
        self.DetectorConfig = DetectorConfig


        self.PUFIN_OUT = os.environ.get("PUFIN_OUT")
        if self.PUFIN_OUT == None:
            raise EnvironmentError("PUFIN_OUT Must be defined for WeightMain")

        
        # Create Specifications for Weighting for each file in a dictionary of dictionaries
        # Dictionary structure is:
        #{"FileName1":{"target": target, "interaction": interaction, "nu_type": nu_type, "detector": detector, "xspline_mode": xspline_mode, "xsec_mode": xsec_mode, "xsec_file": xsec_file, "target_divisor": float(target_divisor), || -> For Genie Only "cc_path": "", "nc_path": "",}}
        self.FileDictionary = {}
        
        # Find files in PUFIN_OUT Based on Config
        AllFiles = glob.glob(f"{self.PUFIN_OUT}/{self.Config['generator'].upper()}/*/Flat*{self.Config['generator']}*{self.Config['version']}*{self.Config['tune']}*.root")
        AllFileDictionary = {}
        for file in AllFiles:
            AllFileDictionary[file] = {}
            AllFileDictionary[file]["filename"] = file.split("/")[-1]
            AllFileDictionary[file]["tune"] = AllFileDictionary[file]["filename"].split("_")[2]
            AllFileDictionary[file]["interaction"] = AllFileDictionary[file]["filename"].split("_")[3]
            AllFileDictionary[file]["flavor"] = AllFileDictionary[file]["filename"].split("_")[4]
            AllFileDictionary[file]["e_range"] = AllFileDictionary[file]["filename"].split("_")[5]
            AllFileDictionary[file]["target"] = AllFileDictionary[file]["filename"].split("_")[6]

        # This loop checks to see if all the requested files exist 
        for interaction,flavor,e_range,target in product(self.Config['filters']['interaction'],self.Config['filters']['flavor'],self.Config['filters']['e_range'],self.Config['filters']['target']):
            FileExists = False
            if e_range == "8-20GeV" and interaction != "NC":
                continue
            elif interaction == "NC" and (flavor == "NuE" or flavor == "NuEBar"):
                continue
            for file in AllFileDictionary:
                if (AllFileDictionary[file]['interaction'] == interaction) and (AllFileDictionary[file]['flavor']==flavor) and (AllFileDictionary[file]['e_range']==e_range) and (AllFileDictionary[file]['target']==target):
                    FileExists = True
                    break

            if FileExists==False:
                raise FileExistsError(f"Requested file with Interaction {interaction} Flavor {flavor} e_range {e_range} target {target} Does Not Exist")

        print(f"All Files length = {len(AllFiles)}")
        #This loop checks if the files in the all files match the filters requested
        for File in AllFiles:
            for filter in self.Config['filters']:
                AllowedBool = AllFileDictionary[File][filter] in self.Config['filters'][filter]
                if not (AllowedBool):
                    break
            if AllowedBool:
                self.FileDictionary[File] = AllFileDictionary[File]
        
        print(f"selected Files length = {len(self.FileDictionary)}")

        if len(self.FileDictionary) == 0:
            raise ValueError(f"No files found for given filters: {self.Config['filters']}")

        self.Chain = ROOT.TChain("FlatTree_VARS")
        for f in self.FileDictionary:
            self.Chain.Add(f)
        print("Root TChain made")

    def MakeDF(self):
        self.df = ROOT.RDataFrame(self.Chain)

    def MakeExpWeights(self):
        if self.df == None:
            raise ValueError("No df found, run MakeDF first")
        self.Fluxes = {}
        # self.FluxFiles = [] #might need this to keep tfiles alive?
        for flavor in self.Config['reweight']['flux_inputs']:
            f = ROOT.TFile.Open(self.Config['reweight']['flux_inputs'][flavor]['rw_file'])
            h = f.Get(self.Config['reweight']['flux_inputs'][flavor]['rw_flux'])
            h.SetDirectory(0)
            f.Close()
            self.Fluxes[flavor] = h
        print("Grabbed Fluxes")

        self.FluxSplines = {}
        # Makes a different Flux spline for each combination of Flavor * Interaction Type but NC doesn't care about flavor  
        for flavor in self.Config['filters']['flavor']:
            hist = self.Fluxes[flavor]
            n_points = hist.GetNbinsX()
            graph = ROOT.TGraph(n_points)
        
            for i in range(1, n_points + 1):
                x = hist.GetBinCenter(i)
                y = hist.GetBinContent(i)
                graph.SetPoint(i - 1, x, y)

            # SHAPE (RELATIVE SCALE): First spline made from original histogram
            spline_name = f"g_fluxSpline_{flavor}"
            spline = ROOT.TSpline3(spline_name, graph)
            self.FluxSplines[flavor] = spline
        print("Made Splines")
        self.SplineNormalizations = {}

        # Make Exp Scaling per target
        ExpScaling = {}

        common_factor = (
                self.DetectorConfig['exp_pot']
                * self.DetectorConfig['fv_nucleon_targets']
                * self.DetectorConfig['flux_cm_conv']
                / self.DetectorConfig['flux_pot']
                /  self.DetectorConfig['flux_gev_norm']
            )
        for target in self.Config['filters']['target']:
            ExpScaling[target] = common_factor*self.DetectorConfig['target_percent'][target]

        for interaction, flavor, target, energy_range, in product(self.Config['filters']['interaction'], self.Config['filters']['flavor'], self.Config['filters']['target'],self.Config['filters']['e_range']):
            if interaction == "NC" and flavor == "NuE":
                continue
            elif interaction == "NC" and flavor == "NuEBar":
                continue

            label = f"{interaction}_{flavor}_{target}_{energy_range}"
            hist = self.Fluxes[flavor]
            Fscale = ExpScaling[target]
            

            if self.Config['generator'].upper() == "GENIE":
                PathLabelDic = {"NuMu":"nu_mu", "NuMuBar":"nu_mu_bar","NuE":"nu_e","NuEBar":"nu_e_bar"}
                Fscale = Fscale *1e-38 #Genie xsec values don't include the 1e-38
                cc_path = f"{PathLabelDic[flavor]}_{target}/tot_cc"
                nc_path = f"{PathLabelDic[flavor]}_{target}/tot_nc"

                fx = ROOT.TFile.Open(self.Config['reweight']['xsec_file'], "READ")
                if not fx or fx.IsZombie():
                    raise RuntimeError(f"Could not open xsec file: {self.Config['reweight']['xsec_file']}")

                g_cc = fx.Get(cc_path)
                g_nc = fx.Get(nc_path)
                if not g_cc or not g_nc:
                    fx.ls()
                    raise RuntimeError(f"Missing graph(s): CC={cc_path} NC={nc_path}")

                g_cc = g_cc.Clone(f"g_cc_{label}")
                g_nc = g_nc.Clone(f"g_nc_{label}")
                fx.Close()

            elif self.Config['generator'].upper() == "NEUT":
                xsec_path = f"{self.PUFIN_OUT}/NEUT/Xsecs/NEUT{self.Config['version']}_{self.Config['tune']}_{target}_XSECHIST.root"
                fx = ROOT.TFile.Open(xsec_path, "READ")
                if not fx or fx.IsZombie():
                    raise RuntimeError(f"Could not open NEUT xsec file: {xsec_path}")
                fx.Close()
        
                neut_graph = pp.MakeNeutXsecGraph(xsec_path, interaction, Flavor=flavor)
                neut_spline = ROOT.TSpline3(f"neut_spline_{label}", neut_graph)

            else:
                raise ValueError("No Matching Generator Type")
            
            Spline_normalization = 0.0
            energy_min = float(energy_range[0])
            energy_max_s = energy_range.replace(str(energy_min),"")
            energy_max_s = energy_max_s.replace("-","")
            energy_max = float(energy_max_s.replace("GeV",""))

            for i in range(1, hist.GetNbinsX() + 1):
                
                x = hist.GetBinCenter(i)
                if energy_min is not None and x < energy_min:
                    continue
                if energy_max is not None and x > energy_max:
                    continue
                y = hist.GetBinContent(i)
                w = hist.GetBinWidth(i)
        
                if self.Config['generator'].upper() == "GENIE":
                    if target == "H1":
                        target_divisor = 1
                    else:
                        target_divisor = int(target[-2])
                    cc_xsec = max(0.0, float(g_cc.Eval(x)))
                    nc_xsec = max(0.0, float(g_nc.Eval(x)))
        
                    if interaction == "CC":
                        xsec = cc_xsec / target_divisor
                    elif interaction == "NC":
                        xsec = nc_xsec / target_divisor
                    else:
                        raise ValueError(f"Unsupported xsec_mode '{interaction}'")
        
                elif self.Config['generator'].upper() == "NEUT":
                    xsec = max(0.0, float(neut_spline.Eval(x)))
        
                if self.Config['reweight']['undoNormB']:
                    Spline_normalization += y * w * Fscale * xsec
                else:
                    Spline_normalization += y * Fscale * xsec
            self.SplineNormalizations[label] = Spline_normalization
        

        FlavorToNumber = {"NuMu":14,"NuMuBar":-14,"NuE":12,"NuEBar":-12 }
        RFunctionDeclare = ""

        for flavor in self.Config['filters']['flavor']:
            spline = self.FluxSplines[flavor]
            spline_name = f"g_fluxSpline_{flavor}"
            # Give the dataframe the correct Spline and Normalization
            ROOT.gInterpreter.Declare(f"TSpline3* {spline_name};")
                # Assign from Python side using setattr
            setattr(ROOT, spline_name, spline)
            ROOT.gInterpreter.Declare(f"""
                extern TSpline3* {spline_name};
            """)
            RFunctionDeclare = RFunctionDeclare + f"""
            if (flavor=={FlavorToNumber[flavor]}){{
                return {spline_name}->Eval(E);
            }}"""
        
        ROOT.gInterpreter.Declare(f"""
            double GetFluxSplineValue (double E, int flavor) {{
                {RFunctionDeclare}
            else {{
                return 0.0;
            }}
        }}
        """)
        self.df = self.df.Define("Flux_weights", f"GetFluxSplineValue(Enu_true,PDGnu)")

        # Make get the denominator for the normalization for each spline
        self.SplineNormalizationsDenom = {}
        print("Making Spline Normalization Denominator, this part takes while")
        for file in self.FileDictionary:
            cut = f'source=="{file}/FlatTree_VARS"'
            fileDF = self.df
            fileDF = fileDF.DefinePerSample("source", "rdfsampleinfo_.AsString()")
            self.SplineNormalizationsDenom[f"{file}_m"] = fileDF.Filter(cut).Sum('Flux_weights')  #this line takes a long time
            # some extremely strange bullshit happens if you uncomment this:
            # if fileDF.Count().GetValue() ==0:
            #     raise ValueError("Cut Resulted in empty df")
            # else:
            #     print(fileDF.Count().GetValue())

        current = self.df.Sum('Flux_weights').GetValue()

        print(f"got current {current}")

        for file in self.FileDictionary:
            self.SplineNormalizationsDenom[file] = self.SplineNormalizationsDenom[f"{file}_m"].GetValue()
            if self.SplineNormalizationsDenom[file] == 0:
                raise ValueError("file cut resulted in 0 events")

        for file in self.FileDictionary:
            file_flavor = self.FileDictionary[file]['flavor']
            file_interaction = self.FileDictionary[file]['interaction']
            file_target = self.FileDictionary[file]['target']
            file_energy_range =self.FileDictionary[file]['e_range']
            fileLabel = f"{file_interaction}_{file_flavor}_{file_target}_{file_energy_range}"
            self.FileDictionary[file]["Normalization"] = self.SplineNormalizations[fileLabel]/self.SplineNormalizationsDenom[file]
        PerFileWeight = ""
        for file in self.FileDictionary:
            PerFileWeight = PerFileWeight + f"""
            if (file=="{file}/FlatTree_VARS"){{
                return {self.FileDictionary[file]["Normalization"]};
        }}"""



        self.df = self.df.DefinePerSample("source", "rdfsampleinfo_.AsString()") #This will tell you which file is associated to each even. Warning that this is very buggy!!      

        
        ROOT.gInterpreter.Declare(f"""
            #include <string>
            double FileNorm (const std::string& file) {{
                {PerFileWeight}
            else {{
                return 0.0;
            }}
        }}
        """)
        self.df = self.df.Define("File_Norms", "FileNorm(source)")
        self.df = self.df.Define("UHMC_Weights","Flux_weights*File_Norms")

        print("UHMC WEIGHTS")
        print("Weighting Done!!")
    
class T2KReWeight:
    def __init__(self, dial, value, group_name=None, values_name=None):
        if type(dial) != str and type(dial) != list:
            raise TypeError(f"Dial must be a string or list: {dial} type: {type(dial)}")
        if type(dial) == list and group_name == None:
            raise TypeError("Need Group name for a list of dials")
        elif type(dial) == list:
            self.DialName = group_name
            self.Dial = dial
        elif type(dial) == str:
            self.DialName = dial
            self.Dial = [dial]
        else:
            raise ImportError("Weird Error")

        if type(value) != list and type(value) != float and type(value) != tuple:
            raise TypeError(f"Value must be a list or a float or a tuple: {value}")

        if type(value) == tuple:
            step, interv = value
            if len(interv) != 2:
                raise ValueError(f"Interval must have a length of 2 (start, stop)")
            if interv[0] < 0:
                self.ValueName = f"m{int(interv[0]*-1)}_{int(interv[1])}for{abs(int((interv[1]-interv[0])/step))}points"
            else:
                self.ValueName = f"{int(interv[0])}_{int(interv[1])}for{abs(int((interv[1]-interv[0])/step))}points"

            points_list = []
            for i in np.arange(interv[0], interv[1]+step, step):
                points_list.append(float(i))
            self.Values = points_list
        elif type(value) == list and values_name==None:
            raise ValueError("List of values must have a value name")
        elif type(value) == list:
            self.ValueName = values_name
            self.Values = value 

        elif type(value) == float:
            self.ValueName = "at"+str(int(value))
            self.Values = [value]
        else:
            raise ImportError("Value must be Tuple, list, or float")

    
    def MakeScript(self, path_to_template, temp_dir, original_file_path, original_card_path, output_dir):
        if output_dir[-1] != "/":
            output_dir = output_dir + "/"
        # copy the template into temp dir with descriptive name
        template_name = path_to_template.split("/")[-1]
        file_name = original_file_path.split("/")[-1]
        file_name = file_name.replace(".","_")
        file_name = file_name.replace("-","_")
        if template_name[-1] != "C":
            raise ValueError(f"Template should end with C: {template_name}")
        new_name = "T2KRW" + "_" + file_name.replace(".root","") + f"_{self.DialName}_{self.ValueName}" + ".C"
        if temp_dir[-1] != "/":
            temp_dir = temp_dir + "/"
        shutil.copy(path_to_template, f"{temp_dir}{new_name}")
        self.ScriptDir = temp_dir
        self.ScriptPath = f"{temp_dir}{new_name}"
        self.ScriptName = new_name.replace(".C","")

        # now it takes the code in the template and turns it into a string
        with open(path_to_template, 'r') as file:
            template_content = file.read()

        # change the input file macro name:
        templ_macro = "void t2krwSave()"
        new_macro = f"void {self.ScriptName}()"
        template_content = template_content.replace(templ_macro, new_macro)
        
        # change the template input file
        templ_input_file = 'const char* infile = "/path/to/the/generated/file.root"'
        templ_new_file = f'const char* infile ="{original_file_path}" '
        template_content = template_content.replace(templ_input_file,templ_new_file)

        # change the template card file
        templ_input_card = 'std::string card_file = "/path/to/the/card/file.card"'
        templ_new_card = f'std::string card_file = "{original_card_path}" '
        template_content = template_content.replace(templ_input_card,templ_new_card)

        # change the template output file
        templ_input_output = 'const char* outfile = "/path/to/the/output/file.root"'
        templ_new_output = f'const char* outfile ="{output_dir}Weights_{self.ScriptName}.root" '
        template_content = template_content.replace(templ_input_output,templ_new_output)

        # change the template dials
        i = 0
        dial_string = "{\n"
        for dial in self.Dial:
            if i+1 == len(self.Dial):
                dial_string = dial_string + f'    "{dial}"\n'
            else:
                dial_string = dial_string + f'    "{dial}",\n'
            i+= 1
        dial_string = dial_string + "    }"

        templ_input_dials = """std::vector<std::string> syst_names = {"Dial1","Dial2"}"""
        templ_new_dials = f'std::vector<std::string> syst_names = {dial_string}'
        template_content = template_content.replace(templ_input_dials,templ_new_dials)

        # change the template values
        value_string = "{"
        for i in range(0, len(self.Values)):
            if i == len(self.Values)-1:
                value_string = value_string + str(self.Values[i])
            else:
                value_string = value_string + f"{self.Values[i]}, "
        
        value_string = value_string + "}"
        templ_input_values = 'std::vector<float> DialValues = {-1.0, 0.0, 1.0}'
        templ_new_values = f'std::vector<float> DialValues ={value_string} '
        template_content = template_content.replace(templ_input_values,templ_new_values)

        # print("FULL TEMPLATE:")
        # print(template_content)
        with open(self.ScriptPath, "w", encoding="utf-8") as file:
            file.write(template_content)

    def RunRW(self, source_path=None, timing=None):
        run_str = ""
        if source_path != None:
            run_str = f"source {source_path} &&"
        if timing != None:
            import time
            start = time.perf_counter()
    
        if self.ScriptName == None:
            raise ValueError("Script Name doesn't exist, run MakeScript first")
        run_str = run_str + f"root -l -b -q {self.ScriptPath}" 
        subprocess.run(run_str, cwd=self.ScriptDir, shell=True)

        if timing != None:
            elapsed = time.perf_counter() - start
            with open("timing.log", "a") as f:
                f.write(f"{self.ScriptName}.C took {elapsed:.3f} seconds\n")

    def CleanUp(self):
        if self.ScriptName == None:
            raise ValueError("Script Name doesn't exist, run MakeScript first")
        if not os.path.exists(self.ScriptPath):
            print("Already cleaned up (─ ‿ ─)")
            exit()
        else:
            os.remove(self.ScriptPath)
            print(f"Deleted {self.ScriptPath}")


class NuSystematics:
    def __init__(self):
        print("Under Construction")
        pass

class SpliningSyst:
    #######################################
    ## Grabs the file with reweights in it
    ## Makes a list of all branches
    ## Saves points based on StartingPoints
    ### X points if StartingPoints is an int
    ### [X,Y,Z...] exact points if StartingPoints is a list
    ## These Points make a branch of Splines that can get saved, or stay within the Splining Obj
    ###############################################
    def __init__(self,RWPath,TreeName,SplinePoints=None,Bounds=None):
        MakeSplines = True #will make splines unless you give it a file with splines already made
        
        # decide on spline points
        if Bounds == None:
            Bounds = (-3,3)
        lower_b, upper_b = Bounds
        if lower_b>upper_b:
            temp = lower_b
            lower_b = upper_b
            upper_b = temp
            print("Wrong Bound Order, fixing")

        KnotPoints = [] #this will actually store the points

        if type(SplinePoints) == int:
            mult_value = 10 #shouldn't go lower than the 10s place for splines (?)
            Range = upper_b - lower_b

            if SplinePoints > Range*mult_value:
                raise ValueError("too many points requested")

            step = int(Range*mult_value/SplinePoints)

            for i in range(lower_b*mult_value,upper_b*mult_value,step):
                KnotPoints.append(i/mult_value)
    
        elif type(SplinePoints) == list:
            KnotPoints = SplinePoints

        
        elif SplinePoints==None:
            KnotPoints = [-3,-2,-1,0,1,2,3]

        KnotPointsF = [float(x) for x in KnotPoints]

        df = ROOT.RDataFrame(TreeName,RWPath)
        branches = df.GetColumnNames()
        branch_list = [str(c) for c in branches]


        for branch in branch_list:
            branch_type = df.GetColumnType(branch) #If there's one spline, assuming all splines are there
            if "TSpline" in branch_type:
                MakeSplines = False
                continue
       
        if MakeSplines: #Makes a branch of splines for each dial and saves it separately this df replace the weight df after
            dial_list = []
            value_list = []
            
            for branch in branch_list:
                # Assuming a branch name of "Dial_Name_DialValue" or "DialName_Dialvalue"
                value = branch.split("_")[-1]
                dial = branch.split(value)[0]
                value_list.append(float(value))
                dial_list.append(dial)

            for i in range(0,len(branch_list)):
                if "-" in branch_list[i] or "." in branch_list[i]:
                    branchSafe = branch_list[i].replace("-","m")
                    branchSafe = branchSafe.replace(".","p")
                    df = df.Alias(branchSafe,branch_list[i])
                    branch_list[i] = branchSafe

            used_branches = []
            used_dial = []
            used_value = []
            for i in range(0,len(value_list)):
                if float(value_list[i]) in KnotPointsF:
                    used_branches.append(branch_list[i])
                    used_dial.append(dial_list[i])
                    used_value.append(value_list[i])

            
            if len(used_branches)%len(KnotPointsF) != 0:
                print("ERROR WARNING")
                for knot in KnotPointsF:
                    if not (knot in value_list):
                        raise RuntimeError(f"X point not found in weight file: {knot} not in {value_list}")

            self.SplineDict = {}
            #This dictionany will take the form {"systematic1":([x1,x2,x3],[branchName1,branchName2]),"systematic2":([x1,...],[branch1,...]),...}
            for i in range (0,len(used_value)):
                if not (used_dial[i] in self.SplineDict):
                    self.SplineDict[used_dial[i]] = ([],[])
                self.SplineDict[used_dial[i]][0].append(used_value[i])
                self.SplineDict[used_dial[i]][1].append(used_branches[i])

            ROOT.gInterpreter.Declare("""
                TSpline3 MakeSpline(const ROOT::RVec<double> &x, const ROOT::RVec<double> &y)
                {
                    return TSpline3("spline", const_cast<double*>(x.data()),const_cast<double*>(y.data()), (Int_t)x.size());
                }
            """)

            for systematic, XValuesAndBranches in self.SplineDict.items():
                xs, ys = XValuesAndBranches
                xsorted,ysorted = zip(*sorted(zip(xs, ys)))
                xsortedL, ysortedL = list(xsorted), list(ysorted)
                xsortedL_inC = "ROOT::RVec<double>{" + ", ".join(repr(float(x)) for x in xsortedL) + "}"
                ysorted_inC = "ROOT::RVec<double>{" + ", ".join(f"{b}" for b in ysortedL) + "}"


                print(f"MakeSpline({systematic}_x, {systematic}_y)")
                df = df.Define(f"{systematic}_x", xsortedL_inC)
                df = df.Define(f"{systematic}_y", ysorted_inC)
                df = df.Define(f"{systematic}_spline", f"MakeSpline({systematic}_x, {systematic}_y)")

                branch_list.append(f"{systematic}_spline")
                branch_list.append(f"{systematic}_x")


            print("Splines Made, Taking a snapshot")
            df.Snapshot("WeightsAndSplines","W&Stest.root",branch_list)
    
        else:
            raise NotImplementedError("Working on already made splines")

    ##################
    ## Takes all splines made and compares them to the full reweights with all points
    ## For each event, grabs all points between spline nodes in the full density rw
    ## Finds difference between spline and RW value and saves it as a new column
    ## Each dial will have a branch that showes the total difference and the fractional difference(?)

    def GroupSplines(self):
        raise NotImplementedError("Working on Spline Tests against full systematics")


if __name__ == "__main__":
    # testrw1 = T2KReWeight(dial="MaCCQE", value=1.0)
    # testrw2 = T2KReWeight(dial=["MaCCQE","MaRES","CA5RES"], value=[-1.0,1.0,0.2],group_name="1st_Group_Test",values_name="randomPoints")

    # file_path = os.path.abspath(__file__)
    # dir_path = os.path.dirname(file_path)

    # templatePath = f"{dir_path}/t2krwSave.C"
    # OutPath = os.environ.get("PUFIN_OUT")
    # if OutPath == None:
    #     raise ValueError("PUFIN_OUT not defined!!")

    # user = os.environ.get("USER")
    # workingDir = f"{OutPath}/{user}_temp_dir"

    # FilePath = "/path/to/your/NeutFileTest.root"
    # CardPath = "/path/to/your/NeutCardTest.card"

    # output_pufin_dir = f"{OutPath}/NEUT/T2KRW"
    # os.makedirs(output_pufin_dir, exist_ok=True)

    # testrw1.MakeScript(path_to_template=templatePath, temp_dir=workingDir, original_file_path=FilePath, original_card_path=CardPath, output_dir=output_pufin_dir)
    # testrw2.MakeScript(path_to_template=templatePath, temp_dir=workingDir, original_file_path=FilePath, original_card_path=CardPath, output_dir=output_pufin_dir)

    # testrw1.RunRW(source_path="/path/to/your/T2KRWsetup.sh")
    # testrw2.RunRW(source_path="/path/to/your/T2KRWsetup.sh")
    import json5
    f = open("/home/lboe/pufin/config/NewNeutT2KWeightALL.json5")
    print("reading json5")
    testConfig = json5.load(f)
    print("read json5")
    testUHMC = UHMC(testConfig)
    testUHMC.MakeDF()
    testUHMC.MakeExpWeights()
    name = "/home/lboe/WeightMainRefactor/NuMuCCSnapShotThree.root"
    testUHMC.df.Snapshot("FlatTree_VARS",name)
    print(f"Snapshot Taken!!! name {name}")



