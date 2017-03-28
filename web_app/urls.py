from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^login/?$', views.login, name='login'),
    url(r'^logout/?$', views.logout, name='logout'),
    url(r'^index/?$', views.index, name='index'),

    url(r'^dashboard/?$', views.index, name='dashboard'),
    url(r'^ng/dashboard/?$', views.dashboard, name='dashboard'),

    # Devices
    url(r'^devices/?$', views.index, name='list_devices'),
    url(r'^ng/devices/?$', views.list_devices, name='list_devices'),

    url(r'^devices/add?$', views.index, name='add_device'),
    url(r'^ng/devices/add/?$', views.add_device, name='add_device'),

    url(r'^ng/devices/delete/?$', views.delete_device, name='delete_device'),

    url(r'^ng/api/devices/?$', views.list_devices_json, name='list_devices_json'),

    # Authgroups
    url(r'^ng/api/authgroups/?$', views.list_authgroup_json, name='list_authgroup_json'),

    # Models
    url(r'^models/?$', views.index, name='list_models'),
    url(r'^ng/models/?$', views.list_models, name='list_models'),

    url(r'^models/add?$', views.index, name='add_model'),
    url(r'^ng/models/add/?$', views.add_model, name='add_model'),

    url(r'^ng/models/delete/?$', views.delete_model, name='delete_model'),

    url(r'^ng/api/models/?$', views.list_models_json, name='list_devices_json'),

    # Basic Config
    url(r'^basic-config/?$', views.index, name='basic_config'),
    url(r'^ng/basic-config/?$', views.basic_config, name='basic_config'),

    url(r'^$', views.index, name='index'),
]
