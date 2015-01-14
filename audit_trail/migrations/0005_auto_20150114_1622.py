# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0004_auto_20150112_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='audittrail',
            name='related_trail',
            field=models.ForeignKey(to='audit_trail.AuditTrail', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Created'), (2, b'Updated'), (3, b'Deleted'), (4, b'Related changed')]),
            preserve_default=True,
        ),
    ]
