import json
from graph_class import Graph
from collections import deque

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


print(graph.get_dependency_order(modules))

