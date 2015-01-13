# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0005_testmodelwithfieldsorder_a'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestModelWithDateField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
