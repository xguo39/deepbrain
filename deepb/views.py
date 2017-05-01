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
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from deepb.configs import Config, Constant
from model_wrapper import Raw_input_table_with_status_and_id

import random


import os.path
BASE = os.path.dirname(os.path.abspath(__file__))

# Create your views here.

@login_required(login_url="login/")
def home(request):
    return render(request, 'home.html')

def upload(request):
    gene_file = request.FILES['gene_file']
    symptom_file = request.FILES['symptom_file']
    user_name = request.user.username
    task_name = request.POST.get('task_name', None)
    task_id = random.randint(1000000,9999999)

    if user_name is None:
        user_name = 'default ' + str(task_id)
    if task_name is None:
        task_name = 'default ' + str(task_id)

    raw_input_id = handle_uploaded_file(gene_file, symptom_file, user_name, task_name)

    trigger_background_main_task.delay(raw_input_id)
    return HttpResponseRedirect(reverse('deepb:home', args=()))

class ResultsView(generic.ListView):
    template_name = 'home.html'
    context_object_name = 'latest_task_list'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['last_result'] = 'Your task has been successfully uploaded'
        return context

    def get_queryset(self):
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        raw_input_table_with_status_and_id_list = []
        for raw_input_table in raw_input_list:
            status, main_table_id = self._task_status_check(raw_input_table)
            raw_input_table_with_status_and_id_list.append(Raw_input_table_with_status_and_id(raw_input_table, status, main_table_id))
        return raw_input_table_with_status_and_id_list

    def _task_status_check(self, raw_input_table):
        # check if the task is succeed
        task_name = raw_input_table.task_name
        user_name = raw_input_table.user_name
        # we use id in raw_input_table as task_id in the main_table
        task_id = raw_input_table.id
        current_time = timezone.now()
        pub_time = raw_input_table.pub_date

        main_table_result = Main_table.objects.filter(user_name=user_name, task_name=task_name, task_id=task_id).first()
        if main_table_result is not None:
            return Constant.SUCCESS_STATUS, main_table_result.id
        elif current_time - pub_time > Config.max_task_waiting_time:
            return Constant.FAIL_STATUS, None
        else:
            return Constant.IN_PROGRESS_STATUS, None

def details(request, pk):
    main_table = get_object_or_404(Main_table, pk=pk)
    return render(request, 'result.html', {
        'task_name': main_table.task_name,
        'result': mark_safe(main_table.result),
        'input_gene': mark_safe(main_table.input_gene),
        'input_phenotype': main_table.input_phenotype,
        })

def handle_uploaded_file(raw_input_gene_file, raw_input_phenotype_file, user_name, task_name):
    raw_gene_input = Raw_input_table(
        raw_input_gene=raw_input_gene_file.read(),
        raw_input_phenotype=raw_input_phenotype_file.read(),
        user_name=user_name,
        task_name=task_name,
        pub_date=timezone.now(),
    )
    raw_gene_input.save()
    return raw_gene_input.id

# def waiting_task(request, task_id):
#     while
#     return HttpResponse("You task %s is being processed. Please be patient." % task_id)