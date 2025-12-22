import pytest
from _pytest._code import ExceptionInfo
from contextlib import contextmanager
from typing import Literal
from .exception import SoftAssertionError, _ExcInfo


class SoftAssert:

    def __init__(self, failure_mode = "xfail"):
        self.errors = []
        self.already_failed = False
        self.set_failure_mode(failure_mode)

    def set_failure_mode(self, mode: Literal['fail', 'xfail']) -> None:
        if mode in ('fail', 'xfail'):
            self.failure_mode = mode

    def get_excinfo(self) -> ExceptionInfo:
        exc = SoftAssertionError('\n'.join(self.errors))
        return ExceptionInfo.from_exc_info((type(exc), exc, ''))

    def assert_all(self) -> None:
        if self.already_failed:
            return 
        if self.errors:
            self.already_failed = True
            if self.failure_mode == "fail":
                pytest.fail()
            else:
                pytest.xfail()

    # Method-style assertion
    def verify(self, condition, msg=None) -> None:
        if not condition:
            self.errors.append(msg or "Soft assertion failed")

    # Context manager style
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # Do NOT swallow real exceptions
        if exc:
            return False
        self.assert_all()
        return True

    # raise context manager
    @contextmanager
    def raises(self, expected_exception, msg=None):
        """Softly assert that a block raises `expected_exception`."""
        excinfo = _ExcInfo()
        try:
            yield excinfo
        except expected_exception as e:
            # Correct exception was raised → do nothing
            excinfo.update(e)
        except Exception as e:
            # Wrong exception type → record as soft failure
            self.errors.append(
                msg or f"Expected {expected_exception.__name__}, got {type(e).__name__}: {e}"
            )
            excinfo.update(e)
        else:
            # No exception was raised → record as soft failure
            self.errors.append(
                msg or f"Expected {expected_exception.__name__}, but nothing was raised"
            )
