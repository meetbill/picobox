"""Scope interface and builtin implementations."""

import abc
import threading
import typing as t

try:
    import contextvars as _contextvars
except ImportError:
    _contextvars = None


class Scope(metaclass=abc.ABCMeta):
    """Scope is an execution context based storage interface.

    Execution context is a mechanism of storing and accessing data bound to a
    logical thread of execution. Thus, one may consider processes, threads,
    greenlets, coroutines, Flask requests to be examples of a logical thread.

    The interface provides just two methods:

     * :meth:`.set` - set execution context item
     * :meth:`.get` - get execution context item

    See corresponding methods for details below.
    """

    @abc.abstractmethod
    def set(self, key: t.Hashable, value: t.Any) -> None:
        """Bind `value` to `key` in current execution context."""

    @abc.abstractmethod
    def get(self, key: t.Hashable) -> t.Any:
        """Get `value` by `key` for current execution context."""


class singleton(Scope):
    """Share instances across application."""

    def __init__(self):
        """初始化函数
        
        Args:
            无
        
        Returns:
            None
        """
        self._store = {}

    def set(self, key: t.Hashable, value: t.Any) -> None:
        """
        设置给定键值对到字典中。
        
        Args:
            key (t.Hashable): 键。
            value (t.Any): 值。
        
        Returns:
            None: 该方法没有返回任何结果。
        
        """
        self._store[key] = value

    def get(self, key: t.Hashable) -> t.Any:
        """
        从缓存中获取指定键的值。
        
        Args:
            key (t.Hashable): 要获取值的键。
        
        Returns:
            Any: 指定键对应的值。
        
        """
        return self._store[key]


class threadlocal(Scope):
    """Share instances across the same thread."""

    def __init__(self):
        """
        重载构造函数，用于初始化线程本地变量。
        
        Args:
            无
        
        Returns:
            无
        
        """
        self._local = threading.local()

    def set(self, key: t.Hashable, value: t.Any) -> None:
        """
        设置字典中指定键值对的值。
        
        Args:
            key (t.Hashable): 要设置的键。
            value (t.Any): 需要设置的值。
        
        Returns:
            None: 方法没有返回任何值。
        
        Raises:
            AttributeError: 如果本地存储未初始化，则会引发该异常。
        """
        try:
            store = self._local.store
        except AttributeError:
            store = self._local.store = {}
        store[key] = value

    def get(self, key: t.Hashable) -> t.Any:
        """
        获取指定键的值。
        
        Args:
            key (t.Hashable): 要获取值的键。
        
        Returns:
            t.Any: 指定键对应的值，如果键不存在则会抛出 KeyError 。
        
        Raises:
            KeyError: 如果指定的键不存在。
        
        """
        try:
            rv = self._local.store[key]
        except AttributeError:
            raise KeyError(key)
        return rv


class contextvars(Scope):
    """Share instances across the same execution context (:pep:`567`).

    Since `asyncio does support context variables`__, the scope could be used
    in asynchronous applications to share dependencies between coroutines of
    the same :class:`asyncio.Task`.

    .. __: https://docs.python.org/3.7/library/contextvars.html#asyncio-support

    .. versionadded:: 2.1
    """

    def __init__(self):
        """
        构造函数，用于初始化对象。
        
        Args:
            无参数。
        
        Returns:
            无返回值。
        
        """
        self._store = {}

    def set(self, key: t.Hashable, value: t.Any) -> None:
        """
        设置指定键的值为给定值。
        
            Args:
                key (t.Hashable): 要设置值的键。
                value (t.Any): 设置的新值。
        
            Returns:
                None: 无返回值。
        
        """
        try:
            var = self._store[key]
        except KeyError:
            var = self._store[key] = _contextvars.ContextVar("picobox")
        var.set(value)

    def get(self, key: t.Hashable) -> t.Any:
        """
        获取指定键的值
        
        Args:
            key (t.Hashable): 键值
        
        Returns:
            t.Any: 指定键对应的值
        
        Raises:
            KeyError: 当指定的键不存在时抛出异常
        """
        try:
            return self._store[key].get()
        except LookupError:
            raise KeyError(key)


class noscope(Scope):
    """Do not share instances, create them each time on demand."""

    def set(self, key: t.Hashable, value: t.Any) -> None:
        """
        设置键值对。
        
        Args:
            key (t.Hashable): 键。
            value (t.Any): 对应的值。
        
        Returns:
            None: 无返回值。
        
        """
        pass

    def get(self, key: t.Hashable) -> t.Any:
        """
        Get the value of a specified key in this cache if present, otherwise
        raise `KeyError`.
        
        Args:
            key (t.Hashable): The key to be retrieved from the cache.
        
        Returns:
            t.Any: The value associated with the given key or `KeyError` is raised
                if the key does not exist.
        
        Raises:
            KeyError: If the specified key does not exist in this cache.
        """
        raise KeyError(key)


if not _contextvars:
    del contextvars
