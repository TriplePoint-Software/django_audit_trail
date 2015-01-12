# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodeltrackallfields',
            name='char2',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
    ]
