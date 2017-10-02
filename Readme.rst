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
    and number of other ODSs. When a package is uploaded to an ODS it will send
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
