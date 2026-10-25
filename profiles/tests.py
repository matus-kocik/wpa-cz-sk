import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from members.models import MemberProfile
from profiles.models import ProfileGallery, ProfileVideo, PublicProfile
from users.models import CustomUser


@pytest.fixture
def member():
    user = CustomUser.objects.create_user(
        email="profile@example.com",
        password="test123",
        first_name="Jan",
        last_name="Novák",
    )

    return MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
        city="Praha",
        country="CZ",
    )


@pytest.mark.django_db
def test_public_profile_is_created_for_member(member):
    assert PublicProfile.objects.filter(member=member).exists()


@pytest.mark.django_db
def test_public_profile_slug_is_generated(member):
    profile = PublicProfile.objects.get(member=member)

    assert profile.slug
    assert profile.slug.startswith("jan-novak-")


@pytest.mark.django_db
def test_location_display(member):
    profile = PublicProfile.objects.get(member=member)

    assert profile.location_display == "Praha, CZ"


@pytest.mark.django_db
def test_additional_info_display_prefers_profile_value(member):
    profile = PublicProfile.objects.get(member=member)
    profile.additional_info = "Informace z veřejného profilu"
    profile.save()

    assert profile.additional_info_display == "Informace z veřejného profilu"


@pytest.mark.django_db
def test_additional_info_display_falls_back_to_member_notes(member):
    member.notes = "Interní poznámka člena"
    member.save()

    profile = PublicProfile.objects.get(member=member)

    assert profile.additional_info_display == "Interní poznámka člena"


@pytest.mark.django_db
def test_profile_allows_max_three_videos(member):
    profile = PublicProfile.objects.get(member=member)

    for index in range(3):
        ProfileVideo.objects.create(
            profile=profile,
            url=f"https://youtube.com/watch?v=test{index}",
        )

    with pytest.raises(ValidationError, match="Maximálně 3 videa"):
        ProfileVideo.objects.create(
            profile=profile,
            url="https://youtube.com/watch?v=test4",
        )


@pytest.mark.django_db
def test_profile_allows_max_six_gallery_images(member, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    profile = PublicProfile.objects.get(member=member)

    for index in range(6):
        ProfileGallery.objects.create(
            profile=profile,
            image=f"profiles/gallery/test{index}.jpg",
        )

    with pytest.raises(ValidationError, match="Maximálně 6 fotografií"):
        ProfileGallery.objects.create(
            profile=profile,
            image="profiles/gallery/test6.jpg",
        )


@pytest.mark.django_db
def test_profile_allows_only_one_primary_image(member, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    profile = PublicProfile.objects.get(member=member)

    ProfileGallery.objects.create(
        profile=profile,
        image="profiles/gallery/primary1.jpg",
        is_primary=True,
    )

    with pytest.raises(
        ValidationError,
        match="Každý profil může mít pouze jednu hlavní fotografii",
    ):
        ProfileGallery.objects.create(
            profile=profile,
            image="profiles/gallery/primary2.jpg",
            is_primary=True,
        )


@pytest.mark.django_db
def test_replacing_avatar_deletes_old_file(member, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    profile = PublicProfile.objects.get(member=member)

    profile.avatar = SimpleUploadedFile(
        "old.jpg",
        b"old image",
        content_type="image/jpeg",
    )
    profile.save()

    old_path = profile.avatar.path
    assert profile.avatar.storage.exists(old_path)

    profile.avatar = SimpleUploadedFile(
        "new.jpg",
        b"new image",
        content_type="image/jpeg",
    )
    profile.save()

    assert not profile.avatar.storage.exists(old_path)
    assert profile.avatar.storage.exists(profile.avatar.path)


@pytest.mark.django_db
def test_deleting_profile_deletes_avatar_file(member, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    profile = PublicProfile.objects.get(member=member)

    profile.avatar = SimpleUploadedFile(
        "avatar.jpg",
        b"avatar image",
        content_type="image/jpeg",
    )
    profile.save()

    avatar_path = profile.avatar.path
    storage = profile.avatar.storage

    assert storage.exists(avatar_path)

    profile.delete()

    assert not storage.exists(avatar_path)


@pytest.mark.django_db
def test_replacing_gallery_image_deletes_old_file(member, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    profile = PublicProfile.objects.get(member=member)

    item = ProfileGallery.objects.create(
        profile=profile,
        image=SimpleUploadedFile(
            "old.jpg",
            b"old image",
            content_type="image/jpeg",
        ),
    )

    old_path = item.image.path
    storage = item.image.storage

    assert storage.exists(old_path)

    item.image = SimpleUploadedFile(
        "new.jpg",
        b"new image",
        content_type="image/jpeg",
    )
    item.save()

    assert not storage.exists(old_path)
    assert storage.exists(item.image.path)


@pytest.mark.django_db
def test_deleting_gallery_item_deletes_file(member, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    profile = PublicProfile.objects.get(member=member)

    item = ProfileGallery.objects.create(
        profile=profile,
        image=SimpleUploadedFile(
            "gallery.jpg",
            b"gallery image",
            content_type="image/jpeg",
        ),
    )

    image_path = item.image.path
    storage = item.image.storage

    assert storage.exists(image_path)

    item.delete()

    assert not storage.exists(image_path)


@pytest.mark.django_db
def test_public_profile_visible_to_anonymous_when_public(member, client):
    profile = PublicProfile.objects.get(member=member)
    profile.is_public = True
    profile.save()

    response = client.get(
        reverse("public_profile_detail", kwargs={"slug": profile.slug})
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_private_profile_hidden_from_anonymous(member, client):
    profile = PublicProfile.objects.get(member=member)
    profile.is_public = False
    profile.save()

    response = client.get(
        reverse("public_profile_detail", kwargs={"slug": profile.slug})
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_can_view_private_profile(member, client):
    profile = PublicProfile.objects.get(member=member)
    profile.is_public = False
    profile.save()

    client.force_login(member.user)

    response = client.get(
        reverse("public_profile_detail", kwargs={"slug": profile.slug})
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_other_logged_in_user_cannot_view_private_profile(member, client):
    profile = PublicProfile.objects.get(member=member)
    profile.is_public = False
    profile.save()

    other_user = CustomUser.objects.create_user(
        email="other@example.com",
        password="test123",
        first_name="Other",
        last_name="User",
    )
    MemberProfile.objects.create(
        user=other_user,
        payment_status="unpaid",
    )

    client.force_login(other_user)

    response = client.get(
        reverse("public_profile_detail", kwargs={"slug": profile.slug})
    )

    assert response.status_code == 404
