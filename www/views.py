# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def ping(request):
    return HttpResponse(request.GET.get('echo', 'hello'))
