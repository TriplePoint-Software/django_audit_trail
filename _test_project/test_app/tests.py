from django.test import TestCase
from audit_trail.models import AuditTrail
from .models import TestModelTrackAllFields, TestModelTrackOneField


class TestSimple(TestCase):
    def test_create_audit_trail_on_creation(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.changes, [{
            'field': 'char',
            'old_value': '',
            'new_value': 'a'
        }])

    def test_create_audit_trail_on_deletion(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.delete()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.DELETED)
        self.assertEqual(trail.changes, [{
            'field': 'char',
            'old_value': 'a',
            'new_value': ''
        }])

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
        self.assertEqual(trail.changes, [{
            'field': 'char',
            'old_value': 'a',
            'new_value': 'b'
        }])

    def test_audit_trail_history_for_all_fields(self):
        model = TestModelTrackAllFields.objects.create(char='a', char2='x')
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.changes, [{
            'field': 'char',
            'old_value': 'a',
            'new_value': 'b'
        }])

        model.char2 = 'y'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 3)

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.changes, [{
            'field': 'char2',
            'old_value': 'x',
            'new_value': 'y'
        }])

        trail = AuditTrail.objects.all()[1]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.changes, [{
            'field': 'char',
            'old_value': 'a',
            'new_value': 'b'
        }])

        model.char = 'c'
        model.char2 = 'z'
        model.save()

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.changes, [{
            'field': 'char',
            'old_value': 'b',
            'new_value': 'c'
        }, {
            'field': 'char2',
            'old_value': 'y',
            'new_value': 'z'
        }])
