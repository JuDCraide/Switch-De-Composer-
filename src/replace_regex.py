import re
def replaceWithRegex(module_name, base_string, string_to_replace):
    regex = r'\/\/@TableInstantiateBegin\(\"'+module_name+'\"\)([.\s\S]*?)\/\/@TableInstantiateEnd\(\"'+module_name+'\"\)'
 
    result = re.sub(regex, string_to_replace, base_string, 0, re.MULTILINE)
 
    if result:
        return result
    return base_string

def findRegex(regex, base_string):
    result = re.search(regex, base_string, re.MULTILINE)
 
    if result:
        return True
    return False