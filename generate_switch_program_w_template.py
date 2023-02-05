import sys
import argparse
from graph_class import Graph

parser = argparse.ArgumentParser(description='One Big Switch program generation')
parser.add_argument('--switchname', help='Name of the switch that will receive the program',
                    type=str, action="store", required=True)
parser.add_argument('--modules', help='Name of the modules that will be added to the switch program',
                    type=str, action="store", required=True)
parser.add_argument('--filename', help='Name of the OBS program that has the module',
                    type=str, action="store", required=True)
parser.add_argument('--template', help='Name of the template that will be used as base of the program',
                    type=str, action="store", required=True)

args = parser.parse_args()

obs_program = open(args.filename, "r")
template = open(args.template, "r")

if args.modules == 'all':
    with obs_program as t:
        all_code = t.read()
    output = open(args.switchname + "_" + args.modules  + "_main.up4", "w")
    output.write(all_code)
    output.close()
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

    print(dependencies)
        
    lines = []

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
        if '@Module' in l:
            continue
        else:
            output.write(l)
    output.close()