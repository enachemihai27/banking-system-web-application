from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    iban = models.CharField(max_length=200, null=True)
    phone = PhoneNumberField()
    company_name = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    amount = models.PositiveIntegerField(default=0,validators=[
            MaxValueValidator(999999999),
            MinValueValidator(0),
        ])

class Transaction(models.Model):
    from_user = models.ForeignKey(User, null=True,  on_delete=models.CASCADE,  related_name='from_user')
    to_user = models.ForeignKey(User, null=True,  on_delete=models.CASCADE, related_name='to_user')
    date = models.DateTimeField(default=datetime.now, blank=True)
    details = models.CharField(max_length=250)
    code = models.IntegerField(validators=[
            MaxValueValidator(999999),
            MinValueValidator(10000),
        ])
    amount = models.PositiveIntegerField(null=True, validators=[
        MaxValueValidator(999999999),
        MinValueValidator(0),
    ])




# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()