# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
#
class Main_table(models.Model):
    task_id = models.IntegerField(default=0)
    input_gene = models.TextField()
    input_phenotype = models.TextField()
    result_table = models.TextField()
    pub_date = models.DateTimeField()