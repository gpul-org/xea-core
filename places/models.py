from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    line1 = models.CharField(max_length=70)
    line2 = models.CharField(max_length=70)


class Place(models.Model):
    class Meta:
        app_label = 'places'

    name = models.CharField(max_length=140)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500)
    address = models.ForeignKey(Address)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
