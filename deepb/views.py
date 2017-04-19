# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'deepb/index.html')

def upload(request):
    gene_file = request.FILES['gene_file']
    symptom_file = request.FILES['symptom_file']
    task_id = handle_uploaded_gene_file(gene_file)
    handle_uploaded_symptom_file(symptom_file)
    return HttpResponseRedirect(reverse('deepb:waiting', args=(task_id,)))

def handle_uploaded_gene_file(f):
    with open('/Users/xinguo/Desktop/deepbrain/gene_output.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return 1

def handle_uploaded_symptom_file(f):
    with open('/Users/xinguo/Desktop/deepbrain/symptom_output.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def waiting_task(request, task_id):
    return HttpResponse("You task %s is being processed. Please be patient." % task_id)