from datetime import date

import pytest
from django.core.exceptions import ValidationError

from members.models import MemberProfile
from studbook.models import BirdRecord
from taxonomy.models import Family, Genus, Species
from users.models import CustomUser


@pytest.fixture
def member_profile(db):
    user = CustomUser.objects.create_user(
        email="bird@example.com",
        password="test123",
        first_name="Bird",
        last_name="Owner",
    )

    return MemberProfile.objects.create(
        user=user,
        payment_status="paid",
        joined_at=date(2024, 1, 1),
        valid_until=date(2025, 3, 31),
    )


@pytest.fixture
def species(db):
    family = Family.objects.create(latin_name="Testidae")
    genus = Genus.objects.create(latin_name="Testus", family=family)
    return Species.objects.create(latin_name="Testus birdus", genus=genus)


@pytest.mark.django_db
def test_bird_cannot_be_its_own_father(member_profile, species):
    bird = BirdRecord.objects.create(member=member_profile, species=species)
    bird.father = bird

    with pytest.raises(ValidationError):
        bird.full_clean()


@pytest.mark.django_db
def test_bird_cannot_be_its_own_mother(member_profile, species):
    bird = BirdRecord.objects.create(member=member_profile, species=species)
    bird.mother = bird

    with pytest.raises(ValidationError):
        bird.full_clean()


@pytest.mark.django_db
def test_father_cannot_be_female(member_profile, species):
    father = BirdRecord.objects.create(
        member=member_profile,
        species=species,
        sex="female",
    )

    bird = BirdRecord(
        member=member_profile,
        species=species,
        father=father,
    )

    with pytest.raises(ValidationError):
        bird.full_clean()


@pytest.mark.django_db
def test_mother_cannot_be_male(member_profile, species):
    mother = BirdRecord.objects.create(
        member=member_profile,
        species=species,
        sex="male",
    )

    bird = BirdRecord(
        member=member_profile,
        species=species,
        mother=mother,
    )

    with pytest.raises(ValidationError):
        bird.full_clean()
