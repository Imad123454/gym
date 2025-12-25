from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def create_director(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        director_role = Role.objects.get(name="director")
        instance.role = director_role
        instance.save()
        Director.objects.get_or_create(user=instance)


from gmsapp.services.telegram import send_inquiry_to_telegram

@receiver(post_save, sender=Inquiry)
def inquiry_created_send_telegram(sender, instance, created, **kwargs):
    if created:
        send_inquiry_to_telegram(instance)