import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from .models import AuditTrail
from .utils import get_request

__author__ = 'syabro'


class AuditTrailWatcher(object):
    """ A class which adds trailing changes in models.

    Usage:

    class MyModel(models.Model):
        field1, field2, field3 = models.IntegerField(), models.IntegerField(), models.IntegerField()
        field4, field5         = models.TextField(), models.TextField()
        audit = audit_trail(field2, field5)  # only field2 and field5 are tracked
        OR
        audit = audit_trail('field2', 'field5') # specify field names in string
        OR
        audit = audit_trail(field2, field5, track_creation=False, track_deletion=False) # tracks only update
    """
    tracked_models = set()
    fields = None

    def __init__(self, fields=None, **kwargs):
        self.fields = fields

        self.track_creation = kwargs.get('track_creation', True)
        self.track_update = kwargs.get('track_update', True)
        self.track_deletion = kwargs.get('track_deletion', True)

    def contribute_to_class(self, cls, name):
        if cls in self.__class__.tracked_models:
            return
        self.__class__.tracked_models.add(cls)

        if self.fields is None:
            self.fields = [field.name for field in cls._meta.fields]

        signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        if self.track_creation or self.track_update:
            signals.post_init.connect(self.on_post_init, sender=sender, weak=False)
            signals.post_save.connect(self.on_post_save, sender=sender, weak=False)
        if self.track_deletion:
            signals.post_delete.connect(self.on_post_delete, sender=sender, weak=False)

    def get_raw_values(self, instance):
        """ Returns stringified values for tracked fields. """
        data = {}
        for field in instance._meta.fields:
            if field.name in self.fields:
                data[field.name] = unicode(field.value_from_object(instance))
        return data

    def get_diff(self, instance):
        """ Returns list of changed fields."""
        diff = []
        original_data = instance._original_values
        for key, value in self.get_raw_values(instance).iteritems():
            if original_data[key] != value:
                diff.append((key, original_data[key], value))
        return diff

    def on_post_init(self, instance, sender, **kwargs):
        """ Stores original field values. """
        instance._original_values = self.get_raw_values(instance)

    def on_post_save(self, instance, sender, created, **kwargs):
        """ Checks for difference and saves, if it's present. """
        if created:
            action_flag = AuditTrail.ACTIONS.CREATED
        else:
            action_flag = AuditTrail.ACTIONS.UPDATED

        # if self.should_process_action(action_flag, created):
        diff = self.get_diff(instance)
        if diff:
            audit_log = self._create_auditlog_object(instance, action_flag)
            audit_log.json_values = json.dumps(diff)
            audit_log.save()

    def on_post_delete(self, instance, sender, **kwargs):
        """ Saves deleted data to audit. """
        data = [(key, value, value) for key, value in self.get_raw_values(instance).iteritems()]
        audit_log = self._create_auditlog_object(instance, AuditTrail.ACTIONS.DELETED)
        audit_log.json_values = json.dumps(data)
        audit_log.save()

    def _create_auditlog_object(self, instance, action):
        """ Creates AuditTrail object and sets user id and ip from request. """
        audit_log = AuditTrail(
            user_ip='',
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            object_repr=unicode(instance),
            action=action
        )
        request = get_request(['user', 'META'])
        if request:
            if request.user.is_authenticated():
                audit_log.user = request.user
            audit_log.user_ip = request.META.get('HTTP_X_FORWARDED_FOR', None) or request.META.get('REMOTE_ADDR')
        return audit_log