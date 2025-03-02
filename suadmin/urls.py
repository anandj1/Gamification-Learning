from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'su-index'),
    path('staff', views.staff, name = 'su-staff'),
    path('predict', views.predict, name='su-predict'),
    path('event', views.event, name='su-event'),
    path('event-participants/<int:pk>', views.eventParti, name='su-event-parti'),
    path('feedback', views.feedback, name='su-feedback'),
    path('train', views.train, name='su-train'),
   

]