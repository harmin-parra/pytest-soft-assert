import pytest
from contextlib import contextmanager
from typing import Literal
from .exception import SoftAssertionError


class SoftAssert:

    def __init__(self, fail_mode: Literal['fail', 'xfail'] = "xfail"):
        self.errors: list[str] = []
        self.already_failed: bool = False
        self.fail_mode: str = "xfail"
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

    # Method-style assertion
    def verify(self, condition, msg=None) -> None:
        if not condition:
            self.errors.append(msg or "Soft assertion failed")

    # # Context manager style assertion
    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc, tb):
    #     # Do NOT swallow real exceptions
    #     if exc:
    #         return False
    #     self.assert_all()
    #     return True

    # raise context manager
    @contextmanager
    def raises(self, expected_exception, msg=None):
        """Soft assert that a block raises `expected_exception`."""
        excinfo = pytest.ExceptionInfo.for_later()
        try:
            yield excinfo
        except expected_exception as e:
            # Correct exception was raised → do nothing
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        except Exception as e:
            # Wrong exception type → record as soft failure
            self.errors.append(
                msg or f"Expected {expected_exception.__name__}, got {type(e).__name__}: {e}"
            )
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        else:
            # No exception was raised → record as soft failure
            self.errors.append(
                msg or f"Expected {expected_exception.__name__}, but nothing was raised"
            )
