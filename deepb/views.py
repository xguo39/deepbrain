# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from deepb.models import Main_table, Raw_input_table
from deepb.tasks import trigger_background_main_task
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.utils.safestring import mark_safe
from django.views import generic


import random


import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

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

class ResultsView(generic.ListView):
    model = Main_table
    template_name = 'deepb/index.html'
    context_object_name = 'latest_task_list'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['last_result'] = 'Your task has been successfully uploaded'
        return context

def details(request, pk):
    try:
        main_table = Main_table.objects.get(pk=pk)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'deepb/result.html', {
        'task_id': main_table.task_id,
        'result': mark_safe(main_table.result),
        'input_gene': mark_safe(main_table.input_gene),
        'input_phenotype': main_table.input_phenotype,
        })

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