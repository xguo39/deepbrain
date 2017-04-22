# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.utils import timezone

import pandas as pd
# import main

id = 10000

# Create your views here.
def index(request):
    return render(request, 'deepb/index.html')

def upload(request):
    global id
    gene_file = request.FILES['gene_file']
    symptom_file = request.FILES['symptom_file']
    task_id = id+1
    handle_uploaded_gene_file(gene_file)
    handle_uploaded_symptom_file(symptom_file)

    # try:
    #     ACMG_result, df_genes, phenos = main.master_function('input/input_phenotype.txt', 'input/input_genes.txt')
    # except (KeyError):
    #     return render(request, 'deepb/index.html', {
    #         'error_message': "The process has failed. Please try again.",
    #     })
    # else:
    #     input_gene = df_genes.to_json(orient='records')[1:-1].replace('},{', '} {')
    #     input_phenotype = ', '.join(phenos)
    #     result_table = ACMG_result.to_json(orient='records')[1:-1].replace('},{', '} {')
    #     pub_date = timezone.now()


    return render(request, 'deepb/result.html')


def handle_uploaded_gene_file(f):
    with open('input/input_genes.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def handle_uploaded_symptom_file(f):
    with open('input/input_phenotype.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

# def waiting_task(request, task_id):
#     while
#     return HttpResponse("You task %s is being processed. Please be patient." % task_id)