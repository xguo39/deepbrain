# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
import numpy as np

id = 10000

# Create your views here.
def index(request):
    return render(request, 'deepb/index.html')

def upload(request):
    global id
    gene_file = request.FILES['gene_file']
    symptom_file = request.FILES['symptom_file']
    task_id = id+1
    result = []
    while result == []:
        return render(request, 'deepb/index.html', {
            'running_message': "Here is your task ID: %s. You task is being processed. Please be patient. The page will refresh automatically when it's done." %task_id,
        })

    try:
        result = main.master(gene_file, symptom_file)
    except(KeyError):
        return render(request, 'deepb/index.html', {
            'error_message': "The process has failed. Please upload your files again.",
        })
    else:
        main_table.

        return render(request, 'polls/results.html', {'question': question})

# def handle_uploaded_gene_file(f):
#     with open('/Users/xinguo/Desktop/deepbrain/gene_output.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
#     return 1
#
# def handle_uploaded_symptom_file(f):
#     with open('/Users/xinguo/Desktop/deepbrain/symptom_output.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)

# def waiting_task(request, task_id):
#     while
#     return HttpResponse("You task %s is being processed. Please be patient." % task_id)