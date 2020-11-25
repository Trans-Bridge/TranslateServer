ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

ARG SOURCEDIR=/root/translate_server_py/

ADD . ${SOURCEDIR}
WORKDIR ${SOURCEDIR}

# install python package
RUN pip install -i https://pypi.douban.com/simple -r requirements.txt

# manualy install faiseq (use the version which we train model on)
RUN git clone https://github.com/pytorch/fairseq.git && \
    cd fairseq && \
    git checkout 265791b727b664d4d7da3abd918a3f6fb70d7337 && \
    pip install -i https://pypi.douban.com/simple . && \
    cd .. && \
    rm -rf fairseq

ENV MKL_VERSION=${SOURCEDIR}}
EXPOSE 80
CMD [ "python", "service.py" ]
