from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard.prefetching_panel import Utils as utils
import logging

class AddForm(forms.SelfHandlingForm):

    host_name = forms.ChoiceField(
        label=_("Host name"),
        required=True,
        widget=forms.Select())

    image_id = forms.ChoiceField(
        label=_("Image"),
        required=True,
        widget=forms.Select())

    def _populate_initial(self, request, host_name=None):
        """
        Populate the HostName and ImageId fields according to the logged user and the chosen compute node.
        If no node has been chosen, every possible choise is displayed.
        :param request:
        :param host_name:
        :return:
        """
        if host_name is None:
            self.fields['host_name'].choices = utils.get_hosts_list(request)
            self.fields['image_id'].choices = utils.get_images_list(request)
        else:
            self.fields['host_name'].choices = [(host_name, host_name)]
            # Now get all images compatible with that host
            # This means all the images except the one already cached on the node
            self.fields['image_id'].choices = utils.get_available_images_for_host(request, host_name)


    def __init__(self, request, *args, **kwargs):
        # Alberto's note:
        # This constructor is invoked by the framework after the View get_initial() method.
        # The view might set an initial status for the form fields.
        # In this case, if the host_name has been set, we only want to display IMAGES that can be added
        # to the chose hostname. We will display only that hostname and get the possible images that can be
        # prefetched on that hostname (i.e. we don't present duplicates)
        #import pdb; pdb.set_trace()
        super(AddForm, self).__init__(request, *args, **kwargs)

        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'host_name' in initial:
                # If an hostname has been specified, populate fields accordingly
                self._populate_initial(request=request,host_name=initial['host_name'])
            else:
                # Otherwise populate as a generic add form
                self._populate_initial(request=request,host_name=None)
        else:
            # No initial state has been specified. Display the most generic form
            self._populate_initial(request=request,host_name=None)

    def handle(self, request, data):
        #import pdb; pdb.set_trace()
        try:
            # TODO: Security issue! Check the user can access image passed as param on post
            res = utils.add_image_to_cache(request, data['host_name'], data['image_id'])
            messages.success(request,"Image queued for prefetching!")
            # TODO: What should I return?
            res = (data['host_name'], data['image_id'])

            return True
        except Exception:
            # TODO: notify the user about the duplicate entry.
            exceptions.handle(request,_('Cannot add image to queue.'))
            return False


class DeleteForm(forms.SelfHandlingForm):

    host_name = forms.CharField(
        label=_("Host name"),
        required=True,
        widget=forms.HiddenInput()
    )
    image_id = forms.CharField(
        label=_("Image id"),
        required=True,
        widget=forms.HiddenInput()
    )


    def __init__(self, request, *args, **kwargs):
        super(DeleteForm, self).__init__(request, *args, **kwargs)
        initial = kwargs['initial']
        self.host_name = initial['host_name']
        self.image_id = initial['image_id']

    def handle(self, request, data):
        #import pdb; pdb.set_trace()
        try:
            res = utils.remove_image_from_precache(request, data['host_name'], data['image_id'])
            messages.success(request,"Image marked for deletion from " + data['host_name'])
            return True
        except Exception:
            # TODO: notify the user about the duplicate entry ? For now, simply die.
            exceptions.handle(request,_('Cannot delete image from queue.'))
            return False