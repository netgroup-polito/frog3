# Service Layer installation guide (Tested on ubuntu 14.04.1)

- Required ubuntu packages:
    
        sudo apt-get install python-dev python-setuptools
        sudo easy_install pip
        sudo apt-get install python-sqlalchemy libmysqlclient-dev
        sudo pip install --upgrade cython falcon requests gunicorn jsonschema mysql-python json_hyper_schema
    
- Create database
    - Create database and user for service layer database:
        
            mysql -u root -p
            mysql> CREATE DATABASE service_layer;
            mysql> GRANT ALL PRIVILEGES ON service_layer.* TO 'service_layer'@'localhost' IDENTIFIED BY 'SL_DBPASS';
            mysql> GRANT ALL PRIVILEGES ON service_layer.* TO 'service_layer'@'%' IDENTIFIED BY 'SL_DBPASS';    
            mysql> exit;
    
    - Create tables in the orchestrator db:
            
            cd frog-service-layer
            mysql -u service_layer -p service_layer < db.sql

    - Change the db connection in configuration/service_layer.conf:

            [db]
            # Mysql DB
            connection = mysql://service_layer:SL_DBPASS@127.0.0.1/service_layer
    
    - Change the orchestrator endpoint:
            
            [orchestrator]
            port = ORCH_PORT
            ip = ORCH_IP
        
    - Change templates inside the "templates" directory with right information
    
    - Associate for eache user in the DB a service graph (for this step could be useful to install phpmyadmin)
        - Insert a row in the table user

- Run the service layer
        
        ./start_service_layer.sh
