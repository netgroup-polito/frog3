from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/login/')),
	url(r'^login/$', "webContent.views.login_view"),
	url(r'^logout/$', "webContent.views.logout_view"),
	url(r'^app/$', "webContent.views.app"),
	url(r'^store/$', "webContent.views.store"),
	url(r'^upload/$', "webContent.views.user_image_upload"),
	url(r'^config/$', "webContent.views.config"),
]
