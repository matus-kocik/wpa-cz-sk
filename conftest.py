import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def isolated_cache():
    """Keep request limits and other cached state within one test."""
    cache.clear()
    yield
    cache.clear()
