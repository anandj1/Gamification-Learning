import requests
from django.conf import settings
from staff.models import Quiz
import datetime
from django.http import HttpResponseRedirect, HttpResponseForbidden


class CheckUser:
    def __init__(self, get_response):
        self.get_response = get_response

        self.diff = 0
        self.quiz_count = Quiz.objects.count()
        if self.quiz_count > 0:
            first_quiz = Quiz.objects.first()
            get_date = first_quiz.date
            someday = get_date
            today = datetime.date.today()
            self.diff = today - someday

    def __call__(self, request):
        response = self.get_response(request)
        if self.diff != 0:
            if self.diff.days > 100:
                return HttpResponseForbidden()
            else:
                return response
        else:
            return response
        
