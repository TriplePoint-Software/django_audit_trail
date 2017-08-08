from django.contrib.postgres.fields import ArrayField
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

        if isinstance(field, ArrayField):
            return force_text(', '.join(value))

        if getattr(field, 'choices', None):
            try:
                choices_dict = dict(field.choices)
                value = choices_dict[value]
                return force_text(value)
            except KeyError:
                return force_text(value)

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

        # iterate over to fields trying to look up the fk
        if not isinstance(value, field.related_model):
            success = False
            to_fields = field.to_fields or []
            if 'pk' not in to_fields:
                to_fields.append('pk')

            for to_field in to_fields:
                try:
                    value = field.related_model.objects.get(**{to_field: value})
                    success = True
                    break
                except ObjectDoesNotExist:
                    pass
            if not success:
                return None

        return force_text(value)

    @classmethod
    def add_stringifier(cls, field_class, callback):
        cls.custom_stringify_methods[field_class] = callback
