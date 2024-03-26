from typing import Callable, Generic, TypeVar, Union

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')
F = TypeVar('F')


class BadValueAccess(LookupError, Generic[E]):
    """
    Exception used when an Expected does not hold a value
    """

    def __init__(self, error: E) -> None:
        self._error = error

    def error(self) -> E:
        return self._error


class BadErrorAccess(LookupError, Generic[T]):
    """
    Exception used when an Expected does not hold an error
    """

    def __init__(self, value: T) -> None:
        self._value = value

    def value(self) -> T:
        return self._value


class Unexpected(Generic[E]):
    """
    Dummy class to hold an error
    """

    def __init__(self, error: E) -> None:
        self._error = error


class Expected(Generic[T, E]):
    """
    A Class resembling std::expected in C++23

    The class is aimed at providing a similar functionnality to std::expected
    albeit better suited to Python

    An Expected can never have an Unexpected value. It is admitted that
    Unexpected[E] denotes an error. This is used to differenciate an error
    from an actual value

    Some methods have not been implemented, and others are not implemented the
    exact same way (different signature), as implementing them like in C++
    would make the usage of the object too awkward
    """

    @classmethod
    def from_error(cls, error: E) -> 'Expected[T, E]':
        """
        Construct an Expected with an error

        Equivalent to calling Expected(Unexpected(error))
        """
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
        """
        Does the object contain a valid value
        """
        return bool(self)

    def value(self) -> T:
        """
        Get the value

        If no value is present, raisees a BadValueAccess[E] containing the
        error from the object
        """
        if self._has_value:
            return self._value
        raise BadValueAccess(self._error)

    def error(self) -> E:
        """
        Get the error

        If no error is present, raisees a BadErrorAccess[T] containing the
        value from the object
        """
        if not self._has_value:
            return self._error
        raise BadErrorAccess(self._value)

    def value_or(self, default: T) -> T:
        """
        Get the value; or a default value

        Should always provide a valid value
        """
        if not self._has_value:
            return default
        return self._value

    def transform(self, f: Callable[[T], U]) -> 'Expected[U, E]':
        """
        Transform the value or return a copy of the object itself

        If the Expected holds a value, transform the value using the provided
        function and return the value in an Expected
        Otherwise, return an Expected containing the error
        """
        if self._has_value:
            return Expected(f(self._value))
        return Expected.from_error(self._error)

    def transform_error(self, f: Callable[[E], F]) -> 'Expected[T, F]':
        """
        Transform the error or return a copy of the object itself

        If the Expected holds an error, transform the error using the provided
        function and return it in an Expected (as an error)
        Otherwise, return a copy of the object itself (holding a valid value)
        """
        if self._has_value:
            return Expected(self._value)
        return Expected.from_error(f(self._error))
