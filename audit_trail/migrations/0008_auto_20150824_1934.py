# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('audit_trail', '0007_auto_20150422_0548'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='audittrail',
            options={'ordering': ('-id',), 'verbose_name': 'audit trail', 'verbose_name_plural': 'audit trails'},
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='action',
            field=models.PositiveSmallIntegerField(verbose_name='action', choices=[(1, 'Created'), (2, 'Updated'), (3, 'Deleted'), (4, 'Related changed')]),
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='action_time',
            field=models.DateTimeField(auto_now=True, verbose_name='date and time'),
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='content_type',
            field=models.ForeignKey(verbose_name='content type', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='object_repr',
            field=models.CharField(max_length=200, verbose_name='object repr'),
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='user',
            field=models.ForeignKey(verbose_name='user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='user_ip',
            field=models.GenericIPAddressField(null=True, verbose_name='IP address'),
        ),
    ]
