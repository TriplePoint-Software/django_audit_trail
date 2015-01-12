# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audittrail',
            name='json_values',
        ),
        migrations.AddField(
            model_name='audittrail',
            name='changes',
            field=jsonfield.fields.JSONField(default=dict),
            preserve_default=True,
        ),
    ]
