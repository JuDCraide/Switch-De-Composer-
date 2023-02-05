import sys
import argparse
from graph_class import Graph
import json

parser = argparse.ArgumentParser(description='One Big Switch program generation')
parser.add_argument('--switchname', help='Name of the switch that will receive the program',
                    type=str, action="store", required=True)
parser.add_argument('--modules', help='Name of the modules that will be added to the switch program',
                    type=str, action="store", required=True)
parser.add_argument('--filename', help='Name of the OBS program that has the module',
                    type=str, action="store", required=True)
parser.add_argument('--topology', help='Path to json topology config file',
                    type=str, action="store", required=True)
parser.add_argument('--output-folder', help='Path to output up4 files',
                    type=str, action="store", required=True)

args = parser.parse_args()


topology = open(args.topology, "r")

with open(args.topology, 'r') as file:
    topology = json.load(file)

switch = [x for x in topology["switches"] if x["switchname"] == args.switchname][0]
hosts = [x for x in topology["hosts"] if x["switchname"] == args.switchname]
output_folder = args.output_folder

#ethernet table
eth_table = ""
for host in hosts:
    eth_table += "(%s) : forward(%s, %s, %s); \n" % (host["port"],host["mac"],switch["mac"],host["port"])
#print(eth_table)

#ipv4 table
ipv4_table = ""
for host in hosts:
    ipv4_table += "(%s, _): process(%s); \n" % (host["ipv4"],host["port"])
#print(ipv4_table)

#ipv6 table
ipv6_table = ""
for host in hosts:
    ipv6_table += "(%s, _, _): process(%s); \n" % (host["ipv6"],host["port"])
#print(ipv6_table)

# Ethernet
with open('../modules/obs_main_x.up4', 'r') as file :
  filedata = file.read()
filedata = filedata.replace('//@TableInstantiate("ethernet")', eth_table)
with open(output_folder + '/obs_main.up4', 'w') as file:
  file.write(filedata)

# IPv4
with open('../modules/ipv4_x.up4', 'r') as file :
  filedata = file.read()
filedata = filedata.replace('//@TableInstantiate("ipv4")', ipv4_table)
with open(output_folder + '/ipv4.up4', 'w') as file:
  file.write(filedata)

# IPv6
with open('../modules/ipv6_x.up4', 'r') as file :
  filedata = file.read()
filedata = filedata.replace('//@TableInstantiate("ipv6")', ipv6_table)
with open(output_folder + '/ipv6.up4', 'w') as file:
  file.write(filedata)

obs_program = open(args.filename, "r")

lines = []
if args.modules == 'all':
    with obs_program as t:
        lines = t.readlines()
else:
    edges = [('ethernet', 'ipv4'), ('ethernet', 'ipv6'), ('ipv4', 'ipv4_nat'), ('ipv6', ''), ('ipv4_nat', '')]
    graph = Graph(edges, directed=True)

    modules = args.modules.split(',')
    # print(modules)
    dependencies = set()
    for module in modules:
        # print(graph.get_dependencies_rec(module))
        dependencies.update(graph.get_dependencies_rec(module))
        dependencies.add(module)
        # print(dependencies)

    dependencies.add('all')
        
    with open(args.filename, "r") as file:
        can_write = True
        for line in file:
            if '@ModuleDeclareBegin' in line:
                if any('@ModuleDeclareBegin(\"'+word+'\")' in line for word in dependencies):
                    can_write = True
                else:
                    can_write = False
            if '@ModuleDeclareEnd' in line:
                can_write = True

            if '@ModuleInstantiateBegin' in line:
                if any('@ModuleInstantiateBegin(\"'+word+'\")' in line for word in dependencies):
                    can_write = True
                else:
                    can_write = False
            if '@ModuleInstantiateEnd' in line:
                can_write = True
                        
            if '@ModuleInvokeBegin' in line:
                if any('@ModuleInvokeBegin(\"'+word+'\")' in line for word in dependencies):
                    can_write = True
                else:
                    can_write = False
            if '@ModuleInvokeEnd' in line:
                can_write = True

            if(can_write):
                lines.append(line)
    
output = open(args.switchname + "_" + args.modules  + "_main.up4", "w")
for l in lines:
    if '//' not in l:
        output.write(l)
output.close()



