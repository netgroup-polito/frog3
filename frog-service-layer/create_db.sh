echo 'Insert the mysql password of user root.'
echo 'drop database if exists orchestrator; create database orchestrator; use orchestrator; source db.sql;' | mysql -u root -p
echo 'Database created.'
