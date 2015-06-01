from django.utils.translation import ugettext_lazy as _
from django.template import defaultfilters as filters
from django.core import urlresolvers
from django.utils.http import urlencode
from openstack_dashboard.prefetching_panel import Utils as utils
from horizon import tables


def get_node_images_table(host):
    res = "<table>"
    for i in host.get_images():
        res += "<tr style='border:0px;'>"
        res += "<td style='border:0px;'>"
        """
        # FIXME: should we extend the status diagram for pending deletion? For now, workaround the problem
        if i.marked_for_deletion and i.status != 'ERROR':
            res += 'Pending deletion'
        else:
            res += i.status
        """
        res += i.status
        res += "</td>"
        res += "<td style='border:0px;'>"
        url = urlresolvers.reverse("horizon:admin:prefetching_panel:delete", kwargs={'host_name':i.compute_host, 'image_id':i.image_id})
        res += "<a class='btn btn-small btn-danger btn-delete ajax-modal' href=\""+url+"\"> X </a>"
        res += "</td>"
        res += "<td style='border:0px;'>"
        url = urlresolvers.reverse("horizon:admin:images:detail",args=(i.image_id,))
        res += "<a href=\""+url+"\">"+i.image_name + "</a>"
        res += "</td>"
        res += "</tr>"
    res += "</table>"
    return res


def get_node_images(host):
    res = []
    for i in host.get_images():
        url = urlresolvers.reverse("horizon:admin:images:detail",args=(i.image_id,))
        str = "<a href=\""+url+"\">"+i.image_name + "</a>" + " - " + i.status
        res.append(str)
    return res

def get_link_by_raw_line(value):
    url = urlresolvers.reverse("horizon:admin:images:detail",args=(value.image_id,))
    return url


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class AddImageToNodeAction(tables.LinkAction):
    name = "add_to_node"
    classes = ("ajax-modal", "btn-create")
    verbose_name = _("Prefetch image...")
    url = "horizon:admin:prefetching_panel:add"
    icon = "plus"

    # Overriding the get_link_url to point to /add/compute_chosen
    def get_link_url(self, row):
        base_url = urlresolvers.reverse(self.url)
        return "".join([base_url,row.hostname])

class AddImageToPrecacheAction(tables.LinkAction):
    name = "add"
    verbose_name = _("Add Prefetching Image")
    url = "horizon:admin:prefetching_panel:add"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"

class DeleteRawEntryAction(tables.DeleteAction):
    data_type_singular = _("Cache Image")
    name = "delete_record"

    def delete(self, request, obj_id):
        # The id is a concatenation of host_name/image_id
        tokens = obj_id.split("/")
        hostname = tokens[0]
        imageid = tokens[1]
        utils.remove_image_from_precache(request, hostname, imageid)
        return False

class NodeTable(tables.DataTable):
    name = tables.Column('id', verbose_name=_("Hypervisor HostName"))
    image_id = tables.Column(get_node_images_table,
                             #wrap_list=True,
                             filters=(filters.safe,), # Alberto's hint: Needed to render custom html inside custom column.
                             verbose_name=_("Image"))

    def get_object_id(self,datum):
        return datum.hostname

    class Meta:
        name = "nodes"
        verbose_name = _("Nodes")
        table_actions = (AddImageToPrecacheAction, MyFilterAction)
        row_actions = (AddImageToNodeAction,)
        multi_select = False


class RawTable(tables.DataTable):
    name = tables.Column('compute_host', verbose_name=_("Hypervisor HostName"))
    image_id = tables.Column('image_id', verbose_name=_("Image"), link=get_link_by_raw_line)
    status = tables.Column('status', status=True, status_choices=(('DOWNLOADING', None), ('CACHED', True),
                                                                  ('ERROR', False)), verbose_name=_("Cache Status"))
    message = tables.Column('message', verbose_name=_("Message"))

    def get_object_id(self, datum):
        """
        Alberto's note
        This method is used by the framework to get Unique ids for each row.
        Using a table, those ids will be rendered as the VALUE fields of the ids checkboxes
        :param datum:
        :return:
        """
        return datum.compute_host+"/"+datum.image_id

    class Meta:
        name = "rows"
        verbose_name = _("Raw Table")
        table_actions = (AddImageToPrecacheAction, DeleteRawEntryAction)
        multi_select = True