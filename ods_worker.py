from ods.factory import create_app
from ods.tasks import celery

app = create_app(is_worker=True)
app.app_context().push()
