import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from .models import AuditTrail
from .utils import get_request


class AuditTrailWatcher(object):
    tracked_models = set()
    tracked_fields = None

    def __init__(self, fields=None, **kwargs):
        self.tracked_fields = fields

        self.track_creation = kwargs.get('track_creation', True)
        self.track_update = kwargs.get('track_update', True)
        self.track_deletion = kwargs.get('track_deletion', True)

    def contribute_to_class(self, cls, name):
        if cls in self.__class__.tracked_models:
            return

        self.__class__.tracked_models.add(cls)

        # if self.fields is None:
        #     self.fields = [field.name for field in cls._meta.fields]

        signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        if self.track_creation:
            signals.post_save.connect(self.on_post_save_create, sender=sender, weak=False)

        if self.track_update:
            signals.post_init.connect(self.on_post_init, sender=sender, weak=False)
            signals.post_save.connect(self.on_post_save_update, sender=sender, weak=False)

        if self.track_deletion:
            signals.post_delete.connect(self.on_post_delete, sender=sender, weak=False)

    def serialize_object(self, instance):
        """ Returns stringified values for tracked fields. """
        data = {}
        for field in instance._meta.fields:

            # Skip untracked fields
            if self.tracked_fields is not None and field.name not in self.tracked_fields:
                continue

            data[field.name] = unicode(field.value_from_object(instance))
        return data

    def get_changes(self, instance):
        """ Returns list of changed fields."""
        diff = []
        original_data = instance._original_values
        for key, value in self.serialize_object(instance).iteritems():
            if original_data[key] != value:
                diff.append((key, original_data[key], value))
        return diff

    def on_post_init(self, instance, sender, **kwargs):
        """ Stores original field values. """
        instance._original_values = self.serialize_object(instance)

    def on_post_save_update(self, instance, sender, created, **kwargs):
        """ Checks for difference and saves, if it's present. """
        if created:
            return
        changes = self.get_changes(instance)
        if changes:
            audit_trail = AuditTrail.objects.generate_trail_for_instance_updated(instance)
            audit_trail.changes = changes
            audit_trail.save()

    def on_post_save_create(self, instance, sender, created, **kwargs):
        """ Saves object's data. """
        if not created:
            return
        audit_trail = AuditTrail.objects.generate_trail_for_instance_created(instance)
        audit_trail.changes = self.serialize_object(instance)
        audit_trail.save()

    def on_post_delete(self, instance, sender, **kwargs):
        """ Saves deleted data. """
        audit_trail = AuditTrail.objects.generate_trail_for_instance_deleted(instance)
        audit_trail.changes = [(key, value, value) for key, value in self.serialize_object(instance).iteritems()]
        audit_trail.save()