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
from deepb.map_chpo import map_chpo
from lof import check_lof

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework import status, generics
from deepb.serializers import New_task_Serializer
from deepb.serializers import Progress_task_Serializer
from deepb.serializers import All_task_Serializer
from deepb.serializers import Case_result_Serializer




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
        try:
            a = self.kwargs['show_all']
            context['all_back'] = 1
        except:
            if task_count > 6:
                context['show_all'] = "all"
                context['task_count'] = task_count

        if task_count > 0:
            ordered_task = raw_input_list.order_by('-id')
            for task in ordered_task:
                status, main_table_id = self._task_status_check(task)
                if status == 'In progress':
                    context['refresh'] = 1
                    break
        if self.request.user.username == 'guest':
            context['guest'] = 1
        return context

    def get_queryset(self):
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        raw_input_table_with_status_and_id_list = []
        # show_all = self.request.GET.get('show_all')            
        for raw_input_table in raw_input_list:
            status, main_table_id = self._task_status_check(raw_input_table)
            raw_input_table_with_status_and_id_list.append(Raw_input_table_with_status_and_id(raw_input_table, status, main_table_id))

        if self.request.user.username == 'guest':
            return raw_input_table_with_status_and_id_list[::-1][:1]
        else:
            try:
                a = self.kwargs['show_all']
                return raw_input_table_with_status_and_id_list[::-1]
            except:
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
        elif current_time - pub_time > Config.max_task_waiting_time:
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

def upload_ch(request):
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
    return redirect('/home/ch')


def handle_uploaded_file(raw_input_gene_file, raw_input_phenotype_file, user_name, task_name):
    
    if raw_input_gene_file.name.endswith('.xls') or raw_input_gene_file.name.endswith('.xlsx'):
        input_gene = pd.read_excel(raw_input_gene_file).to_csv(index=False)
    else:
        input_gene = raw_input_gene_file.read()

    estimate_time = round((0.14*len(input_gene.split('\n')) + 1.69*len(raw_input_phenotype_file.split(','))+93.83)/60, 0)+1
    print("raw_input_phenotype: {}".format(raw_input_phenotype_file))

    raw_gene_input = Raw_input_table(
        raw_input_gene=input_gene,
        raw_input_phenotype=raw_input_phenotype_file,
        user_name=user_name,
        task_name=task_name,
        pub_date=timezone.now(),
        status = "Preprocessing data for interpretation",
        process_time = estimate_time
    )
    raw_gene_input.save()

    return raw_gene_input.id

@login_required(login_url='/login/')
def result(request, pk):
    main_table = get_object_or_404(Main_table, pk=pk)
    input_gene_field = [i.split('":"')[0] for i in main_table.input_gene.split("},{")[0][3:].split('","')]

    return render(request, 'result.html', {
        'task_name': main_table.task_name,
        'result': mark_safe(main_table.result),
        'input_gene': mark_safe(main_table.input_gene),
        'input_phenotype': Raw_input_table.objects.get(id=main_table.task_id).raw_input_phenotype,
        'User_name': request.user.username,
        'field_names': input_gene_field,
        'pk': pk,
        })

@login_required(login_url='/login/')
def result_ch(request, pk):
    main_table = get_object_or_404(Main_table, pk=pk)
    input_gene_field = [i.split('":"')[0] for i in main_table.input_gene.split("},{")[0][3:].split('","')]

    return render(request, 'result_ch.html', {
        'task_name': main_table.task_name,
        'result': mark_safe(main_table.result),
        'input_gene': mark_safe(main_table.input_gene),
        'input_phenotype': Raw_input_table.objects.get(id=main_table.task_id).raw_input_phenotype,
        'input_phenotype_hpo': main_table.input_phenotype,
        'User_name': request.user.username,
        'field_names': input_gene_field,
        'pk': pk,
        })

@login_required(login_url='/login/')
def interpretation(request, pk):
    main_table = get_object_or_404(Main_table, pk=pk)

    return render(request, 'interpretation.html', {
        'User_name': request.user.username,
        'interpretation': mark_safe(main_table.interpretation),
        'task_name': main_table.task_name,
        'pk': pk,
        })

@login_required(login_url='/login/')
def interpretation_ch(request, pk):
    main_table = get_object_or_404(Main_table, pk=pk)

    return render(request, 'interpretation_ch.html', {
        'User_name': request.user.username,
        'interpretation': mark_safe(main_table.interpretation_chinese),
        'task_name': main_table.task_name,
        'pk': pk,
        })



class HomeView_ch(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'home_ch.html'
    context_object_name = 'latest_task_list'

    def get_context_data(self, **kwargs):
        context = super(HomeView_ch, self).get_context_data(**kwargs)
        context['User_name'] = self.request.user.username
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        task_count = raw_input_list.count()
        try:
            a = self.kwargs['show_all']
            context['all_back'] = 1
        except:
            if task_count > 5:
                context['show_all'] = "all"
                context['task_count'] = task_count

        if task_count > 0:
            ordered_task = raw_input_list.order_by('-id')
            for task in ordered_task:
                status, main_table_id = self._task_status_check(task)
                if status == 'In progress':
                    context['refresh'] = 1
                    break
        if self.request.user.username == 'guest':
            context['guest'] = 1
        
        return context

    def get_queryset(self):
        raw_input_list = Raw_input_table.objects.filter(user_name=self.request.user.username)
        raw_input_table_with_status_and_id_list = []
        # show_all = self.request.GET.get('show_all')            
        for raw_input_table in raw_input_list:
            status, main_table_id = self._task_status_check(raw_input_table)
            raw_input_table_with_status_and_id_list.append(Raw_input_table_with_status_and_id(raw_input_table, status, main_table_id))

        if self.request.user.username == 'guest':
            return raw_input_table_with_status_and_id_list[::-1][:1]
        else:
            try:
                a = self.kwargs['show_all']
                return raw_input_table_with_status_and_id_list[::-1]
            except:
                return raw_input_table_with_status_and_id_list[::-1][:5]

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
        elif current_time - pub_time > Config.max_task_waiting_time:
            return Constant.FAIL_STATUS, None
        else:
            return Constant.IN_PROGRESS_STATUS, None

def chpo(request):
    chinese_pheno = request.POST.get('chpo', None)
    match_result = map_chpo(chinese_pheno)
    return render(request, 'chpo.html', {
        'match_result': mark_safe(match_result),
        })

def lof(request):
    input_gene = request.POST.get('gene', None)
    lof_result = []
    if not input_gene:
        status = 0
    else:
        status, lof_result = check_lof(input_gene)
    return render(request, 'lof.html', {
        'status': status,
        'lof_result': lof_result,
        })

class new_task(APIView):

    @permission_classes((IsAdminUser,))
    def post(self, request, format=None):
        user = request.user
        serializer = New_task_Serializer(data=request.data, context={'user':user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class progress_task_list(APIView):

    def get(self, request, format=None):
        post = Raw_input_table.objects.filter(user_name=request.user.username)
        serializer = Progress_task_Serializer(post, many=True)
        return Response(serializer.data)

class all_task_list(APIView):

    def get(self, request, format=None):
        post = Raw_input_table.objects.filter(user_name=request.user.username)
        serializer = All_task_Serializer(post, many=True)
        return Response(serializer.data)

class case_result(generics.RetrieveUpdateDestroyAPIView):
    queryset = Main_table.objects.all()
    serializer_class = Case_result_Serializer
