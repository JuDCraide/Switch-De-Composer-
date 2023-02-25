import ipaddress

def ConvertIpToInt(ip):
    return int(ipaddress.ip_interface(ip))

def ConvertIpToHex(ip):
    return hex(int(ipaddress.ip_interface(ip)))