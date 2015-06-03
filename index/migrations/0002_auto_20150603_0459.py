# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='jack',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='date published')),
                ('comment', models.CharField(max_length=160)),
            ],
        ),
        migrations.RenameModel(
            old_name='users',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='jacks',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='jacks',
        ),
        migrations.AddField(
            model_name='jack',
            name='user_id',
            field=models.ForeignKey(to='index.user'),
        ),
    ]
