from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='st-index'),
    path('student', views.student, name='st-student'),
    path('quiz-by-you', views.quiz, name='st-quiz'),
    path('qa-setup', views.quizQA, name='st-quiz-qa'),
    path('edit-qa-setup', views.editQuizQA, name='st-edit-quiz-qa'),
    path('classroom-disucssion', views.classroomDiscussion, name='st-cr-discussion'),
    path('classroom-disucssion-fill-coins/<int:pk>', views.classroomDiscussionFillCoins, name='st-cr-discussion-fill-coins'),
    path('classroom-disucssion-fill-coins-store/<int:pk>', views.classroomDiscussionFillCoinsPost, name='st-cr-discussion-fill-coins-store'),
    path('attendance-models', views.attendanceModel, name='st-att-model'),
    path('attendance-conduct/<int:pk>', views.attendanceConduct, name='st-att-conduct'),
    path('attendance-conduct-present/<int:pk>', views.attPresent, name='st-att-conduct-present'),
    path('attendance-conduct-absent/<int:pk>', views.attAbsent, name='st-att-conduct-absent'),
    path('attendance-conduct-leave/<int:pk>', views.attLeave, name='st-att-conduct-leave'),
    path('extra-cirricular', views.extraCirricular, name='st-extra-cirricular'),
    path('flipped', views.flippedDiscussionOverview, name='st-flipped'),
    path('best-performer', views.bestPerformer, name='st-best-performer'),
    path('resolve-discussion/<int:pk>', views.resolveDiscussion, name='resolve-discussion'),
]