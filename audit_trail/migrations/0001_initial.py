# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditTrail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.TextField(null=True, blank=True)),
                ('user_ip', models.IPAddressField(blank=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, b'Created'), (2, b'Updated'), (3, b'Deleted')])),
                ('action_time', models.DateTimeField(auto_now=True)),
                ('json_values', models.TextField()),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-action_time',),
            },
            bases=(models.Model,),
        ),
    ]
