from django.db.models import signals
from .models import AuditTrail


class AuditTrailWatcher(object):
    tracked_models = set()
    tracked_fields = None
    excluded_fields = None
    model_class = None
    field_names = None
    order = None

    def __init__(self, fields=None, field_labels=None, order=None, **kwargs):
        self.tracked_fields = fields
        self.field_labels = field_labels
        self.order = order

        self.excluded_fields = ['id'] + kwargs.get('excluded_fields', [])

        self.track_creation = kwargs.get('track_creation', True)
        self.track_update = kwargs.get('track_update', True)
        self.track_deletion = kwargs.get('track_deletion', True)

    def contribute_to_class(self, cls, name):
        if cls in self.__class__.tracked_models:
            return

        self.model_class = cls

        self.__class__.tracked_models.add(cls)

        signals.class_prepared.connect(self.finalize, sender=cls)
        setattr(cls, name, self)

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
            not_tracked_field = (self.tracked_fields is not None and field.name not in self.tracked_fields)
            if not_tracked_field or field.name in self.excluded_fields:
                continue
            data[field.name] = field.value_from_object(instance)
        return data

    def get_changes(self, old_values, new_values):
        """ Returns list of changed fields."""
        diff = []
        old_values = old_values or {}
        new_values = new_values or {}

        tracked_fields = self.tracked_fields or [field.name for field in self.model_class._meta.fields]

        for field in tracked_fields:
            old_value = old_values.get(field, '')
            new_value = new_values.get(field, '')

            if old_value is None:
                old_value = ''

            if new_value is None:
                new_value = ''
            if old_value != new_value:
                diff.append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value
                })
        return diff

    def on_post_init(self, instance, sender, **kwargs):
        """ Stores original field values. """
        instance._original_values = self.serialize_object(instance)

    def on_post_save_create(self, instance, sender, created, **kwargs):
        """ Saves object's data. """
        if not created:
            return
        audit_trail = AuditTrail.objects.generate_trail_for_instance_created(instance)
        audit_trail.changes = self.get_changes({}, self.serialize_object(instance))
        audit_trail.save()
        instance._original_values = self.serialize_object(instance)

    def on_post_save_update(self, instance, sender, created, **kwargs):
        """ Checks for difference and saves, if it's present. """
        if created:
            return
        changes = self.get_changes(instance._original_values, self.serialize_object(instance))
        if changes:
            audit_trail = AuditTrail.objects.generate_trail_for_instance_updated(instance)
            audit_trail.changes = changes
            audit_trail.save()
        instance._original_values = self.serialize_object(instance)

    def on_post_delete(self, instance, sender, **kwargs):
        """ Saves deleted data. """
        audit_trail = AuditTrail.objects.generate_trail_for_instance_deleted(instance)
        audit_trail.changes = self.get_changes(self.serialize_object(instance), {})
        audit_trail.save()