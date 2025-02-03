import pytest

from whispr.server.config import DEFAULT_NAMESPACE
from whispr.server.cache.memory_cache import (
    MemoryCache,
    create_namespace,
    set_value,
    get_value,
    delete_value,
    get_namespace,
    get_all,
    remove_namespace,
)


@pytest.fixture(autouse=True)
def reset_cache():
    """
    Fixture to reset the cache instance before each test.
    Ensures tests do not interfere with each other.
    """
    # Reinitialize the internal cache by replacing it with a new MemoryCache
    global cache_instance
    cache_instance = MemoryCache()
    yield


def test_default_namespace_exists():
    """
    Test that the default namespace exists upon initialization.
    """
    ns = get_namespace()
    assert isinstance(ns, dict)
    assert ns == {}


def test_create_and_overwrite_namespace():
    """
    Test that a new namespace can be created and overwritten.
    """
    # Create a new namespace 'test_ns'
    create_namespace("test_ns")
    ns = get_namespace("test_ns")
    assert ns == {}

    # Set a value in 'test_ns'
    set_value("key1", "value1", "test_ns")
    ns = get_namespace("test_ns")
    assert ns == {"key1": "value1"}

    # Overwrite the existing namespace
    create_namespace("test_ns", overwrite=True)
    ns = get_namespace("test_ns")
    assert ns == {}  # Should be reinitialized


def test_set_and_get_value_default_namespace():
    """
    Test setting and getting a value in the default namespace.
    """
    set_value("my_key", "my_value")
    value = get_value("my_key")
    assert value == "my_value"


def test_set_and_get_value_custom_namespace():
    """
    Test that set_value auto-creates a namespace if it does not exist.
    """
    # Namespace 'custom_ns' does not exist yet.
    set_value("a_key", 123, "custom_ns")
    value = get_value("a_key", "custom_ns")
    assert value == 123

    # Ensure that get_namespace returns the correct dict.
    ns = get_namespace("custom_ns")
    assert ns == {"a_key": 123}


def test_get_value_nonexistent():
    """
    Test that getting a non-existent key returns None.
    """
    # No value has been set for this key in default namespace.
    assert get_value("nonexistent") is None

    # Also for a non-existent namespace.
    assert get_value("some_key", "nonexistent_ns") is None


def test_delete_value():
    """
    Test deletion of a key in a namespace.
    """
    set_value("delete_me", "to be deleted")
    # Ensure the value is set.
    assert get_value("delete_me") == "to be deleted"

    # Delete the key and verify deletion returns True.
    result = delete_value("delete_me")
    assert result is True

    # Trying to get the value should now return None.
    assert get_value("delete_me") is None

    # Deleting a non-existent key should return False.
    assert delete_value("nonexistent") is False


def test_get_namespace_returns_shallow_copy():
    """
    Test that get_namespace returns a shallow copy and external modifications do not affect the cache.
    """
    set_value("k1", "v1", "mod_ns")
    ns_copy = get_namespace("mod_ns")
    ns_copy["k1"] = "changed"
    # The original in the cache should remain unchanged.
    assert get_value("k1", "mod_ns") == "v1"


def test_get_all_returns_deep_copy():
    """
    Test that get_all returns a deep copy of the cache.
    """
    # Set some values in different namespaces.
    set_value("dkey", "dvalue")  # Default namespace
    set_value("ckey", "cvalue", "custom_ns")

    all_data = get_all()
    # Modify the returned copy.
    all_data[DEFAULT_NAMESPACE]["dkey"] = "modified"
    all_data["custom_ns"]["ckey"] = "modified"

    # The internal cache should remain unchanged.
    assert get_value("dkey") == "dvalue"
    assert get_value("ckey", "custom_ns") == "cvalue"


def test_remove_namespace_non_default():
    """
    Test that a non-default namespace can be removed.
    """
    # Create and populate a namespace.
    set_value("key", "value", "remove_ns")
    ns = get_namespace("remove_ns")
    assert ns == {"key": "value"}

    # Remove the namespace.
    result = remove_namespace("remove_ns")
    assert result is True

    # The namespace should now be empty.
    ns_after = get_namespace("remove_ns")
    assert ns_after == {}


def test_remove_default_namespace_raises_error():
    """
    Test that attempting to remove the default namespace raises a ValueError.
    """
    with pytest.raises(ValueError, match="Default namespace cannot be removed"):
        remove_namespace(DEFAULT_NAMESPACE)
