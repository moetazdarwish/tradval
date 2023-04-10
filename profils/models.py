from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token
# Create your models here.
from django.db.models.signals import post_save


def Tokencreatoruser(sender, instance, created, *args, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)
post_save.connect(Tokencreatoruser, sender=User)