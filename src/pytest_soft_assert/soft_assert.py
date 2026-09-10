import pytest
from contextlib import contextmanager
from typing import Literal
from .exception import SoftAssertionError


class SoftAssert:

    def __init__(self, fail_mode: Literal['fail', 'xfail'] = "fail"):
        """
        Create a soft assertion instance.
        A soft_assertion failure will result in the following test status:
          - Failed if the soft assertion mode is 'fail'.
          - XFailed if the soft assertion mode is 'xfail'.
        Args:
            fail_mode (str): The soft assertion mode. Possible values: 'fail' or 'xfail'.
        """
        self.errors: list[str] = []
        self.already_failed: bool = False
        if fail_mode not in ('fail', 'xfail'):
            fail_mode = "fail"
        self.set_fail_mode(fail_mode)

    def set_fail_mode(self, fail_mode: Literal['fail', 'xfail']) -> None:
        """
        Set the soft assertion mode.
        A soft_assertion failure will result in the following test status:
          - Failed if the soft assertion mode is 'fail'.
          - XFailed if the soft assertion mode is 'xfail'.
        Args:
            fail_mode (str): The soft assertion mode. Possible values: 'fail' or 'xfail'.
        """
        if fail_mode in ('fail', 'xfail'):
            self.fail_mode = fail_mode

    def get_excinfo(self) -> pytest.ExceptionInfo:
        exc = SoftAssertionError('\n'.join(self.errors))
        return pytest.ExceptionInfo.from_exc_info((type(exc), exc, ''))

    def assert_all(self) -> None:
        """ Verify that all supplied verifications are true. """
        if self.already_failed:
            return 
        if self.errors:
            self.already_failed = True
            if self.fail_mode == "fail":
                pytest.fail()
            else:
                pytest.xfail()

    #
    # Method-style verification
    #
    def verify(self, condition: bool, msg: str = None) -> None:
        """
        Verify a condition.
        Args:
            condition (bool): The condition to verify.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if not condition:
            self.errors.append(msg + "Soft assertion failed")

    def equal(self, actual: object, expected: object, msg: str = None) -> None:
        """
        Verify two values are equals.
        Args:
            actual (object): The first value to compare.
            expected (object): The second value to compare.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if expected != actual:
            self.errors.append(msg + f"Soft assertion failed: Expected: '{expected}', got: '{actual}'")

    def not_equal(self, actual: object, unexpected: object, msg: str = None) -> None:
        """
        Verify two values are different.
        Args:
            actual (object): The first value to compare.
            unexpected (object): The second value to compare.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if unexpected == actual:
            self.errors.append(msg + f"Soft assertion failed: Unexpected: '{unexpected}'")

    def true(self, condition: bool, msg: str = None) -> None:
        """
        Verify a condition is true.
        Args:
            condition (bool): The condition to verify.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if not condition:
            self.errors.append(msg + "Soft assertion failed: Expected: 'True'")

    def false(self, condition: bool, msg: str = None) -> None:
        """
        Verify a condition is false.
        Args:
            condition (bool): The condition to verify.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if condition:
            self.errors.append(msg + "Soft assertion failed: Expected: 'False'")

    def none(self, obj: object, msg: str = None) -> None:
        """
        Verify a value is None.
        Args:
            obj (object): The value to verify.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if obj is not None:
            self.errors.append(msg + f"Soft assertion failed: Expected: 'None', got: '{obj}'")

    def not_none(self, obj: object, msg: str = None) -> None:
        """
        Verify a value is not None.
        Args:
            obj (object): The value to verify.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if obj is None:
            self.errors.append(msg + "Soft assertion failed: Unexpected: 'None'")

    def instance_of(self, obj: object, clazz: type, msg=None) -> None:
        """
        Verify a value is an instance of class.
        Args:
            obj (object): The value to verify.
            clazz (type):  The expected class-type.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if not isinstance(obj, clazz):
            self.errors.append(msg + f"Soft assertion failed: Expected: '{clazz.__name__}', got: '{type(obj).__name__}'")

    def not_instance_of(self, obj: object, clazz: type, msg: str = None) -> None:
        """
        Verify a value is not an instance of class.
        Args:
            obj (object): The value to verify.
            clazz (type):  The unexpected class-type.
            msg (str): The message to display if the verification fails.
        """
        msg = msg + '\n' if msg else ''
        if isinstance(obj, clazz):
            self.errors.append(msg + f"Soft assertion failed: Unexpected: '{clazz.__name__}'")

    #
    # raise context manager
    #
    @contextmanager
    def raises(self, expected_exception: Exception = Exception, msg: str = None):
        """
        Verify that a block raises a given exception.
        Args:
            expected_exception (Exception): The exception to verify.
            msg (str): The message to display if the verification fails.
        """
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
    def does_not_raise(self, unexpected_exception: Exception = Exception, msg: str = None):
        """
        Verify that a block raises does not raise a given exception.
        Args:
            unexpected_exception (Exception): The exception to verify.
            msg (str): The message to display if the verification fails.
        """
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
