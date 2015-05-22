from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/login/')),
	url(r'^login/$', "libreria.views.login_view"),
	url(r'^logout/$', "libreria.views.logout_view"),
	url(r'^app/$', "libreria.views.app"),
	url(r'^store/$', "libreria.views.store"),
	url(r'^upload/$', "libreria.views.user_image_upload"),
]
