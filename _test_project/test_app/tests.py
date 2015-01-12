from django.test import TestCase
from audit_trail.models import AuditTrail
from .models import TestModelTrackAllFields, TestModelTrackOneField


class TestSimple(TestCase):

    def test_create_audit_trail_on_creation(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.changes['char'], 'a')

    def test_create_audit_trail_on_deletion(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.delete()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.DELETED)

    def test_audit_for_selected_field(self):
        self.assertEqual(AuditTrail.objects.all().count(), 0)
        model = TestModelTrackOneField.objects.create(char='a')

        model.text = 'sometext'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)

    def test_audit_trail_history_for_all_fields(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)