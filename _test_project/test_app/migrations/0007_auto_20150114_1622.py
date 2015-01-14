# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0006_testmodelwithdatefield'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='TestModelWithDateField',
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='test_app.User', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='test_app.Post', null=True),
            preserve_default=True,
        ),
    ]
