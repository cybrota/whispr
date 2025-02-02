# memory_cache.py

import threading
import copy
from typing import Any, Optional, Dict
from whispr.server.config import DEFAULT_NAMESPACE


class MemoryCache:
    def __init__(self) -> None:
        """
        Initialize the in-memory cache with a default namespace.
        """
        # Internal cache structure: namespace -> { key: value }
        self._cache: Dict[str, Dict[str, Any]] = {DEFAULT_NAMESPACE: {}}
        # A lock to ensure thread-safe access to the cache.
        self._lock = threading.Lock()

    def create_namespace(
        self, namespace: str = DEFAULT_NAMESPACE, overwrite: bool = False
    ) -> None:
        """
        Create a new namespace if it does not exist. If the namespace exists
        and `overwrite` is True, clear and reinitialize the namespace.

        Args:
            namespace: The namespace to create. Defaults to DEFAULT_NAMESPACE.
            overwrite: If True and the namespace exists, the namespace is reinitialized.
        """
        with self._lock:
            if namespace in self._cache:
                if overwrite:
                    self._cache[namespace] = {}
            else:
                self._cache[namespace] = {}

    def set_value(
        self, key: str, value: Any, namespace: str = DEFAULT_NAMESPACE
    ) -> None:
        """
        Set or update the value associated with `key` in the specified namespace.
        If the namespace does not exist, it is created automatically.

        Args:
            key: The key to set or update.
            value: The value to associate with the key.
            namespace: The namespace in which to set the key-value pair. Defaults to DEFAULT_NAMESPACE.
        """
        with self._lock:
            # Auto-create namespace if not exists
            if namespace not in self._cache:
                self._cache[namespace] = {}
            self._cache[namespace][key] = value

    def get_value(self, key: str, namespace: str = DEFAULT_NAMESPACE) -> Optional[Any]:
        """
        Retrieve the value associated with `key` in the specified namespace.

        Args:
            key: The key whose value should be returned.
            namespace: The namespace from which to retrieve the value. Defaults to DEFAULT_NAMESPACE.

        Returns:
            The value if found, otherwise None.
        """
        with self._lock:
            if namespace not in self._cache:
                return None
            return self._cache[namespace].get(key)

    def delete_value(self, key: str, namespace: str = DEFAULT_NAMESPACE) -> bool:
        """
        Delete the key from the specified namespace.

        Args:
            key: The key to be deleted.
            namespace: The namespace from which to delete the key. Defaults to DEFAULT_NAMESPACE.

        Returns:
            True if the key was found and deleted; otherwise, False.
        """
        with self._lock:
            if namespace in self._cache and key in self._cache[namespace]:
                del self._cache[namespace][key]
                return True
            return False

    def get_namespace(self, namespace: str = DEFAULT_NAMESPACE) -> Dict[str, Any]:
        """
        Return a shallow copy of the entire key-value dictionary for the given namespace.
        If the namespace does not exist, an empty dictionary is returned.

        Args:
            namespace: The namespace to retrieve. Defaults to DEFAULT_NAMESPACE.

        Returns:
            A copy of the namespace's dictionary or an empty dict if not found.
        """
        with self._lock:
            if namespace in self._cache:
                return self._cache[namespace].copy()
            return {}

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve a deep copy (full snapshot) of the entire cache across all namespaces.

        Returns:
            A deep copy of the internal cache dictionary.
        """
        with self._lock:
            return copy.deepcopy(self._cache)

    def remove_namespace(self, namespace: str = DEFAULT_NAMESPACE) -> bool:
        """
        Remove an entire namespace from the cache. The default namespace cannot be removed.

        Args:
            namespace: The namespace to remove. Defaults to DEFAULT_NAMESPACE.

        Returns:
            True if the namespace was found and removed; otherwise, False.

        Raises:
            ValueError: If an attempt is made to remove the default namespace.
        """
        if namespace == DEFAULT_NAMESPACE:
            raise ValueError("Default namespace cannot be removed")
        with self._lock:
            if namespace in self._cache:
                del self._cache[namespace]
                return True
            return False


# Optionally, you can create a singleton instance of MemoryCache for module-level use.
cache_instance = MemoryCache()


# Module-level functions that delegate to the instance
def create_namespace(
    namespace: str = DEFAULT_NAMESPACE, overwrite: bool = False
) -> None:
    cache_instance.create_namespace(namespace, overwrite)


def set_value(key: str, value: Any, namespace: str = DEFAULT_NAMESPACE) -> None:
    cache_instance.set_value(key, value, namespace)


def get_value(key: str, namespace: str = DEFAULT_NAMESPACE) -> Optional[Any]:
    return cache_instance.get_value(key, namespace)


def delete_value(key: str, namespace: str = DEFAULT_NAMESPACE) -> bool:
    return cache_instance.delete_value(key, namespace)


def get_namespace(namespace: str = DEFAULT_NAMESPACE) -> Dict[str, Any]:
    return cache_instance.get_namespace(namespace)


def get_all() -> Dict[str, Dict[str, Any]]:
    return cache_instance.get_all()


def remove_namespace(namespace: str = DEFAULT_NAMESPACE) -> bool:
    return cache_instance.remove_namespace(namespace)
