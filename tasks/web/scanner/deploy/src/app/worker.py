import os

from celery import current_app as current_celery_app
from app.config import get_config


def create_celery():
    celery = current_celery_app
    celery_url = get_config().redis_celery_url
    celery.conf.broker_url = celery_url
    celery.conf.result_backend = celery_url
    return celery
