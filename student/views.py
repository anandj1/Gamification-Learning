from numpy import single
from staff.views import student
from suadmin.models import Event, EventParticipants
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from account.models import Profile, Roles
from student.models import ExtraCirricular, Feedback, Flipped, Student, Coin, StudentAttendance, StudentCRDiscussion, StudentQuiz, StudentQuizQuestion
from staff.models import Staff, Quiz, QuizQA
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime
import datetime
from django.utils import timezone

# Create your views here.
def index(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Welcome to Gamification Student Panel'
            coins = Coin.objects.filter(profile_id = int(request.session['account_id'])).first()
            content['coins'] = coins
            quiz_played = StudentQuiz.objects.filter(status = True, profile_id = int(request.session['account_id'])).count()
            content['quiz_played'] = quiz_played
            extra_cs = ExtraCirricular.objects.filter(student_profile_id = int(request.session['account_id'])).count()
            content['extra_cs'] = extra_cs
            most_coins = Coin.objects.order_by('-coin')
            content['most_coins'] = most_coins
            return render(request, 'student/index.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def quiz(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Play quiz to earn'
            content['quizs'] = Quiz.objects.all()
            return render(request, 'student/quiz/quiz.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def playQuiz(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            quiz = Quiz.objects.get(pk = pk)
            content['quiz'] = quiz  

            # Check quiz record
            student_quiz = StudentQuiz.objects.filter(quiz_id = pk, profile_id = int(request.session['account_id'])).first()
            if student_quiz:
                print('Data already exists')
            else:
                # Add quiz record
                current_time = datetime.datetime.now()
                std_quiz = StudentQuiz()
                std_quiz.quiz = Quiz.objects.get(pk=pk)
                std_quiz.student = Student.objects.get(pk=int(request.session['student_id']))
                std_quiz.profile = Profile.objects.get(pk=int(request.session['account_id']))
                std_quiz.time_start = current_time
                std_quiz.save()
            
            # Get question ids in an array list
            question_data = QuizQA.objects.filter(quiz_id = pk)
            questions_array = []
            for x in question_data:
                questions_array.append(x.id)

            # Loop through questions
            content['question'] = ''
            questions_array_final = questions_array.copy()      # tooked one and half days to figure out the problem. Just haven't placed .copy()
            for x in questions_array:
                check_pre_question = StudentQuizQuestion.objects.filter(question_id = x, quiz_id = pk, profile_id = int(request.session['account_id'])).last()
                if check_pre_question:
                    questions_array_final.remove(x)
                else:
                    continue

            # content['que_arrays'] = questions_array
            # content['que_arrays_final'] = questions_array_final

            qa = None     
            if len(questions_array_final) > 0:
                qa = QuizQA.objects.get(pk = questions_array_final[0])
                content['question'] = qa
            else:
                content['question'] = None
            
            # Display question name as title
            content['title'] = quiz.name

            # Post the data
            if request.method == 'POST':
                qa_option = request.POST['qa_option']
                add_quiz_data = StudentQuizQuestion()
                add_quiz_data.quiz = Quiz.objects.get(pk=pk)
                add_quiz_data.student = Student.objects.get(pk=int(request.session['student_id']))
                add_quiz_data.profile = Profile.objects.get(pk=int(request.session['account_id']))
                add_quiz_data.question = QuizQA.objects.get(pk=qa.id)
                if qa_option == qa.right_option:
                    add_quiz_data.is_right = True
                    add_quiz_data.coins = quiz.each_point
                else:
                    add_quiz_data.is_right = False
                    add_quiz_data.coins = 0
                add_quiz_data.save()
                return HttpResponseRedirect(reverse('std-play-quiz', kwargs={'pk': pk}))
            return render(request, 'student/quiz/play-quiz.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def submitQuiz(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            if request.method == 'POST':
                quiz = Quiz.objects.get(pk=pk)
                student_quiz = StudentQuiz.objects.filter(quiz_id = pk, profile_id = int(request.session['account_id'])).first()
                # End time
                end_time = datetime.datetime.now(timezone.utc)

                # Get difference in seconds
                difference = (end_time - student_quiz.time_start)
                total_seconds = difference.total_seconds()
                student_quiz_questions = StudentQuizQuestion.objects.filter(quiz_id = pk, profile_id = int(request.session['account_id']))

                # Collect coins
                coins = 0
                for x in student_quiz_questions:
                    coins = coins + x.coins
                
                # Save data
                student_quiz.score = coins
                student_quiz.status = True
                student_quiz.date_finished = end_time
                student_quiz.time_end = end_time
                student_quiz.seconds = total_seconds
                student_quiz.save()

                # Student coins
                std = Coin.objects.filter(profile_id = int(request.session['account_id'])).first()
                std_coins = std.coin
                std.coin = std_coins + coins
                std.save()

                get_all_list = StudentQuiz.objects.filter(quiz_id = pk).order_by('-score', 'seconds')[:5]
                for x in get_all_list:
                    single_quiz = StudentQuiz.objects.filter(quiz_id = pk, profile_id = int(request.session['account_id'])).first()
                    if x.profile_id == single_quiz.profile_id:
                        std = Coin.objects.filter(profile_id = int(request.session['account_id'])).first()
                        std_coins = std.coin
                        std.coin = std_coins + (coins * 2)
                        std.save()

                messages.success(request, 'You have successfully completed the quiz.')
                return HttpResponseRedirect(reverse('std-quiz'))
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def classRoomDiscussion(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Classrom Discussions'
            content['data'] = StudentCRDiscussion.objects.filter(profile_id = int(request.session['account_id']))
            return render(request, 'student/classroomdiscussion.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def flippedClassRoomDiscussion(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Classrom Discussions'
            daat = Flipped.objects.filter(student_profile_id = int(request.session['account_id']))
            content['data'] = Flipped.objects.filter(student_profile_id = int(request.session['account_id']))
            return render(request, 'student/flippedclassroomdiscussion.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def attendance(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Your Attendance'
            content['data'] = StudentAttendance.objects.filter(student_profile_id=int(request.session['account_id']))
            return render(request, 'student/attendance.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def extraCirricular(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Extra Cirricular'
            content['exts'] = ExtraCirricular.objects.filter(student_profile_id = int(request.session['account_id']))
                
            return render(request, 'student/extra_cirricular.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def event(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Events'
            content['events'] = Event.objects.all().order_by('-id')
            return render(request, 'student/event/event.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def eventApply(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            event = Event.objects.get(pk = pk)
            content['title'] = event
            content['event'] = event
            check_parti = EventParticipants.objects.filter(profile_id = int(request.session['account_id']), event_id = event.id).first()
            content['check_parti'] = check_parti
            if request.method == "POST":
                check_coins = Coin.objects.filter(profile_id = int(request.session['account_id'])).first()
                if check_coins.coin >= (event.redeem * event.fee):
                    event_p = EventParticipants()
                    event_p.event = Event.objects.get(pk = pk)
                    event_p.profile = Profile.objects.get(pk = int(request.session['account_id']))
                    event_p.redeem = event.redeem * event.fee
                    event_p.save()

                    # Student coins
                    std = Coin.objects.filter(profile_id = int(request.session['account_id'])).first()
                    std_coins = std.coin
                    std.coin = std_coins - (event.redeem * event.fee)
                    std.save()

                    messages.error(request, 'Your participation done.')
                    return HttpResponseRedirect(reverse('std-event'))
                else:
                    messages.error(request, 'You do not have enough coins. Try to earn more and come back later')
            return render(request, 'student/event/apply.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def feedback(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 3):
            content = {}
            content['title'] = 'Feedback'
            content['staffs'] = Profile.objects.filter(role_id = 2)
            content['my_ratings'] = Feedback.objects.filter(student_profile_id=int(request.session['account_id']))
            if request.method == 'POST':
                staff = int(request.POST['staff'])
                feed = request.POST['feedback']
                rating = float(request.POST['rating'])

                getstd = Student.objects.filter(profile_id = int(request.session['account_id'])).first()
                getstaff = Staff.objects.filter(profile_id = staff).first()

                feedback = Feedback()
                feedback.staff_profile = Profile.objects.get(pk = staff)
                feedback.staff = Staff.objects.get(pk = getstaff.id)
                feedback.student_profile = Profile.objects.get(pk = int(request.session['account_id']))
                feedback.student = Student.objects.get(pk = getstd.id)
                feedback.feedback = feed
                feedback.rating = rating
                feedback.save()

                feed_staff = Feedback.objects.filter(staff_profile_id = staff)
                total = 0
                for f in feed_staff:
                    total = total + f.rating
                feed_count = feed_staff.count()
                final_rating = total / feed_count

                # Update rating
                stf = Profile.objects.get(pk=staff)
                stf.rating = final_rating
                stf.save()
            return render(request, 'student/feedback.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))
