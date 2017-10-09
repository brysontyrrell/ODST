#!/bin/bash

/usr/local/bin/celery worker --app ods_worker.celery --workdir /opt/odst/ &

/usr/bin/uwsgi --ini /etc/uwsgi/apps-enabled/web-app.ini
