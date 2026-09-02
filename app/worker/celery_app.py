from celery import Celery

from app.config import settings


celery_app = Celery(
    "rag_pipeline",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)

# Import tasks so Celery registers them
celery_app.autodiscover_tasks(
    ["app.worker"],
    related_name="tasks",
)