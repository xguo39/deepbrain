# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.utils import timezone
from deepb.models import Main_table
from deepb.tasks import trigger_background_main_task

# import pandas as pd
# import main

import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

task_id = 10000

gene_file_path = os.path.join(BASE, 'input/input_genes.txt')
phenotype_file_path = os.path.join(BASE, 'input/input_phenotype.txt')

# Create your views here.
def index(request):
    return render(request, 'deepb/index.html')

def upload(request):
    global task_id
    gene_file = request.FILES['gene_file']
    symptom_file = request.FILES['symptom_file']
    task_id = task_id+1
    handle_uploaded_gene_file(gene_file)
    handle_uploaded_symptom_file(symptom_file)

    trigger_background_main_task.delay(phenotype_file_path, gene_file_path, task_id)
    return HttpResponse("Success! You task ID is %s " % task_id)


def handle_uploaded_gene_file(f):
    # TODO: need to write to DB
    with open(gene_file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def handle_uploaded_symptom_file(f):
    # TODO: need to write to DB
    with open(phenotype_file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

# def waiting_task(request, task_id):
#     while
#     return HttpResponse("You task %s is being processed. Please be patient." % task_id)