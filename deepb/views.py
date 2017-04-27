# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.utils import timezone
from deepb.models import Main_table, Raw_input_table
from deepb.tasks import trigger_background_main_task
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.utils.safestring import mark_safe

import random


import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

gene_file_path = os.path.join(BASE, 'input/input_genes.txt')
phenotype_file_path = os.path.join(BASE, 'input/input_phenotype.txt')

# Create your views here.
def index(request):
    return render(request, 'deepb/index.html')

def upload(request):
    gene_file = request.FILES['gene_file']
    symptom_file = request.FILES['symptom_file']
    user_name = request.POST.get('user_name', None)
    task_name = request.POST.get('task_name', None)
    task_id = random.randint(1000000,9999999)

    if user_name is None:
        user_name = 'default ' + str(task_id)
    if task_name is None:
        task_name = 'default ' + str(task_id)

    raw_input_id = handle_uploaded_file(gene_file, symptom_file, user_name, task_name)

    trigger_background_main_task.delay(raw_input_id)
    return HttpResponseRedirect(reverse('deepb:results', args=()))

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

def handle_uploaded_file(raw_input_gene_file, raw_input_phenotype_file, user_name, task_name):
    raw_gene_input = Raw_input_table(
        raw_input_gene=raw_input_gene_file.read(),
        raw_input_phenotype=raw_input_phenotype_file.read(),
        user_name=user_name,
        task_name=task_name
    )
    raw_gene_input.save()
    return raw_gene_input.id

# def waiting_task(request, task_id):
#     while
#     return HttpResponse("You task %s is being processed. Please be patient." % task_id)