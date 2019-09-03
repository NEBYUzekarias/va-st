FROM opencog/opencog-deps:18.04-no-haskell

RUN apt-get update && apt-get -y upgrade
ENV POSTGIS_MAJOR 2.5
ENV POSTGIS_VERSION 2.5.1+dfsg-1.pgdg90+1

RUN apt-get update \
      && apt-cache showpkg postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
      && apt-get install -y --no-install-recommends \
           postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR=$POSTGIS_VERSION \
           postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR-scripts=$POSTGIS_VERSION \
           postgis=$POSTGIS_VERSION \
      && rm -rf /var/lib/apt/lists/*

RUN apt-get install -y \
            nlohmann-json-dev \
            libcurl4-gnutls-dev \
            cxxtest \
            build-essential \
            autoconf \
            libtool \
            pkg-config \
            libgflags-dev \
            libgtest-dev \
            clang \
            libc++-dev \
            git \
            curl \
            nano \
            wget \
            libudev-dev \
            libusb-1.0-0-dev \
            nodejs \
            npm \
            python3 \
            python3-pip \
            libboost-all-dev

RUN cd / && \
    git clone https://github.com/opencog/cogutil.git && \
    cd cogutil && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

RUN cd / && \
    git clone https://github.com/opencog/atomspace.git && \
    cd atomspace && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

RUN cd / && \
    git clone https://github.com/opencog/ure.git && \
    cd ure && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

RUN cd / && \
    git clone https://github.com/aconchillo/guile-json.git && \
    cd /guile-json && \
    apt-get install -y dh-autoreconf && \
    autoreconf -vif && \
    ./configure --prefix=/usr --libdir=/usr/lib && \
    make && \
    make install && \
    ldconfig

# opencog is built later to incorporate new atom types used by the virtual assistant
RUN cd / && git clone https://github.com/opencog/opencog.git &&\
    cd opencog &&\
    mkdir build &&\
    cd build &&\
    cmake .. &&\
    make -j$(nproc) &&\
    make install && \
    ldconfig

RUN git clone -b $(curl -L https://grpc.io/release) https://github.com/grpc/grpc /var/local/git/grpc && \
    cd /var/local/git/grpc && \
    git submodule update --init && \
    make -j$(nproc) && make install && ldconfig && \
    cd third_party/protobuf && \
    make install && make clean && ldconfig && \
    cd /var/local/git/grpc && make clean && \
    cd / && \
    rm -rf /var/local/git/grpc

WORKDIR /
