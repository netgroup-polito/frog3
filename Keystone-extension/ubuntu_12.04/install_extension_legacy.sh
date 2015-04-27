#!/bin/bash

# copy file from workspace to keystone
# you must run this script as su

keystone_path_shared="/usr/share/pyshared"

mkdir $keystone_path_shared/keystone/contrib/user_profile
cp -R user_profile/validator.py $keystone_path_shared/keystone/contrib/user_profile/
cp -R user_profile/core.py $keystone_path_shared/keystone/contrib/user_profile/
cp -R user_profile/controllers.py $keystone_path_shared/keystone/contrib/user_profile/
cp -R user_profile/routers.py $keystone_path_shared/keystone/contrib/user_profile/
cp -R user_profile/__init__.py $keystone_path_shared/keystone/contrib/user_profile/

mkdir $keystone_path_shared/keystone/contrib/user_profile/backends
cp -R user_profile/backends/__init__.py $keystone_path_shared/keystone/contrib/user_profile/backends/
cp -R user_profile/backends/sql.py $keystone_path_shared/keystone/contrib/user_profile/backends/

mkdir $keystone_path_shared/keystone/contrib/user_profile/migrate_repo
cp -R user_profile/migrate_repo/__init__.py $keystone_path_shared/keystone/contrib/user_profile/migrate_repo 
cp -R user_profile/migrate_repo/migrate.cfg $keystone_path_shared/keystone/contrib/user_profile/migrate_repo

mkdir $keystone_path_shared/keystone/contrib/user_profile/migrate_repo/versions
cp -R user_profile/migrate_repo/versions/__init__.py $keystone_path_shared/keystone/contrib/user_profile/migrate_repo/versions/
cp -R user_profile/migrate_repo/versions/001_user_profile_table.py $keystone_path_shared/keystone/contrib/user_profile/migrate_repo/versions/


patch $keystone_path/keystone/common/config.py  < config.patch
patch $keystone_path/keystone/common/sql/core.py  < core.patch
patch /etc/keystone/keystone-paste.ini  < keystone-paste.patch

##########################################################################################

# Create symbol link in /usr/lib/python2.7/dist-packages/keystone
keystone_path="/usr/lib/python2.7/dist-packages"

mkdir $keystone_path/keystone/contrib/user_profile
cd $keystone_path/keystone/contrib/user_profile/
ln -s $keystone_path/keystone/contrib/user_profile/__init__.py __init__.py
ln -s $keystone_path/keystone/contrib/user_profile/core.py core.py
ln -s $keystone_path/keystone/contrib/user_profile/controllers.py controllers.py
ln -s $keystone_path/keystone/contrib/user_profile/routers.py routers.py
ln -s $keystone_path/keystone/contrib/user_profile/__init__.py __init__.py

mkdir backends
cd backends
ln -s $keystone_path/keystone/contrib/user_profile/backends/__init__.py __init__.py
ln -s $keystone_path/keystone/contrib/user_profile/backends/sql.py sql.py

cd ..
mkdir migrate_repo
cd migrate_repo
ln -s $keystone_path/keystone/contrib/user_profile/migrate_repo/__init__.py __init__.py
ln -s $keystone_path/keystone/contrib/user_profile/migrate_repo/migrate.cfg

mkdir versions
cd versions
ln -s $keystone_path/keystone/contrib/user_profile/migrate_repo/versions/__init__.py __init__.py
ln -s $keystone_path/keystone/contrib/user_profile/migrate_repo/versions/001_user_profile_table.py 001_user_profile_table.py

./usr/bin/keystone-manage db_sync --extension example
sudo service keystone restart

echo "keystone extension successfully installed"



