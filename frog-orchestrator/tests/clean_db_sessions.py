'''
Created on Oct 23, 2015

@author: fabiomignini
'''
from orchestrator_core.sql.sql_server import get_session
from orchestrator_core.sql.graph import ActionModel, EndpointModel, EndpointResourceModel, FlowRuleModel, GraphModel, MatchModel, OpenstackNetworkModel, OpenstackSubnetModel, PortModel, VNFInstanceModel, GraphConnectionModel 
from orchestrator_core.sql.session import SessionModel

session = get_session()
session.query(ActionModel).delete()
session.query(EndpointModel).delete()
session.query(EndpointResourceModel).delete()
session.query(FlowRuleModel).delete()
session.query(GraphModel).delete()
session.query(GraphConnectionModel).delete()
session.query(MatchModel).delete()
session.query(OpenstackNetworkModel).delete()
session.query(OpenstackSubnetModel).delete()
session.query(PortModel).delete()
session.query(VNFInstanceModel).delete()
session.query(SessionModel).delete()

print "Database sessions deleted"
