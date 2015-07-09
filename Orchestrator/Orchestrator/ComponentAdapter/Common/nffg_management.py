'''
Created on Jul 6, 2015

@author: fabiomignini
'''
import copy, logging
from Common.NF_FG.nf_fg import NF_FG

class NFFG_Management(object):
    def __init__(self):
        pass
    
    def diff(self, nffg_old, nffg_new):
        nffg = NF_FG()
        nffg._id = nffg_new._id
        nffg.name = nffg_new.name
        
        nffg.listVNF = nffg_new.listVNF
        nffg.listEndpoint = nffg_new.listEndpoint
        for new_vnf in nffg_new.listVNF:
            new_vnf.status = 'new'
        # check vnfs
        for old_vnf in nffg_old.listVNF:
            vnf_found = False
            for new_vnf in nffg_new.listVNF:
                if old_vnf.id == new_vnf.id and old_vnf.name == new_vnf.name and old_vnf.template == new_vnf.template:
                    new_vnf.status = 'already_deployed'
                    new_vnf.db_id = old_vnf.db_id
                    new_vnf.internal_id = old_vnf.internal_id
                    # check ports
                    
                    for new_port in new_vnf.listPort:
                        new_port.status = 'new'
                    for old_port in old_vnf.listPort:
                        port_found = False
                        for new_port in new_vnf.listPort:
                            if old_port.id == new_port.id:
                                new_port.status = 'already_deployed'
                                new_port.db_id = old_port.db_id
                                new_port.internal_id = old_port.internal_id
                                # check flow-rules
                                for new_flowrule in new_port.list_outgoing_label:
                                    new_flowrule.status = 'new'
                                for old_flowrule in old_port.list_outgoing_label:
                                    flowrule_found = False
                                    for new_flowrule in new_port.list_outgoing_label:
                                        if old_flowrule.getJSON() == new_flowrule.getJSON():
                                            new_flowrule.status = 'already_deployed'
                                            new_flowrule.db_id = old_flowrule.db_id
                                            new_flowrule.internal_id = old_flowrule.internal_id
                                            flowrule_found = True
                                            break
                                    if flowrule_found is False:
                                        old_flowrule.status = 'to_be_deleted'
                                        new_port.list_outgoing_label.append(old_flowrule)
                                    
                                for new_flowrule in new_port.list_ingoing_label:
                                    new_flowrule.status = 'new'
                                for old_flowrule in old_port.list_ingoing_label:
                                    flowrule_found = False
                                    for new_flowrule in new_port.list_ingoing_label:
                                        if old_flowrule.getJSON() == new_flowrule.getJSON():
                                            new_flowrule.status = 'already_deployed'
                                            new_flowrule.db_id = old_flowrule.db_id
                                            flowrule_found = True
                                            break
                                    if flowrule_found is False:
                                        old_flowrule.status = 'to_be_deleted'
                                        new_port.list_ingoing_label.append(old_flowrule)
                                port_found = True
                                break
                        if port_found is False:
                            old_port.status = 'to_be_deleted'
                            new_vnf.listPort.append(old_port)
                    vnf_found = True
                    break
            if vnf_found is False:
                old_vnf.status = 'to_be_deleted'
                nffg.listVNF.append(old_vnf)
        for new_endpoint in nffg_new.listEndpoint:
            new_endpoint.status = 'new'     
        for old_endpoint in nffg_old.listEndpoint:
            endpoint_found = False
            for new_endpoint in nffg_new.listEndpoint:
                if old_endpoint.id == new_endpoint.id:
                    new_endpoint.status = 'already_deployed'
                    new_endpoint.db_id = old_endpoint.db_id
                    endpoint_found = True
            if endpoint_found is False:
                old_endpoint.status = 'to_be_deleted'
                nffg.listEndpoint.append(old_endpoint)
                
        return nffg
        