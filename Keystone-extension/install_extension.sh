#!/bin/bash

# copy file from workspace to keystone
# you must run this script as su

keystone_path="/usr/lib/python2.7/dist-packages"

mkdir $keystone_path/keystone/contrib/user_profile
cp -R user_profile/validator.py $keystone_path/keystone/contrib/user_profile/
cp -R user_profile/core.py $keystone_path/keystone/contrib/user_profile/
cp -R user_profile/controllers.py $keystone_path/keystone/contrib/user_profile/
cp -R user_profile/routers.py $keystone_path/keystone/contrib/user_profile/
cp -R user_profile/__init__.py $keystone_path/keystone/contrib/user_profile/

mkdir $keystone_path/keystone/contrib/user_profile/backends
cp -R user_profile/backends/__init__.py $keystone_path/keystone/contrib/user_profile/backends/
cp -R user_profile/backends/sql.py $keystone_path/keystone/contrib/user_profile/backends/

mkdir $keystone_path/keystone/contrib/user_profile/migrate_repo
cp -R user_profile/migrate_repo/__init__.py $keystone_path/keystone/contrib/user_profile/migrate_repo 
cp -R user_profile/migrate_repo/migrate.cfg $keystone_path/keystone/contrib/user_profile/migrate_repo

mkdir $keystone_path/keystone/contrib/user_profile/migrate_repo/versions
cp -R user_profile/migrate_repo/versions/__init__.py $keystone_path/keystone/contrib/user_profile/migrate_repo/versions/
cp -R user_profile/migrate_repo/versions/001_user_profile_table.py $keystone_path/keystone/contrib/user_profile/migrate_repo/versions/

patch $keystone_path/keystone/common/config.py  < config.patch
patch $keystone_path/keystone/common/sql/core.py  < core.patch
patch /etc/keystone/keystone-paste.ini < keystone-paste.patch

/usr/bin/keystone-manage db_sync --extension user_profile 

echo '' > /var/log/keystone/keystone-all.log

echo 'changes applied, now restarting'

sudo service keystone restart
#echo 'waiting for errors (5 seconds)....'
sleep 5

echo "errors"
cat /var/log/keystone/keystone-all.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/keystone/keystone-all.log | grep CRITICAL |wc -l
