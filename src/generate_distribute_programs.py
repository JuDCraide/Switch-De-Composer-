import json
import os
import argparse
from graph_class import Graph
from policies import get_modules_from_policies


parser = argparse.ArgumentParser(description='Switch (De)Composer program generation')
parser.add_argument('--topology-path', help='Path to the topology JSON file',
                    type=str, action="store", required=False)
parser.add_argument('--dependencies-folder-path', help='Path to the folder with the dependencies graph JSON',
                    type=str, action="store", required=False)
parser.add_argument('--policies-folder-path', help='Path to the folder with the policies file',
                    type=str, action="store", required=False)
parser.add_argument('--output-folder', help='Path to the folder where the switches will be generated',
                    type=str, action="store", required=False)

parser.add_argument('--not-run-mininet', help='Boolean if don\'t want to run Mininet test',
                    action="store_true", required=False, default=False)
parser.add_argument('--separate-mininet', help='Boolean if should put Mininet test on separate shell script',
                    action="store_true", required=False, default=False)
parser.add_argument('--not-auto-run', help='Boolean if don\'t want to automatically run generate switches',
                    action="store_true", required=False, default=False)

args = parser.parse_args()

basePath = os.getcwd()

if(args.topology_path):
    topologyJsonLocation = args.topology_path
else:
    topologyJsonLocation = f'{basePath}/topology-json/topology_e1.json'
with open(topologyJsonLocation, 'r') as file:
    topology = json.load(file)

runMininet = not args.not_run_mininet
separateMininet = args.separate_mininet
autoRun = not args.not_auto_run

if(args.dependencies_folder_path):
    dependenciesPath = f"{args.dependencies_folder_path.rstrip('/')}/"
else:
    dependenciesPath = f'{basePath}/dependencies-json/'

if(args.policies_folder_path):
    policiesPath = f"{args.policies_folder_path.rstrip('/')}/"
else:
    policiesPath = f'{basePath}/policies/'

if(args.output_folder):
    outputFolder = args.output_folder.rstrip('/')
else:
    outputFolder = f'{basePath}/outputs'

destination = f"{outputFolder}/generated_distribute_programs.sh"
f = open(destination, "w+")

f.write(f"export SWITCHDECOMPOSER={basePath}\n")
f.write("export UP4ROOT=${SWITCHDECOMPOSER}/obs-microp4\n")

f.write('sudo mn -c\n')

for switch in topology["switches"]:
    if "dependencies" in switch.keys() and switch["dependencies"]:
        dependenciesJsonLocation = dependenciesPath + switch["dependencies"]
    else:
        dependenciesJsonLocation = dependenciesPath + "dependencies_e1.json"
    with open(dependenciesJsonLocation, 'r') as file:
        dependencies = json.load(file)

    modules = []
    if("modules" in switch.keys() and switch["modules"]):
        if(switch["modules"] == "all"):         
            all=[]
            for module in dependencies:
                if ("head" in module.keys() and module["head"]): continue
                all.append(module["name"])
            modules = all
        else:
            modules = switch["modules"].split(',')
    elif("policies" in switch.keys() and switch["policies"]):
        policiesLocation = policiesPath + switch["policies"]
        modules = get_modules_from_policies(policiesLocation, dependencies)    
    
    edges = []
    for module in dependencies:
        for dependency in module["directDependencies"]:
            edges.append((module["name"], dependency))
        if "head" in module.keys() and module["head"]:
            head = module["name"]

    graph = Graph(edges, directed=True)
    modules = graph.get_dependencies_from_array(modules)
    modules = graph.get_dependency_order(modules)

    f.write('\necho -e "\\n*********************************"\n')
    f.write(f'echo -e "\\n Generating {switch["switchname"]} up4 program "\n')

    line = 'python3 {}/src/generate_switch_program.py --switchname {} --modules {} --head {} --topology {} --dependencies {} --output-folder {}\n'.format(
        basePath,
        switch["switchname"],
        ','.join(modules),
        head,
        topologyJsonLocation,
        dependenciesJsonLocation,
        outputFolder,
    )
    f.write(line)

    f.write(f'\necho -e "\\n Compiling uP4 includes for {switch["switchname"]}"\n')
    for module in modules:
        dep_module = next(obj for obj in dependencies if obj["name"] == module)       
        if "head" in dep_module.keys() and dep_module["head"]: continue
        fixedPart = "${UP4ROOT}/build/p4c-msa -I ${UP4ROOT}/build/p4include"
        line = '{0} -o {1}.json {2}\n'.format(fixedPart, dep_module["name"], dep_module["file"])
        f.write(line)

    f.write(f'\necho -e "\\n Compiling uP4 {switch["switchname"]} main program \\n"\n')
    submodules = ""
    for module in modules:        
        dep_module = next(obj for obj in dependencies if obj["name"] == module)
        if "head" in dep_module.keys() and dep_module["head"]: continue
        submodules += dep_module["name"] + ".json,"
    
    submodules = submodules.rstrip(',')
    p4cMsa = "${UP4ROOT}/build/p4c-msa"
    p4include = "${UP4ROOT}/build/p4include"
    line = '{0} --target-arch v1model -I {1} -l {2} {3}_main.up4\n'.format(
        p4cMsa, p4include, submodules, switch["switchname"])
    f.write(line)


