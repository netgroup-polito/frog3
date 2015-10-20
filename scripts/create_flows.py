from __future__ import division
import json, requests, sys, re, os


def bash(command):
    command = command +" 2>&1"
    pipe = os.popen(command)
    output = pipe.read()
    exit_code = pipe.close()
    if exit_code is not None:
        print "Error code: "+str(exit_code)+" - Due to command: "+str(command)+" - Message: "+output
        #raise BashError("Error code: "+str(exit_code))
    return output

def getPortID(bridge, port_name):
    port_id = "ovs-ofctl show "+bridge+" | grep "+port_name+" | awk '{print $1}'"
    print "Bash command \""+port_id+"\""
    port_id = bash(port_id)
    port_id= str(port_id).strip('\n')
    port_id = port_id.split("(")
    port_id = port_id[0]
    print "Port name: "+port_name
    print "Port id: "+port_id
    return port_id

def createFlowrule(bridge, in_port, out_port, priority):
    param = "in_port="+in_port+",priority="+priority+",actions=output:"+out_port
    command = "ovs-ofctl add-flow "+bridge+" \""+param+"\""
    print "Bash command \""+command+"\""
    bash(command)
    

if len(sys.argv) != 5:
    print "Usage: create_flows.py <bridge> <port_1> <port_2> <priority>"
    sys.exit()
    
bridge = sys.argv[1]
port1 = sys.argv[2]
port2 = sys.argv[3]
priority = sys.argv[4]

port1_id = getPortID(bridge, port1)
port2_id = getPortID(bridge, port2)


print "Creating flows"

createFlowrule(bridge, port1_id, port2_id, priority)
createFlowrule(bridge, port2_id, port1_id, priority)

print "Flows created"


