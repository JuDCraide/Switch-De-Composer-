import json
from graph_class import Graph
from specific_functions import Specific_functions

modules = ["x", "a", "b", "d"]


with open('../dependencies-json/dependencies_ficticious.json', 'r') as file:
    dependencies = json.load(file)

edges = []
for module in dependencies:
    for dependency in module["directDependencies"]:
        edges.append((module["name"], dependency))
    if "head" in module.keys() and module["head"]:
        head = module["name"]

print(edges)
graph = Graph(edges, head, directed=True)

order_modules = graph.get_dependency_order(modules)
print(order_modules)

for module_name in order_modules:
    module = next(obj for obj in dependencies if obj["name"] == module_name)
    function = getattr(Specific_functions, module["function"])
    function()