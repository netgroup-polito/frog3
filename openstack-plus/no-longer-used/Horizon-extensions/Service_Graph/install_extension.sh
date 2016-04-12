#!/bin/bash
# Service graph extension installation script

path_horizon="/usr/share/openstack-dashboard"
path_source_horizon="/usr/share/pyshared/horizon"

sudo cp -r static/service_graph $path_horizon/static

sudo chown horizon:horizon $path_horizon/static/service_graph -R

sudo cp -r project/service_graph $path_horizon/openstack_dashboard/dashboards/project

sudo patch $path_horizon/openstack_dashboard/dashboards/project/dashboard.py  < dashboard.patch

sudo cp sg_conf.cfg /etc/openstack-dashboard/sg_conf.cfg

# TODO: copy templates

sudo python $path_horizon/manage.py compress
sudo service apache2 restart

echo "Service graph extension successfully installed"
