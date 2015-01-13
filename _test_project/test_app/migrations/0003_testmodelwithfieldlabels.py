# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0002_testmodeltrackallfields_char2'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestModelWithFieldLabels',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('char', models.CharField(max_length=255, null=True)),
                ('char2', models.CharField(max_length=255, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
