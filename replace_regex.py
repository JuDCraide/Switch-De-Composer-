import re
def replaceWithRegex(module_name, base_string, string_to_replace):
    regex = r'\/\/@TableInstantiateBegin\(\"'+module_name+'\"\)([.\s\S]*?)\/\/@TableInstantiateEnd\(\"'+module_name+'\"\)'
 
    result = re.sub(regex, string_to_replace, base_string, 0, re.MULTILINE)
 
    if result:
        return result
    return base_string
 
def testReplaceWithRegex():
    module_name = "ipv4"
    test_str = ("//@TableInstantiateBegin(\"ipv4\")\n"
                "IPv6() ipv6_i;\n"
                "//@TableInstantiateEnd(\"ipv4\")")
    subst = "aaaaa"
    
    new_string = replaceWithRegex(module_name,test_str,subst)
    print(new_string)
