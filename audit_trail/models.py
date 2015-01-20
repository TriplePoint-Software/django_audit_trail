from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.module_loading import import_string

from jsonfield import JSONField

from utils import get_request


encoder_class = DjangoJSONEncoder
if hasattr(settings, 'JSONFIELD_ENCODER'):
    encoder_class = import_string(getattr(settings, 'JSONFIELD_ENCODER'))

dump_kwargs = {
    'cls': encoder_class,
    'separators': (',', ':')
}


class AuditTrailQuerySet(models.QuerySet):
    def get_changes(self):
        changes = []
        changes_dict = {}
        if not self.exists():
            return changes

        model_class = self[0].content_type.model_class()

        for trail in self.order_by('id'):
            if not isinstance(trail.content_object, model_class):
                raise ValueError(
                    'AuditTrailQuerySet.get_changes couldn\'t get changes for different models: %s and %s' % (
                        model_class.__name__, trail.content_object.__class__.__name__
                    ))
            for field_change in trail.get_changes():
                field = field_change['field']
                if not field in changes_dict:
                    changes_dict[field] = field_change
                    continue
                changes_dict[field]['new_value'] = field_change['new_value']
        changes = changes_dict.values()

        audit_watcher = model_class.audit
        if audit_watcher.order:
            def sort_key(change):
                try:  # Trying to order by `order`
                    return audit_watcher.order.index(change['field'])
                except ValueError:  # if field isn't in order put it after ordered fields and order by name
                    return '%d%s' % (len(audit_watcher.order), change['field'])

            changes = sorted(changes, key=sort_key)

        return changes


class AuditTrailManager(models.Manager):
    def get_queryset(self):
        return AuditTrailQuerySet(self.model, using=self._db)

    def generate_for_instance(self, instance, action):
        audit_trail = self.model(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            object_repr=unicode(instance),
            action=action
        )

        request = get_request(['user', 'META'])
        if request:
            if request.user.is_authenticated():
                audit_trail.user = request.user
            audit_trail.user_ip = request.META.get('HTTP_X_FORWARDED_FOR', None) or request.META.get('REMOTE_ADDR')
        audit_trail.save()
        return audit_trail

    def generate_trail_for_instance_created(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.CREATED)

    def generate_trail_for_instance_updated(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.UPDATED)

    def generate_trail_for_instance_deleted(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.DELETED)

    def generate_trail_for_related_change(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.RELATED_CHANGED)


class AuditTrail(models.Model):
    class ACTIONS:
        CREATED = 1
        UPDATED = 2
        DELETED = 3
        RELATED_CHANGED = 4

    ACTION_CHOICES = (
        (ACTIONS.CREATED, 'Created'),
        (ACTIONS.UPDATED, 'Updated'),
        (ACTIONS.DELETED, 'Deleted'),
        (ACTIONS.RELATED_CHANGED, 'Related changed')
    )

    """ Table to store all changes of subscribed models. """
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.TextField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, blank=True, null=True)
    user_ip = models.IPAddressField(null=True)

    object_repr = models.CharField(max_length=200)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    action_time = models.DateTimeField(auto_now=True)
    changes = JSONField(dump_kwargs=dump_kwargs)

    related_trail = models.ForeignKey(to='self', null=True)

    objects = AuditTrailManager()

    class Meta:
        ordering = ('-id',)

    def __repr__(self):
        return smart_unicode(self.action_time)

    @property
    def is_created(self):
        return self.action == self.ACTIONS.CREATED

    @property
    def is_updated(self):
        return self.action == self.ACTIONS.UPDATED

    @property
    def is_deleted(self):
        return self.action == self.ACTIONS.DELETED

    @property
    def is_related_changed(self):
        return self.action == self.ACTIONS.RELATED_CHANGED

    def get_changes(self):
        model_class = self.content_type.model_class()
        audit_watcher = model_class.audit
        changes = [change.copy() for change in self.changes]
        if audit_watcher.field_labels is not None:
            for change in changes:
                change['field_label'] = audit_watcher.field_labels.get(change['field'], '')

        if audit_watcher.order:
            def sort_key(change):
                try:  # Trying to order by `order`
                    return audit_watcher.order.index(change['field'])
                except ValueError:  # if field isn't in order put it after ordered fields and order by name
                    return '%d%s' % (len(audit_watcher.order), change['field'])

            changes = sorted(changes, key=sort_key)

        return changes