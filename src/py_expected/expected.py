from typing import Callable, Generic, TypeVar, Union

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')
F = TypeVar('F')


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
    def __init__(self, error: E) -> None:
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

    def __bool__(self) -> bool:
        return self._has_value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expected):
            return NotImplemented
        if self._has_value != other._has_value:
            return False

        if self._has_value and other._has_value:
            return self._value == other._value
        else:
            return self._error == other._error

    def has_value(self) -> bool:
        return bool(self)

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
        return Expected.from_error(self._error)

    def transform_error(self, f: Callable[[E], F]) -> 'Expected[T, F]':
        if self._has_value:
            return Expected(self._value)
        return Expected.from_error(f(self._error))
