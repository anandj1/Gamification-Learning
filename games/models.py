from statistics import mode
from django.db import models
from account.models import Profile
from student.models import Student

# Create your models here.
class GamesPlayed(models.Model):
    game = models.CharField(max_length=100)
    coins = models.IntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    seconds = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.profile.name

    class Meta:
        db_table = 'games_played'
