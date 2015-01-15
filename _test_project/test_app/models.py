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


# Test related tracking
class User(models.Model):
    name = models.CharField(blank=True, max_length=255)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    audit = AuditTrailWatcher(track_related=['comment_set', 'author'])


class Comment(models.Model):
    post = models.ForeignKey(Post, null=True)
    text = models.CharField(blank=True, max_length=255)


# Test related tracking with audit instance existing in related object
class AA(models.Model):
    audit = AuditTrailWatcher(track_related=['ab_set'])


class BB(models.Model):
    audit = AuditTrailWatcher(track_related=['ab_set'])


class AB(models.Model):
    aa = models.ForeignKey(AA)
    bb = models.ForeignKey(BB)
    audit = AuditTrailWatcher()
