"""
A module for caching and retrieving computational results to disk.

This module provides utility functions to save and load intermediate processing results,
which helps avoid redundant computations and speeds up development iterations.
"""

import os 
import pickle

CACHE_SCHEMA_VERSION = 2

def save_stub(stub_path, object, cache_key=None):
    """
    Save a Python object to disk at the specified path.

    Creates necessary directories if they don't exist and serializes the object using pickle.

    Args:
        stub_path (str): File path where the object should be saved.
        object: Any Python object that can be pickled.
    """
    if stub_path is None:
        return
    directory = os.path.dirname(stub_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    payload = object
    if cache_key is not None:
        payload = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "cache_key": cache_key,
            "data": object,
        }
    with open(stub_path, 'wb') as f:
        pickle.dump(payload, f)

def read_stub(read_from_stub, stub_path, cache_key=None):
    """
    Read a previously saved Python object from disk if available.

    Args:
        read_from_stub (bool): Whether to attempt reading from disk.
        stub_path (str): File path where the object was saved.

    Returns:
        object: The loaded Python object if successful, None otherwise.
    """
    if read_from_stub and stub_path is not None and os.path.exists(stub_path):
        with open(stub_path,'rb') as f:
            payload = pickle.load(f)
        if cache_key is None:
            return payload
        if not isinstance(payload, dict):
            return None
        if payload.get("schema_version") != CACHE_SCHEMA_VERSION:
            return None
        if payload.get("cache_key") != cache_key:
            return None
        return payload.get("data")
    return None
