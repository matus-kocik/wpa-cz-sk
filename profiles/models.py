from django.db import models

from common.models import SlugModel, TimeStampedModel


class PublicProfile(TimeStampedModel, SlugModel):
    member = models.OneToOneField(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="public_profile"
    )
    species = models.ManyToManyField(
        "taxonomy.Species",
        blank=True,
        related_name="public_profiles",
        verbose_name="Chované druhy",
    )
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True
    )
    location = models.CharField(max_length=150, blank=True)
    public_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    breeding_focus = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # visibility
    is_public = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    show_location = models.BooleanField(default=True)
    show_breeding = models.BooleanField(default=True)

    # extra
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Veřejný profil"
        verbose_name_plural = "Veřejné profily"

    def __str__(self):
        return self.display_name or str(self.member)
