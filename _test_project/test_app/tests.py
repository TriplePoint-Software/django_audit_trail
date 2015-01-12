from django.test import TestCase
from audit_trail.models import AuditTrail
from .models import TestModelTrackAllFields, TestModelTrackOneField


class TestSimple(TestCase):

    def test_audit_for_selected_field(self):
        self.assertEqual(AuditTrail.objects.all().count(), 0)
        model = TestModelTrackOneField.objects.create(char='a')

        model.text = 'sometext'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 0)

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 1)

    def test_audit_trail_history_for_all_fields(self):
        model = TestModelTrackAllFields.objects.create(char='a')

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 1)