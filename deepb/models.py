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
    take_name = models.CharField(max_length=20)


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