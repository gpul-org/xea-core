from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _



class UserProfile(models.Model):
    class Meta:
        app_label = 'accounts'

    # Gender strings
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'

    GENDER_CHOICES = ((MALE, _('Male')), (FEMALE, _('Female')), (OTHER, _('Other')))

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField(null=True)
    nationality = models.CharField(max_length=140, blank=True)  # Or use django_countries?
    location = models.CharField(max_length=300, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    def __str__(self):
        return u'Profile of user: %s' % self.user.username
