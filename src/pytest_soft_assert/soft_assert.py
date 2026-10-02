import pytest
import re
from contextlib import contextmanager
from typing import Literal
from _pytest._code import ExceptionInfo
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
        self._fail_mode: Literal['fail', 'xfail'] = None
        self._already_failed: bool = False
        self._exc: SoftAssertionError = SoftAssertionError()
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
            self._fail_mode = fail_mode

    def _get_excinfo(self) -> pytest.ExceptionInfo:
        return pytest.ExceptionInfo.from_exc_info((type(self._exc), self._exc, None))

    def assert_all(self) -> None:
        """ Verify that all supplied verifications are true. """
        if self._already_failed:
            return 
        if len(getattr(self._exc, "__notes__", [])) > 0:
            self._already_failed = True
            if self._fail_mode == "fail":
                pytest.fail()
            else:
                pytest.xfail()

    #
    # Method-style verifications
    #

    def verify(self, condition: bool, msg: str = None) -> None:
        """
        Verify a condition.
        Args:
            condition (bool): The condition to verify.
            msg (str): The message to display if the verification fails.
        """
        if not condition:
            self._exc.add_note(_build_exception_message(None, msg))

    def equal(self, actual: object, expected: object, msg: str = None) -> None:
        """
        Verify two values are equals.
        Args:
            actual (object): The first value to compare.
            expected (object): The second value to compare.
            msg (str): The message to display if the verification fails.
        """
        if expected != actual:
            self._exc.add_note(
                _build_exception_message(f"Expected: '{expected}', got: '{actual}'", msg)
            )

    def not_equal(self, actual: object, unexpected: object, msg: str = None) -> None:
        """
        Verify two values are different.
        Args:
            actual (object): The first value to compare.
            unexpected (object): The second value to compare.
            msg (str): The message to display if the verification fails.
        """
        if unexpected == actual:
            self._exc.add_note(
                _build_exception_message(f"Unexpected: '{unexpected}'", msg)
            )

    def true(self, condition: bool, msg: str = None) -> None:
        """
        Verify a condition is true.
        Args:
            condition (bool): The condition to verify.
            msg (str): The message to display if the verification fails.
        """
        if not condition:
            self._exc.add_note(
                _build_exception_message(f"Expected: 'True'", msg)
            )

    def false(self, condition: bool, msg: str = None) -> None:
        """
        Verify a condition is false.
        Args:
            condition (bool): The condition to verify.
            msg (str): The message to display if the verification fails.
        """
        if condition:
            self._exc.add_note(
                _build_exception_message(f"Expected: 'False'", msg)
            )

    def none(self, obj: object, msg: str = None) -> None:
        """
        Verify a value is None.
        Args:
            obj (object): The value to verify.
            msg (str): The message to display if the verification fails.
        """
        if obj is not None:
            self._exc.add_note(
                _build_exception_message(f"Expected: 'None', got: '{obj}'", msg)
            )

    def not_none(self, obj: object, msg: str = None) -> None:
        """
        Verify a value is not None.
        Args:
            obj (object): The value to verify.
            msg (str): The message to display if the verification fails.
        """
        if obj is None:
            self._exc.add_note(
                _build_exception_message(f"Unexpected: 'None'", msg)
            )

    def instance_of(self, obj: object, clazz: type, msg=None) -> None:
        """
        Verify a value is an instance of class.
        Args:
            obj (object): The value to verify.
            clazz (type):  The expected class-type.
            msg (str): The message to display if the verification fails.
        """
        if not isinstance(obj, clazz):
            self._exc.add_note(
                _build_exception_message(f"Expected: '{clazz.__name__}', got: '{type(obj).__name__}'", msg)
            )

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
            self._exc.add_note(
                _build_exception_message(f"Unexpected: '{clazz.__name__}'", msg)
            )

    #
    # Context managers for exception verifications
    #

    @contextmanager
    def raises(
        self,
        expected_exception: type[Exception] | tuple[type[Exception], ...] = type[Exception],
        match: str | re.Pattern[str] = None,
        msg: str = None
    ) -> ExceptionInfo:
        """
        Verify that a code block raises a given exception.
        Args:
            expected_exception (Exception | tuple): The exception(s) to verify.
            match (str | regexp): The text or regular expression to verify in the exception string representation and its notes.
            msg (str): The message to display if the verification fails.
        """
        # msg = msg if msg else ''
        excinfo = pytest.ExceptionInfo.for_later()
        check_match = False
        try:
            yield excinfo
        except expected_exception as e:
            # Correct exception was raised → check match later
            check_match = True and match not in (None, "", r'^$')
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        except Exception as e:
            # Wrong exception type → record as soft failure
            self._exc.add_note(_build_exception_message(
                f"Expected: '{expected_exception.__name__}', got: '{type(e).__name__}: {e}'", msg)
            )
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        else:
            # No exception was raised → record as soft failure
            self._exc.add_note(_build_exception_message(
                f"Expected: '{expected_exception.__name__}', but nothing was raised", msg)
            )

        # Verify match in exception constructor argument(s) and notes
        if check_match and not _search_matches(excinfo, match):
            # No match → record as soft failure
            notes = hasattr(excinfo.value, '__notes__')
            representation = f"the exception representation '{excinfo.value}'"
            if notes:
                representation += f" or notes {notes}"
            self._exc.add_note(_build_exception_message(
                f"Match '{match}' not found in {representation}'", msg)
            )

    @contextmanager
    def does_not_raise(
        self,
        unexpected_exception: type[Exception] | tuple[type[Exception], ...] = type[Exception],
        match: str | re.Pattern[str] = None,
        msg: str = None
    ) -> ExceptionInfo:
        """
        Verify that a code block raises does not raise a given exception.
        Args:
            unexpected_exception (Exception | tuple): The exception(s) to verify.
            match (str | regexp): The text or regular expression to verify in the exception string representation and its notes.
            msg (str): The message to display if the verification fails.
        """
        # msg = msg if msg else ''
        excinfo = pytest.ExceptionInfo.for_later()
        check_match = False
        exc_raised = False
        try:
            yield excinfo
        except unexpected_exception as e:
            # Wrong exception type → check match later
            exc_raised = True
            check_match = True and match not in (None, "", r'^$')
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
        except Exception as e:
            # Correct exception was raised → do nothing
            excinfo.fill_unfilled((type(e), e, e.__traceback__))

        # Check matches
        match_found = check_match and _search_matches(excinfo, match)

        # Record soft failure
        if exc_raised and unexpected_exception is not Exception:
            if not check_match or match_found:
                self._exc.add_note(_build_exception_message(
                    f"Unexpected: '{unexpected_exception.__name__}'", msg)
                )

        if match_found:
            notes = getattr(excinfo.value, "__notes__", None)
            representation = f"the exception representation '{excinfo.value}'"
            if notes:
                representation += f" or notes {notes}"
            self._exc.add_note(_build_exception_message(
                f"Match '{match}' found in {representation}", msg)
            )


def _build_exception_message(reason: str = None, msg: str = None) -> str:
    """
    Build the soft assertion failure message
    """
    message = f"SoftAssertionError: {reason}" if reason else "SoftAssertionError"
    message = f"{message}\n    {msg}" if msg else message
    return message


def _search_matches(excinfo: ExceptionInfo, match: str | re.Pattern[str]) -> bool:
    """
    Utility function to find a match in the exception string representation or in its notes.
    """
    if match is None:
        raise Exception("'match' parameter must be string or compiled pattern")
    # search in exception constructor arguments
    for arg in excinfo.value.args:
        result = re.search(match, str(arg))
        if result:
            return True
    # search in exception notes
    notes = getattr(excinfo.value, "__notes__", [])
    for note in notes:
        result = re.search(match, note)
        if result:
            return True
    return False
