# myapp/apps.py
from django.apps import AppConfig
from signals import audit_trail_app_ready


class AuditTrailAppConfig(AppConfig):

    name = 'audit_trail'
    verbose_name = 'Audit Trail'

    def ready(self):
        audit_trail_app_ready.send(sender=self.__class__)