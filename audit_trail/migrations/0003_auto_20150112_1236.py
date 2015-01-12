# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0002_auto_20150112_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audittrail',
            name='user_ip',
            field=models.IPAddressField(null=True),
            preserve_default=True,
        ),
    ]
