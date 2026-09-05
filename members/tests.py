from datetime import date
from unittest.mock import patch

import pytest

from members.forms import MembershipApplicationForm
from members.models import MemberProfile, MembershipApplication
from profiles.models import PublicProfile
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

    with pytest.raises(ValueError, match="Cannot approve unpaid application"):
        app.approve()

    assert CustomUser.objects.count() == 0
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

    assert (
        member.valid_until.year == old_valid_until.year
    )  # no extension without transition


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


@pytest.mark.django_db
def test_icch_number_is_assigned_automatically():
    user = CustomUser.objects.create_user(
        email="icch1@example.com",
        password="test123",
        first_name="ICCH",
        last_name="One",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
    )

    assert member.icch_number == "001"


@pytest.mark.django_db
def test_icch_numbers_increment():
    user1 = CustomUser.objects.create_user(
        email="icch1@example.com",
        password="test123",
        first_name="ICCH",
        last_name="One",
    )
    user2 = CustomUser.objects.create_user(
        email="icch2@example.com",
        password="test123",
        first_name="ICCH",
        last_name="Two",
    )

    member1 = MemberProfile.objects.create(
        user=user1,
        payment_status="unpaid",
    )
    member2 = MemberProfile.objects.create(
        user=user2,
        payment_status="unpaid",
    )

    assert member1.icch_number == "001"
    assert member2.icch_number == "002"


@pytest.mark.django_db
def test_icch_number_cannot_be_changed():
    user = CustomUser.objects.create_user(
        email="icch@example.com",
        password="test123",
        first_name="ICCH",
        last_name="User",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
    )

    original_icch = member.icch_number
    member.icch_number = "999"

    with pytest.raises(ValueError, match="ICCH number cannot be changed"):
        member.save()

    member.refresh_from_db()
    assert member.icch_number == original_icch


@pytest.mark.django_db
def test_approve_creates_public_profile(application):
    application.approve()

    user = CustomUser.objects.get(email="jan@example.com")
    member = MemberProfile.objects.get(user=user)

    assert PublicProfile.objects.filter(member=member).exists()


@pytest.mark.django_db
def test_application_remains_saved_when_email_sending_fails(client, settings):
    settings.TURNSTILE_SITE_KEY = ""
    settings.TURNSTILE_SECRET_KEY = ""

    data = {
        "first_name": "Jan",
        "last_name": "Novák",
        "birth_date": "1990-01-01",
        "city": "Praha",
        "street": "Test",
        "house_number": "1",
        "postal_code": "12345",
        "district": "Praha",
        "country": "CZ",
        "phone_number": "",
        "email": "mailfail@example.com",
        "notes": "",
        "declaration_place": "Praha",
        "declaration_date": date.today().strftime("%d.%m.%Y"),
        "declaration_signature": "Jan Novak",
        "agree_membership_terms": "on",
        "agree_gdpr": "on",
        "website": "",
        "turnstile": "test",
    }

    with patch("core.forms.requests.post") as turnstile_post:
        turnstile_post.return_value.json.return_value = {"success": True}

        with patch(
            "members.views.EmailMultiAlternatives.send",
            side_effect=Exception("SMTP failure"),
        ):
            response = client.post("/prihlaska/", data=data)

    assert MembershipApplication.objects.filter(email="mailfail@example.com").exists()

    assert response.status_code == 302
    assert response.url == "/prihlaska/"


@pytest.mark.django_db
def test_approve_sets_correct_membership_validity(application):
    application.approve()

    member = MemberProfile.objects.get(user=application.user)

    today = date.today()

    assert member.joined_at == application.declaration_date
    assert member.valid_until == date(today.year + 1, 3, 31)
    assert member.payment_status == "paid"
    assert member.is_active is True


@pytest.mark.django_db
def test_membership_renewal_after_payment():
    user = CustomUser.objects.create_user(
        email="renewal@example.com",
        password="test123",
        first_name="Renewal",
        last_name="User",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="unpaid",
        valid_until=date(2026, 3, 31),
    )

    member.payment_status = "paid"
    member.save()
    member.refresh_from_db()

    today = date.today()

    assert member.payment_status == "paid"
    assert member.is_active is True
    assert member.valid_until == date(today.year + 1, 3, 31)


@pytest.mark.django_db
def test_membership_early_renewal_extends_validity():
    user = CustomUser.objects.create_user(
        email="early-renewal@example.com",
        password="test123",
        first_name="Early",
        last_name="Renewal",
    )

    member = MemberProfile.objects.create(
        user=user,
        payment_status="paid",
    )

    original_valid_until = member.valid_until

    # Simulujeme začiatok nového platobného cyklu.
    member.payment_status = "unpaid"
    member.save()

    member.payment_status = "paid"
    member.save()
    member.refresh_from_db()

    assert member.payment_status == "paid"
    assert member.is_active is True
    assert member.valid_until == date(original_valid_until.year + 1, 3, 31)


@pytest.mark.django_db
def test_membership_form_rejects_duplicate_active_email(application_data):
    MembershipApplication.objects.create(
        **application_data,
        initial_payment_status="unpaid",
        status="pending",
    )

    form = MembershipApplicationForm(
        data={
            **application_data,
            "birth_date": "1990-01-01",
            "declaration_date": "01.01.2024",
            "district": "Praha",
            "agree_membership_terms": "on",
            "agree_gdpr": "on",
            "website": "",
            "turnstile": "test",
        }
    )

    with patch("core.forms.requests.post") as turnstile_post:
        turnstile_post.return_value.json.return_value = {"success": True}
        assert not form.is_valid()

    assert "email" in form.errors


@pytest.mark.django_db
def test_membership_form_allows_email_after_rejected_application(application_data):
    MembershipApplication.objects.create(
        **application_data,
        initial_payment_status="unpaid",
        status="rejected",
    )

    form = MembershipApplicationForm(
        data={
            **application_data,
            "birth_date": "1990-01-01",
            "declaration_date": "01.01.2024",
            "district": "Praha",
            "agree_membership_terms": "on",
            "agree_gdpr": "on",
            "website": "",
            "turnstile": "test",
        }
    )

    with patch("core.forms.requests.post") as turnstile_post:
        turnstile_post.return_value.json.return_value = {"success": True}
        assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_membership_form_rejects_honeypot(application_data):
    form = MembershipApplicationForm(
        data={
            **application_data,
            "birth_date": "1990-01-01",
            "declaration_date": "01.01.2024",
            "district": "Praha",
            "agree_membership_terms": "on",
            "agree_gdpr": "on",
            "website": "spam.example.com",
            "turnstile": "test",
        }
    )

    with patch("core.forms.requests.post") as turnstile_post:
        turnstile_post.return_value.json.return_value = {"success": True}
        assert not form.is_valid()

    assert "website" in form.errors
