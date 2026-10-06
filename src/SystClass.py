import os
import subprocess
import shutil
import numpy as np


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


if __name__ == "__main__":
    testrw1 = T2KReWeight(dial="MaCCQE", value=1.0)
    testrw2 = T2KReWeight(dial=["MaCCQE","MaRES","CA5RES"], value=[-1.0,1.0,0.2],group_name="1st_Group_Test",values_name="randomPoints")

    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)

    templatePath = f"{dir_path}/t2krwSave.C"
    OutPath = os.environ.get("PUFIN_OUT")
    if OutPath == None:
        raise ValueError("PUFIN_OUT not defined!!")

    user = os.environ.get("USER")
    workingDir = f"{OutPath}/{user}_temp_dir"

    FilePath = "/path/to/your/NeutFileTest.root"
    CardPath = "/path/to/your/NeutCardTest.card"

    output_pufin_dir = f"{OutPath}/NEUT/T2KRW"
    os.makedirs(output_pufin_dir, exist_ok=True)

    testrw1.MakeScript(path_to_template=templatePath, temp_dir=workingDir, original_file_path=FilePath, original_card_path=CardPath, output_dir=output_pufin_dir)
    testrw2.MakeScript(path_to_template=templatePath, temp_dir=workingDir, original_file_path=FilePath, original_card_path=CardPath, output_dir=output_pufin_dir)

    testrw1.RunRW(source_path="/path/to/your/T2KRWsetup.sh")
    testrw2.RunRW(source_path="/path/to/your/T2KRWsetup.sh")



