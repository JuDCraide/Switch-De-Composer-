import json
import os

topologyJsonLocation = f'{os.getcwd()}/topology-json/topology_e1.json'
with open(topologyJsonLocation, 'r') as file:
    topology = json.load(file)

startMininet = True 
destination = "./example-julia/generated_distribute_programs.sh"
allModulesTopology1 = ["ipv4", "ipv6"]
allModulesTopology2 = ["ipv4_nat_acl","ipv4", "ipv6"]
allModules = allModulesTopology1
modules = set()

f = open(destination, "w+")

f.write(f"export SWITCHDECOMPOSER={os.getcwd()}\n")
f.write("export UP4ROOT=${SWITCHDECOMPOSER}/obs-microp4\n")

f.write('sudo mn -c\n')
f.write('\necho -e "\\n*********************************"\n')
f.write('echo -e "\\n Generating switch programs with a template "\n')

for switch in topology["switches"]:
    line = 'python ../generate_switch_program_w_template.py --switchname {0} --modules {1} --filename {2} --topology {3}\n'.format(
        switch["switchname"],
        switch["modules"],
        switch["filename"],
        topologyJsonLocation,
    )
    f.write(line)
    switch["modulesString"] = switch["modules"].replace(",","_")
    switchModules = switch["modules"].split(",")
    switch["modulesParsed"] = switchModules
    for module in switchModules:
        if (module == "all"):
            modules.update(allModules)
            switch["modulesParsed"] = allModules
            continue
        else:
            modules.add(module)

f.write('\necho -e "\\n*********************************"\n')
f.write('echo -e "\\n Compiling uP4 includes "\n')
for module in modules:
    fixedPart = "${UP4ROOT}/build/p4c-msa -I ${UP4ROOT}/build/p4include"
    line = '{0} -o {1}.json {2}.up4\n'.format(fixedPart, module, module)
    f.write(line)

f.write('\necho -e "\\n*********************************"\n')
f.write('echo -e "\\n Compiling uP4 main programs \\n"\n')
for switch in topology["switches"]:
    submodules = ""
    for i, module in enumerate(switch["modulesParsed"]):
        submodules += module + ".json"
        if i < len(switch["modulesParsed"])-1:
            submodules += ","
        else: submodules += " "
    p4cMsa = "${UP4ROOT}/build/p4c-msa"
    p4include = "${UP4ROOT}/build/p4include"
    line = '{0} --target-arch v1model -I {1}  -l {2}{3}_{4}_main.up4\n'.format(
        p4cMsa, p4include, submodules, switch["switchname"], switch["modules"])
    f.write(line)

f.write('\necho -e "\\n*********************************"\n')
f.write('echo -e "\\n Compiling P4 programs "\n')
for switch in topology["switches"]:
    line = '../p4c-compile.sh {0}_{1}_main_v1model.p4\n'.format(switch["switchname"], switch["modulesString"])
    f.write(line)

if(startMininet):
    f.write('\nbold=$(tput bold)\n')
    f.write('normal=$(tput sgr0)\n')

    f.write('\nBMV2_MININET_PATH=./\n')
    f.write('BMV2_SIMPLE_SWITCH_BIN=${UP4ROOT}/extensions/csa/msa-examples/bmv2/targets/simple_switch/simple_switch\n')

    f.write('\nP4_MININET_PATH=${UP4ROOT}/extensions/csa/msa-examples/bmv2/mininet\n')

    f.write('\necho -e "${bold}\\n*********************************"\n')
    f.write('echo -e "Running Tutorial program: obs_example_v1model${normal}"\n')
    f.write('sudo bash -c "')
    f.write('export P4_MININET_PATH=${P4_MININET_PATH}; ')
    f.write('${BMV2_MININET_PATH}obs_simple_topo_v1model_sw.py ')
    f.write('--behavioral-exe $BMV2_SIMPLE_SWITCH_BIN ')
    f.write(f'--topology-json {topologyJsonLocation}')
    f.write('"\n')

f.write('\necho -e "*********************************\\n${normal}"\n')
f.write('echo -e "\\n Remove Intermediate Files \\n"\n')
#f.write('rm *.json\n')
f.write('rm *.p4i\n')
f.write('rm *.p4rt\n')
#f.write('rm s*.up4\n')

f.write('\necho -e "\\n*********************************"\n')
f.close()
