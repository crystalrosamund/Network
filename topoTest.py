#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections, quietRun
from mininet.log import setLogLevel
from mininet.cli import CLI
import subprocess

class MyTopo(Topo):
    
    def __init__(self, q=176, d='21ms', **opts):
        Topo.__init__(self, **opts)

        hosts = []
        switches = []
        for i in irange(1,4):
            hosts.append(self.addHost('h%s'%i, cpu=.5/4))
            switches.append(self.addSwitch('s%s'%i))
        self.addLink(hosts[0], switches[0], bw=252, max_queue_size=q, use_htb=True)
        self.addLink(hosts[1], switches[0], bw=252, max_queue_size=q, use_htb=True)
        self.addLink(hosts[2], switches[1], bw=252, max_queue_size=q, use_htb=True)
        self.addLink(hosts[3], switches[1], bw=252, max_queue_size=q, use_htb=True)
        
        self.addLink(switches[0], switches[2], bw=984)
        self.addLink(switches[1], switches[3], bw=984)
        self.addLink(switches[2], switches[3], delay=d)

def perfTest(control, q, d):
    "Create network"
    topo = MyTopo(q=q,d=d)
    setControl = "sysctl -w net.ipv4.tcp_congestion_control="+control
    quietRun(setControl)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    net.pingAll()
    h1,h2,h3,h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    outputs= ["result/h1_"+d+"_"+control,"result/h2_"+d+"_"+control]
    cmd_r = "iperf3 -s -p 5566 &"
    h3.cmd(cmd_r)
    h4.cmd(cmd_r)
    host3 = h3.IP()
    host4 = h4.IP()
    h1.cmd('nohup iperf3 -c %s -p 5566 -i 0.1 -t 350 -b 960m > %s &'% (host3, outputs[0]))
    h2.cmd('sleep 50;nohup iperf3 -c %s -p 5566 -i 0.1 -t 300 -b 960m > %s' % (host4, outputs[1]))
    #CLI(net)
    net.stop()


if  __name__ == '__main__':
    setLogLevel('info')
    #controls = ["reno", "cubic", "westwood", "vegas"]
    controls = ["reno","westwood"]
    #arguments = [[176,'21ms'],[680,'81ms'],[1360,'162ms']]
    arguments = [[176,'21ms']]
    for c in controls:
        for a in arguments:
            print subprocess.check_output(['sudo','mn','-c'])
            perfTest(c,a[0],a[1])
