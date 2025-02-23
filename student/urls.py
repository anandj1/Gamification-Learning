from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='std-index'),
    path('quiz', views.quiz, name='std-quiz'),
    path('play-quiz/<int:pk>', views.playQuiz, name='std-play-quiz'),
    path('submit-quiz/<int:pk>', views.submitQuiz, name='std-submit-quiz'),
    path('classroom-discussion', views.classRoomDiscussion, name='std-classroom-discussion'),
    path('flipped-classroom-discussion', views.flippedClassRoomDiscussion, name='std-flipped-classroom-discussion'),
    path('attendance', views.attendance, name='std-attendance'),
    path('extra-cirricular', views.extraCirricular, name='std-extra-cirricular'),
    path('event', views.event, name='std-event'),
    path('event-apply/<int:pk>', views.eventApply, name='std-event-apply'),
    path('feedback', views.feedback, name='std-feedback'),
]
