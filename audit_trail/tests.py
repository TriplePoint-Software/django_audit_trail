"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.db import models

from audit_trail.models import audit_trail
from mock import Mock
from audit_trail.trail import AuditTrailWatcher


class TestModel(models.Model):
    name  = models.TextField()
    title = models.TextField()
    year  = models.IntegerField()

    audit_trail(name, year)


class AuditTrailTest(TestCase):
    def test_creation_with_audit(self):
        m = TestModel()
        m.save = Mock()
        AuditTrailWatcher.save = Mock()
        self.assertEqual(1 + 1, 2)

    def test_double_save_audit(self):
        pass
        #m = TestModel()
        #m.save()
        #m.save()
        #log should contain 2 records

