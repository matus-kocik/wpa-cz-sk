import pytest
from django.core.exceptions import ValidationError

from users.models import CustomUser

# =========================
# MANAGER TESTS
# =========================

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


# =========================
# MODEL TESTS
# =========================

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


# =========================
# VALIDATION (CLEAN)
# =========================

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


# =========================
# SAVE BEHAVIOR
# =========================

@pytest.mark.django_db
def test_save_calls_full_clean():
    user = CustomUser(
        email="test@test.com",
        first_name="",
        last_name="Doe",
    )

    with pytest.raises(ValidationError):
        user.save()
