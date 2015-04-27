#!/bin/bash

path_horizon="/usr/share/openstack-dashboard"
path_source_horizon="/usr/share/pyshared/horizon"
sudo cp -r forwarding_graph/ $path_horizon/openstack_dashboard/dashboards/admin/
patch $path_horizon/openstack_dashboard/dashboards/admin/dashboard.py  < dashboard.patch

sudo cp conf.cfg /etc/openstack-dashboard/

cp horizon.forwarding_graph.js /usr/share/openstack-dashboard/static/horizon/js/

patch $path_horizon/templates/horizon/_scripts.html  < _scripts.patch

sudo cp images/user.png $path_horizon/static/dashboard/img
sudo cp images/internet.png $path_horizon/static/dashboard/img
sudo cp images/control.png $path_horizon/static/dashboard/img

sudo apt-get install python-lesscpy
sudo python $path_horizon/manage.py compress
sudo service apache2 restart

echo "Forwarding graph extension successfully installed"
