# pylint: disable=E1101
from django.contrib.contenttypes.models import ContentType

from .stringifier import ModelFieldStringifier
from .watcher import AuditTrailWatcher
from .models import AuditTrail


def audit_trail_watch(cls, **kwargs):
    related_watcher = AuditTrailWatcher(**kwargs)
    if related_watcher.contribute_to_class(cls):
        related_watcher.init_signals()


def get_for_object(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return AuditTrail.objects.filter(content_type=content_type, object_id=obj.id)


def audit_trail_register_field_stringifier(field_class, callback):
    ModelFieldStringifier.add_stringifier(field_class, callback)

# C0103 / Invalid constant name "default_app_config"
# pylint: disable=C0103
default_app_config = 'audit_trail.app.AuditTrailAppConfig'

__all__ = ('audit_trail_watch', 'get_for_object', 'default_app_config', 'audit_trail_register_field_stringifier')