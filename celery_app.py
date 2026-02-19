"""
Celery app setup for blood test analysis tasks
"""
import os
from celery import Celery

# Load environment variable or fallback
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery application
celery_app = Celery(
    "blood_test_analysis",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["worker_tasks"]
)

# Configure task handling
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,

    task_soft_time_limit=600,
    task_time_limit=7200,

    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,

    result_expires=9000,
)
