FROM      ubuntu
MAINTAINER Politecnico di Torino

RUN apt-get update && apt-get install -y --no-install-recommends openjdk-7-jdk wget ssh iptraf python python-pip python-dev screen build-essential lsof

RUN mkdir /usr/java
RUN ln -s /usr/lib/jvm/java-7-openjdk-amd64 /usr/java/default

#Install tomcat 
RUN wget mirrors.muzzy.it/apache/tomcat/tomcat-8/v8.0.21/bin/apache-tomcat-8.0.21.tar.gz && tar xzf apache-tomcat-8.0.21.tar.gz 
RUN cd /apache-tomcat-8.0.21/webapps && rm -rf ROOT
RUN cd /apache-tomcat-8.0.21/conf && rm server.xml
ADD root.war /apache-tomcat-8.0.21/webapps/ROOT.war
ADD server.xml /apache-tomcat-8.0.21/conf/server.xml

#Prepare the ssh server
RUN mkdir -p /var/run/sshd && \
	mkdir -p /root/.ssh && \
	echo 'root:root' | chpasswd
	
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed '/PermitRootLogin without-password/d' /etc/ssh/sshd_config > tmp_file && \
	rm /etc/ssh/sshd_config && \
	mv tmp_file /etc/ssh/sshd_config



#RUN wget http://dist.codehaus.org/jetty/jetty-hightide-8.0.0/jetty-hightide-8.0.0.v20110901.tar.gz
#RUN tar xf jetty*.tar.gz && rm -rf jetty*.tar.gz
#RUN mkdir /opt/jetty && cd jetty* && ls | while read r; do cp -R $r /opt/jetty; done && cd .. && rm -rf jetty*

#RUN cp /opt/jetty/bin/jetty.sh /etc/init.d/jetty

#RUN cd /opt/jetty/webapps/ && rm -rf *

#ADD jetty.conf /etc/default/jetty
#ADD root.war /opt/jetty/webapps/root.war

#Add the takeMac server
ADD TakeMac /opt/TakeMac/
RUN pip install --upgrade cython falcon requests gunicorn jsonschema

#Add the scripts to run the function
ADD start_cp.sh start_cp.sh

RUN chmod +x start_cp.sh

CMD ./start_cp.sh
