#!/usr/bin/env python2

#
# Author: Hardik Soni
# Email: hks57@cornell.edu
#

import sys
import os
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import json

sys.path.insert(1, './bmv2/mininet/')
sys.path.insert(1, './../')

# Get the value of
P4_MININET_PATH = os.environ['P4_MININET_PATH']
if P4_MININET_PATH is None:
    print("P4_MININET_PATH is not set, p4_mininet may not be found")
# Print the value ofswitch
print("P4_MININET_PATH", P4_MININET_PATH)
sys.path.insert(1, P4_MININET_PATH)
from p4_mininet import P4Switch, P4Host


import argparse
from time import sleep

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--topology-json', help='Path to json topology config file',
                     type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()

class IPv6Node( Node ):
    def config( self, ipv6, ipv6_gw=None, **params ):
        super( IPv6Node, self).config( **params )
        self.cmd( 'ip -6 addr add %s dev %s' % ( ipv6, self.defaultIntf() ) )

    def terminate( self ):
        super( IPv6Node, self ).terminate()


class MultipleSwitchTopo(Topo):
    "Multiple switches connected to 3 hosts."
    def __init__(self, sw_path, topology, thrift_port, pcap_dump, n, **opts):
    # Initialize topology and default options
        Topo.__init__(self, **opts)

        switches = dict()
        for i, switch in enumerate(topology["switches"]):
            path = './' + switch["switchname"] + '_main_v1model.json'
            switches[switch["switchname"]] = self.addSwitch(switch["switchname"],
                                             sw_path = sw_path,
                                             json_path = path,
                                             thrift_port = thrift_port + i,
                                             pcap_dump = pcap_dump,
                                             log_console = True,
                                             enable_debugger = True)

        for i, host in enumerate(topology["hosts"]):
            temphost = self.addHost(host["hostname"],
                                    cls = IPv6Node,  
                                    ipv6= host["ipv6"], #+ "/64",
                                    ip = host["ipv4"], #+ "/24",
                                    mac = host["mac"])
            self.addLink(temphost, switches[host["switchname"]])

        for link in topology["switchlink"]:
            self.addLink( switches[link[0]], switches[link[1]]) 
           

def main():

    with open(args.topology_json, 'r') as file:
        topology = json.load(file)

    num_hosts = len(topology["hosts"])
    topo = MultipleSwitchTopo(args.behavioral_exe,
                            topology,
                            args.thrift_port,
                            args.pcap_dump,
                            num_hosts)
    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)


    net.start()
    sw_mac = ["00:aa:bb:00:00:%02x" % (n+1) for n in xrange(num_hosts)]
    sw_addr = ["10.0.%d.1" % (n+1) for n in xrange(num_hosts)]
    gw_addr = ["10.0.%d.254" % (n+1) for n in xrange(num_hosts)]
    sw_addr6 = ["202%01x::1" % (n+1) for n in xrange(num_hosts)]
    gw_addr6 = ["202%01x::10" % (n+1) for n in xrange(num_hosts)]

    for n in xrange(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.cmd('arp -s ' +gw_addr[n] +' '+ sw_mac[n])
        h.cmd(' route add default gw ' +gw_addr[n] +' '+ str(h.defaultIntf()))
        h.cmd('ethtool -K '+str(h.defaultIntf())+' rx off ')
        h.cmd('ethtool -K '+str(h.defaultIntf())+' tx off ')
        h.cmd('ip -6 neigh add '+ gw_addr6[n] +' lladdr '+ sw_mac[n]+ ' dev '+ str(h.defaultIntf()))
        h.cmd('ip -6 route add default via '+ gw_addr6[n])
        for k in xrange(num_hosts):
            if n == k:
                continue

    sleep(3)

    print "Ready !"

    print "Ipv6 ping command"
    print "h1 ping -6 2001::2"
    CLI( net ) 


    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()