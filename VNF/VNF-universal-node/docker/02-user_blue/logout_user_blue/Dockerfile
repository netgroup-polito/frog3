FROM      ubuntu
MAINTAINER Politecnico di Torino

RUN apt-get update && apt-get install -y  apache2 ssh php5 php5-curl lsof 

#Prepare the ssh server
RUN mkdir -p /var/run/sshd && \
	mkdir -p /root/.ssh && \
	echo 'root:root' | chpasswd
	
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN sed '/PermitRootLogin without-password/d' /etc/ssh/sshd_config > tmp_file && \
	rm /etc/ssh/sshd_config && \
	mv tmp_file /etc/ssh/sshd_config

#RUN /var/www/html/index.html

#Add the files 
ADD delete.tar.gz delete
#RUN tar -xvf delete.tar.gz
RUN cd delete/delete && cp -r * /var/www/html/
RUN cd /var/www/html && chmod 777 unify.png

#Add the scripts to run the function
ADD start.sh start.sh

RUN chmod +x start.sh

CMD ./start.sh
