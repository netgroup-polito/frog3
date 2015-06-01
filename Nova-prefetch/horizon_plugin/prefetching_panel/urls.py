# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.prefetching_panel import views

# Alberto's notes
# Note: how is it working?
# Have a look here! https://docs.djangoproject.com/en/1.8/topics/http/urls/
# Basically, given an url, python checks it against the following list of regex. Once a match occurs,
# it stops and passes the control to the corresponding view.
# Some info:
# url(<regex>, <view_to_call_if_match>, <name>)
# Regex is the regular expression used to check if the URL should be passed to a particular view.
# Every time we want to capture a parameter and pass it to the view, we simply need to specify the param
# inside a couple of parenthesis "()". The parsed value will be passed to the matching view. In that case,
# we are using non-named params, i.e. they get passed to the view without any name, just invoking
# view(param1,param2,...). There's the possibility to name every param, so the view can uniquely
# refer to each one. In this case, we need to follow the particular syntax for regex, like the following
# r'^add/(?P<host_name>[^/]+)$' => this will parse the sub regex "[^/]+" and assign its value to host_name param.
# In this case, the view gets invoked as view(host_name=...).
# Note that if any 1 named argument is found, non named args are ignored. If no named arg is found, the view
# gets called with non-named args.
# Be advised: no leading slash is needed! Every url already starts with a slash.

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index$', views.IndexView.as_view(), name='index'),
    # Follows the mapping for a new cache entry
    url(r'^add/(?P<host_name>[^/]+)$',views.AddView.as_view(), name='add'), # Needed to add an image to a specific host
    url(r'^add/$',views.AddView.as_view(), name='add'),
    # The following url regards the image_cache deletion
    url(r'^delete/(?P<host_name>[^/]+)/(?P<image_id>[^/]+)$',views.DeleteView.as_view(), name='delete'),

    # Follows the mapping for the detailed view
    #url(r'^(?P<mapping_id>[^/]+)/$', views.PrecacheDetailView.as_view(), name='detail'),
)
