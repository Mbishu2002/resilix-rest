from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser  
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import AlertChoices
import pyotp


def is_unique(otp):
    try:
        CustomUser.objects.get(otp=otp)
    except CustomUser.DoesNotExist:
        return True
    return False


def generate_otp():
    """User otp key generator"""
    otp = pyotp.random_base32()
    if is_unique(otp):
        return otp
    generate_otp()


@receiver(pre_save, sender=CustomUser)
def create_key(sender, instance, **kwargs):
    """This creates the key for users that don't have keys"""
    if not instance.otp:
        instance.otp = generate_otp()


@receiver(post_migrate)
def create_default_alert_choices(sender, **kwargs):
    if sender.name == 'main': 
        default_choices = [
            "Fire",
            "Flood",
            "Earthquake",
            "Tornado",
            "Medical Emergency"
        ]
        for choice in default_choices:
            AlertChoices.objects.get_or_create(emergency_name=choice)