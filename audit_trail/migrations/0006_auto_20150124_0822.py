# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0005_auto_20150114_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audittrail',
            name='changes',
            field=jsonfield.fields.JSONField(),
            preserve_default=True,
        ),
    ]
