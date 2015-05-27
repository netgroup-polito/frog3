FROM ubuntu:latest
MAINTAINER Ivano Cerrato <ivano.cerrato@polito.it>

RUN apt-get update && \
	apt-get install -y ssh  && \ 
	apt-get install iptraf && \
	apt-get install bridge-utils && \
	apt-get install -y build-essential && \
        apt-get install -y wget && \
        apt-get install -y python && \
	apt-get install -y tcpdump

RUN wget http://openvswitch.org/releases/openvswitch-2.1.2.tar.gz && tar -xvf openvswitch-2.1.2.tar.gz  && rm openvswitch-2.1.2.tar.gz*

RUN cd openvswitch-2.1.2 && ./configure && make -j 4 && make install
RUN mkdir -p /usr/local/etc/openvswitch
RUN cd openvswitch-2.1.2 && ovsdb-tool create /usr/local/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema


RUN mkdir -p /var/run/sshd && \
	mkdir -p /root/.ssh && \
	echo 'root:root' | chpasswd
	
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed '/PermitRootLogin without-password/d' /etc/ssh/sshd_config > tmp_file && \
	rm /etc/ssh/sshd_config && \
	mv tmp_file /etc/ssh/sshd_config
	
ADD start.sh start.sh
RUN chmod +x start.sh

ADD configure_ovs.sh /
RUN chmod +x configure_ovs.sh 


CMD ./start.sh






