from replace_regex import replaceWithRegex
from ip_functions import ConvertIpToInt, ConvertIpToHex, ConvertMacToHex

class Specific_functions(object):
    def ethernet(filedata, hosts, switch):
        eth_table = ""
        for host in hosts:
            eth_table += "(%s) : forward(%s, %s, %s); \n" % (host["port"], ConvertMacToHex(host["mac"]), ConvertMacToHex(switch["mac"]), host["port"])
        return replaceWithRegex("ethernet", filedata, eth_table)


    def ipv4(filedata, hosts, switch):
        ipv4_table = ""
        for host in hosts:
            ipv4_table += "(%s, _): process(%s); \n" % (ConvertIpToInt(host["ipv4"]),host["port"])
        return replaceWithRegex("ipv4", filedata, ipv4_table)
        
        
    def ipv6(filedata, hosts, switch):
        ipv6_table = ""
        for host in hosts:
            ipv6_table += "(%s, _, _): process(%s); \n" % (ConvertIpToHex(host["ipv6"]),host["port"])
        return replaceWithRegex("ipv6", filedata, ipv6_table)
        