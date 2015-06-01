from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs
from openstack_dashboard import api
from openstack_dashboard.prefetching_panel import tables
from openstack_dashboard import api
from openstack_dashboard.prefetching_panel import Utils as utils


class AllTab(tabs.TableTab):
    """
    Shows all the data into a nice table.
    """
    name = _("Full detailed View")
    slug = "full_tab"
    table_classes = (tables.RawTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_rows_data(self):
        request = self.tab_group.request
        try:
            visible_hosts, visible_images = utils.get_user_hosts_and_images(request)
            self._has_more = False
            return visible_images
        except Exception:
            error_message = _('Unable to get node-image rows')
            exceptions.handle(request, error_message)
            return []


class NodeTab(tabs.TableTab):
    """
    Organizes by hosts
    """
    name = _("View By Node")
    slug = "node_tab"
    table_classes = (tables.NodeTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_nodes_data(self):
        request = self.tab_group.request
        try:
            visible_hosts, visible_images = utils.get_user_hosts_and_images(request)

            hosts = []
            # Group by hostname into a list of hosts. Each host wraps a list of related images.
            for h in visible_hosts:
                wrap = utils.NodeWrapper(h.host_name)
                hosts.append(wrap)

            for i in visible_images:
                for h in hosts:
                    if h.hostname == i.compute_host:
                        h.append_img(i)

            self._has_more = False
            return hosts
        except Exception:
            error_message = _('Unable to get nodes')
            exceptions.handle(request, error_message)
            return []


class PrefetchingTabs(tabs.TabGroup):
    slug = "image_prefetching"
    tabs = (NodeTab, AllTab)
    sticky = True
