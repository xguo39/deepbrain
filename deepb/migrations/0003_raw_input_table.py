# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-26 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deepb', '0002_auto_20170425_2054'),
    ]

    operations = [
        migrations.CreateModel(
            name='Raw_input_table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_input_gene', models.TextField()),
                ('raw_input_phenotype', models.TextField()),
                ('user_name', models.CharField(default='', max_length=10)),
                ('task_name', models.CharField(default='', max_length=20)),
            ],
        ),
    ]
