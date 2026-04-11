from datetime import date

import pytest
from django.core.exceptions import ValidationError

from articles.models import Contributor
from members.models import MemberProfile
from users.models import CustomUser


# simple fixture for member_profile (reuse minimal required fields)
@pytest.fixture
def member_profile(db):
    user = CustomUser.objects.create_user(
        email="fixture@example.com",
        password="test123",
        first_name="Fixture",
        last_name="User",
    )

    return MemberProfile.objects.create(
        user=user,
        payment_status="paid",
        joined_at=date(2024, 1, 1),
        valid_until=date(2025, 3, 31),
    )


@pytest.mark.django_db
def test_contributor_requires_name_or_member():
    contributor = Contributor()

    with pytest.raises(ValidationError):
        contributor.full_clean()


@pytest.mark.django_db
def test_contributor_valid_with_name_only():
    contributor = Contributor(name="John Doe", role="author")

    # should not raise
    contributor.full_clean()


@pytest.mark.django_db
def test_contributor_valid_with_member(member_profile):
    contributor = Contributor(member=member_profile, role="author")

    # should not raise
    contributor.full_clean()
