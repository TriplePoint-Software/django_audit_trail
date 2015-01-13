from django.db import models
from audit_trail import AuditTrailWatcher


class TestModelTrackOneField(models.Model):
    char = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)

    audit = AuditTrailWatcher(fields=['char'])


class TestModelTrackAllFields(models.Model):
    char = models.CharField(max_length=255, null=True)
    char2 = models.CharField(max_length=255, null=True)

    audit = AuditTrailWatcher()


class TestModelWithFieldLabels(models.Model):
    char = models.CharField(max_length=255, null=True)
    char2 = models.CharField(max_length=255, null=True)

    FIELD_LABELS = {'char': 'Char Label', 'char2': 'Char Label 2'}
    audit = AuditTrailWatcher(field_labels=FIELD_LABELS)


class TestModelWithFieldsOrder(models.Model):
    a = models.IntegerField(null=True)
    char = models.CharField(max_length=255, null=True)
    char2 = models.CharField(max_length=255, null=True)

    audit = AuditTrailWatcher(order=['char2', 'char'])


class TestModelWithDateField(models.Model):
    date = models.DateField(null=True)

    audit = AuditTrailWatcher()