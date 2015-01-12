from audit_trail.utils import get_request
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
import json


class audit_trail(object):
    """ A class which adds trailing changes in models.

    Usage:

    class MyModel(models.Model):
        field1, field2, field3 = models.IntegerField(), models.IntegerField(), models.IntegerField()
        field4, field5         = models.TextField(), models.TextField()
        audit = audit_trail(field2, field5)  # only field2 and field5 are tracked
        OR
        audit = audit_trail('field2', 'field5') # specify field names in string
        OR
        audit = audit_trail(field2, field5, audit_action_create=False, audit_action_delete=False) # tracks only update
    """
    tracked_models = set()

    def __init__(self, *fields, **kwargs):
        self.mdl_fields = filter(lambda x: not isinstance(x, str), fields)
        self.str_fields = filter(lambda x:     isinstance(x, str), fields)
        self.audit_action_create = kwargs.get('audit_action_create', True)
        self.audit_action_update = kwargs.get('audit_action_update', True)
        self.audit_action_delete = kwargs.get('audit_action_delete', True)

    def contribute_to_class(self, cls, name):
        if cls not in self.__class__.tracked_models:
            self.__class__.tracked_models.add(cls)

        self.name = name
        self.original_field = '%s_original' % (self.name,)
        signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        if self.audit_action_create or self.audit_action_update:
            signals.post_init.connect(self.on_post_init, sender=sender, weak=False)
            signals.post_save.connect(self.on_post_save, sender=sender, weak=False)
        if self.audit_action_delete:
            signals.post_delete.connect(self.on_post_delete, sender=sender, weak=False)

    def get_raw_values(self, instance):
        """ Returns stringified values for tracked fields. """
        data = {}
        for field in instance._meta.fields:
            if field in self.mdl_fields or field.name in self.str_fields:
                data[field.name] = unicode(field.value_from_object(instance))
        return data

    def should_process_action(self, action_flag, created):
        """ Checks if action should be processed based on initial configuration."""
        return action_flag == AuditTrail.TYPE_CREATED and created or \
           action_flag == AuditTrail.TYPE_UPDATED and not created

    def get_diff(self, instance):
        """ Returns diff between loaded data and save after change for tracked fields."""
        diff = []
        original_data = getattr(instance, self.original_field)
        for key, value in self.get_raw_values(instance).iteritems():
            if original_data[key] != value:
                 diff.append((key, original_data[key], value))
        return diff

    def on_post_init(self, instance, sender, **kwargs):
        """ Stores original field values. """
        setattr(instance, self.original_field, self.get_raw_values(instance))

    def on_post_save(self, instance, sender, created, **kwargs):
        """ Checks for difference and saves, if it's present. """
        action_flag = AuditTrail.TYPE_CREATED if created else AuditTrail.TYPE_UPDATED
        if self.should_process_action(action_flag, created):
            diff = self.get_diff(instance)
            if diff:
                audit_log = self._create_auditlog_object(instance, action_flag)
                audit_log.json_values = json.dumps(diff)
                audit_log.save()

    def on_post_delete(self, instance, sender, **kwargs):
        """ Saves deleted data to audit. """
        data = [(key, value, value) for key, value in self.get_raw_values(instance).iteritems()]
        audit_log = self._create_auditlog_object(instance, AuditTrail.TYPE_DELETED)
        audit_log.json_values = json.dumps(data)
        audit_log.save()

    def _create_auditlog_object(self, instance, action_flag):
        """ Creates AuditTrail object and sets user id and ip from request. """
        audit_log = AuditTrail(user_ip='',
                               content_type=ContentType.objects.get_for_model(instance),
                               object_id=instance.id,
                               object_repr=unicode(instance),
                               action_flag=action_flag)
        request = get_request(['user', 'META'])
        if request:
            if request.user.is_authenticated():
                audit_log.user = request.user
            audit_log.user_ip = request.META.get('HTTP_X_FORWARDED_FOR', None) \
                                or request.META.get('REMOTE_ADDR')
        return audit_log


class AuditTrailFormatter(object):
    @classmethod
    def format(cls, action_flag, data):
        method = 'format_' + {AuditTrail.TYPE_CREATED: 'created',
                              AuditTrail.TYPE_UPDATED: 'updated',
                              AuditTrail.TYPE_DELETED: 'deleted'}[action_flag]
        return getattr(cls, method)(data)

    @classmethod
    def format_created(cls, data):
        result = []
        for item in data:
            result.append('<b>"%s"</b>=<b>"%s"</b>' % (item[0], item[2]))
        return 'created with %s' % (', '.join(result))

    @classmethod
    def format_updated(cls, data):
        result = []
        for item in data:
            result.append('<b>"%s"</b> changed from <b>"%s"</b> to <b>"%s"</b>' % tuple(item))
        return '<br />'.join(result)

    @classmethod
    def format_deleted(cls, data):
        result = []
        for item in data:
            result.append('<b>"%s"</b>=<b>"%s"</b>' % (item[0], item[2]))
        return 'deleted where %s' % (', '.join(result))


class AuditTrail(models.Model):
    TYPE_CREATED = 1
    TYPE_UPDATED = 2
    TYPE_DELETED = 3

    TYPES = (
        (TYPE_CREATED, 'Created'),
        (TYPE_UPDATED, 'Updated'),
        (TYPE_DELETED, 'Deleted')
    )

    """ Table to store all changes of subscribed models. """
    action_time  = models.DateTimeField(auto_now=True)
    user         = models.ForeignKey(User, blank=True, null=True)
    user_ip      = models.CharField(max_length=100, blank=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id    = models.TextField(blank=True, null=True)
    object_repr  = models.CharField(max_length=200)
    action_flag  = models.PositiveSmallIntegerField(choices=TYPES)
    # keeps serialized values for previous values
    json_values  = models.TextField()

    class Meta:
        ordering = ('-action_time',)

    def get_formatted_values(self, formatter=AuditTrailFormatter):
        values = json.loads(self.json_values)
        return formatter.format(self.action_flag, values)

    def __repr__(self):
        return smart_unicode(self.action_time)
