import sys
import os
import argparse
import json
from specific_functions import Specific_functions

parser = argparse.ArgumentParser(description='One Big Switch program generation')
parser.add_argument('--switchname', help='Name of the switch that will receive the program',
                    type=str, action="store", required=True)
parser.add_argument('--modules', help='Name of the modules that will be added to the switch program',
                    type=str, action="store", required=True)
parser.add_argument('--head', help='Name of the base OBS module in the dependencies graph',
                    type=str, action="store", required=True)
parser.add_argument('--topology', help='Path to json topology config file',
                    type=str, action="store", required=True)
parser.add_argument('--dependencies', help='Path to json dependencies config file',
                    type=str, action="store", required=True)
parser.add_argument('--output-folder', help='Path to output up4 files',
                    type=str, action="store", required=True)

args = parser.parse_args()

with open(args.topology, 'r') as file:
    topology = json.load(file)

with open(args.dependencies, 'r') as file:
    dependencies = json.load(file)

output_folder = args.output_folder
modules = args.modules.split(',')
switchname = args.switchname

switch = [x for x in topology["switches"] if x["switchname"] == switchname][0]
hosts = [x for x in topology["hosts"] if x["switchname"] == switchname]

os.system(f"cp $SWITCHDECOMPOSER/modules/* {output_folder}")

for module_name in modules:
    module = next(obj for obj in dependencies if obj["name"] == module_name)

    filename = module["name"]
    filepath = output_folder + "/" + module["file"]
    with open(filepath, "r") as file:
        filedata = file.read()
        function = getattr(Specific_functions, module["function"])
        filedata = function(filedata, hosts, switch) 
    with open(filepath, 'w') as file:
        file.write(filedata)

    with open(filepath, "r") as file:
        lines = []
        can_write = True
        for line in file:
            if '@ModuleDeclareBegin' in line:
                if any('@ModuleDeclareBegin(\"'+word+'\")' in line for word in modules):
                    can_write = True
                else:
                    can_write = False
            if '@ModuleDeclareEnd' in line:
                can_write = True

            if '@ModuleInstantiateBegin' in line:
                if any('@ModuleInstantiateBegin(\"'+word+'\")' in line for word in modules):
                    can_write = True
                else:
                    can_write = False
            if '@ModuleInstantiateEnd' in line:
                can_write = True
                        
            if '@ModuleInvokeBegin' in line:
                if any('@ModuleInvokeBegin(\"'+word+'\")' in line for word in modules):
                    can_write = True
                else:
                    can_write = False
            if '@ModuleInvokeEnd' in line:
                can_write = True

            if(can_write):
                lines.append(line)
    
    if filename == args.head:
        filepath = output_folder + "/" + switchname + "_main.up4"

    with open(filepath, "w") as output:
        for l in lines:
            if '//@' not in l:
                output.write(l)
