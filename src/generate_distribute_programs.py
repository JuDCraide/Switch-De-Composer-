import json
import os
import subprocess

basePath = os.getcwd()

topologyJsonLocation = f'{basePath}/topology-json/topology_e1.json'
with open(topologyJsonLocation, 'r') as file:
    topology = json.load(file)

dependenciesJsonLocation = f'{basePath}/dependencies-json/dependencies_e1.json'
with open(dependenciesJsonLocation, 'r') as file:
    dependencies = json.load(file)

all=[]
for module in dependencies:
    if "head" in module.keys() and module["head"]: continue
    all.append(module["name"])

runMininet = True
autoRun = True
outputFolder = f'{basePath}/outputs'
destination = f"{outputFolder}/generated_distribute_programs.sh"
modules = set()

f = open(destination, "w+")

f.write(f"export SWITCHDECOMPOSER={basePath}\n")
f.write("export UP4ROOT=${SWITCHDECOMPOSER}/obs-microp4\n")

f.write('sudo mn -c\n')

for switch in topology["switches"]:
    f.write('\necho -e "\\n*********************************"\n')
    f.write(f'echo -e "\\n Generating {switch["switchname"]} up4 program "\n')

    line = 'python3 {}/src/generate_switch_program.py --switchname {} --modules {} --filename {} --topology {} --dependencies {} --output-folder {}\n'.format(
        basePath,
        switch["switchname"],
        switch["modules"],
        switch["filename"],
        topologyJsonLocation,
        dependenciesJsonLocation,
        outputFolder,
    )
    f.write(line)

    f.write(f'\necho -e "\\n Compiling uP4 includes for {switch["switchname"]}"\n')
    modules = switch["modules"].split(',')
    if(switch["modules"] == "all"): 
        modules = all
    for module in modules:
        dep_module = next(obj for obj in dependencies if obj["name"] == module)       
        if "head" in dep_module.keys() and dep_module["head"]: continue
        fixedPart = "${UP4ROOT}/build/p4c-msa -I ${UP4ROOT}/build/p4include"
        line = '{0} -o {1}.json {2}\n'.format(fixedPart, dep_module["name"], dep_module["file"])
        f.write(line)

    f.write(f'\necho -e "\\n Compiling uP4 {switch["switchname"]} main program \\n"\n')
    submodules = ""
    modules = switch["modules"].split(',')
    if(switch["modules"] == "all"): 
        modules = all
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

f.write('\necho -e "\n*********************************\\n${normal}"\n')
f.write('echo -e "\\n Remove Intermediate Files \\n"\n')
f.write('rm *.p4i\n')
f.write('rm *.p4rt\n')
f.write('rm *.json\n')
f.write('rm *.up4\n')

f.write('\necho -e "\\n*********************************"\n')
f.close()

os.chmod(destination, 0o755)
if(autoRun):
    os.chdir(outputFolder)
    os.system("bash -c ./generated_distribute_programs.sh")
