from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    #the user in particpants has a related name to differentate it, because user has already been called in this same model, in host
    participants = models.ManyToManyField(User, related_name='participants', blank=True) 
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # ordering, to make the newest updated item the first on the list we add dash(-) at the beginning to invert it
    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # room = models.ForeignKey(Room, on_delete=models.SET_NULL) SET_NULL means if room is deleted, all msgs remain undeleted, CASCADE = opp
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] #this returns d first 50 char