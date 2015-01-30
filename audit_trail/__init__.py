# pylint: disable-msg=E1101
from django.contrib.contenttypes.models import ContentType
from watcher import AuditTrailWatcher
from models import AuditTrail


def audit_trail_watch(cls, **kwargs):
    related_watcher = AuditTrailWatcher(**kwargs)
    if related_watcher.contribute_to_class(cls):
        related_watcher.init_signals()


def get_for_object(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return AuditTrail.objects.filter(content_type=content_type, object_id=obj.id)


default_app_config = 'audit_trail.app.AuditTrailAppConfig'

__all__ = ['audit_trail_watch', 'get_for_object', 'default_app_config']