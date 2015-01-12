# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0003_auto_20150112_1236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='audittrail',
            options={'ordering': ('-id',)},
        ),
    ]
