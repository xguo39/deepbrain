# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.utils import timezone
from deepb.models import Main_table
from deepb.tasks import trigger_background_main_task
from django.views.generic.list import ListView
from django.views.generic import DetailView

import pandas as pd
import main

task_id = 10000

gene_file_path = '/Users/xinguo/input/input_genes.txt'
phenotype_file_path = '/Users/xinguo/input/input_phenotype.txt'

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
    return HttpResponseRedirect(reverse('deepb:results', args=()))
    # return HttpResponse("Success! You task ID is %s " % task_id)

class ResultsView(ListView):
    model = Main_table
    template_name = 'deepb/index.html'
    context_object_name = 'latest_task_list'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['last_result'] = 'Your task has been successfully uploaded'
        return context


class DetailsView(DetailView):
    model = Main_table
    template_name = 'deepb/result.html'

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