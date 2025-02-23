from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from account.models import Profile
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.
def index(request):
    return HttpResponseRedirect(reverse('account-login'))
    # if request.session.has_key('account_id'):
    #     if(request.session['account_role'] == 2):
    #         content = {}
    #         content['title'] = 'Welcome to Gamification'
    #         return render(request, 'home/index.html', content)
    #     else:
    #         return HttpResponseForbidden()
    # else:
    #     messages.error(request, "Please login first.")
    #     return HttpResponseRedirect(reverse('account-login'))