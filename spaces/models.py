from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    street_name = models.CharField(max_length=140)
    civic = models.CharField(max_length=20)
    floor = models.IntegerField(blank=True)
    door = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=140)
    postal_code = models.IntegerField(blank=True)
    region = models.CharField(max_length=140)
    nation = models.CharField(max_length=140)


class Place(models.Model):
    class Meta:
        app_label = 'spaces'

    name = models.CharField(max_length=140)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500)
    address = models.ForeignKey(Address)
