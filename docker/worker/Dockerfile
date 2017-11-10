FROM ubuntu:16.04

RUN /usr/bin/apt-get update -q && \
    /usr/bin/apt-get install -qqy build-essential git && \
    /usr/bin/apt-get install -qqy python-pip python-dev && \
    /usr/bin/pip install pipenv && \
    /usr/bin/apt-get install -qqy libssl-dev libffi-dev && \
    /usr/bin/apt-get clean && \
    /bin/rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY /Pipfile* /opt/odst/
WORKDIR /opt/odst/
RUN  /usr/local/bin/pipenv install --system --deploy

COPY /ods/ /opt/odst/ods/
COPY /ods_worker.py /opt/odst/
COPY /docker/ods_conf.cfg /opt/odst/

RUN /bin/chown -R www-data:www-data /opt/odst/ods/static

CMD ["/usr/local/bin/celery", "worker", "--app", "ods_worker.celery", "--workdir", "/opt/odst/"]