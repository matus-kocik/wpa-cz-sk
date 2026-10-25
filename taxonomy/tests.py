import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from taxonomy.models import (
    Family,
    Genus,
    Species,
    Subfamily,
    Subspecies,
)


@pytest.fixture
def family():
    return Family.objects.create(
        latin_name="Psittacidae",
        czech_name="Papouškovití",
        slovak_name="Papagájovité",
    )


@pytest.fixture
def other_family():
    return Family.objects.create(
        latin_name="Cacatuidae",
        czech_name="Kakaduovití",
    )


@pytest.fixture
def subfamily(family):
    return Subfamily.objects.create(
        latin_name="Psittacinae",
        family=family,
    )


@pytest.fixture
def genus(family, subfamily):
    return Genus.objects.create(
        latin_name="Psittacus",
        family=family,
        subfamily=subfamily,
    )


@pytest.fixture
def species(genus):
    return Species.objects.create(
        latin_name="Psittacus erithacus",
        czech_name="Žako šedý",
        genus=genus,
    )


@pytest.fixture
def subspecies(species):
    return Subspecies.objects.create(
        latin_name="Psittacus erithacus erithacus",
        species=species,
    )


# Taxonomic hierarchy


@pytest.mark.django_db
def test_family_creation(family):
    assert family.latin_name == "Psittacidae"
    assert str(family) == "Psittacidae"


@pytest.mark.django_db
def test_subfamily_belongs_to_family(subfamily, family):
    assert subfamily.family == family
    assert subfamily in family.subfamilies.all()


@pytest.mark.django_db
def test_genus_belongs_to_family_and_subfamily(
    genus,
    family,
    subfamily,
):
    assert genus.family == family
    assert genus.subfamily == subfamily
    assert genus in family.genera.all()
    assert genus in subfamily.genera.all()


@pytest.mark.django_db
def test_genus_without_subfamily(family):
    genus = Genus.objects.create(
        latin_name="Ara",
        family=family,
    )

    assert genus.family == family
    assert genus.subfamily is None


@pytest.mark.django_db
def test_species_belongs_to_genus(species, genus):
    assert species.genus == genus
    assert species in genus.species.all()


@pytest.mark.django_db
def test_subspecies_belongs_to_species(subspecies, species):
    assert subspecies.species == species
    assert subspecies in species.subspecies.all()


# Taxonomic hierarchy validation


@pytest.mark.django_db
def test_genus_rejects_subfamily_from_different_family(
    family,
    other_family,
):
    wrong_subfamily = Subfamily.objects.create(
        latin_name="Cacatuinae",
        family=other_family,
    )

    genus = Genus(
        latin_name="Ara",
        family=family,
        subfamily=wrong_subfamily,
    )

    with pytest.raises(ValidationError) as exc:
        genus.full_clean()

    assert "subfamily" in exc.value.message_dict


@pytest.mark.django_db
def test_genus_accepts_matching_family_and_subfamily(
    family,
    subfamily,
):
    genus = Genus(
        latin_name="Ara",
        family=family,
        subfamily=subfamily,
    )

    genus.full_clean()


@pytest.mark.django_db
def test_genus_requires_family():
    genus = Genus(latin_name="Ara")

    with pytest.raises(ValidationError) as exc:
        genus.full_clean()

    assert "family" in exc.value.message_dict


# Unique scientific names


@pytest.mark.django_db
def test_family_latin_name_is_unique(family):
    duplicate = Family(latin_name=family.latin_name)

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_subfamily_latin_name_is_unique(subfamily, family):
    duplicate = Subfamily(
        latin_name=subfamily.latin_name,
        family=family,
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_genus_latin_name_is_unique(genus, family):
    duplicate = Genus(
        latin_name=genus.latin_name,
        family=family,
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_species_latin_name_is_unique(species, genus):
    duplicate = Species(
        latin_name=species.latin_name,
        czech_name="Duplicate species",
        genus=genus,
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_subspecies_latin_name_is_unique(subspecies, species):
    duplicate = Subspecies(
        latin_name=subspecies.latin_name,
        species=species,
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_database_rejects_duplicate_family_name(family):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Family.objects.create(
                latin_name=family.latin_name,
            )


# Deletion behavior


@pytest.mark.django_db
def test_deleting_subfamily_preserves_genus(
    genus,
    subfamily,
    family,
):
    subfamily.delete()

    genus.refresh_from_db()

    assert genus.family == family
    assert genus.subfamily is None


@pytest.mark.django_db
def test_deleting_subfamily_preserves_species(
    species,
    genus,
    subfamily,
):
    species_id = species.pk

    subfamily.delete()

    assert Species.objects.filter(pk=species_id).exists()

    genus.refresh_from_db()
    assert genus.subfamily is None


@pytest.mark.django_db
def test_deleting_family_with_genus_is_protected(
    family,
    genus,
):
    with pytest.raises(ProtectedError):
        family.delete()

    assert Family.objects.filter(pk=family.pk).exists()
    assert Genus.objects.filter(pk=genus.pk).exists()


@pytest.mark.django_db
def test_deleting_species_deletes_subspecies(
    species,
    subspecies,
):
    subspecies_id = subspecies.pk

    species.delete()

    assert not Subspecies.objects.filter(pk=subspecies_id).exists()


# Automatic slug generation


@pytest.mark.django_db
def test_family_slug_is_generated(family):
    assert family.slug == "psittacidae"


@pytest.mark.django_db
def test_genus_slug_is_generated(genus):
    assert genus.slug == "psittacus"


@pytest.mark.django_db
def test_species_slug_is_generated(species):
    assert species.slug == "psittacus-erithacus"


# Species biological validation


@pytest.mark.django_db
@pytest.mark.parametrize(
    "minimum,maximum",
    [
        ("length_male_min", "length_male_max"),
        ("length_female_min", "length_female_max"),
        ("weight_male_min", "weight_male_max"),
        ("weight_female_min", "weight_female_max"),
        ("clutch_min", "clutch_max"),
        ("incubation_min", "incubation_max"),
    ],
)
def test_species_rejects_min_greater_than_max(
    genus,
    minimum,
    maximum,
):
    species = Species(
        latin_name="Ara ararauna",
        czech_name="Ara ararauna",
        genus=genus,
        **{
            minimum: 100,
            maximum: 50,
        },
    )

    with pytest.raises(ValidationError) as exc:
        species.full_clean()

    assert minimum in exc.value.message_dict


@pytest.mark.django_db
def test_species_accepts_valid_biological_ranges(genus):
    species = Species(
        latin_name="Ara ararauna",
        czech_name="Ara ararauna",
        genus=genus,
        length_male_min=70,
        length_male_max=90,
        weight_male_min=900,
        weight_male_max=1200,
        clutch_min=2,
        clutch_max=4,
        incubation_min=24,
        incubation_max=28,
    )

    species.full_clean()


@pytest.mark.django_db
def test_species_rejects_negative_length(genus):
    species = Species(
        latin_name="Ara ararauna",
        czech_name="Ara ararauna",
        genus=genus,
        length_male_min=-10,
    )

    with pytest.raises(ValidationError) as exc:
        species.full_clean()

    assert "length_male_min" in exc.value.message_dict


@pytest.mark.django_db
def test_species_strips_whitespace(genus):
    species = Species(
        latin_name="  Ara ararauna  ",
        czech_name="  Ara ararauna  ",
        genus=genus,
    )

    species.full_clean()

    assert species.latin_name == "Ara ararauna"
    assert species.czech_name == "Ara ararauna"
