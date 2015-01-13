# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0004_testmodelwithfieldsorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodelwithfieldsorder',
            name='a',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
