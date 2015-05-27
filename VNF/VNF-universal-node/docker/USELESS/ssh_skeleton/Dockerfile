FROM ubuntu:latest
MAINTAINER Ivano Cerrato <ivano.cerrato@polito.it>

RUN apt-get update && \
	apt-get install ssh -y && \ 
	apt-get install iptraf

RUN mkdir -p /var/run/sshd && \
	mkdir -p /root/.ssh && \
	echo 'root:root' | chpasswd
	
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed '/PermitRootLogin without-password/d' /etc/ssh/sshd_config > tmp_file && \
	rm /etc/ssh/sshd_config && \
	mv tmp_file /etc/ssh/sshd_config
	
ADD start.sh start.sh
RUN chmod +x start.sh

CMD ./start.sh
