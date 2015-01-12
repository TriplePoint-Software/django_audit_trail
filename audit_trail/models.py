from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jsonfield import JSONField

from .formatter import AuditTrailFormatter
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

    user = models.ForeignKey(User, blank=True, null=True)
    user_ip = models.IPAddressField(null=True)

    object_repr = models.CharField(max_length=200)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    action_time = models.DateTimeField(auto_now=True)
    # keeps serialized values for previous values
    changes = JSONField()

    objects = AuditTrailManager()

    class Meta:
        ordering = ('-id',)

    def get_formatted_changes(self, formatter=AuditTrailFormatter):
        return formatter.format(self.action_flag, self.changes)

    def __repr__(self):
        return smart_unicode(self.action_time)
