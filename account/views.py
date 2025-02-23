from urllib import response
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from account.models import Roles, Profile
from django.db.models import Q
from django.contrib import messages
from staff.models import Staff

from student.models import Student

# Create your views here.
def insertRoles():
    roles = Roles.objects.count()
    if(roles < 1):
        role = Roles()
        role.name = 'Admin'
        role.save()
        role = Roles()
        role.name = 'Staff'
        role.save()
        role = Roles()
        role.name = 'Student'
        role.save()

def insertAdmin():
    profiles = Profile.objects.count()
    if(profiles < 1):
        profile = Profile()
        profile.name = 'Admin'
        profile.username = 'admin'
        profile.password = 'admin'
        profile.role = Roles.objects.get(pk = 1)
        profile.save()

def login(request):
    content = {}
    insertRoles()
    insertAdmin()
    content['title'] = 'Login'
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        # select * from profiles where username = admin and password = admin limit 1
        profile = Profile.objects.filter(username = username, password = password).first()
        if(profile):
            request.session['account_name'] = profile.name
            request.session['account_id'] = profile.id
            request.session['account_role'] = profile.role_id

            if(profile.role_id == 3):
                std = Student.objects.filter(profile_id = int(request.session['account_id'])).first()
                request.session['student_id'] = std.id

                # Set cookie for games
                response = HttpResponseRedirect(reverse('std-index'))
                response.set_cookie('ck_std_name', str(request.session['account_name']), 86400)
                response.set_cookie('ck_std_profile_id', str(request.session['account_id']), 86400)
                response.set_cookie('ck_std_id', str(request.session['student_id']), 86400)
                print(response)
                return response
            elif(profile.role_id == 2):
                std = Staff.objects.filter(profile_id = int(request.session['account_id'])).first()
                request.session['staff_id'] = std.id
                return HttpResponseRedirect(reverse('st-index'))
            else:
                return HttpResponseRedirect(reverse('su-index'))
        else:
            messages.error(request, "Credentials provided does not matched in our records.")
    return render(request, 'account/login.html', content)

def logout(request):
    del request.session['account_name']
    del request.session['account_role']
    del request.session['account_id']
    messages.success(request, "You are logged out!.")
    return HttpResponseRedirect(reverse('account-login'))

def getCookies(request):
    cks = dict(csid = request.COOKIES['ck_std_id'], cpid = request.COOKIES['ck_std_profile_id'], ckname = request.COOKIES['ck_std_name'])
    return cks