FROM      ubuntu
MAINTAINER Politecnico di Torino

# This file is based on the guide provided at:
# 	http://pietervogelaar.nl/ubuntu-12-04-install-jetty-9 

RUN apt-get update && apt-get install -y --no-install-recommends wget ssh iptraf bind9 vim bash-completion

#Prepare the ssh server
RUN mkdir -p /var/run/sshd && \
	mkdir -p /root/.ssh && \
	echo 'root:root' | chpasswd
	
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed '/PermitRootLogin without-password/d' /etc/ssh/sshd_config > tmp_file && \
	rm /etc/ssh/sshd_config && \
	mv tmp_file /etc/ssh/sshd_config

#Prepare Bind9
ADD named.conf.options /etc/bind/ 
#Prepare the captive portal
#RUN mkdir /usr/java
#RUN ln -s /usr/lib/jvm/java-7-openjdk-amd64 /usr/java/default

#RUN wget http://dist.codehaus.org/jetty/jetty-hightide-8.0.0/jetty-hightide-8.0.0.v20110901.tar.gz
#RUN tar xf jetty*.tar.gz && rm -rf jetty*.tar.gz
#RUN mkdir /opt/jetty && cd jetty* && ls | while read r; do cp -R $r /opt/jetty; done && cd .. && rm -rf jetty*

#RUN cp /opt/jetty/bin/jetty.sh /etc/init.d/jetty

#RUN cd /opt/jetty/webapps/ && rm -rf *

#ADD jetty.conf /etc/default/jetty
#ADD root.war /opt/jetty/webapps/root.war

#Add the scripts to run the function
ADD start_dns.sh start_dns.sh

RUN chmod +x start_dns.sh

CMD ./start_dns.sh
