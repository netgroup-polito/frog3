from horizon import tabs
from horizon import forms
from django.core.urlresolvers import reverse_lazy
from horizon.utils import memoized
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.prefetching_panel import tabs as mydashboard_tabs
from openstack_dashboard.prefetching_panel import forms as cache_forms
from django.core.urlresolvers import reverse
from openstack_dashboard.prefetching_panel import Utils as utils


class IndexView(tabs.TabbedTableView):
    tab_group_class = mydashboard_tabs.PrefetchingTabs
    template_name = 'admin/prefetching_panel/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class AddView(forms.ModalFormView):
    form_class = cache_forms.AddForm
    form_id = "add_precache_form"
    modal_header = _("Add image to precache")
    submit_label = _("Prefetch")
    submit_url = reverse_lazy('horizon:admin:prefetching_panel:add')
    template_name = 'admin/prefetching_panel/add_image_to_precache.html'
    context_object_name = 'precache'
    success_url = reverse_lazy("horizon:admin:prefetching_panel:index")
    page_title = _("Prefetch an image")

    def get_context_data(self,**kwargs):
        """
        Alberto's note
        This method is invoked secondly, after get_initial has been invoked and the view has been build with its contructor.
        The goal of this method is to set the CONTEXT data, which the template can refer to. Basically, if we define
        context['varname'] = 'test' -> inside the template we can refer to the 'test' value by using {{ varname }}.
        :param kwargs:
        :return:
        """
        #import pdb; pdb.set_trace()
        context = super(AddView, self).get_context_data(**kwargs)
        return context

    def get_initial(self):
        """
        Alberto's note.
        This method is called after the Django dispatcher has chosen the view to load (as first in Views). This is needed in order to initialize
        the form we want to display to the user with custom data. The form might be able to read initial data from
        the return value we pass over here. We basically need to populate accordingly out return object so that
        the form can initiate correctly its fields.
        :return:
        """
        #import pdb; pdb.set_trace()
        # The parent isn't returning anything useful
        #initial = super(AddView, self).get_initial()

        initial = {}

        # Prasing values from URL and setting those into the return initial form status
        params = self.kwargs
        if 'host_name' in params:
            initial['host_name'] = params['host_name']

        return initial


class DeleteView(forms.ModalFormView):
    form_class = cache_forms.DeleteForm
    form_id = "delete_precache_form"
    submit_label = _("Delete")
    cancel_label = _("Cancel")
    submit_url = "horizon:admin:prefetching_panel:delete"
    template_name = 'admin/prefetching_panel/delete_image.html'
    success_url = reverse_lazy("horizon:admin:prefetching_panel:index")
    page_title = _("Remove an image from cache")

    def get_context_data(self,**kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['fom_id'] = self.form_id
        context['submit_label'] = self.submit_label
        context['cancel_label'] = self.cancel_label
        context['page_title'] = self.page_title
        context['host_name'] = self.kwargs['host_name']
        context['image_id'] = self.kwargs['image_id']
        context['submit_url'] = reverse(self.submit_url, kwargs={'host_name': self.kwargs['host_name'],
                                                                 'image_id': self.kwargs['image_id']})
        context['success_url'] = self.success_url
        return context

    def get_initial(self):
        initial = {}

        # Prasing values from URL and setting those into the return initial form status
        params = self.kwargs
        if 'host_name' in params:
            initial['host_name'] = params['host_name']
        else:
            raise Exception("Missing host_name parameter.")

        if 'image_id' in params:
            initial['image_id'] = params['image_id']
        else:
            raise Exception("Missing image_id parameter.")

        return initial