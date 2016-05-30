import datetime
from django.test import TestCase
from django.utils import formats
from audit_trail.stringifier import ModelFieldStringifier
from ..models import TestStringifierModel, SomePerson, AzazaField
from audit_trail.models import AuditTrail


class TestModelDefaultFieldStringifier(TestCase):
    def get_field(self, field_name):
        return TestStringifierModel._meta.get_field(field_name)

    def test_char_field(self):
        tsm = TestStringifierModel(char='abc')
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('char'), tsm.char), 'abc')

    def test_integer_field(self):
        tsm = TestStringifierModel(integer=123)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('integer'), tsm.integer), '123')

    def test_integer_field_negative(self):
        tsm = TestStringifierModel(integer=-123)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('integer'), tsm.integer), '-123')

    def test_datetime_field(self):
        now = datetime.datetime.now()
        tsm = TestStringifierModel(datetime=now)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('datetime'), tsm.datetime),
                         formats.date_format(now, "DATETIME_FORMAT"))

    def test_datetime_field_null(self):
        tsm = TestStringifierModel.objects.create()
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('datetime'), tsm.datetime), None)

    def test_date_field(self):
        today = datetime.date.today()
        tsm = TestStringifierModel(date=today)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('date'), tsm.date),
                         formats.date_format(today, "DATE_FORMAT"))

    def test_fk_field(self):
        person = SomePerson.objects.create()
        AuditTrail.objects.all().delete()
        tsm = TestStringifierModel(fk=person)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('fk'), tsm.fk), unicode(person))

    def test_fk_field_update(self):
        person = SomePerson.objects.create()
        AuditTrail.objects.all().delete()
        tsm = TestStringifierModel(fk=person)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('fk'), tsm.fk_id), unicode(person))

    def test_boolean_field(self):
        tsm = TestStringifierModel(boolean=True)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('boolean'), tsm.boolean), 'True')
        tsm = TestStringifierModel(boolean=False)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('boolean'), tsm.boolean), 'False')

    def test_float_field(self):
        tsm = TestStringifierModel(float=3.14)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('float'), tsm.float), '3.14')

    def test_choices(self):
        tsm = TestStringifierModel(choice=0)
        self.assertEqual(ModelFieldStringifier.stringify(self.get_field('choice'), tsm.choice),
                         tsm.get_choice_display())


def stringify_azaza_field(value, *args):
    return u'Azaza %s' % unicode(value)


class TestExtendModelDefaultFieldStringifier(TestCase):
    def test_add_custom_stringifier(self):
        self.assertNotIn(AzazaField, ModelFieldStringifier.custom_stringify_methods)
        ModelFieldStringifier.add_stringifier(AzazaField, stringify_azaza_field)
        self.assertEqual(ModelFieldStringifier.custom_stringify_methods[AzazaField], stringify_azaza_field)

    def test_custom_stringifier(self):
        ModelFieldStringifier.add_stringifier(AzazaField, stringify_azaza_field)
        tsm = TestStringifierModel(azaza='ololo')
        field = TestStringifierModel._meta.get_field('azaza')
        self.assertEqual(ModelFieldStringifier.stringify(field, tsm.azaza), stringify_azaza_field(tsm.azaza))
