import pytest
from django.db import connection, models
from django.utils.text import slugify

from common.models import PublishableModel, SlugModel, SoftDeleteModel

# -----------------------------
# TEST MODELS
# -----------------------------

class SlugTestModel(SlugModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "common"

    def __str__(self):
        return self.name


class SoftDeleteTestModel(SoftDeleteModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "common"


class PublishableTestModel(PublishableModel):
    title = models.CharField(max_length=100)

    class Meta:
        app_label = "common"


@pytest.fixture(scope="module", autouse=True)
def create_test_tables(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(SlugTestModel)
            schema_editor.create_model(SoftDeleteTestModel)
            schema_editor.create_model(PublishableTestModel)
    yield
    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(SlugTestModel)
            schema_editor.delete_model(SoftDeleteTestModel)
            schema_editor.delete_model(PublishableTestModel)


# -----------------------------
# SLUG MODEL TESTS
# -----------------------------

@pytest.mark.django_db
def test_slug_is_generated():
    obj = SlugTestModel.objects.create(name="Hello World")
    assert obj.slug == slugify("Hello World")


@pytest.mark.django_db
def test_slug_is_unique():
    obj1 = SlugTestModel.objects.create(name="Same Name")
    obj2 = SlugTestModel.objects.create(name="Same Name")

    assert obj1.slug != obj2.slug


# -----------------------------
# SOFT DELETE TESTS
# -----------------------------

@pytest.mark.django_db
def test_soft_delete_sets_flag():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete()

    obj.refresh_from_db()
    assert obj.is_deleted is True


@pytest.mark.django_db
def test_hard_delete_removes_object():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete(hard=True)

    assert SoftDeleteTestModel.objects.filter(id=obj.id).count() == 0


# -----------------------------
# PUBLISHABLE MODEL TESTS
# -----------------------------

@pytest.mark.django_db
def test_publish_sets_timestamp():
    obj = PublishableTestModel.objects.create(title="Test", is_published=True)

    assert obj.published_at is not None


@pytest.mark.django_db
def test_publish_does_not_override_existing_timestamp():
    obj = PublishableTestModel.objects.create(title="Test", is_published=True)
    original_timestamp = obj.published_at

    obj.save()

    assert obj.published_at == original_timestamp


@pytest.mark.django_db
def test_unpublished_has_no_timestamp():
    obj = PublishableTestModel.objects.create(title="Test", is_published=False)

    assert obj.published_at is None



@pytest.mark.django_db
def test_slug_does_not_change_on_update():
    obj = SlugTestModel.objects.create(name="Initial Name")
    original_slug = obj.slug

    obj.name = "Updated Name"
    obj.save()

    assert obj.slug == original_slug


@pytest.mark.django_db
def test_soft_deleted_object_not_in_default_queryset():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete()

    assert SoftDeleteTestModel.objects.filter(id=obj.id).count() == 0


@pytest.mark.django_db
def test_publish_toggle_sets_timestamp_only_once():
    obj = PublishableTestModel.objects.create(title="Test", is_published=False)

    # first publish
    obj.is_published = True
    obj.save()
    first_timestamp = obj.published_at

    # toggle off and on again
    obj.is_published = False
    obj.save()
    obj.is_published = True
    obj.save()

    assert obj.published_at == first_timestamp
