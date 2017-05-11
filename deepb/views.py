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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
import pandas as pd





def index(request):
    return render(request, 'index.html')

def index_en(request):
    return render(request, 'index_en.html')

class HomeView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'home.html'
    context_object_name = 'latest_task_list'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['User_name'] = self.request.user.username
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        task_count = raw_input_list.count()
        if task_count > 6:
            context['show_all'] = "all"
            context['task_count'] = task_count

        if task_count > 0:
            last_task = raw_input_list.order_by('-id')[0]
            status, main_table_id = self._task_status_check(last_task)
            context['last_task_status'] = status
            context['status_step'] = last_task.status
            context['estimate_time'] = round((0.14*len(last_task.raw_input_gene.split('\n')) + 1.69*len(last_task.raw_input_phenotype.split(','))+93.83)/60, 1)
        
        return context

    def get_queryset(self):
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        raw_input_table_with_status_and_id_list = []
        # show_all = self.request.GET.get('show_all')
        for raw_input_table in raw_input_list:
            status, main_table_id = self._task_status_check(raw_input_table)
            raw_input_table_with_status_and_id_list.append(Raw_input_table_with_status_and_id(raw_input_table, status, main_table_id))
        return raw_input_table_with_status_and_id_list[::-1][:6]

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
        elif raw_input_table.status[-6:]=="failed":
            return Constant.FAIL_STATUS, None
        else:
            return Constant.IN_PROGRESS_STATUS, None

class HomeAllView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'home.html'
    context_object_name = 'latest_task_list'

    def get_context_data(self, **kwargs):
        context = super(HomeAllView, self).get_context_data(**kwargs)
        context['User_name'] = self.request.user.username
        context['all_back'] = 1
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        last_task = raw_input_list.order_by('-id')[0]
        status, main_table_id = self._task_status_check(last_task)
        context['last_task_status'] = status
        context['status_step'] = last_task.status
        context['estimate_time'] = round((0.14*len(last_task.raw_input_gene.split('\n')) + 1.69*len(last_task.raw_input_phenotype.split(','))+93.83)/60, 1)
        return context

    def get_queryset(self):
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        raw_input_table_with_status_and_id_list = []
        for raw_input_table in raw_input_list:
            status, main_table_id = self._task_status_check(raw_input_table)
            raw_input_table_with_status_and_id_list.append(Raw_input_table_with_status_and_id(raw_input_table, status, main_table_id))
        return raw_input_table_with_status_and_id_list[::-1]


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
        elif raw_input_table.status[-6:]=="failed":
            return Constant.FAIL_STATUS, None
        else:
            return Constant.IN_PROGRESS_STATUS, None


def upload(request):
    user_name = request.user.username
    task_name = request.POST.get('task_name', None)
    gene_file = request.FILES['gene_file']

    phenotype_type = ''
    phenotype_file = ''
    try:
        phenotype_file = request.FILES['symptom_file']   
    except:
        phenotype = ''
    phenotype_type = request.POST.get('input_text_phenotype', None)

    if phenotype_type:
        phenotype = phenotype_type
    if phenotype_file:
        phenotype = phenotype_file.read()


    raw_input_id = handle_uploaded_file(gene_file, phenotype, user_name, task_name)

    trigger_background_main_task.delay(raw_input_id)
    return redirect('/home/')


def result(request, pk):
    main_table = get_object_or_404(Main_table, pk=pk)
    field = [i.split(":")[0][1:-1] for i in main_table.input_gene.split("},{")[0][2:].split(',')]

    return render(request, 'result.html', {
        'task_name': main_table.task_name,
        'result': mark_safe(main_table.result),
        'input_gene': mark_safe(main_table.input_gene),
        'input_phenotype': main_table.input_phenotype,
        'User_name': request.user.username,
        'field_names': field
        })

def handle_uploaded_file(raw_input_gene_file, raw_input_phenotype_file, user_name, task_name):
    
    if raw_input_gene_file.name.endswith('.xls') or raw_input_gene_file.name.endswith('.xlsx'):
        input_gene = pd.read_excel(raw_input_gene_file).to_csv(index=False)
    if raw_input_gene_file.name.endswith('.txt'):
        input_gene = raw_input_gene_file.read()

    raw_gene_input = Raw_input_table(
        raw_input_gene=input_gene,
        raw_input_phenotype=raw_input_phenotype_file,
        user_name=user_name,
        task_name=task_name,
        pub_date=timezone.now(),
        status = "Preprocessing data for interpretation"
    )
    raw_gene_input.save()
    return raw_gene_input.id

# def waiting_task(request, task_id):
#     while
#     return HttpResponse("You task %s is being processed. Please be patient." % task_id)