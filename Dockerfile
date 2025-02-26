FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3.7 \
    python3.7-dev \
    python3-pip \
    build-essential \
    wget \
    && apt-get clean

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN python3 -m pip install --upgrade pip

WORKDIR /env

COPY . /env

RUN pip install -e .

RUN cd / && \
    wget -O boost_1_69_0.tar.gz https://sourceforge.net/projects/boost/files/boost/1.69.0/boost_1_69_0.tar.gz/download && \
    tar -zxvf boost_1_69_0.tar.gz && \
    cd boost_1_69_0 && \
    ./bootstrap.sh --with-libraries=python --with-toolset=gcc && \
    ./b2 cflags='-fPIC' cxxflags='-fPIC' --with-python include="/usr/include/python3.7m/" && \
    ./b2 install && \
    cd stage/lib && \
    ln -s libboost_python37.so libboost_python.so && \
    ln -s libboost_python37.a libboost_python.a

ENV LD_LIBRARY_PATH=/boost_1_69_0/stage/lib:$LD_LIBRARY_PATH

CMD ["bash", "-c", "cd /env/test/ && python env_test.py"]
