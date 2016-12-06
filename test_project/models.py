from django.contrib.postgres.fields import ArrayField
from django.db import models
from audit_trail import audit_trail_watch
from audit_trail.watcher import AuditTrailWatcher


class TestModelTrackOneField(models.Model):
    char = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)

    audit = AuditTrailWatcher(fields=['char'])


class TestModelTrackAllFields(models.Model):
    char = models.CharField(max_length=255, null=True)
    char2 = models.CharField(max_length=255, null=True)

    audit = AuditTrailWatcher()


class TestModelWithFieldLabels(models.Model):
    char = models.CharField(verbose_name='Char 1', max_length=255, null=True)
    char2 = models.CharField(verbose_name='Char 2', max_length=255, null=True)
    char_3 = models.CharField(max_length=255, null=True)

    audit = AuditTrailWatcher()


# Test related tracking
class User(models.Model):
    name = models.CharField(blank=True, max_length=255)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    audit = AuditTrailWatcher(track_related=['comment_set', 'author'])


class Comment(models.Model):
    post = models.ForeignKey(Post, null=True)
    text = models.CharField(blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    audit = AuditTrailWatcher(fields=['text'], track_only_with_related=True)

    def __unicode__(self):
        return 'Comment %d' % self.id


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


# Test FK object changing
class Animal(models.Model):
    name = models.CharField(max_length=12)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    pet = models.ForeignKey(Animal, null=True)

    audit = AuditTrailWatcher()


# Test Values with changes
class SomePerson(models.Model):
    name = models.CharField(default="", max_length=16)
    season = models.IntegerField(default=0, choices=((0, 'Winter'), (1, 'Spring'), (2, 'Summer'), (3, 'Autumn')))

    def __unicode__(self):
        return self.name

    audit = AuditTrailWatcher()


# Test stringifier

class AzazaField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        super(AzazaField, self).__init__(*args, **kwargs)


class TestStringifierModel(models.Model):
    char = models.CharField(max_length=255, null=True)
    integer = models.IntegerField(null=True)
    datetime = models.DateTimeField(null=True)
    date = models.DateField(null=True)
    fk = models.ForeignKey(SomePerson, null=True)
    boolean = models.BooleanField(null=True)
    float = models.FloatField(null=True)
    choice = models.PositiveIntegerField(null=True, choices=((0, 'Good choice'),))
    azaza = AzazaField(null=True)

    ARRAY_CHOICES = ['alfa', 'beta', 'charlie']
    array = ArrayField(models.CharField(max_length=16), default=[], blank=True, choices=ARRAY_CHOICES)

    audit = AuditTrailWatcher()

