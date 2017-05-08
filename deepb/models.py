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
    user_name = models.CharField(max_length=10)
    task_name = models.CharField(max_length=20)

class Raw_input_table(models.Model):
    raw_input_gene = models.TextField()
    raw_input_phenotype = models.TextField()
    user_name = models.CharField(max_length=10, default='')
    task_name = models.CharField(max_length=20, default='')
    pub_date = models.DateTimeField()
    status = models.CharField(max_length=50, default='')

# class pubmed(models.Model):
# 	gene = models.CharField(max_length=20)
# 	protein_variant = models.CharField(max_length=30)
# 	pmid = models.CharField(max_length=15)
# 	title = models.TextField()
# 	journal = models.TextField()
# 	year = models.CharField(max_length=4)
# 	month = models.CharField(max_length=3)
# 	impact_factor = models.FloatField()
# 	abstract = models.TextField()
# 	variant_id = models.CharField(max_length=30)
# 	protein_domain = models.CharField(max_length=500)