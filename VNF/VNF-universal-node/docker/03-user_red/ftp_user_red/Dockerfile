FROM      ubuntu
MAINTAINER Politecnico di Torino

RUN apt-get update && apt-get install -y ssh iptraf tcpdump

#Prepare the ssh server

RUN mkdir -p /var/run/sshd && \
	mkdir -p /root/.ssh && \
	echo 'root:root' | chpasswd
	
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed '/PermitRootLogin without-password/d' /etc/ssh/sshd_config > tmp_file && \
	rm /etc/ssh/sshd_config && \
	mv tmp_file /etc/ssh/sshd_config
	
#Prepare the DHCP server

ADD user_red.txt /root/user_red.txt
#ADD dhcp.conf /etc/dhcp/dhcpd.conf
ADD start_ftp.sh start_ftp.sh

RUN chmod +x start_ftp.sh

CMD ./start_ftp.sh
