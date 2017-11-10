Known Issues
============

.. note::

    The ODST Project is currently in an Alpha state. Known issues as they are
    reported by users and admins testing the iterative builds that won't be
    immediately addressed will be recorded here with links to the GitHub issue
    and information on what is planned to address them.

File Syncing
------------

- There is likely an issue with the concurrent connections to the database
  causing the ORM to throw `InternalError` and `InterfaceError` exceptions as
  it attempts to handle multiple simultaneous requests and tasks. File sync
  operations currently are not performing adequate error handling to prevent
  the data from entering an invalid state in the event an error occurs, nor
  are there any mechanisms in place to initiate an automatic retry. Those
  items, as well as vastly improved logging, will be implemented to begin
  addressing these issues. (discovered during testing)

- It has been reported that upload operations can consume up to 3x the disk
  space of the uploaded file until complete. (reported in Slack #odst)
