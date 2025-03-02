from msilib.schema import Class
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from account.models import Profile, Roles
from student.models import BestPerfomer, ExtraCirricular, Flipped, Student, Coin, StudentAttendance, StudentCRDiscussion
from staff.models import Attendance, ClassRoomDiscussion, Staff, Quiz, QuizQA
from urllib.parse import urlparse, parse_qs

# Create your views here.


def index(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Welcome to Gamification Staff Panel'
            content['rating'] = Profile.objects.get(pk = int(request.session['account_id']))
            return render(request, 'staff/index.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def student(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Students'
            content['stds'] = Student.objects.all()
            content['coins'] = Coin.objects.all()
            if request.method == 'POST':
                name = request.POST['name']
                email = request.POST['email']
                contact = request.POST['contact']
                roll = int(request.POST['roll_no'])
                enrollment = int(request.POST['enrollment'])
                username = request.POST['username']
                password = request.POST['password']

                try:
                    profile = Profile()
                    profile.name = name.title()
                    profile.username = username.lower()
                    profile.password = password
                    profile.role = Roles.objects.get(pk=3)
                    profile.save()

                    getlastid = Profile.objects.filter(username=username.lower(), password=password).first()
                    std = Student()
                    std.email = email.lower()
                    std.rollno = roll
                    std.enrollment = enrollment
                    std.contact = contact
                    std.profile = Profile.objects.get(pk=int(getlastid.id))
                    std.save()

                    # Add default coins
                    getlaststd = Student.objects.filter(profile_id = int(getlastid.id)).first()
                    coin = Coin()
                    coin.coin = 0
                    coin.profile = Profile.objects.get(pk=int(getlastid.id))
                    coin.student = Student.objects.get(pk=int(getlaststd.id))
                    coin.save()

                    messages.success(request, f'{name.title()} saved in student list.')
                    content['stds'] = Student.objects.all()
                    content['coins'] = Coin.objects.all()
                except IntegrityError as e:
                    messages.error(request, str(e.args))
            return render(request, 'staff/student.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def quiz(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Quiz by you'
            quizes = Quiz.objects.filter(profile_id = int(request.session['account_id']))
            for x in quizes:
                qas = QuizQA.objects.filter(quiz_id=x.id).count()
                update_quiz = Quiz.objects.get(pk=int(x.id))
                total = update_quiz.each_point * qas
                update_quiz.total = total
                update_quiz.save()
            quizes = Quiz.objects.filter(profile_id = int(request.session['account_id']))
            content['quizs'] = quizes
            
            if request.method == 'POST':
                name = request.POST['name']
                point = int(request.POST['each_point'])

                getstaff = Staff.objects.filter(profile_id = int(request.session['account_id'])).first()

                quiz = Quiz()
                quiz.name = name.title()
                quiz.each_point = point
                quiz.profile = Profile.objects.get(pk = int(request.session['account_id']))
                quiz.staff = Staff.objects.get(pk = int(getstaff.id))
                quiz.save()
                messages.success(request, f'{name.title()} added to your quiz list.')
                quizes = Quiz.objects.filter(profile_id = int(request.session['account_id']))
                content['quizs'] = quizes
            return render(request, 'staff/quiz/quiz.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def quizQA(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            question_id = int(request.GET.get('qid'))
            content['question_id'] = str(question_id)
            quizdata = Quiz.objects.get(pk = question_id)
            content['title'] = 'Q&A for ' + str(quizdata.name)
            content['qas'] = QuizQA.objects.filter(quiz_id = question_id)
            if request.method == 'POST':
                qa = QuizQA()
                question = request.POST['question']
                op1 = request.POST['option_1']
                op2 = request.POST['option_2']
                op3 = request.POST['option_3']
                op4 = request.POST['option_4']
                opr = request.POST['right_option']

                qa.question = question
                qa.option_1 = op1
                qa.option_2 = op2
                qa.option_3 = op3
                qa.option_4 = op4
                qa.right_option = opr
                qa.quiz = Quiz.objects.get(pk = question_id)
                qa.save()
                messages.success(request, f'Question and answers option added for {quizdata.name}')
                content['qas'] = QuizQA.objects.filter(quiz_id=question_id)
            return render(request, 'staff/quiz/qa.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def editQuizQA(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            question_id = int(request.GET.get('qid'))
            question_answer_id = int(request.GET.get('qaid'))
            content['question_id'] = str(question_id)
            quizdata = Quiz.objects.get(pk = question_id)
            content['title'] = 'Q&A for ' + str(quizdata.name)
            content['qas'] = QuizQA.objects.filter(quiz_id = question_id)
            qa = QuizQA.objects.get(pk=int(question_answer_id))
            content['qa'] = qa
            if request.method == 'POST':
                question = request.POST['question']
                op1 = request.POST['option_1']
                op2 = request.POST['option_2']
                op3 = request.POST['option_3']
                op4 = request.POST['option_4']
                opr = request.POST['right_option']

                qa.question = question
                qa.option_1 = op1
                qa.option_2 = op2
                qa.option_3 = op3
                qa.option_4 = op4
                qa.right_option = opr
                qa.quiz = Quiz.objects.get(pk = question_id)
                qa.save()
                messages.success(request, f'Question and answers option updated for {quizdata.name}')
                content['qas'] = QuizQA.objects.filter(quiz_id=question_id)
            return render(request, 'staff/quiz/edit_qa.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def classroomDiscussion(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Classroom Discussion'
            content['discussions'] = ClassRoomDiscussion.objects.filter(profile_id = int(request.session['account_id']))
            getstaff = Staff.objects.filter(profile_id = int(request.session['account_id'])).first()
            if request.method == 'POST':
                name = request.POST['name']
                crd = ClassRoomDiscussion()
                crd.name = name
                crd.profile = Profile.objects.get(pk = int(request.session['account_id']))
                crd.staff = Staff.objects.get(pk = int(getstaff.id))
                crd.save()
                messages.success(request, 'Discussion topic created')
            return render(request, 'staff/classroom/discussion.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def classroomDiscussionFillCoins(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            crd = ClassRoomDiscussion.objects.get(pk = pk)
            content['title'] = 'Fill out the coins for ' + crd.name
            students = Student.objects.all()

            # Load students data first DB
            # Check pred data before adding data
            pre_data = StudentCRDiscussion.objects.filter(discussion_id = pk).count()
            if pre_data < 1:
                for x in students:
                    crds = StudentCRDiscussion()
                    crds.discussion = ClassRoomDiscussion.objects.get(pk=pk)
                    crds.profile = Profile.objects.get(pk = int(x.profile.id))
                    crds.student = Student.objects.get(pk = int(x.id))
                    crds.save()

            # Show the data
            content['students'] = StudentCRDiscussion.objects.filter(discussion_id = pk)

            return render(request, 'staff/classroom/fillcoins.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def classroomDiscussionFillCoinsPost(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            if request.method == 'POST':
                crd = StudentCRDiscussion.objects.get(pk = pk)
                coins = request.POST['coins']

                crd.coins = int(coins)
                crd.save()

                # Student coins
                crd = StudentCRDiscussion.objects.get(pk=pk)
                std = Coin.objects.filter(profile_id = crd.profile_id).first()
                std_coins = std.coin
                std.coin = std_coins + crd.coins
                std.save()
                return HttpResponseRedirect(reverse('st-cr-discussion-fill-coins', kwargs={'pk': crd.discussion_id}))
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def attendanceModel(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Attendance Models'
            att_models = Attendance.objects.filter(profile_id=int(request.session['account_id']))
            content['att_models'] = att_models

            if request.method == 'POST':
                day = request.POST['day_type']
                att = Attendance()
                att.day = day
                att.profile = Profile.objects.get(pk = int(request.session['account_id']))
                att.staff = Staff.objects.get(pk = int(request.session['staff_id']))
                att.save()
                messages.success(request, 'Attendance model created')
            return render(request, 'staff/attendance/model.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))


def attendanceConduct(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            att = Attendance.objects.get(pk = pk)
            content['title'] = 'Conduct attendance for ' + att.day + ' batch of date ' + str(att.date)

            students = Student.objects.all()

            # Load students data first DB
            # Check pred data before adding data
            pre_data = StudentAttendance.objects.filter(attendance_id = pk).count()
            if pre_data < 1:
                for x in students:
                    std_atts = StudentAttendance()
                    std_atts.attendance = Attendance.objects.get(pk=pk)
                    std_atts.student_profile = Profile.objects.get(pk = int(x.profile.id))
                    std_atts.student = Student.objects.get(pk = int(x.id))
                    std_atts.staff_profile = Profile.objects.get(pk = int(request.session['account_id']))
                    std_atts.staff = Staff.objects.get(pk = int(request.session['staff_id']))
                    std_atts.status = 'NA'
                    std_atts.save()

            # Show the data
            content['students'] = StudentAttendance.objects.filter(attendance_id = pk)
            return render(request, 'staff/attendance/conduct.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def attPresent(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            if request.method == 'POST':
                sta = StudentAttendance.objects.get(pk = pk)
                att_id = sta.attendance_id
                att_day = sta.attendance.day

                coin = 0
                if att_day == 'Regular':
                    coin = 0
                elif att_day == 'Bonus':
                    coin = 100

                sta.status = 'Present'
                sta.coin = coin
                sta.save()

                crd = StudentAttendance.objects.get(pk=pk)
                std = Coin.objects.filter(profile_id=crd.student_profile_id).first()
                std_coins = std.coin
                std.coin = std_coins + coin
                std.save()
                return HttpResponseRedirect(reverse('st-att-conduct', kwargs={'pk': att_id}))
        else:
            return HttpResponseForbidden()

def attAbsent(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            if request.method == 'POST':
                sta = StudentAttendance.objects.get(pk = pk)
                att_id = sta.attendance_id
                att_day = sta.attendance.day

                coin = 0
                if att_day == 'Regular':
                    coin = -100
                elif att_day == 'Bonus':
                    coin = -120

                sta.status = 'Absent'
                sta.coin = coin
                sta.save()

                crd = StudentAttendance.objects.get(pk=pk)
                std = Coin.objects.filter(profile_id=crd.student_profile_id).first()
                std_coins = std.coin
                std.coin = std_coins + coin
                std.save()
                return HttpResponseRedirect(reverse('st-att-conduct', kwargs={'pk': att_id}))
        else:
            return HttpResponseForbidden()


def attLeave(request, pk):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            if request.method == 'POST':
                sta = StudentAttendance.objects.get(pk=pk)
                att_id = sta.attendance_id
                att_day = sta.attendance.day

                coin = 0
                if att_day == 'Regular':
                    coin = 100
                elif att_day == 'Bonus':
                    coin = 120

                sta.status = 'Leave (Extra Cirricular)'
                sta.coin = coin
                sta.is_extra = True
                sta.save()

                crd = StudentAttendance.objects.get(pk=pk)
                std = Coin.objects.filter(profile_id=crd.student_profile_id).first()
                std_coins = std.coin
                std.coin = std_coins + coin
                std.save()
                return HttpResponseRedirect(reverse('st-att-conduct', kwargs={'pk': att_id}))
        else:
            return HttpResponseForbidden()

def extraCirricular(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Extra Cirricular'
            content['stds'] = Student.objects.all()
            content['exts'] = ExtraCirricular.objects.filter(staff_profile_id = int(request.session['account_id']))
            if request.method == 'POST':
                student = int(request.POST['student'])
                level = request.POST['extra_type']
                coin = 0
                if level == 'International':
                    coin = 500
                elif level == 'National':
                    coin = 300
                elif level == 'Inter University':
                    coin = 200
                else:
                    coin = 100

                getstaff = Staff.objects.filter(profile_id = int(request.session['account_id'])).first()
                getstd = Student.objects.filter(profile_id = student).first()
                extra_c = ExtraCirricular()
                extra_c.staff_profile = Profile.objects.get(pk = int(request.session['account_id']))
                extra_c.student_profile = Profile.objects.get(pk = student)
                extra_c.staff = Staff.objects.get(pk = getstaff.id)
                extra_c.student = Student.objects.get(pk = getstd.id)
                extra_c.level = level
                extra_c.coin = coin
                extra_c.save()

                std = Coin.objects.filter(profile_id=student).first()
                std_coins = std.coin
                std.coin = std_coins + coin
                std.save()
                messages.success(request, 'Extra cirricular added for selected student')
                return HttpResponseRedirect(reverse('st-extra-cirricular'))
                
            return render(request, 'staff/extra_cirricular.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def flipped(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Flipped Classroom Discussions'
            content['fl_title'] = ''
            content['stds'] = Student.objects.all()
            content['discussions'] = Flipped.objects.filter(staff_profile_id = int(request.session['account_id']))
            if request.method == 'POST':
                getstaff = Staff.objects.filter(profile_id = int(request.session['account_id'])).first()
                getstd = Student.objects.filter(profile_id = int(request.POST['student'])).first()

                flip = Flipped()
                flip.name = request.POST['name'].title()
                flip.staff_profile = Profile.objects.get(pk = int(request.session['account_id']))
                flip.student_profile = Profile.objects.get(pk = int(request.POST['student']))
                flip.staff = Staff.objects.get(pk = getstaff.id)
                flip.student = Student.objects.get(pk = getstd.id)
                flip.coin = int(request.POST['coin'])
                flip.badge = request.POST['badge']
                flip.save()
                content['fl_title'] = request.POST['name'].title()
                std = Coin.objects.filter(profile_id=int(request.POST['student'])).first()
                std_coins = std.coin
                std.coin = std_coins + int(request.POST['coin'])
                std.save()
                messages.success(request, 'Flipped discussion added for selected student')
                content['discussions'] = Flipped.objects.filter(staff_profile_id = int(request.session['account_id']))
                # return HttpResponseRedirect(reverse('st-flipped'))
                
            return render(request, 'staff/flipped/flipped.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))

def bestPerformer(request):
    if request.session.has_key('account_id'):
        if(request.session['account_role'] == 2):
            content = {}
            content['title'] = 'Best Performers'
            content['stds'] = Student.objects.all()
            content['discussions'] = BestPerfomer.objects.filter(staff_profile_id = int(request.session['account_id']))
            if request.method == 'POST':
                getstaff = Staff.objects.filter(profile_id = int(request.session['account_id'])).first()
                getstd = Student.objects.filter(profile_id = int(request.POST['student'])).first()

                best_performer = BestPerfomer()
                best_performer.title = request.POST['title'].title()
                best_performer.staff_profile = Profile.objects.get(pk = int(request.session['account_id']))
                best_performer.student_profile = Profile.objects.get(pk = int(request.POST['student']))
                best_performer.staff = Staff.objects.get(pk = getstaff.id)
                best_performer.student = Student.objects.get(pk = getstd.id)
                best_performer.save()
                messages.success(request, 'Best performer added for selected student')
                return HttpResponseRedirect(reverse('st-best-performer'))
            return render(request, 'staff/best.html', content)
        else:
            return HttpResponseForbidden()
    else:
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse('account-login'))
