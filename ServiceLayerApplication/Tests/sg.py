'''
Created on Apr 27, 2015

@author: fabiomignini
'''
from Common.ServiceGraph.service_graph import ServiceGraph
from Common.NF_FG.validator import ValidateNF_FG
import json
graph = {
    "user_id": "c172e054cf734d6ca35b7750013bd645",
    "vnf_list": {
        "vnf_1": {
            "id": "vnf_1",
            "vnfDesc": {
                "CPUrequirements": {
                    "platformType": "x86",
                    "socket": [
                        {
                            "coreNumbers": 1
                        }
                    ]
                },
                "name": "dhcp",
                "memory-size": 4096,
                "vnf-type": "virtual-machine",
                "uri": "http://repository_of_vnf_descriptor/example",
                "ports": [
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "dhcp_port",
                        "ipv4-config": "static",
                        "position": "0-0",
                        "ipv6-config": "none"
                    }
                ],
                "swap-disk-size": 0,
                "expandable": False,
                "ephemeral-file-system-size": 0,
                "root-file-system-size": 40
            },
            "ports": [
                {
                    "label": "dhcp_port",
                    "min": "1",
                    "cnt": 1,
                    "max": 1,
                    "ipv4c": "static",
                    "ipv6c": "none",
                    "type": "active",
                    "colour": "#000000"
                }
            ],
            "drawedPorts": [],
            "links": [
                "link_2"
            ]
        },
        "vnf_2": {
            "id": "vnf_2",
            "vnfDesc": {
                "name": "Firewall",
                "memory-size": 4096,
                "vnf-type": "virtual-machine",
                "uri": "http://repository_of_vnf_descriptor/example",
                "ports": [
                    {
                        "name": "eth",
                        "min": "0",
                        "label": "control",
                        "ipv4-config": "dhcp",
                        "position": "0-0",
                        "ipv6-config": "none"
                    },
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "external",
                        "ipv4-config": "none",
                        "position": "1-1",
                        "ipv6-config": "none"
                    },
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "internal",
                        "ipv4-config": "none",
                        "position": "2-N",
                        "ipv6-config": "none"
                    }
                ],
                "swap-disk-size": 0,
                "expandable": False,
                "cpu-requirements": {
                    "platform-type": "x86",
                    "socket": [
                        {
                            "coreNumbers": 1
                        }
                    ]
                },
                "ephemeral-file-system-size": 0,
                "root-file-system-size": 40
            },
            "ports": [
                {
                    "label": "external",
                    "min": "1",
                    "cnt": 1,
                    "max": 1,
                    "ipv4c": "none",
                    "ipv6c": "none",
                    "type": "transparent",
                    "colour": "#000000"
                },
                {
                    "label": "internal",
                    "min": "1",
                    "cnt": 1,
                    "max": 16,
                    "ipv4c": "none",
                    "ipv6c": "none",
                    "type": "transparent",
                    "colour": "#000000"
                }
            ],
            "drawedPorts": [],
            "links": [
                "link_4",
                "link_5"
            ]
        },
        "vnf_3": {
            "id": "vnf_3",
            "vnfDesc": {
                "CPUrequirements": {
                    "platformType": "x86",
                    "socket": [
                        {
                            "coreNumbers": 1
                        }
                    ]
                },
                "name": "nat",
                "memory-size": 4096,
                "vnf-type": "virtual-machine",
                "uri": "http://repository_of_vnf_descriptor/example",
                "ports": [
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "user_side",
                        "ipv4-config": "static",
                        "position": "0-0",
                        "ipv6-config": "none"
                    },
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "wan_side",
                        "ipv4-config": "static",
                        "position": "1-1",
                        "ipv6-config": "none"
                    }
                ],
                "swap-disk-size": 0,
                "expandable": False,
                "ephemeral-file-system-size": 0,
                "root-file-system-size": 40
            },
            "ports": [
                {
                    "label": "user_side",
                    "min": "1",
                    "cnt": 1,
                    "max": 1,
                    "ipv4c": "static",
                    "ipv6c": "none",
                    "type": "active",
                    "colour": "#000000"
                },
                {
                    "label": "wan_side",
                    "min": "1",
                    "cnt": 1,
                    "max": 1,
                    "ipv4c": "static",
                    "ipv6c": "none",
                    "type": "active",
                    "colour": "#000000"
                }
            ],
            "drawedPorts": [],
            "links": [
                "link_5",
                "link_6",
                "link_7"
            ]
        }
    },
    "splitter_list": {
        "splittermerger_1": {
            "id": "splittermerger_1",
            "num_inout": 3,
            "rules": [
                {
                    "in": 1,
                    "out": 3,
                    "priority": "1000",
                    "settings": {
                        "macsrc": "",
                        "macdst": "",
                        "ipsrc": "",
                        "ipdst": "",
                        "vlanid": "",
                        "portsrc": "",
                        "portdst": "80",
                        "protocol": "TCP"
                    }
                },
                {
                    "in": 1,
                    "out": 2,
                    "priority": "100",
                    "settings": {
                        "macsrc": "",
                        "macdst": "",
                        "ipsrc": "",
                        "ipdst": "",
                        "vlanid": "",
                        "portsrc": "",
                        "portdst": "",
                        "protocol": ""
                    }
                },
                {
                    "in": 2,
                    "out": 1,
                    "priority": "100",
                    "settings": {
                        "macsrc": "",
                        "macdst": "",
                        "ipsrc": "",
                        "ipdst": "",
                        "vlanid": "",
                        "portsrc": "",
                        "portdst": "",
                        "protocol": ""
                    }
                }
            ],
            "links": [
                "link_3",
                "link_4",
                "link_7"
            ],
            "drawedPorts": []
        }
    },
    "endpoint_list": {
        "endpoint_1": {
            "id": "endpoint_1",
            "type": "user",
            "links": [
                "link_1"
            ]
        },
        "endpoint_2": {
            "id": "endpoint_2",
            "type": "internet",
            "links": [
                "link_6"
            ]
        }
    },
    "lan_list": {
        "lan_1": {
            "id": "lan_1",
            "links": [
                "link_1",
                "link_2",
                "link_3"
            ]
        }
    },
    "link_list": {
        "link_1": {
            "id": "link_1",
            "elem1": {
                "id": "endpoint_1",
                "type": "endpoint"
            },
            "elem2": {
                "id": "lan_1",
                "type": "lan",
                "offset": 40
            }
        },
        "link_2": {
            "id": "link_2",
            "elem1": {
                "id": "vnf_1",
                "type": "vnf",
                "port": "vnf_1-port_0-dhcp_port_0"
            },
            "elem2": {
                "id": "lan_1",
                "type": "lan",
                "offset": 59
            }
        },
        "link_3": {
            "id": "link_3",
            "elem1": {
                "id": "splittermerger_1",
                "type": "splittermerger",
                "port": "splittermerger_1-port_0"
            },
            "elem2": {
                "id": "lan_1",
                "type": "lan",
                "offset": 124
            }
        },
        "link_4": {
            "id": "link_4",
            "elem1": {
                "id": "splittermerger_1",
                "type": "splittermerger",
                "port": "splittermerger_1-port_2"
            },
            "elem2": {
                "id": "vnf_2",
                "type": "vnf",
                "port": "vnf_2-port_0-external_0"
            }
        },
        "link_5": {
            "id": "link_5",
            "elem1": {
                "id": "vnf_3",
                "type": "vnf",
                "port": "vnf_3-port_0-user_side_0"
            },
            "elem2": {
                "id": "vnf_2",
                "type": "vnf",
                "port": "vnf_2-port_1-internal_0"
            }
        },
        "link_6": {
            "id": "link_6",
            "elem1": {
                "id": "endpoint_2",
                "type": "endpoint"
            },
            "elem2": {
                "id": "vnf_3",
                "type": "vnf",
                "port": "vnf_3-port_1-wan_side_0"
            }
        },
        "link_7": {
            "id": "link_7",
            "elem1": {
                "id": "splittermerger_1",
                "type": "splittermerger",
                "port": "splittermerger_1-port_1"
            },
            "elem2": {
                "id": "vnf_3",
                "type": "vnf",
                "port": "vnf_3-port_0-user_side_0"
            }
        }
    },
    "position_list": {
        "vnf_1": {
            "left": "172px",
            "top": "153px"
        },
        "vnf_2": {
            "left": "445px",
            "top": "201px"
        },
        "vnf_3": {
            "left": "465px",
            "top": "311px"
        },
        "splittermerger_1": {
            "left": "333px",
            "top": "231px"
        },
        "endpoint_1": {
            "left": "76px",
            "top": "251px"
        },
        "endpoint_2": {
            "left": "656px",
            "top": "269px"
        },
        "lan_1": {
            "left": "143px",
            "top": "369px"
        }
    }
}

