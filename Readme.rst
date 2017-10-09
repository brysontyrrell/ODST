Open Distribution Server (Tech)
===============================

The Open Distribution Server (ODS) is an in-progress web application to provide
a potential alternative package distribution server for IT administrators to the
existing Jamf Distribution Server (JDS).

The goal of the ODS project is to provide the base feature set of the JDS with
several additional technologies to better control and integrate distribution
servers into IT environments.

In addition to core tenant of simple and automatic package replication, the ODST
project is being written around the following design:

* Better cross-platform compatibility

    The ODS application is written to be de-coupled from the underlying OS
    and using cross-platform friendly technologies. While developed and testing
    primarily on Linux, the goal is for the ODS to also work on Windows and Mac
    systems as well. This de-coupling will also prevent issues arising where
    updates to platform prevent the application from working.

* Push notification framework

    ODS instances use webhooks and APIs to perform on-demand actions as events
    occur. File and data changes in one ODS instance are "pushed" to others
    resulting in faster propagation of changes across the ODS network as opposed
    to timed sync operations.

* Mesh network style syncing

    Instead of a parent-child relationship structure as used by the JDS, the ODS
    will adopt a many-to-many relationship model. One ODS may be registered to
    any number of other ODSs. When a package is uploaded to an ODS it will send
    a sync notification to each ODS it is registered to. Once they have finished
    syncing the package, each one of those recipients will repeat the process
    until the package has been synced throughout the network.

* Automation and scripting accessibility

    In addition to the private API used by ODS instances for automation, a full
    "admin" API will be made available to allow an ODS instance to be integrated
    into existing workflows (such as Autopkg). In addition to the admin API, a
    webhook framework will also be built to allow the ODS to directly notify
    other IT systems of events as they occur (some carried over from the ODS
    automation mentioned before).

* Web UI

    A user interface will be available for managing each ODS instance directly.
    Instead of being a separate interface from the admin API, the web UI will be
    built directly on top of the admin API providing 1:1 feature parity between
    the two forms of interaction.

Custom Installation
-------------------

The ODS application has variable requirements depending upon the environment.

The application code is contained within the ``ods`` directory. When deploying
with a WSGI server you can use the ``application.py`` file and the
``application`` object within it for your WSGI congfiguration.

    The ODS APIs use token authentication and your production ODS
    instances should use TLS encryption for all traffic!

    An example WSGI configuration file for deploying the ODS
    application with uWSGI can be found in ``/docker/webapp/web-app.ini``.

There are a number of options available for deploying the ODS application. See
`<http://flask.pocoo.org/docs/0.12/deploying/>`_ for more information.

In a single server installation (a standard, minimal install), the ODS is
capable of using a local SQLite database for server data. ODS also supports
connecting to a MySQL server. MySQL can be running locally on the same server as
the ODS application or remotely.

    PostgreSQL and MSSQL support are planned future enhancements.

The ODS uses Redis for queuing tasks and Celery for processing those tasks.
Redis can be running locally on the same server as the ODS application or
remotely.

To start the Celery worker run the following command from the application
directory:

.. code-block:: bash

    celery worker --app ods_worker.celery --workdir /path/to/ODS-dir/

Environment Variables
---------------------

The ODS application will read environment variables from the system to configure
itself at runtime.

========================= ==================================================
Required Env Vars         Description
========================= ==================================================
``ODS_CONF``              The path to a configuration file written in Python
                          that contains any of the described environment
                          variables listed here. It is recommended that your
                          ``SECRET_KEY`` and ``DATABASE_KEY`` be populated using
                          this file.

``SECRET_KEY``            A cryptographically random key used to secure user
                          sessions.

``DATABASE_KEY``          A cryptographically random 32-byte key used to encrypt
                          sensitive data within the ODS database.

``CELERY_BROKER_URL``     The URL to the Redis server. If not provided the value
                          will default to ``redis://localhost:6379``.

``CELERY_BACKEND_URL``    *(optional)* An alternative URL to the Redis backend.
                          If not provided it will default to the value of
                          ``CELERY_BROKER_URL``.

``UPLOAD_STAGING_DIR``    *(optional)* You may specify the staging directory
                          where file uploads are cached. If not provided, a
                          randomized temp directory will be created.

``DEBUG``                 *(optional)* Runs the server in ``Debug`` mode
                          providing additional logging output.
========================= ==================================================

    The following code will generate a randomized 32-byte key::

        >> import os
        >>> os.urandom(32)

By default, the ODS will create a local SQLite database located within the
application's directory on the system. To use a database server, set the
appropriate environment variables as shown below.

========================= ==================================================
MySQL Server Configuration
============================================================================
``MYSQL_SERVER``          The URL to the MySQL server (with port).

``MYSQL_DATABASE``        The name of the MySQL database to connect to.

``MYSQL_USER``            The user to authenticate to the database.

``MYSQL_PASSWORD``        The password to the user.
========================= ==================================================

Docker Compose
--------------

    This option as provided is primarily meant to serve as a development
    and testing solution, but it can be adapted to fit a production environment.

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
    docker-computer up -d

Navigate to the IP address of your Docker host in a web browser to begin using
the ODS web UI.

Web UI Screenshots
------------------

Here are a collection of images showing the in-progress web UI for admins.

.. image:: images/ods_login.png
   :width: 350px

.. image:: images/ods_admin.png
   :width: 350px

.. image:: images/ods_packages.png
   :width: 350px

.. image:: images/ods_network.png
   :width: 350px

Completed Features
------------------

* Admin web login

    Default username: ``admin``

    Default password: ``ods1234!``

* Admin web UI

    The web UI page for server administration currently shows ODS settings via
    ``/api/admin/about`` and system information via ``/api/admin/system``.

* Package web UI

    Package data is available via ``/api/admin/packages``.

* Package uploads via ``/api/admin/upload``

    This is also implemented in the package UI.

* ODS network UI

    ODS registration is functional, and instances can make API requests to each
    other, but syncing is not yet implemented.

Known Issues
------------
