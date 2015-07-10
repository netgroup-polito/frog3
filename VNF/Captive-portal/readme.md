Captive portal readme
=====================

This folder contains the files needed to create the captive portal that is used to authenticate users on the FROG3 network.
In order to deplooy this software in a dedicated virtual machine, you have to follow the above steps.

1) Check the content of the following file and update the relevant information:

    WebContent/WEB-INF/captive_portal.properties

2) Check (and, if needed, update) the path of the tomcat server, 
   which can be found at the beginning the 'build.xml' file.

3) To compile the server, type:

    host$ ant

This will create the WAR and copy in the proper Tomcat folder, as
specified in the build.xml file.
