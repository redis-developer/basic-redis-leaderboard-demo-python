import json

from django.apps import AppConfig
from django.conf import settings

from .companies_redis import RedisClient


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        RedisClient().set_init_data()