simple_graph = {
    "user_id": "311bd2418cb5406ea39d9d484877a2ed",
    "vnf_list": {
        "vnf_1": {
            "id": "vnf_1",
            "vnfDesc": {
                "name": "Firewall",
                "memory-size": 4096,
                "vnf-type": "virtual-machine",
                "uri": "http://repository_of_vnf_descriptor/example",
                "ports": [
                    {
                        "name": "eth",
                        "min": "0",
                        "label": "control",
                        "ipv4-config": "dhcp",
                        "position": "0-0",
                        "ipv6-config": "none"
                    },
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "external",
                        "ipv4-config": "none",
                        "position": "1-1",
                        "ipv6-config": "none"
                    },
                    {
                        "name": "eth",
                        "min": "1",
                        "label": "internal",
                        "ipv4-config": "none",
                        "position": "2-N",
                        "ipv6-config": "none"
                    }
                ],
                "swap-disk-size": 0,
                "expandable": False,
                "cpu-requirements": {
                    "platform-type": "x86",
                    "socket": [
                        {
                            "coreNumbers": 1
                        }
                    ]
                },
                "ephemeral-file-system-size": 0,
                "root-file-system-size": 40
            },
            "ports": [
                {
                    "label": "external",
                    "min": "1",
                    "cnt": 1,
                    "max": 1,
                    "ipv4c": "none",
                    "ipv6c": "none",
                    "type": "transparent",
                    "colour": "#000000"
                },
                {
                    "label": "internal",
                    "min": "1",
                    "cnt": 1,
                    "max": 16,
                    "ipv4c": "none",
                    "ipv6c": "none",
                    "type": "transparent",
                    "colour": "#000000"
                }
            ],
            "drawedPorts": [],
            "links": [
                "link_1",
                "link_2"
            ]
        }
    },
    "splitter_list": {},
    "endpoint_list": {
        "endpoint_1": {
            "id": "endpoint_1",
            "type": "user",
            "links": [
                "link_1"
            ]
        },
        "endpoint_2": {
            "id": "endpoint_2",
            "type": "internet",
            "links": [
                "link_2"
            ]
        }
    },
    "lan_list": {},
    "link_list": {
        "link_1": {
            "id": "link_1",
            "elem1": {
                "id": "endpoint_1",
                "type": "endpoint"
            },
            "elem2": {
                "id": "vnf_1",
                "type": "vnf",
                "port": "vnf_1-port_0-external_0"
            }
        },
        "link_2": {
            "id": "link_2",
            "elem1": {
                "id": "vnf_1",
                "type": "vnf",
                "port": "vnf_1-port_1-internal_0"
            },
            "elem2": {
                "id": "endpoint_2",
                "type": "endpoint"
            }
        }
    },
    "position_list": {
        "vnf_1": {
            "left": "290px",
            "top": "198px"
        },
        "endpoint_1": {
            "left": "84px",
            "top": "196px"
        },
        "endpoint_2": {
            "left": "571px",
            "top": "193px"
        }
    }
}

sg = ServiceGraph()
sg.loads(simple_graph)
print sg.getNetworkFunctionForwardingGraph()
print ValidateNF_FG(sg.getNetworkFunctionForwardingGraph(False)).validate()
