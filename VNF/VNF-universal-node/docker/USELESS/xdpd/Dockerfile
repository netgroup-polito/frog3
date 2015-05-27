FROM ubuntu:latest
MAINTAINER Ivano Cerrato <ivano.cerrato@polito.it>

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    autoconf \
    automake \
    libtool \
    pkg-config \
    libconfig++-dev

RUN git clone -b devel-0.4 --depth 1 git://codebasin.net/rofl-core.git
RUN cd rofl-core && sed -i 's/-Werror/ /g' configure.ac

RUN cd rofl-core && ./autogen.sh && ./configure && make -j 4 && make install && \
    cd .. && rm -rf rofl-core

RUN git clone -b devel-0.4 --depth 1 git://codebasin.net/xdpd.git
RUN cd xdpd && find . -name "configure.ac" -type f | xargs sed -i 's/-Werror/ /g' configure.ac


RUN  export LD_LIBRARY_PATH=/usr/local/lib && cd xdpd && ./autogen.sh && ./configure  && make -j 4 && make install && \
     cd .. && rm -rf xdpd

ADD ./xdpd.conf /
ADD start_switch.sh start_switch.sh

RUN chmod +x start_switch.sh

CMD export LD_LIBRARY_PATH=/usr/local/lib && ./start_switch.sh
