from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.project import dashboard


class ServiceGraph(horizon.Panel):
    name = _("Service Graph")
    slug = "service_graph"


dashboard.Project.register(ServiceGraph)
