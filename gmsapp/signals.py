from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role, Director

@receiver(post_save, sender=User)
def create_director(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        director_role = Role.objects.get(name="director")
        instance.role = director_role
        instance.save()
        Director.objects.get_or_create(user=instance)
