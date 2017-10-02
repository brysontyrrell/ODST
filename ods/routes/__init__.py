"""
/
    Web admin

/api/ods/packages
/api/admin/packages
    Get all packages

/api/ods/packages/<id_or_name>
/api/admin/packages/<id_or_name>
    Get a package by name or database ID.

/api/ods/command
    Receive a notification/command relating to a new or existing package.

/api/ods/register
    Allows other JDS instances to register with this JDS

/login
    Web admin login redirect

/upload
    Upload files
    curl -X POST http://localhost:5000/upload -F file=@/path/to

"""
