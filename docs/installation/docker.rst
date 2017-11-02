Example Docker Compose Setup
============================

.. note::

    This option as provided is primarily meant to serve as a development
    and testing environment.

You can create a full ODS instance using the provided ``docker-compose.yml``
file on a running Docker host. This Docker Compose configuration will create and
launch the following containers on your host:

- Nginx
- ODS Application (uWSGI)
- MySQL
- Redis

There will also be two data volumes for persisting the MySQL database as well as
the file share directory located at ``/opt/odst/ods/static/share``. The file
share volume is shared between the ODS application and Nginx containers. In this
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
