Captive portal readme
=====================

1) Check the content of the following file and update the relevant information:

    WebContent/WEB-INF/captive_portal.properties

2) Check (and, if needed, update) the path of the tomcat server, 
   which can be found at the beginning the 'build.xml' file.

3) To compile the server, type:

       host$ ant

   This will create the WAR and copy in the proper Tomcat folder, as
   specified in the build.xml file.
