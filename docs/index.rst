.. ODST documentation master file, created by
   sphinx-quickstart on Wed Nov  1 23:45:15 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Open Distribution Server Technologies
=====================================

The ODST project aims to deliver an open and automated file distribution
solution for IT administrators. The core application of this solution is the
Open Distribution Server (ODS).

.. warning::

   This project is currently in an Alpha state and is being actively developed
   and tested. See **Contributing to ODST** below to learn more about how you
   can help!

Features
--------

- Secure and Automatic Bi-Directional File Syncing
- Web Interface
- Admin API for Integrations
- File and Server Stage Taging
- Webhook and Email Notification Options
- Support for Jamf Pro
- And More...

The Open Distribution Server
----------------------------

The ODS is a Flask application and Celery worker that connect to a Redis server
(for worker queues), a database server (SQLite and MySQL currently supported
with MSSQL and PostgreSQL planned), and fronted by a web server (Nginx or
Apache).

While single-server installers are planned for Linux (Ubuntu/RHEL), Windows, and
macOS, the ODS application can be deployed in many different models, such as the
application and worker server connecting to remote Redis and database servers,
or running as a containerized server in Docker or Kubernetes.

.. note::

   See the :doc:`Docker documentation <../installation/docker>` to read more about using the included
   ``docker-compose.yml`` example to launch a development/test instance.

.. toctree::
   :caption: Admin Guide
   :maxdepth: 1

   admin/known_issues

.. toctree::
   :caption: Installation Guides
   :maxdepth: 1

   installation/config
   installation/docker

.. toctree::
   :caption: Developer Docs

Completed Features and Notes
----------------------------

- Admin Web UI Logins

    Default username: ``admin``

    Default password: ``ods1234!``

- Server Admin page (UI)

- Package Management (UI)

- ODS Network (UI)
    ODS registration is functional, instances can make API requests to each
    other, and one-way syncing is implemented.

- Admin API Endpoints
   - ``GET /api/admin/about``
      Returns application information.

   - ``GET /api/admin/system``
      Returns system information.

   - ``GET /api/admin/packages``
      Returns all files that have been uploaded.

   - ``POST /api/admin/packages``
      Upload a file to the server. The content-type must be
      ``multipart/form-data`` containing ``file`` and ``stage`` attributes.

Contributing to ODST
--------------------

The ODST project originated with the Mac Admins community. If you have not,
please join the `Mac Admins Slack <http://macadmins.org>`_ and join the
`#odst channel <https://macadmins.slack.com/messages/C7FRXLNQM>`_ to join the
conversation. Feedback and putting up feature requests for discussion are
entirely welcome and desired!

You can also contribute to the development of the ODST project in any of the
following ways:

- Build Testing
   Run the latest version as features are committed and test them. Submit
   issues, provide logs, and provide details on the application deployment.
   Testing and submitting issues will ensure quality!

- Optimal Configurations
   Administrators and developers experienced with Redis, Nginx, Apache, MySQL,
   or any of the other technologies that comprise the ODST stack, can help
   define the baseline configuration of these services for documentation and to
   be set as a part of the planned installers.

- Installers
   The ODS application can be custom setup for almost any kind of deployment,
   but an easy option where an administrator can run an installer on a single
   server is a goal for the project. If you have experience building installers
   on any platform please reach out!

- Documentation
   Read and scrutinize this documentation. Feel free to make a pull request to
   correct errors - spelling and grammatical - and incorrect information.