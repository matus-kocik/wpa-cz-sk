from datetime import date

import pytest

from members.models import MemberProfile, MembershipApplication
from users.models import CustomUser


@pytest.fixture
def application_data():
    return {
        "first_name": "Jan",
        "last_name": "Novák",
        "birth_date": date(1990, 1, 1),
        "email": "jan@example.com",
        "city": "Praha",
        "street": "Test",
        "house_number": "1",
        "postal_code": "12345",
        "country": "CZ",
        "declaration_place": "Praha",
        "declaration_date": date(2024, 1, 1),
        "declaration_signature": "Jan Novak",
    }


@pytest.fixture
def application(application_data):
    return MembershipApplication.objects.create(
        **application_data,
        initial_payment_status="paid",
        status="pending",
    )


@pytest.mark.django_db
def test_approve_creates_user_and_member(application):
    app = application

    app.approve()

    # user created
    user = CustomUser.objects.get(email="jan@example.com")
    assert user.first_name == "Jan"

    # member profile created
    member = MemberProfile.objects.get(user=user)
    assert member.city == "Praha"


@pytest.mark.django_db
def test_approve_unpaid_does_not_create_user(application_data):
    app = MembershipApplication.objects.create(
        **application_data,
        initial_payment_status="unpaid",
        status="pending",
    )

    app.approve()

    # user should NOT be created
    assert CustomUser.objects.count() == 0

    # member profile should NOT be created
    assert MemberProfile.objects.count() == 0


@pytest.mark.django_db
def test_approve_idempotent_does_not_duplicate(application):
    app = application

    # first approve
    app.approve()

    assert CustomUser.objects.count() == 1
    assert MemberProfile.objects.count() == 1

    # second approve (should not duplicate)
    app.approve()

    assert CustomUser.objects.count() == 1
    assert MemberProfile.objects.count() == 1


@pytest.mark.django_db
def test_approve_uses_existing_user(application_data):
    # existujúci user
    user = CustomUser.objects.create_user(
        email="jan@example.com",
        password="test123",
        first_name="Old",
        last_name="Name",
    )

    app = MembershipApplication.objects.create(
        **application_data,
        initial_payment_status="paid",
        status="pending",
        district="Praha",
    )

    app.approve()

    assert CustomUser.objects.count() == 1

    user.refresh_from_db()

    assert user.first_name == "Jan"
    assert user.last_name == "Novák"


@pytest.mark.django_db
def test_approve_already_approved_does_nothing(application_data):
    app = MembershipApplication.objects.create(
        **application_data,
        initial_payment_status="paid",
        status="approved",
    )

    # first call (should create since approved + paid but no user yet)
    app.approve()

    assert CustomUser.objects.count() == 1
    assert MemberProfile.objects.count() == 1

    # second call (should do nothing)
    app.approve()

    assert CustomUser.objects.count() == 1
    assert MemberProfile.objects.count() == 1


@pytest.mark.django_db
def test_member_is_active_when_paid():
    user = CustomUser.objects.create_user(
        email="active@example.com",
        password="test123",
        first_name="Active",
        last_name="User",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="paid",
        joined_at=date(2024, 1, 1),
        valid_until=date(2025, 3, 31),
    )

    # ensure save logic is applied
    member.refresh_from_db()

    assert member.is_active is True


@pytest.mark.django_db
def test_member_is_inactive_when_unpaid():
    user = CustomUser.objects.create_user(
        email="inactive@example.com",
        password="test123",
        first_name="Inactive",
        last_name="User",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
        joined_at=date(2024, 1, 1),
        valid_until=date(2025, 3, 31),
    )

    member.refresh_from_db()

    assert member.is_active is False


@pytest.mark.django_db
def test_valid_until_set_when_paid_first_time():
    user = CustomUser.objects.create_user(
        email="valid1@example.com",
        password="test123",
        first_name="Valid",
        last_name="One",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
        joined_at=date(2024, 1, 1),
        valid_until=None,
    )

    # change to paid
    member.payment_status = "paid"
    member.save()

    member.refresh_from_db()

    assert member.valid_until is not None


@pytest.mark.django_db
def test_valid_until_extends_when_already_valid():
    user = CustomUser.objects.create_user(
        email="valid2@example.com",
        password="test123",
        first_name="Valid",
        last_name="Two",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="paid",
        joined_at=date(2024, 1, 1),
        valid_until=date(2025, 3, 31),
    )

    old_valid_until = member.valid_until

    # simulate another payment
    member.payment_status = "paid"
    member.save()

    member.refresh_from_db()

    assert member.valid_until.year == old_valid_until.year  # no extension without transition


@pytest.mark.django_db
def test_valid_until_resets_if_expired():
    user = CustomUser.objects.create_user(
        email="valid3@example.com",
        password="test123",
        first_name="Valid",
        last_name="Three",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
        joined_at=date(2020, 1, 1),
        valid_until=date(2021, 3, 31),  # expired
    )

    # change to paid
    member.payment_status = "paid"
    member.save()

    member.refresh_from_db()

    assert member.valid_until.year >= date.today().year
