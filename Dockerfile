FROM ubuntu:xenial
# Install base package dependencies
RUN echo "deb http://archive.ubuntu.com/ubuntu cosmic main" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends autoconf  automake  bzip2  build-essential  curl dpkg-dev  file  g++  gcc  git  imagemagick \
    && apt-get install -y --no-install-recommends libbz2-dev libc6-dev libcurl4-openssl-dev libdb-dev libevent-dev libffi-dev libgdbm-dev \
    && apt-get install -y --no-install-recommends libgeoip-dev libgeos-dev libglib2.0-dev libjpeg-dev libkrb5-dev liblzma-dev libmagickcore-dev \
    && apt-get install -y --no-install-recommends libmagickwand-dev libncurses5-dev libncursesw5-dev libpng-dev libpq-dev libreadline-dev libsqlite3-dev \
    && apt-get install -y --no-install-recommends libssl-dev libtool libwebp-dev libxml2-dev libxslt-dev libyaml-dev make patch ssh tk-dev vim xz-utils zlib1g-dev wget \
    && rm -rf /var/lib/apt/lists/*

#Install Python2,7, Python3.6, Pithon3.7, Pip2, Pip3.6, Pip3.7, Tox
RUN apt update \
    && apt install -y --no-install-recommends python python-dev python3 python3-wheel python3.6 python3.6-dev python3.7 python3.7-dev \
    && curl https://bootstrap.pypa.io/get-pip.py -k -s | python \
    && pip install tox \
    && curl https://bootstrap.pypa.io/get-pip.py -k -s | python3.6 \
    && curl https://bootstrap.pypa.io/get-pip.py -k -s | python3.7 \
    && sed -i 's/python3.7/python2/' /usr/local/bin/pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/urim

COPY . ./

CMD /bin/bash

RUN rm -rf *@tmp \
    && echo "git+file:///root/urim/patricia-common/@$(grep requirements.txt -e 'patricia-common' | cut -d ""@"" -f3)" >> requirements.txt \
    && echo "git+file:///root/urim/Urim/@$(grep requirements.txt -e 'Urim' | cut -d ""@"" -f3)" >> requirements.txt \
    && sed -i '/git+ssh:/d' requirements.txt
