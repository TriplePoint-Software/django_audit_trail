from django.db import models
from django.utils import formats


class ModelFieldStringifier(object):

    custom_stringify_methods = {
        models.DateTimeField: 'stringify_datetime',
        models.DateField: 'stringify_date',
    }

    @classmethod
    def stringify(cls, instance, field_name):
        value = getattr(instance, field_name)
        field_instance = instance.__class__._meta.get_field(field_name)
        field_class = field_instance.__class__

        if field_class in cls.custom_stringify_methods:
            stringifier = cls.custom_stringify_methods[field_class]

            if isinstance(stringifier, basestring):
                stringifier = getattr(cls, stringifier)

            return stringifier(value)

        if value is None:
            return None

        if field_instance.choices:
            return unicode(getattr(instance, 'get_%s_display' % field_name)())

        return unicode(value)

    @staticmethod
    def stringify_datetime(value):
        return formats.date_format(value, "DATETIME_FORMAT")

    @staticmethod
    def stringify_date(value):
        return formats.date_format(value, "DATE_FORMAT")

    @classmethod
    def add_stringifier(cls, field_class, callback):
        cls.custom_stringify_methods[field_class] = callback

