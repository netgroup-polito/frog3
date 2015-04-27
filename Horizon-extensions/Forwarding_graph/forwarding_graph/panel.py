from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class Forwarding_Graph(horizon.Panel):
    name = _("Forwarding Graphs")
    slug = "forwarding_graph"
	#permissions = ('openstack.roles.admin',)

dashboard.Admin.register(Forwarding_Graph)
