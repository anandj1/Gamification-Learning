from django.db import models
from account.models import Profile

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    fee = models.FloatField()
    redeem = models.FloatField()
    on_date = models.DateField()
    created_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'events'

class EventParticipants(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    redeem = models.FloatField()
    date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.profile.name

    class Meta:
        db_table = 'event_participants'