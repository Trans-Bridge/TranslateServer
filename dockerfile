ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

ARG SOURCEDIR=/root/translate_server_py/

ADD . ${SOURCEDIR}
WORKDIR ${SOURCEDIR}

RUN pip install -i https://pypi.douban.com/simple -r requirements.txt

ENV MKL_VERSION=${SOURCEDIR}}
EXPOSE 80
CMD [ "python", "service.py" ]
