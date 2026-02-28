import pytest
from contextlib import contextmanager
from typing import Literal
from .exception import SoftAssertionError


class SoftAssert:

    def __init__(self, fail_mode: Literal['fail', 'xfail'] = "fail"):
        self.errors: list[str] = []
        self.already_failed: bool = False
        if fail_mode not in ('fail', 'xfail'):
            fail_mode = "fail"
        self.set_fail_mode(fail_mode)

    def set_fail_mode(self, fail_mode: Literal['fail', 'xfail']) -> None:
        if fail_mode in ('fail', 'xfail'):
            self.fail_mode = fail_mode

    def get_excinfo(self) -> pytest.ExceptionInfo:
        exc = SoftAssertionError('\n'.join(self.errors))
        return pytest.ExceptionInfo.from_exc_info((type(exc), exc, ''))

    def assert_all(self) -> None:
        if self.already_failed:
            return 
        if self.errors:
            self.already_failed = True
            if self.fail_mode == "fail":
                pytest.fail()
            else:
                pytest.xfail()

    #
    # Method-style assertions
    #
    def verify(self, condition, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if not condition:
            self.errors.append(msg + "Soft assertion failed")

    def equal(self, expected, actual, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if expected != actual:
            self.errors.append(msg + f"Soft assertion failed: Expected: '{expected}', got: '{actual}'")

    def not_equal(self, unexpected, actual, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if unexpected == actual:
            self.errors.append(msg + f"Soft assertion failed: Unexpected: '{unexpected}'")

    def true(self, condition, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if not condition:
            self.errors.append(msg + "Soft assertion failed: Expected: 'True'")

    def false(self, condition, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if condition:
            self.errors.append(msg + "Soft assertion failed: Expected: 'False'")

    def none(self, obj, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if obj is not None:
            self.errors.append(msg + f"Soft assertion failed: Expected: 'None', got: '{obj}'")

    def not_none(self, obj, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if obj is None:
            self.errors.append(msg + "Soft assertion failed: Unexpected: 'None'")

    def instance_of(self, obj, clazz, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if not isinstance(obj, clazz):
            self.errors.append(msg + f"Soft assertion failed: Expected: '{clazz.__name__}', got: '{type(obj).__name__}'")

    def not_instance_of(self, obj, clazz, msg=None) -> None:
        msg = msg + '\n' if msg else ''
        if isinstance(obj, clazz):
            self.errors.append(msg + f"Soft assertion failed: Unexpected: '{clazz.__name__}'")

    #
    # raise context manager
    #
    @contextmanager
    def raises(self, expected_exception: Exception, msg=None):
        """Soft assert that a block raises `expected_exception`."""
        msg = msg + '\n' if msg else ''
        excinfo = pytest.ExceptionInfo.for_later()
        try:
            yield excinfo
        except expected_exception as e:
            # Correct exception was raised → do nothing
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        except Exception as e:
            # Wrong exception type → record as soft failure
            self.errors.append(
                msg + f"Expected: '{expected_exception.__name__}', got: '{type(e).__name__}: {e}'"
            )
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        else:
            # No exception was raised → record as soft failure
            self.errors.append(
                msg + f"Expected: '{expected_exception.__name__}', but nothing was raised"
            )

    @contextmanager
    def does_not_raise(self, unexpected_exception: Exception, msg=None):
        """Soft assert that a block does not raise `unexpected_exception`."""
        msg = msg + '\n' if msg else ''
        excinfo = pytest.ExceptionInfo.for_later()
        try:
            yield excinfo
        except unexpected_exception as e:
            # Wrong exception type → record as soft failure
            self.errors.append(
                msg + f"Unexpected: '{unexpected_exception.__name__}'"
            )
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        except Exception as e:
            # Correct exception was raised → do nothing
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
