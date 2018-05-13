"""Test picobox's scopes implementations."""

import threading

import pytest
import picobox


@pytest.mark.parametrize('scopeclass', [
    picobox.singleton,
    picobox.threadlocal,
])
def test_scope_set_key(scopeclass, supported_key):
    scope = scopeclass()
    value = object()

    scope.set(supported_key, value)
    assert scope.get(supported_key) is value


@pytest.mark.parametrize('scopeclass', [
    picobox.singleton,
    picobox.threadlocal,
])
def test_scope_set_value(scopeclass, supported_value):
    scope = scopeclass()

    scope.set('the-key', supported_value)
    assert scope.get('the-key') is supported_value


def test_singleton():
    scope = picobox.singleton()
    value = object()

    with pytest.raises(KeyError) as excinfo:
        scope.get('the-key')
    excinfo.match('the-key')

    scope.set('the-key', value)
    assert scope.get('the-key') is value


def test_singleton_threads():
    scope = picobox.singleton()
    value = object()
    rv = None

    with pytest.raises(KeyError) as excinfo:
        scope.get('the-key')
    excinfo.match('the-key')

    scope.set('the-key', value)

    def worker_fn():
        nonlocal rv
        rv = scope.get('the-key')

    worker = threading.Thread(target=worker_fn)
    worker.start()
    worker.join()

    assert rv is value


def test_threadlocal():
    scope = picobox.threadlocal()
    value = object()

    with pytest.raises(KeyError) as excinfo:
        scope.get('the-key')
    excinfo.match('the-key')

    scope.set('the-key', value)
    assert scope.get('the-key') is value


def test_threadlocal_threads():
    scope = picobox.threadlocal()
    value = object()
    rv = None

    with pytest.raises(KeyError) as excinfo:
        scope.get('the-key')
    excinfo.match('the-key')

    scope.set('the-key', value)

    def worker_fn():
        nonlocal rv
        rv = scope.get('the-key')

    worker = threading.Thread(target=worker_fn)
    worker.start()
    worker.join()

    assert rv is not value
    assert rv is None

    def worker_fn():
        nonlocal rv
        scope.set('the-key', value)
        rv = scope.get('the-key')

    worker = threading.Thread(target=worker_fn)
    worker.start()
    worker.join()

    assert rv is value


def test_noscope():
    scope = picobox.noscope()
    value = object()

    with pytest.raises(KeyError) as excinfo:
        scope.get('the-key')
    excinfo.match('the-key')

    scope.set('the-key', value)

    with pytest.raises(KeyError) as excinfo:
        scope.get('the-key')
    excinfo.match('the-key')
