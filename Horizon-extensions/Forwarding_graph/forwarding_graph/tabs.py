from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.forwarding_graph import tables
from openstack_dashboard.dashboards.admin.forwarding_graph import api as project_api

class GraphsTab(tabs.Tab):
    name = _("Graphs")
    slug = "graphs_tab"
    template_name = "admin/forwarding_graph/_detail_forwarding_graph.html"

    def get_context_data(self, request):
        context = {}
		#context['d3_data'] = project_api.json_data(request)
        return context

class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (GraphsTab,)
    sticky = True


