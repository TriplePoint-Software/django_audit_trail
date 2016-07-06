from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import IntegerField
from django.utils import formats
from django.utils.encoding import force_text
from django.utils import six


class ModelFieldStringifier(object):

    custom_stringify_methods = {
        models.DateTimeField: 'stringify_datetime',
        models.DateField: 'stringify_date',
        models.ForeignKey: 'stringify_fk'
    }

    @classmethod
    def stringify(cls, field, value=None):
        value = value
        field_class = field.__class__

        if field_class in cls.custom_stringify_methods:
            stringifier = cls.custom_stringify_methods[field_class]

            if isinstance(stringifier, six.string_types):
                stringifier = getattr(cls, stringifier)

            return stringifier(value, field)

        if value is None:
            return None

        if isinstance(field, IntegerField):
            value = int(value)

        if getattr(field, 'choices', None):
            try:
                choices_dict = dict(field.choices)
                value = choices_dict[value]
                return force_text(value)
            except KeyError:
                return force_text(value)
            except Exception:
                raise

        return force_text(value)

    @staticmethod
    def stringify_datetime(value, *args):
        if value is None:
            return None

        # Like models.DateField(default=date.today)
        if hasattr(value, '__call__'):
            value = value()

        return formats.date_format(value, "DATETIME_FORMAT")

    @staticmethod
    def stringify_date(value, *args):
        if value is None:
            return None

        # Like models.DateField(default=date.today)
        if hasattr(value, '__call__'):
            value = value()

        return formats.date_format(value, "DATE_FORMAT")

    @staticmethod
    def stringify_fk(value, field):
        if value is None:
            return None

        # if it's not model instance we assume it's an id
        if not isinstance(value, field.related_model):
            try:
                value = field.related_model.objects.get(pk=value)
            except ObjectDoesNotExist:
                return None

        return force_text(value)

    @classmethod
    def add_stringifier(cls, field_class, callback):
        cls.custom_stringify_methods[field_class] = callback
