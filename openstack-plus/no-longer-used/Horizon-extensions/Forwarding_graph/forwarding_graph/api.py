# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import urllib
import json

class ForwardingGraph(object):
    pass

def json_data(request):
	j_data = {
		  "profile": {
			"VNFs": [
			  {
				"vnf_descriptor": "http://controller:9292/v2/images/483ae2c1-9c8b-49c8-bfdb-b9626a768a18/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/07ef1ffe-ecbe-4126-9ba5-8b7bf1baa299",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-N",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "L2Port"
				    }
				  ]
				},
				"ports": [
				  {
				    "id": "L2Port:1",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "IPTraf",
				              "port": "in/out:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2898",
				                "etherType": "0x800",
				                "protocol": "tcp",
				                "destPort": "80",
				                "id": "91757d0619644685ba0d30483f6321df"
				              }
				            ]
				          }
				        },
				        {
				          "action": {
				            "VNF": {
				              "id": "IPTraf_no80",
				              "port": "in/out:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "100",
				                "id": "1248d6944a1a4716be44a09ee362b829"
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
				              "id": "Ingress_DHCP",
				              "port": "in/out:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "200",
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
				              "id": "Client_Switch",
				              "port": "L2Port:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "40000",
				                "sourceMAC": "aa:bb:cc:dd:ee:ff",
				                "id": "659"
				              }
				            ],
				            "ingress_endpoint": "Ingress_endpoint"
				          }
				        }
				      ]
				    },
				    "id": "L2Port:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "endpoint": {
				              "port": "Ingress_endpoint"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "40000",
				                "id": "8"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "Client_Switch",
				"name": "Switch"
			  },
			  {
				"vnf_descriptor": "http://controller:9292/v2/images/e713087c-718f-4ac2-93bd-45e0ab9a52c9/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/b53b87fb-5b3b-41a2-a01a-3c1f34fecd06",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-0",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'true',
				      "label": "in/out"
				    }
				  ]
				},
				"ports": [
				  {
				    "id": "in/out:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Client_Switch",
				              "port": "L2Port:2"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "400",
				                "id": "5"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "Ingress_DHCP",
				"name": "dh_nat"
			  },
			  {
				"vnf_descriptor": "http://controller:9292/v2/images/ebfcf44b-744b-49a5-8424-82067aaf6b2d/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/bee7701f-2c01-4cbb-8c0e-d15ca79bf233",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-0",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "User"
				    },
				    {
				      "position": "1-1",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "Internet"
				    }
				  ]
				},
				"ports": [
				  {
				    "id": "User:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Firewall_80",
				              "port": "Internet:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2898",
				                "etherType": "0x800",
				                "protocol": "tcp",
				                "destPort": "80",
				                "id": "5db83c0166b44acf9fb418dc7ca252da"
				              }
				            ]
				          }
				        },
				        {
				          "action": {
				            "VNF": {
				              "id": "IPTraf_no80",
				              "port": "in/out:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "100",
				                "id": "b173b2678dda4eaeb1f54891d89d9828"
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
				              "id": "Egress_NAT",
				              "port": "Internet:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "100",
				                "id": "9875"
				              }
				            ],
				            "ingress_endpoint": "Egress_endpoint"
				          }
				        }
				      ]
				    },
				    "id": "Internet:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "endpoint": {
				              "port": "Egress_endpoint"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "11222"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "Egress_NAT",
				"name": "nat"
			  },
			  {
				"vnf_descriptor": "http://130.192.225.162:9292/v2/images/483ae2c1-9c8b-49c8-bfdb-b9626a768a18/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/07ef1ffe-ecbe-4126-9ba5-8b7bf1baa299",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-N",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "L2Port"
				    }
				  ]
				},
				"ports": [
				  {
				    "ingoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "77050850c51948bd86a48098d2485387",
				              "port": "L2Port:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "8a4f1c082d9b42fa8f0004bbff2901f5"
				              }
				            ],
				            "ingress_endpoint": "b9c520d0e85744ada397fdf638452ffc"
				          }
				        }
				      ]
				    },
				    "id": "L2Port:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "endpoint": {
				              "port": "b9c520d0e85744ada397fdf638452ffc"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "d2bf0c59aea1439a95e3a95df3987cbb"
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
				              "id": "IPTraf",
				              "port": "control:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "29443"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  },
				  {
				    "id": "L2Port:1",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "IPTraf_no80",
				              "port": "control:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "100",
				                "id": "134248"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "77050850c51948bd86a48098d2485387",
				"name": "Switch"
			  },
			  {
				"vnf_descriptor": "http://130.192.225.162:9292/v2/images/483ae2c1-9c8b-49c8-bfdb-b9626a768a18/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/07ef1ffe-ecbe-4126-9ba5-8b7bf1baa299",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-N",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "L2Port"
				    }
				  ]
				},
				"ports": [
				  {
				    "ingoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "a9cba4c0a87d472d9c48b4380f37302d",
				              "port": "L2Port:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "aa39cbbd1f5848f5a073e10949e87126"
				              }
				            ],
				            "ingress_endpoint": "b9c520d0e85744ada397fdf638452ffc"
				          }
				        }
				      ]
				    },
				    "id": "L2Port:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "endpoint": {
				              "port": "b9c520d0e85744ada397fdf638452ffc"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "69fdb7f13f45472eb63b4b273361f393"
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
				              "id": "a9cba4c0a87d472d9c48b4380f37302d",
				              "port": "L2Port:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "a0bfb6df096e4ee58301c4a3bdb253cb"
				              }
				            ],
				            "ingress_endpoint": "8:6206f9f3db6e49af8aa35d0b506705a1"
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
				              "port": "8:6206f9f3db6e49af8aa35d0b506705a1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "3848c8fa2afd42278583ef7068884c04"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "a9cba4c0a87d472d9c48b4380f37302d",
				"name": "Endpoint_Switch"
			  },
			  {
				"vnf_descriptor": "http://130.192.225.162:9292/v2/images/483ae2c1-9c8b-49c8-bfdb-b9626a768a18/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/07ef1ffe-ecbe-4126-9ba5-8b7bf1baa299",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-N",
				      "min": "1",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "L2Port"
				    }
				  ]
				},
				"ports": [
				  {
				    "ingoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "0f24b10cf89b4626b5b771e17994c514",
				              "port": "L2Port:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "e6b20d5b59fe453da4c2b9882bc3cb40"
				              }
				            ],
				            "ingress_endpoint": "Egress_endpoint"
				          }
				        }
				      ]
				    },
				    "id": "L2Port:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "endpoint": {
				              "port": "Egress_endpoint"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "9a84164c22e44f65a6a235d1cc54dae7"
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
				              "id": "0f24b10cf89b4626b5b771e17994c514",
				              "port": "L2Port:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "8e2dd5eb82b345dfb34657cf2c6cc9bd"
				              }
				            ],
				            "ingress_endpoint": "8:dfb8a942cb1948a195bf4355253dcaa1"
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
				              "port": "8:dfb8a942cb1948a195bf4355253dcaa1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "20000",
				                "id": "c1beb0315f7c4bed995d5b8821a70729"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "0f24b10cf89b4626b5b771e17994c514",
				"name": "Endpoint_Switch"
			  },
			  {
				"vnf_descriptor": "http://controller:9292/v2/images/65b93325-45b5-40dc-ac82-4c03fedf334b/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/01a76bd3-026b-48d9-afdd-16a3716e7337",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "1-2",
				      "min": "2",
				      "type": "physical",
				      "configurable": 'true',
				      "label": "in/out"
				    },
				    {
				      "position": "0-0",
				      "min": "0",
				      "type": "physical",
				      "configurable": 'true',
				      "label": "control"
				    }
				  ]
				},
				"ports": [
				  {
				    "id": "in/out:1",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Firewall_80",
				              "port": "User:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "166623948"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  },
				  {
				    "id": "in/out:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Client_Switch",
				              "port": "L2Port:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "c3f1dcde6b3048159180b6b2f7927a19"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  },
				  {
				    "id": "control:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "77050850c51948bd86a48098d2485387",
				              "port": "L2Port:2"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "589"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "IPTraf",
				"name": "ntop80"
			  },
			  {
				"vnf_descriptor": "http://controller:9292/v2/images/6bb87de2-ea33-4c01-bda9-cf891bc3fc3c/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/bee7701f-2c01-4cbb-8c0e-d15ca79bf233",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "0-0",
				      "min": "2",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "User"
				    },
				    {
				      "position": "1-1",
				      "min": "2",
				      "type": "physical",
				      "configurable": 'false',
				      "label": "Internet"
				    }
				  ]
				},
				"ports": [
				  {
				    "id": "User:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "IPTraf",
				              "port": "in/out:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "121773"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  },
				  {
				    "id": "Internet:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Egress_NAT",
				              "port": "User:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "100",
				                "id": "dce100cf822d4ca0b40580f4f4a84d04"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "Firewall_80",
				"name": "dpi_bbc"
			  },
			  {
				"vnf_descriptor": "http://controller:9292/v2/images/65b93325-45b5-40dc-ac82-4c03fedf334b/file",
				"manifest": {
				  "rootFileSystemSize": 40,
				  "CPUrequirements": {
				    "platformType": "x86",
				    "socket": [
				      {
				        "coreNumbers": 1
				      }
				    ]
				  },
				  "memorySize": 4096,
				  "ephemeralFileSystemSize": 0,
				  "uri": "http://controller:9292/v2/images/01a76bd3-026b-48d9-afdd-16a3716e7337",
				  "vnfType": "1",
				  "ports": [
				    {
				      "position": "1-2",
				      "min": "2",
				      "type": "physical",
				      "configurable": 'true',
				      "label": "in/out"
				    },
				    {
				      "position": "0-0",
				      "min": "0",
				      "type": "physical",
				      "configurable": 'true',
				      "label": "control"
				    }
				  ]
				},
				"ports": [
				  {
				    "id": "in/out:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Client_Switch",
				              "port": "L2Port:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "47e0a652491a4528812c28a3251465fe"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  },
				  {
				    "id": "in/out:1",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "Egress_NAT",
				              "port": "User:0"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "100",
				                "id": "7cca3748d9224d998aeb60aecd730c16"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  },
				  {
				    "id": "control:0",
				    "outgoing_label": {
				      "flowrules": [
				        {
				          "action": {
				            "VNF": {
				              "id": "77050850c51948bd86a48098d2485387",
				              "port": "L2Port:1"
				            },
				            "type": "output"
				          },
				          "flowspec": {
				            "matches": [
				              {
				                "priority": "2",
				                "id": "543433"
				              }
				            ]
				          }
				        }
				      ]
				    }
				  }
				],
				"id": "IPTraf_no80",
				"name": "ntopNo80"
			  }
			],
			"endpoints": [
			  {
				"id": "Ingress_endpoint",
				"name": "INGRESS"
			  },
			  {
				"id": "User_egress_endpoint_peer",
				"name": "USER_EGRESS"
			  },
			  {
				"endpoint_switch": "0f24b10cf89b4626b5b771e17994c514",
				"id": "Egress_endpoint",
				"name": "ISP_INGRESS"
			  },
			  {
				"endpoint_switch": "a9cba4c0a87d472d9c48b4380f37302d",
				"id": "b9c520d0e85744ada397fdf638452ffc",
				"name": "USER_CONTROL_EGRESS"
			  },
			  {
				"endpoint_switch": "a9cba4c0a87d472d9c48b4380f37302d",
				"id": "8:6206f9f3db6e49af8aa35d0b506705a1",
				"name": "EDGE_ENDPOINT"
			  },
			  {
				"endpoint_switch": "0f24b10cf89b4626b5b771e17994c514",
				"id": "8:dfb8a942cb1948a195bf4355253dcaa1",
				"name": "EDGE_ENDPOINT"
			  }
			],
			"id": "18",
			"name": "Blue'sNF-FG"
		  }
		}

	#returndata = {}
	#try:
	#	fd = open("nfs.json", 'r')
	#	text = fd.read()
	#	fd.close()
	#	returndata = json.read(text)
	#	# Hm. this returns unicode keys...
	#	#returndata = simplejson.loads(text)
	#except:
	#	print 'COULD NOT LOAD: file'

	#myurl = 'http://www.quandl.com/api/v1/datasets/FRED/GDP.json'
	#response = urllib.urlopen(myurl)

	# Convert bytes to string type and string type to dict
	#string = response.read().decode('utf-8')
	#json_obj = json.loads(string)

	return json.dumps(j_data)

