from datetime import datetime
from itertools import count
from suadmin.models import Event, EventParticipants
import profile
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from sklearn.ensemble import RandomForestClassifier
from account.models import Profile, Roles
from games.models import GamesPlayed
from staff.models import Attendance, ClassRoomDiscussion, Staff
from student.models import BestPerfomer, Coin, ExtraCirricular, Feedback, Flipped, Student, StudentAttendance, StudentCRDiscussion, StudentQuiz
from pathlib import Path
import csv
import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from joblib import dump, load
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.
def index(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            content = {}
            content['title'] = 'Admin Dashboard'
            
            badges_flip = Flipped.objects.all().order_by('-coin')[:3]
            content['badges_flip'] = badges_flip
            content['best_performers'] = Flipped.objects.all()
            most_coins = Coin.objects.order_by('-coin')[:3]
            content['most_coins'] = most_coins
            students = Profile.objects.filter(role_id = 3)
            games_list = []
            for s in students:
                games = GamesPlayed.objects.filter(profile_id = int(s.id))
                print(games)
                count_coin = 0
                game_dict = {}
                for gm in games:
                    count_coin = count_coin + gm.coins
                game_dict = {'name' : s.name, 'coin' : count_coin}
                games_list.append(game_dict)
            content['games_list'] = sorted(games_list, key = lambda i: i['coin'], reverse = True)
            return render(request, 'admin/index.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def train(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            if request.method == 'POST':
                file_exists = Path(str(BASE_DIR) + '/dataset/dataset.csv')
                if file_exists.is_file():
                    os.remove(str(BASE_DIR) + '/dataset/dataset.csv')

                file = open(str(BASE_DIR) + '/dataset/dataset.csv', 'w')
                file.close()

                # ML part
                crd = StudentCRDiscussion.objects.all()
                fc = Flipped.objects.all()
                gms = GamesPlayed.objects.all()
                atts = StudentAttendance.objects.all()
                quiz = StudentQuiz.objects.all()
                extra = ExtraCirricular.objects.all()

                with open(str(BASE_DIR) + '/dataset/dataset.csv', 'w') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(['id', 'student', 'coin', 'date'])

                curret_date = datetime.today()
                for i in crd:
                    enddate = datetime.strptime(str(i.date), "%Y-%m-%d")
                    days = enddate
                    with open(str(BASE_DIR) + '/dataset/dataset.csv', 'a') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i.profile.id, i.profile, i.coins, days])
                # for i in fc:
                #     enddate = datetime.strptime(str(i.date), "%Y-%m-%d")
                #     days = enddate
                #     with open(str(BASE_DIR) + '/dataset/dataset.csv', 'a') as csv_file:
                #         csv_writer = csv.writer(csv_file)
                #         csv_writer.writerow([i.student_profile.id, i.student_profile, i.coin, days])
                for i in gms:
                    enddate = datetime.strptime(str(i.date), "%Y-%m-%d")
                    days = enddate
                    with open(str(BASE_DIR) + '/dataset/dataset.csv', 'a') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i.profile.id, i.profile, i.coins, days])
                for i in atts:
                    enddate = datetime.strptime(str(i.date), "%Y-%m-%d")
                    days = enddate
                    with open(str(BASE_DIR) + '/dataset/dataset.csv', 'a') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i.student_profile.id, i.student_profile, i.coin, days])
                for i in quiz:
                    enddate = datetime.strptime(str(i.date_started), "%Y-%m-%d")
                    days = enddate
                    with open(str(BASE_DIR) + '/dataset/dataset.csv', 'a') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i.profile.id, i.profile, i.score, days])
                for i in extra:
                    enddate = datetime.strptime(str(i.date), "%Y-%m-%d")
                    days = enddate
                    with open(str(BASE_DIR) + '/dataset/dataset.csv', 'a') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i.student_profile.id, i.student_profile, i.coin, days])

                # col_names = ['id', 'coin', 'date']
                df = pd.read_csv(str(BASE_DIR) + '/dataset/dataset.csv')
                df['date'] = pd.to_datetime(df['date'])
                df['date'] = (df['date'] - df['date'].min())  / np.timedelta64(1,'D')
                df['coin'] = df['coin'].astype('float')
                print(df.head())

                #split dataset in features and target variable
                feature_cols = ['coin', 'date']
                X = df[feature_cols] # Features
                y = df.id # Target variable

                # Split dataset into training set and test set
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1) # 80% training and 20% test

                # Create Random Forest classifer object
                rfc = RandomForestClassifier()
                # Train Decision Tree Classifer
                rfc = rfc.fit(X_train, y_train)
                dump(rfc, str(BASE_DIR) + '/dataset/model_rfcc.pkl')
                #Predict the response for test dataset
                y_pred_rfc = rfc.predict(X_test)
                print("Accuracy: ", metrics.accuracy_score(y_test, y_pred_rfc))
                # ML ends
                messages.success(request, 'Model trained')
                return HttpResponseRedirect(reverse('su-predict'))
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def staff(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            content = {}
            content['title'] = 'Staffs'
            content['staffs'] = Staff.objects.all()
            if request.method == 'POST':
                name = request.POST['name']
                email = request.POST['email']
                contact = request.POST['contact']
                username = request.POST['username']
                password = request.POST['password']

                try:
                    profile = Profile()
                    profile.name = name.title()
                    profile.username = username.lower()
                    profile.password = password
                    profile.role = Roles.objects.get(pk = 2)
                    profile.save()

                    getlastid = Profile.objects.filter(username = username.lower(), password = password).first()

                    staff = Staff()
                    staff.email = email.lower()
                    staff.contact = contact
                    staff.profile = Profile.objects.get(pk = int(getlastid.id))
                    staff.save()

                    messages.success(request, f'{name.title()} saved in staff list.')
                    content['staffs'] = Staff.objects.all()
                except IntegrityError as e:
                    messages.error(request, str(e.args))
            return render(request, 'admin/staff.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def predict(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            content = {}
            content['title'] = 'Predict'
            content['student'] = ''
            if request.method == 'POST':
                model = load(str(BASE_DIR) + '/dataset/model_rfcc.pkl')
                predict = model.predict([[int(request.POST['coin']), int(request.POST['days'])]])
                
                student = Profile.objects.get(pk = int(predict))
                if student:
                    content['student'] = student.name + ' is the predicted student'
                else:
                    content['student'] = 'No predictions. Try again with some another data'
            return render(request, 'admin/predict.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def event(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            content = {}
            content['title'] = 'Events'
            content['events'] = Event.objects.all().order_by('-id')
            if request.method == 'POST':
                title = request.POST['title']
                description = request.POST['description']
                fee = float(request.POST['fee'])
                redeem = float(request.POST['redeem'])
                date = request.POST['date']

                event = Event()
                event.title = title
                event.description = description
                event.fee = fee
                event.redeem = redeem
                event.on_date = date
                event.save()
                messages.success(request, 'Event created')
            return render(request, 'admin/event.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def eventParti(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            content = {}
            event = Event.objects.get(pk = pk)
            content['title'] = event
            content['event'] = event
            check_parti = EventParticipants.objects.filter(event_id = event.id)
            content['check_parti'] = check_parti
            return render(request, 'admin/event_p.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def feedback(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 1):
            content = {}
            content['title'] = 'Feedback'
            content['ratings'] = Feedback.objects.all().order_by('-id')
            return render(request, 'admin/feedback.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))