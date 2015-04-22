# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0006_auto_20150124_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audittrail',
            name='user_ip',
            field=models.GenericIPAddressField(null=True),
        ),
    ]
