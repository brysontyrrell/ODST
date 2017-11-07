Example Docker Compose Setup
============================

.. note::

    This option as provided is primarily meant to serve as a development
    and testing environment.

You can create a full ODS instance using the provided ``docker-compose.yml``
file on a running Docker host. This Docker Compose configuration will create and
launch the following containers on your host:

- Nginx
- MySQL
- Redis
- ODS Web App
- ODS Worker

The containers are isolated by three networks: ``proxy`` connects Nginx (the
externally accessible service) to the ODS web app. The ``db`` network connects
MySQL to both the web app and the worker, and the same is true for the ``cache``
network. Nginx cannot contact the MySQL, Redis, or worker containers in this
configuration.

There will be two data volumes for persisting the MySQL database as well as the
file share directory located at ``/opt/odst/ods/static/share``. The file share
volume is shared between the ODS application and Nginx containers. In this
configuration Nginx takes over for serving the packages.

Use the following commands to launch the containers on a Docker host from the
ODST repository's directory:

.. code-block:: bash

    docker-compose build
    docker-compose up -d

Navigate to the IP address of your Docker host in a web browser to begin using
the ODS web UI.

.. note::

    Launch the containers on multiple Docker hosts to test syncing features.
