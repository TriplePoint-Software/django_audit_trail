from django.db import models
from audit_trail import AuditTrailWatcher, audit_trail_watch


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


# Test shortcut
class ShortcutTestModel(models.Model):
    name = models.CharField(blank=True, max_length=255)

audit_trail_watch(ShortcutTestModel)


# Test shortcut related model duplicate
# audit_trail_watch(Post1) shouldn't override track_related
# audit_trail_watch(Comment1) should set track_only_with_related to True
class Post1(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    audit = AuditTrailWatcher(track_related=['comment1_set'])


class Comment1(models.Model):
    post = models.ForeignKey(Post1, null=True)
    text = models.CharField(blank=True, max_length=255)
    audit = AuditTrailWatcher(fields=['text'])


audit_trail_watch(Post1)
audit_trail_watch(Comment1)