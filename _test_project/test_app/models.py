from django.db import models
from audit_trail import AuditTrailWatcher


class TestModelTrackOneField(models.Model):
    char = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)

    audit = AuditTrailWatcher(fields=['char'])


class TestModelTrackAllFields(models.Model):
    char = models.CharField(max_length=255, null=True)

    audit = AuditTrailWatcher()