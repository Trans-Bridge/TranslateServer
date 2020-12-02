ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

# update pip 
RUN pip install -i https://pypi.douban.com/simple --upgrade pip

WORKDIR /root
ENV CMAKE_VERSION=3.18.4
RUN wget -q https://github.com/Kitware/CMake/releases/download/v$CMAKE_VERSION/cmake-$CMAKE_VERSION-Linux-x86_64.tar.gz && \
    tar xf *.tar.gz && \
    rm *.tar.gz
ENV PATH=$PATH:/root/cmake-$CMAKE_VERSION-Linux-x86_64/bin

# manually install pyltp
RUN git clone https://github.com/HIT-SCIR/pyltp.git && \
    cd pyltp && \
    git checkout v0.4.0 && \
    git submodule init && \
    git submodule update && \
    python setup.py install && \
    cd .. && \
    rm -rf pyltp

# manually install faiseq (use the version which we train model on)
RUN git clone https://github.com/pytorch/fairseq.git && \
    cd fairseq && \
    git checkout 265791b727b664d4d7da3abd918a3f6fb70d7337 && \
    pip install -i https://pypi.douban.com/simple . && \
    cd .. && \
    rm -rf fairseq

COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.douban.com/simple -r requirements.txt

ARG SOURCEDIR=/root/translate_server_py/
WORKDIR ${SOURCEDIR}
ADD . ${SOURCEDIR}

EXPOSE 80
CMD [ "python", "service.py" ]
