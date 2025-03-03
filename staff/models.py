from django.db import models
from account.models import Profile
from suadmin.models import Event

# Create your models here.
class Staff(models.Model):
    email = models.CharField(max_length=255, unique=True, null=True)
    contact = models.CharField(max_length=255, unique=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.name

    class Meta:
        db_table = 'staffs'


class Quiz(models.Model):
    name = models.CharField(max_length=255)
    each_point = models.IntegerField()
    total = models.IntegerField(default=0)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    generated_by_ai = models.BooleanField(default=False)
    ai_generation_prompt = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'quiz'


class QuizQA(models.Model):
    question = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
    right_option = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return self.question

    class Meta:
        db_table = 'quiz_qas'


class ClassRoomDiscussion(models.Model):
    name = models.CharField(max_length=255)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'classroom_discussion'


class Attendance(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day = models.CharField(max_length=50)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.profile.name} - {self.date}"

    class Meta:
        db_table = 'attendance_model'


  