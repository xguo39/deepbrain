# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-22 00:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deepb', '0002_auto_20170422_0012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='main_table',
            name='input_gene',
            field=models.CharField(max_length=30000),
        ),
        migrations.AlterField(
            model_name='main_table',
            name='input_phenotype',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='main_table',
            name='result_table',
            field=models.CharField(max_length=12000),
        ),
    ]
