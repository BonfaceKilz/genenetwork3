"""Monadic utilities

This module is a collection of monadic utilities for use in
GeneNetwork. It includes:

* MonadicDict - monadic version of the built-in dictionary
* MonadicDictCursor - monadic version of MySQLdb.cursors.DictCursor
  that returns a MonadicDict instead of the built-in dictionary
"""

from collections import UserDict
from functools import partial
from typing import Any, Hashable, Iterator

from MySQLdb.cursors import DictCursor
from pymonad.maybe import Maybe, Just, Nothing


class MonadicDict(UserDict):
    """
    Monadic version of the built-in dictionary.

    Keys in this dictionary can be any python object, but values must
    be monadic values.

    from pymonad.maybe import Just, Nothing

    Initialize by setting individual keys to monadic values.
    >>> d = MonadicDict()
    >>> d["foo"] = Just(1)
    >>> d["bar"] = Nothing
    >>> d
    {'foo': 1}

    Initialize by converting a built-in dictionary object.
    >>> MonadicDict({"foo": 1})
    {'foo': 1}
    >>> MonadicDict({"foo": 1, "bar": None})
    {'foo': 1}

    Initialize from a built-in dictionary object with monadic values.
    >>> MonadicDict({"foo": Just(1)}, convert=False)
    {'foo': 1}
    >>> MonadicDict({"foo": Just(1), "bar": Nothing}, convert=False)
    {'foo': 1}

    Get values. For non-existent keys, Nothing is returned. Else, a
    Just value is returned.
    >>> d["foo"]
    Just 1
    >>> d["bar"]
    Nothing

    Convert MonadicDict object to a built-in dictionary object.
    >>> d.data
    {'foo': 1}
    >>> type(d)
    <class 'utility.monads.MonadicDict'>
    >>> type(d.data)
    <class 'dict'>

    Delete keys. Deleting non-existent keys does nothing.
    >>> del d["bar"]
    >>> d
    {'foo': 1}
    >>> del d["foo"]
    >>> d
    {}

    Update dictionary object.
    >>> d = MonadicDict()
    >>> d.update(MonadicDict({'foo': 'bar'}))
    >>> d
    {'foo': 'bar'}
    """

    # pylint: disable=dangerous-default-value
    def __init__(self, d: dict = {}, convert: bool = True) -> None:
        """Initialize monadic dictionary.

        If convert is False, values in dictionary d must be
        monadic. If convert is True, values in dictionary d are
        converted to monadic values.
        """
        if convert:
            super().__init__(
                {
                    key: Just(value)
                    for key, value in d.items()
                    if value is not None
                }
            )
        else:
            super().__init__(d)

    def __getitem__(self, key: Hashable) -> Maybe[Any]:
        """Get key from dictionary.

        If key exists in the dictionary, return a Just value. Else,
        return Nothing.
        """
        try:
            return Just(self.data[key])
        except KeyError:
            return Nothing

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Set key in dictionary.

        value must be a monadic value---either Nothing or a Just
        value. If value is a Just value, set it in the dictionary. If
        value is Nothing, do nothing.
        """
        value.bind(partial(super().__setitem__, key))

    def __delitem__(self, key: Hashable) -> None:
        """Delete key from dictionary.

        If key exists in the dictionary, delete it. Else, do nothing.
        """
        try:
            super().__delitem__(key)
        except KeyError:
            pass


def query_sql(conn, query: str) -> Iterator[MonadicDict]:
    """Execute SQL query and return a generator of MonadicDict objects."""
    with conn.cursor(DictCursor) as cursor:
        cursor.execute(query)
        while row := cursor.fetchone():
            yield MonadicDict(row)
