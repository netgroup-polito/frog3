# Orchestrator installation guide (Tested on ubuntu 14.04.1)

- Clone the repository including submodules:

        git clone https://github.com/netgroup-polito/frog3-orchestrator.git
        cd frog3-orchestrator
        git submodule init && git submodule update

- Required ubuntu packages:
    
        sudo apt-get install python-dev python-setuptools
		sudo easy_install pip
        sudo apt-get install python-sqlalchemy libmysqlclient-dev
		sudo pip install --upgrade cython falcon requests gunicorn jsonschema mysql-python
		
- Configuration:
    - The configuration file is stored in configuration/orchestrator.conf		
	
- Create database
    - Create database and user for orchestrator database:
	    
            mysql -u root -p
            mysql> CREATE DATABASE orchestrator;
            mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'localhost' IDENTIFIED BY 'ORCH_DBPASS';
            mysql> GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'%' IDENTIFIED BY 'ORCH_DBPASS';	
            mysql> exit;
    
    - Create tables in the orchestrator db:
            
            mysql -u orchestrator -p orchestrator < db.sql

    - Change the db connection in configuration/orchestrator.conf:

            [db]
            # Mysql DB
            connection = mysql://orchestrator:ORCH_DBPASS@127.0.0.1/orchestrator
        
	- Change templates inside the "templates" directory with right information

- Run the orchestrator
        
        ./start_orchestrator.sh
