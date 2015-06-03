# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='jacks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='date published')),
                ('comment', models.CharField(max_length=160)),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16)),
                ('password_hash', models.CharField(max_length=512)),
                ('password_salt', models.CharField(max_length=32)),
                ('last_online', models.DateTimeField(verbose_name='date published')),
                ('creation_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.AddField(
            model_name='jacks',
            name='user_id',
            field=models.ForeignKey(to='index.users'),
        ),
    ]
