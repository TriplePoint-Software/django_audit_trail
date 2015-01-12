import json

from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .formatter import AuditTrailFormatter


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
    user_ip = models.IPAddressField(blank=True)

    object_repr = models.CharField(max_length=200)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    action_time = models.DateTimeField(auto_now=True)
    # keeps serialized values for previous values
    json_values = models.TextField()

    class Meta:
        ordering = ('-action_time',)

    def get_formatted_values(self, formatter=AuditTrailFormatter):
        values = json.loads(self.json_values)
        return formatter.format(self.action_flag, values)

    def __repr__(self):
        return smart_unicode(self.action_time)
