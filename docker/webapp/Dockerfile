FROM ubuntu:16.04

RUN /usr/bin/apt-get update -q && \
    /usr/bin/apt-get install -qqy build-essential git && \
    /usr/bin/apt-get install -qqy python-pip python-dev && \
    /usr/bin/apt-get install -qqy libssl-dev libffi-dev && \
    /usr/bin/apt-get install -qqy uwsgi uwsgi-plugin-python && \
    /usr/bin/apt-get clean && \
    /bin/rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY /docker/webapp/web-app.ini /etc/uwsgi/apps-enabled/

COPY /requirements.txt /opt/odst/
RUN /usr/bin/pip install -U pip && \
    /usr/bin/pip install -r /opt/odst/requirements.txt

COPY /ods/ /opt/odst/ods/
COPY /application.py /opt/odst/
COPY /ods_worker.py /opt/odst/
COPY /docker/webapp/ods_conf.cfg /opt/odst/

COPY /docker/webapp/startup.sh /opt/odst/

RUN /bin/chown -R www-data:www-data /opt/odst/ods/static

CMD ["/bin/bash", "/opt/odst/startup.sh"]
