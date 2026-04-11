from datetime import date

import pytest

from breeding.models import BreedingRecord, BreedingReport
from members.models import MemberProfile
from taxonomy.models import Family, Genus, Species
from users.models import CustomUser


@pytest.fixture
def member_profile(db):
    user = CustomUser.objects.create_user(
        email="breeding@example.com",
        password="test123",
        first_name="Breed",
        last_name="User",
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


@pytest.fixture
def breeding_report(member_profile):
    return BreedingReport.objects.create(
        member=member_profile,
        year=2024,
    )


@pytest.mark.django_db
def test_total_count_of_species(breeding_report, species):
    record = BreedingRecord.objects.create(
        report=breeding_report,
        species=species,
        number_of_males=2,
        number_of_females=3,
    )

    assert record.total_count_of_species == 5


@pytest.mark.django_db
def test_total_count_offspring(breeding_report, species):
    record = BreedingRecord.objects.create(
        report=breeding_report,
        species=species,
        number_of_male_offspring=1,
        number_of_female_offspring=2,
        number_of_unsexed_offspring=3,
    )

    assert record.total_count_offspring == 6
