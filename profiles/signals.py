from django.db.models.signals import post_save
from django.dispatch import receiver

from members.models import MemberProfile
from profiles.models import PublicProfile


@receiver(post_save, sender=MemberProfile)
def create_public_profile(sender, instance, created, **kwargs):
    if created:
        PublicProfile.objects.get_or_create(member=instance)


@receiver(post_save, sender=MemberProfile)
def update_public_profile(sender, instance, **kwargs):
    if hasattr(instance, "public_profile"):
        profile = instance.public_profile
        profile.save()
