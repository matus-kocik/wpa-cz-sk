import pytest
from django.db import connection, models
from django.utils.text import slugify

from common.models import PublishableModel, SlugModel, SoftDeleteModel


class SlugTestModel(SlugModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "common"

    def __str__(self):
        return self.name


class TitleSlugTestModel(SlugModel):
    title = models.CharField(max_length=100)

    class Meta:
        app_label = "common"


class LatinSlugTestModel(SlugModel):
    latin_name = models.CharField(max_length=100)

    class Meta:
        app_label = "common"


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
            schema_editor.create_model(TitleSlugTestModel)
            schema_editor.create_model(LatinSlugTestModel)
            schema_editor.create_model(SoftDeleteTestModel)
            schema_editor.create_model(PublishableTestModel)

    yield

    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(PublishableTestModel)
            schema_editor.delete_model(SoftDeleteTestModel)
            schema_editor.delete_model(LatinSlugTestModel)
            schema_editor.delete_model(TitleSlugTestModel)
            schema_editor.delete_model(SlugTestModel)


@pytest.mark.django_db
def test_slug_is_generated():
    obj = SlugTestModel.objects.create(name="Hello World")

    assert obj.slug == slugify("Hello World")


@pytest.mark.django_db
def test_slug_is_unique():
    obj1 = SlugTestModel.objects.create(name="Same Name")
    obj2 = SlugTestModel.objects.create(name="Same Name")

    assert obj1.slug != obj2.slug
    assert obj1.slug == "same-name"
    assert obj2.slug == "same-name-1"


@pytest.mark.django_db
def test_slug_does_not_change_on_update():
    obj = SlugTestModel.objects.create(name="Initial Name")
    original_slug = obj.slug

    obj.name = "Updated Name"
    obj.save()
    obj.refresh_from_db()

    assert obj.slug == original_slug


@pytest.mark.django_db
def test_slug_is_generated_from_title():
    obj = TitleSlugTestModel.objects.create(title="Test Title")

    assert obj.slug == "test-title"


@pytest.mark.django_db
def test_slug_is_generated_from_latin_name():
    obj = LatinSlugTestModel.objects.create(latin_name="Ara ararauna")

    assert obj.slug == "ara-ararauna"


@pytest.mark.django_db
def test_soft_delete_sets_flag():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete()

    obj = SoftDeleteTestModel.all_objects.get(pk=obj.pk)

    assert obj.is_deleted is True


@pytest.mark.django_db
def test_soft_delete_sets_deleted_at():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete()

    obj = SoftDeleteTestModel.all_objects.get(pk=obj.pk)

    assert obj.is_deleted is True
    assert obj.deleted_at is not None


@pytest.mark.django_db
def test_soft_deleted_object_not_in_default_queryset():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete()

    assert SoftDeleteTestModel.objects.filter(pk=obj.pk).exists() is False


@pytest.mark.django_db
def test_soft_deleted_object_available_in_all_objects():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    obj.delete()

    assert SoftDeleteTestModel.objects.filter(pk=obj.pk).exists() is False
    assert SoftDeleteTestModel.all_objects.filter(pk=obj.pk).exists() is True


@pytest.mark.django_db
def test_hard_delete_removes_object():
    obj = SoftDeleteTestModel.objects.create(name="Test")
    pk = obj.pk

    obj.delete(hard=True)

    assert SoftDeleteTestModel.all_objects.filter(pk=pk).exists() is False


@pytest.mark.django_db
def test_publish_sets_timestamp():
    obj = PublishableTestModel.objects.create(
        title="Test",
        is_published=True,
    )

    assert obj.published_at is not None


@pytest.mark.django_db
def test_publish_does_not_override_existing_timestamp():
    obj = PublishableTestModel.objects.create(
        title="Test",
        is_published=True,
    )
    original_timestamp = obj.published_at

    obj.save()

    assert obj.published_at == original_timestamp


@pytest.mark.django_db
def test_unpublished_has_no_timestamp():
    obj = PublishableTestModel.objects.create(
        title="Test",
        is_published=False,
    )

    assert obj.published_at is None


@pytest.mark.django_db
def test_publish_after_creation_sets_timestamp():
    obj = PublishableTestModel.objects.create(
        title="Test",
        is_published=False,
    )

    assert obj.published_at is None

    obj.is_published = True
    obj.save()
    obj.refresh_from_db()

    assert obj.published_at is not None


@pytest.mark.django_db
def test_publish_toggle_sets_timestamp_only_once():
    obj = PublishableTestModel.objects.create(
        title="Test",
        is_published=False,
    )

    obj.is_published = True
    obj.save()
    first_timestamp = obj.published_at

    obj.is_published = False
    obj.save()

    obj.is_published = True
    obj.save()
    obj.refresh_from_db()

    assert obj.published_at == first_timestamp
