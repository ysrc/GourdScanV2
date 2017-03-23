############################################################

# Dockerfile to build gourdscan v2.1 environment
# Based on Ubuntu
# https://github.com/ysrc/GourdScanV2
# edit by range

############################################################


FROM ubuntu

#get all the environment
RUN apt-get update
RUN apt-get install -y redis-server python python-pip zip wget vim openssh-server python-libpcap libpcap-dev
RUN pip install --upgrade pip
RUN pip install tornado requests redis scapy
RUN wget https://github.com/sqlmapproject/sqlmap/zipball/master
RUN unzip master -d /root
RUN rm master
RUN mv /root/sqlmap* /root/sqlmap
RUN wget https://github.com/ysrc/GourdScanV2/archive/github.zip
RUN unzip github.zip -d /root
RUN rm github.zip
RUN mv /root/GourdScanV2-github /root/gourdscan
RUN cd /root/gourdscan && python setup.py install

#install sshd service
RUN mkdir -p /var/run/sshd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config  
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config  
RUN echo "root:Y3rc_admin" | chpasswd
RUN usermod -s /bin/bash root
RUN cp -r ~/gourdscan/* /usr/local/lib/python2.7/dist-packages/gourdscan-2.1-py2.7.egg/gourdscan/

EXPOSE 8000
EXPOSE 22
EXPOSE 10086
EXPOSE 10806
