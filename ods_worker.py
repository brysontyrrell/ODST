from ods.factory import create_app
from ods.tasks import celery

app = create_app()
app.app_context().push()
