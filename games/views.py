from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from account.models import Profile, Roles
from games.models import GamesPlayed
from student.models import ExtraCirricular, Student, Coin, StudentAttendance, StudentCRDiscussion, StudentQuiz, StudentQuizQuestion
from staff.models import Staff, Quiz, QuizQA
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime
import os
import subprocess
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.
def index(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Games'
            content['memory_puzzle_top'] = GamesPlayed.objects.filter(game = 'Memory Puzzle').exclude(seconds = None).order_by('seconds')[:5]
            content['keyboard_top'] = GamesPlayed.objects.filter(game = 'Keyboard Jump').exclude(seconds = None).order_by('seconds')[:5]
            return render(request, 'student/games.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def memoryPuzzle(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Games'
            content['memory_puzzle_top'] = GamesPlayed.objects.filter(game = 'Memory Puzzle').exclude(seconds = None).order_by('seconds')[:5]
            content['keyboard_top'] = GamesPlayed.objects.filter(game = 'Keyboard Jump').exclude(seconds = None).order_by('seconds')[:5]
            if request.method == 'POST':
                # from games import memory_puzzle
                game_path = str(BASE_DIR) + '\games\memory_puzzle.py'
                subprocess.call(f'start /wait python {game_path}', shell=True)
            return render(request, 'student/games.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def hangman(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Games'
            if request.method == 'POST':
                # from games import hangman
                game_path = str(BASE_DIR) + '\games\hangman.py'
                subprocess.call(f'start /wait python {game_path}', shell=True)
            return render(request, 'student/games.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def keyboardjunp(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Games'
            content['memory_puzzle_top'] = GamesPlayed.objects.filter(game = 'Memory Puzzle').exclude(seconds = None).order_by('seconds')[:5]
            content['keyboard_top'] = GamesPlayed.objects.filter(game = 'Keyboard Jump').exclude(seconds = None).order_by('seconds')[:5]
            if request.method == 'POST':
                # from games import keyboardjump
                game_path = str(BASE_DIR) + '\games\keyboardjump.py'
                subprocess.call(f'start /wait python {game_path}', shell=True)
            return render(request, 'student/games.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))
