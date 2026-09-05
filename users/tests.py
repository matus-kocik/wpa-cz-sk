import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from users.models import CustomUser


@pytest.mark.django_db
def test_create_user_basic():
    user = CustomUser.objects.create_user(
        email="TEST@EMAIL.COM ",
        password="pass123",
        first_name="John",
        last_name="Doe",
    )

    assert user.email == "test@email.com"
    assert user.check_password("pass123")
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError):
        CustomUser.objects.create_user(
            email="",
            password="pass123",
        )


@pytest.mark.django_db
def test_create_user_without_password():
    user = CustomUser.objects.create_user(
        email="test@test.com",
        first_name="John",
        last_name="Doe",
    )

    assert user.has_usable_password() is False


@pytest.mark.django_db
def test_create_superuser():
    user = CustomUser.objects.create_superuser(
        email="admin@test.com",
        password="pass123",
        first_name="Admin",
        last_name="User",
    )

    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_create_superuser_invalid_flags():
    with pytest.raises(ValueError):
        CustomUser.objects.create_superuser(
            email="admin@test.com",
            password="pass123",
            is_staff=False,
        )


@pytest.mark.django_db
def test_get_by_natural_key_case_insensitive():
    user = CustomUser.objects.create_user(
        email="test@test.com",
        first_name="John",
        last_name="Doe",
    )

    found = CustomUser.objects.get_by_natural_key("TEST@TEST.COM")

    assert found == user


@pytest.mark.django_db
def test_get_by_natural_key_empty():
    with pytest.raises(ValueError):
        CustomUser.objects.get_by_natural_key("")


def test_full_name_property():
    user = CustomUser(first_name="John", last_name="Doe")
    assert user.full_name == "John Doe"


@pytest.mark.django_db
def test_str_uses_full_name():
    user = CustomUser.objects.create_user(
        email="test@test.com",
        first_name="John",
        last_name="Doe",
    )

    assert str(user) == "John Doe"


@pytest.mark.django_db
def test_str_fallback_to_email():
    with pytest.raises(ValidationError):
        CustomUser.objects.create_user(
            email="test@test.com",
            first_name="",
            last_name="",
        )


@pytest.mark.django_db
def test_clean_requires_first_name():
    user = CustomUser(
        email="test@test.com",
        first_name="",
        last_name="Doe",
    )

    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_clean_requires_last_name():
    user = CustomUser(
        email="test@test.com",
        first_name="John",
        last_name="",
    )

    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_clean_normalizes_email():
    user = CustomUser(
        email="TEST@TEST.COM ",
        first_name="John",
        last_name="Doe",
    )

    user.set_password("pass123")
    user.clean()

    assert user.email == "test@test.com"


@pytest.mark.django_db
def test_save_calls_full_clean():
    user = CustomUser(
        email="test@test.com",
        first_name="",
        last_name="Doe",
    )

    with pytest.raises(ValidationError):
        user.save()


@pytest.mark.django_db
def test_create_superuser_rejects_is_superuser_false():
    with pytest.raises(ValueError):
        CustomUser.objects.create_superuser(
            email="admin2@test.com",
            password="pass123",
            first_name="Admin",
            last_name="User",
            is_superuser=False,
        )


@pytest.mark.django_db
def test_create_user_rejects_missing_first_name():
    with pytest.raises(ValidationError):
        CustomUser.objects.create_user(
            email="nofirst@test.com",
            password="pass123",
            first_name="",
            last_name="Doe",
        )


@pytest.mark.django_db
def test_create_user_rejects_missing_last_name():
    with pytest.raises(ValidationError):
        CustomUser.objects.create_user(
            email="nolast@test.com",
            password="pass123",
            first_name="John",
            last_name="",
        )


@pytest.mark.django_db
def test_email_is_stored_lowercase_on_direct_save():
    user = CustomUser(
        email="DIRECT@TEST.COM ",
        first_name="John",
        last_name="Doe",
    )
    user.set_password("pass123")
    user.save()
    user.refresh_from_db()

    assert user.email == "direct@test.com"


@pytest.mark.django_db
def test_login_view_logs_user_in(client):
    user = CustomUser.objects.create_user(
        email="login@example.com",
        password="pass12345",
        first_name="Login",
        last_name="User",
    )

    response = client.post(
        reverse("login"),
        {
            "username": "login@example.com",
            "password": "pass12345",
        },
    )

    assert response.status_code == 302

    user_id = client.session.get("_auth_user_id")
    assert user_id == str(user.pk)


@pytest.mark.django_db
def test_login_view_rejects_invalid_password(client):
    CustomUser.objects.create_user(
        email="login2@example.com",
        password="pass12345",
        first_name="Login",
        last_name="User",
    )

    response = client.post(
        reverse("login"),
        {
            "username": "login2@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_logout_view_logs_user_out(client):
    user = CustomUser.objects.create_user(
        email="logout@example.com",
        password="pass12345",
        first_name="Logout",
        last_name="User",
    )

    client.force_login(user)

    response = client.post(reverse("logout"))

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session
