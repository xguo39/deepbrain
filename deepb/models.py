# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
#
class Main_table(models.Model):
    task_id = models.IntegerField(default=0)
    input_gene = models.TextField()
    input_phenotype = models.TextField()
    result = models.TextField()
    pub_date = models.DateTimeField()

# class test(models.Model):
#     task_id = models.IntegerField(default=0)
#     input_gene = models.CharField(max_length=20)
#     pub_date = models.DateTimeField()