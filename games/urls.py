from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='std-games-index'),
    path('memory-puzzle', views.memoryPuzzle, name='games-memory-puzzle'),
    path('hangman', views.hangman, name='games-hangman'),
    path('keyboard-junp', views.keyboardjunp, name='games-keyboardjunp'),
]
