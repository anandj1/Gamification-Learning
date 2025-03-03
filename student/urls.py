from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='std-index'),
    path('quiz', views.quiz, name='std-quiz'),
    path('play-quiz/<int:pk>', views.playQuiz, name='std-play-quiz'),
    path('submit-quiz/<int:pk>', views.submitQuiz, name='std-submit-quiz'),
    path('classroom-discussion', views.classRoomDiscussion, name='std-classroom-discussion'),
    # Updated: flipped discussion now includes event_id for access control
    path('flipped-classroom-discussion/<int:event_id>/', views.flippedClassRoomDiscussion, name='std-flipped-classroom-discussion'),
    # New endpoints for asking and replying
    path('flipped-discussion/ask/<int:event_id>/', views.askFlippedQuestion, name='std-flipped-ask'),
    path('flipped-discussion/reply/<int:discussion_id>/', views.replyFlippedQuestion, name='std-flipped-reply'),
    path('attendance', views.attendance, name='std-attendance'),
    path('extra-cirricular', views.extraCirricular, name='std-extra-cirricular'),
    path('event', views.event, name='std-event'),
    path('event-apply/<int:pk>', views.eventApply, name='std-event-apply'),
    path('feedback', views.feedback, name='std-feedback'),
    path('lecture', views.lecture, name='std-lecture'),
    path('student/python-lecture/', views.python_lecture, name='python-lecture'),
    path('student/sql-lecture/', views.sql_lecture, name='sql-lecture'),
    path('student/web-lecture/', views.web_lecture, name='web-lecture'),
]