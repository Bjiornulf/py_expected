from typing import (
    Callable,
    Generic,
    Union,
    TypeVar,
    Optional,
    Any,
)

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class BadValueAccess(LookupError, Generic[E]):
    def __init__(self, error: E) -> None:
        self._error = error

    def error(self) -> E:
        return self._error


class BadErrorAccess(LookupError, Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def value(self) -> T:
        return self._value


class Unexpected(Generic[E]):
    def __init__(self, error: Any) -> None:
        self._error = error


class Expected(Generic[T, E]):
    @classmethod
    def from_error(cls, error: E) -> 'Expected[T, E]':
        return Expected(Unexpected(error))

    def __init__(self, value_or_error: Union[T, Unexpected[E]]) -> None:
        if isinstance(value_or_error, Unexpected):
            self._error = value_or_error._error
            self._has_value = False
        else:
            self._value = value_or_error
            self._has_value = True

    def value(self) -> T:
        if self._has_value:
            return self._value
        raise BadValueAccess(self._error)

    def error(self) -> E:
        if not self._has_value:
            return self._error
        raise BadErrorAccess(self._value)

    def value_or(self, default: T) -> T:
        if not self._has_value:
            return default
        return self._value

    def transform(self, f: Callable[[T], U]) -> 'Expected[U, E]':
        if self._has_value:
            return Expected(f(self._value))
        return Expected(Unexpected(self._error))
