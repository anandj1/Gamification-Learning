from operator import mod
from tkinter.tix import Tree
from django.db import models
from account.models import Profile
from staff.models import Quiz, QuizQA, ClassRoomDiscussion, Staff, Attendance
from django.db import models
from account.models import Profile
from staff.models import Quiz, QuizQA, ClassRoomDiscussion, Staff, Attendance
from suadmin.models import Event

# Create your models here.


class Student(models.Model):
    rollno = models.IntegerField()
    enrollment = models.BigIntegerField(unique=True)
    email = models.CharField(max_length=255,unique=True,null=True)
    contact = models.CharField(max_length=255,unique=True,null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.name

    class Meta:
        db_table = 'students'

class Coin(models.Model):
    coin = models.IntegerField(default=0)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.student.profile.name

    class Meta:
        db_table = 'student_coins'


class StudentQuiz(models.Model):
    quiz = models.ForeignKey("staff.Quiz", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    profile = models.ForeignKey("account.Profile", on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    date_started = models.DateField(auto_now=True)
    date_finished = models.DateField(null=True, blank=True)
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
    seconds = models.FloatField(null=True, blank=True)


    def __str__(self):
        return self.quiz.name

    class Meta:
        db_table = 'student_quiz'


class StudentQuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQA, on_delete=models.CASCADE)
    option = models.CharField(max_length=255)
    is_right = models.BooleanField()
    coins = models.FloatField(default=0)

    def __str__(self):
        return self.question.question

    class Meta:
        db_table = 'student_quiz_questions'


class StudentCRDiscussion(models.Model):
    discussion = models.ForeignKey(ClassRoomDiscussion, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    coins = models.FloatField(default=0)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.discussion.name

    class Meta:
        db_table = 'student_classroom_discussion'


class StudentAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    staff_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='staff_profile')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='student_profile')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    is_extra = models.BooleanField(default=False)
    coin = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attendance'


class ExtraCirricular(models.Model):
    staff_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='staff_profile_extra')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='student_profile_extra')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    level = models.CharField(max_length=50)
    coin = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'extra_circullar'

class Flipped(models.Model):
    staff_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='staff_profile_flipped')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='student_profile_flipped')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    coin = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)
    badge = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name + "- Coins: " + str(self.coin)

    class Meta:
        db_table = 'flipped'


class BestPerfomer(models.Model):
    staff_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='staff_profile_best_attendance')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='student_profile_best_attendance')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.student

    class Meta:
        db_table = 'best_perfomer'


   
class FlippedDiscussion(models.Model):
    event = models.ForeignKey('suadmin.Event', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.profile.name}: {self.question[:50]}"

    class Meta:
        db_table = 'flipped_discussions'
        ordering = ['-date']  # Most recent first


class FlippedReply(models.Model):
    discussion = models.ForeignKey(FlippedDiscussion, on_delete=models.CASCADE, related_name='replies')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.student.profile.name}: {self.content[:50]}"

    class Meta:
        db_table = 'flipped_replies'
        ordering = ['date']  # Oldest first


class Feedback(models.Model):
    staff_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='staff_profile_feedback')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    student_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='student_profile_feedback')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=255)
    rating = models.FloatField(default=0)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.feedback

    class Meta:
        db_table = 'feedbacks'