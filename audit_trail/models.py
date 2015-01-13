from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import DateField
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jsonfield import JSONField

from utils import get_request


class AuditTrailManager(models.Manager):
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


class AuditTrail(models.Model):

    class ACTIONS:
        CREATED = 1
        UPDATED = 2
        DELETED = 3

    ACTION_CHOICES = (
        (ACTIONS.CREATED, 'Created'),
        (ACTIONS.UPDATED, 'Updated'),
        (ACTIONS.DELETED, 'Deleted')
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
    changes = JSONField()

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

    def get_changes(self):
        model_class = self.content_type.model_class()
        audit_watcher = model_class.audit
        changes = [change.copy() for change in self.changes]
        if audit_watcher.field_labels is not None:
            for change in changes:
                change['field_label'] = audit_watcher.field_labels.get(change['field'], '')

        if audit_watcher.order:
            def sort_key(change):
                try:
                    return audit_watcher.order.index(change['field'])
                except ValueError:
                    return '%d%s' % (len(audit_watcher.order), change['field'])
            changes = sorted(changes, key=sort_key)

        return changes