f.write('\necho -e "\\n*********************************"\n')
f.write('echo -e "\\n Compiling P4 programs "\n')
for switch in topology["switches"]:
    line = '{}/src/p4c-compile.sh {}_main_v1model.p4\n'.format(
        basePath,
        switch["switchname"]
    )
    f.write(line)

if(runMininet):
    f.write('\nbold=$(tput bold)\n')
    f.write('normal=$(tput sgr0)\n')

    f.write('\nBMV2_MININET_PATH=./\n')
    f.write('BMV2_SIMPLE_SWITCH_BIN=${UP4ROOT}/extensions/csa/msa-examples/bmv2/targets/simple_switch/simple_switch\n')

    f.write('\nP4_MININET_PATH=${UP4ROOT}/extensions/csa/msa-examples/bmv2/mininet\n')

    f.write('\necho -e "${bold}\\n*********************************"\n')
    f.write('echo -e "Running Tutorial program: obs_example_v1model${normal}"\n')
    f.write('sudo bash -c "')
    f.write('export P4_MININET_PATH=${P4_MININET_PATH}; ')
    f.write(f'{basePath}/src/topology_mininet.py ')
    f.write('--behavioral-exe $BMV2_SIMPLE_SWITCH_BIN ')
    f.write(f'--topology-json {topologyJsonLocation}')
    f.write('"\n')

f.write('\necho -e "\\n*********************************\\n${normal}"\n')
f.write('echo -e "\\n Remove Intermediate Files \\n"\n')
f.write('rm *.p4i\n')
f.write('rm *.p4rt\n')
f.write('rm *.json\n')
f.write('rm *.up4\n')

f.write('echo -e "\\n*********************************"\n')
f.close()

os.chmod(destination, 0o755)
if(autoRun):
    os.chdir(outputFolder)
    os.system("bash -c ./generated_distribute_programs.sh")



if separateMininet:
    mininetDestination = f"{outputFolder}/mininet.sh"
    mf = open(mininetDestination, "w+")

    mf.write(f"export SWITCHDECOMPOSER={basePath}\n")
    mf.write("export UP4ROOT=${SWITCHDECOMPOSER}/obs-microp4\n")

    mf.write('sudo mn -c\n')

    mf.write('\necho -e "\\n*********************************"\n')
    mf.write('echo -e "\\n Compiling P4 programs "\n')
    for switch in topology["switches"]:
        line = '{}/src/p4c-compile.sh {}_main_v1model.p4\n'.format(
            basePath,
            switch["switchname"]
        )
        mf.write(line)

    mf.write('\nbold=$(tput bold)\n')
    mf.write('normal=$(tput sgr0)\n')

    mf.write('\nBMV2_MININET_PATH=./\n')
    mf.write('BMV2_SIMPLE_SWITCH_BIN=${UP4ROOT}/extensions/csa/msa-examples/bmv2/targets/simple_switch/simple_switch\n')

    mf.write('\nP4_MININET_PATH=${UP4ROOT}/extensions/csa/msa-examples/bmv2/mininet\n')

    mf.write('\necho -e "${bold}\\n*********************************"\n')
    mf.write('echo -e "Running Tutorial program: obs_example_v1model${normal}"\n')
    mf.write('sudo bash -c "')
    mf.write('export P4_MININET_PATH=${P4_MININET_PATH}; ')
    mf.write(f'{basePath}/src/topology_mininet.py ')
    mf.write('--behavioral-exe $BMV2_SIMPLE_SWITCH_BIN ')
    mf.write(f'--topology-json {topologyJsonLocation}')
    mf.write('"\n')

    mf.write('\necho -e "\\n*********************************\\n${normal}"\n')
    mf.write('echo -e "\\n Remove Intermediate Files \\n"\n')
    mf.write('rm *.p4i\n')
    mf.write('rm *.p4rt\n')
    mf.write('rm *.json\n')
    mf.write('rm *.up4\n')

    mf.write('echo -e "\\n*********************************"\n')
    mf.close()

    os.chmod(mininetDestination, 0o755)

