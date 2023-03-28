from replace_regex import findRegex

def get_modules_from_policies(filepath, dependencies):
    modules = set()
    with open(filepath, "r") as policies_file:
        policies = policies_file.read()

        for dependency in dependencies:
            for regex in dependency["regex"]:
                if(findRegex(regex, policies)):
                    modules.add(dependency["name"])

    return list(modules)

# TEST
# import json
# with open("/home/p4/new-switch-de-composer/dependencies-json/dependencies_e1.json", 'r') as file:
#     dependencies = json.load(file)

#     print(get_modules_from_policies("/home/p4/new-switch-de-composer/polices/s1_policy.txt", dependencies))

