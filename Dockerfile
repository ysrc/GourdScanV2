############################################################

# Dockerfile to build gourdscan v2.1 environment
# Based on Ubuntu
# https://github.com/ysrc/GourdScanV2
# edit by range

############################################################


FROM ubuntu

RUN apt-get update
RUN apt-get install -y redis-server python python-pip zip wget vim openssh-server
RUN pip install tornado requests redis scapy
RUN wget https://github.com/dugsong/libdnet/archive/master.zip
RUN unzip master.zip
RUN cd /libdnet-master && ./configure
RUN cd libdnet-master && make && make install
RUN cd libdnet-master/python/ && python setup.py install
RUN rm -rf /libdnet-master
RUN rm master.zip
RUN wget https://github.com/sqlmapproject/sqlmap/zipball/master
RUN unzip master -d /home
RUN rm master
RUN mv /home/sqlmap* /home/sqlmap
RUN wget https://github.com/ysrc/GourdScanV2/archive/github.zip
RUN unzip github.zip -d /home
RUN rm github.zip
RUN mv /home/GourdScanV2-github /home/gourdscan
RUN mkdir -p /var/run/sshd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config  
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config  
RUN echo "root:Y3rc_admin" | chpasswd
RUN usermod -s /bin/bash admin

EXPOSE 8000
EXPOSE 22
EXPOSE 10086
EXPOSE 10806

CMD ["/usr/sbin/sshd", "-D"]  