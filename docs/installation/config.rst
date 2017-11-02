Application Configuration
=========================

The ODS application has variable requirements depending upon the environment.

The application code is contained within the ``ods`` directory. When deploying
with a WSGI server you can use the ``application.py`` file and the
``application`` object within it for your WSGI congfiguration.

.. warning::

    The ODS APIs use token authentication and your production ODS
    instances should use TLS encryption for all traffic!

.. note::

    An example WSGI configuration file for deploying the ODS
    application with uWSGI can be found in ``/docker/webapp/web-app.ini``.

There are a number of options available for deploying the ODS application. See
`<http://flask.pocoo.org/docs/0.12/deploying/>`_ for more information.

In a single server installation (a standard, minimal install), the ODS is
capable of using a local SQLite database for server data. ODS also supports
connecting to a MySQL server. MySQL can be running locally on the same server as
the ODS application or remotely.

.. note::

    PostgreSQL and MSSQL support are planned for future support.

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

Database Configuration
----------------------

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
