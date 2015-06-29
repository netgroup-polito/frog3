'''
Created on Jun 22, 2015

@author: fabiomignini
'''
from Common.SQL.graph import Graph
from Common.NF_FG.nf_fg import NF_FG
from Common.SQL.session import Session
nffg= {
  "profile": {
    "VNFs": [
      {
        "vnf_descriptor": "switch.json",
        "manifest": {
          "CPUrequirements": {
            "platformType": "x86",
            "socket": [
              {
                "coreNumbers": 1
              }
            ]
          },
          "name": "switch",
          "memory-size": 2048,
          "vnf-type": "virtual-machine",
          "uri": "http://controller:9292/v2/images/89a6a8c5-433a-4724-b7c5-bbeda8dc39e1",
          "ports": [
            {
              "name": "eth",
              "min": "1",
              "label": "L2Port",
              "ipv4-config": "none",
              "position": "0-N",
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
            "id": "L2Port:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "dhcp",
                      "port": "inout:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "1"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "ingoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Switch",
                      "port": "L2Port:1"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "1000",
                        "sourceMAC": "11:11:11:11:11:11",
                        "id": "69b6fa16b8a643938210e0185ff393c1"
                      }
                    ],
                    "ingress_endpoint": "ingress"
                  }
                }
              ]
            },
            "id": "L2Port:1",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "endpoint": {
                      "id": "ingress"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "3"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "id": "L2Port:2",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Firewall",
                      "port": "User:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "4"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "id": "L2Port:3",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Monitor",
                      "port": "control_port:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "5"
                      }
                    ]
                  }
                }
              ]
            }
          }
        ],
        "id": "Switch",
        "name": "Switch"
      },
      {
        "vnf_descriptor": "cisco_dhcp.json",
        "manifest": {
          "CPUrequirements": {
            "platformType": "x86",
            "socket": [
              {
                "coreNumbers": 1
              }
            ]
          },
          "name": "cisco_dhcp",
          "memory-size": 2048,
          "vnf-type": "virtual-machine",
          "uri": "http://controller:9292/v2/images/00491289-3124-41f7-8333-2c8e5dbde3f6",
          "ports": [
            {
              "name": "eth",
              "min": "1",
              "label": "inout",
              "ipv4-config": "none",
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
            "id": "inout:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Switch",
                      "port": "L2Port:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "6"
                      }
                    ]
                  }
                }
              ]
            }
          }
        ],
        "id": "dhcp",
        "name": "dhcp"
      },
      {
        "vnf_descriptor": "cisco_firewall.json",
        "manifest": {
          "CPUrequirements": {
            "platformType": "x86",
            "socket": [
              {
                "coreNumbers": 1
              }
            ]
          },
          "name": "cisco_firewall",
          "memory-size": 2048,
          "vnf-type": "virtual-machine",
          "uri": "http://controller:9292/v2/images/6dc7b8af-3b92-4683-9400-ba40420c784b",
          "ports": [
            {
              "name": "eth",
              "min": "1",
              "label": "User",
              "ipv4-config": "none",
              "position": "0-0",
              "ipv6-config": "none"
            },
            {
              "name": "eth",
              "min": "1",
              "label": "WAN",
              "ipv4-config": "none",
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
            "id": "WAN:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Monitor",
                      "port": "inout:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "7"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "id": "User:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Switch",
                      "port": "L2Port:2"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "8"
                      }
                    ]
                  }
                }
              ]
            }
          }
        ],
        "id": "Firewall",
        "name": "Firewall"
      },
      {
        "vnf_descriptor": "cisco_monitor.json",
        "manifest": {
          "CPUrequirements": {
            "platformType": "x86",
            "socket": [
              {
                "coreNumbers": 1
              }
            ]
          },
          "name": "cisco_monitor",
          "memory-size": 2048,
          "vnf-type": "virtual-machine",
          "uri": "http://controller:9292/v2/images/1e690297-9dd8-4cb7-9373-5c9ddcfadd85",
          "ports": [
            {
              "name": "eth",
              "min": "1",
              "label": "control_port",
              "ipv4-config": "static",
              "position": "0-0",
              "ipv6-config": "none"
            },
            {
              "name": "eth",
              "min": "2",
              "label": "inout",
              "ipv4-config": "none",
              "position": "1-2",
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
            "id": "inout:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Firewall",
                      "port": "WAN:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "9"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "id": "inout:1",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Router-Nat",
                      "port": "User:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "10"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "id": "control_port:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Switch",
                      "port": "L2Port:3"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "11"
                      }
                    ]
                  }
                }
              ]
            }
          }
        ],
        "id": "Monitor",
        "name": "Monitor"
      },
      {
        "vnf_descriptor": "cisco_nat.json",
        "manifest": {
          "CPUrequirements": {
            "platformType": "x86",
            "socket": [
              {
                "coreNumbers": 1
              }
            ]
          },
          "name": "cisco_nat",
          "memory-size": 2048,
          "vnf-type": "virtual-machine",
          "uri": "http://controller:9292/v2/images/483c833b-38ed-404d-b95d-a941d879b2e1",
          "ports": [
            {
              "name": "eth",
              "min": "1",
              "label": "User",
              "ipv4-config": "static",
              "position": "1-1",
              "ipv6-config": "none"
            },
            {
              "name": "eth",
              "min": "1",
              "label": "WAN",
              "ipv4-config": "dhcp",
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
            "ingoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Router-Nat",
                      "port": "WAN:0"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "12"
                      }
                    ],
                    "ingress_endpoint": "egress"
                  }
                }
              ]
            },
            "id": "WAN:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "endpoint": {
                      "id": "egress"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "13"
                      }
                    ]
                  }
                }
              ]
            }
          },
          {
            "id": "User:0",
            "outgoing_label": {
              "flowrules": [
                {
                  "action": {
                    "VNF": {
                      "id": "Monitor",
                      "port": "inout:1"
                    },
                    "type": "output"
                  },
                  "flowspec": {
                    "matches": [
                      {
                        "priority": "32770",
                        "id": "14"
                      }
                    ]
                  }
                }
              ]
            }
          }
        ],
        "id": "Router-Nat",
        "name": "Router-Nat"
      }
    ],
    "endpoints": [
      {
        "interface": "INGRESS_to-br-usr",
        "type": "physical",
        "attached": True,
        "id": "ingress",
        "name": "INGRESS"
      },
      {
        "interface": "em1",
        "type": "physical",
        "attached": True,
        "id": "egress",
        "name": "EGRESS"
      }
    ],
    "id": "Demo-Turin-2015-day2",
    "name": "Protected_access_to_the_internet"
  }
}
Session().add_session(1, 'supercazzola', 'nuc1', 'Demo-Turin-2015-day2', 'Protected_access_to_the_internet', 'nuc1', 'scheduling')
nffg = NF_FG(nffg)
Graph().addNFFG(nffg, 1)
print Graph().get_nffg(1, encode=True)

