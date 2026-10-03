import pytest
import re
from contextlib import contextmanager
from typing import Literal, Iterable
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
        expected_exception: type[Exception] | tuple[type[Exception]] = None,
        match: str = None,
        msg: str = None
    ) -> ExceptionInfo:
        """
        Verify that a code block raises an exception type or one of its subclasses.

        Args:
            expected_exception (type[Exception] | tuple[type[Exception]]): The exception(s) to verify.
            match (str): The text or regular expression to verify in the exception string exc_repr and its notes.
            msg (str): The message to display if the verification fails.

        Yields:
            Exceptioninfo: The information about the captured exception.
        """
        # Make the first argument a tuple
        if expected_exception is None:
            expected_exception = tuple()
        if type(expected_exception) is not tuple:
            expected_exception = (expected_exception, )
        # Build exception(s) name(s) to include in assertion message
        exc_names = [extype.__name__ for extype in expected_exception]
        exc_label = None
        if len(exc_names) == 1:
            exc_label = exc_names[0]
        if len(exc_names) > 1:
            exc_label = f"[{', '.join(exc_names)}]"
        excinfo = pytest.ExceptionInfo.for_later()
        check_match = False
        matched_exc = None
        try:
            yield excinfo
        except Exception as e:
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
            # check against expected exception(s)
            matched_exc = _get_matching_type(type(e), expected_exception)
            if matched_exc:
                # Expected exception was raised → check match later
                check_match = True and match not in (None, "", r'^$')
            elif exc_label is not None:
                # Unexpected exception was raised → record soft failure
                self._exc.add_note(_build_exception_message(
                    f"Expected exception: '{exc_label}', got: '{type(e).__name__}'", msg)
                )
        else:
            # No exception was raised → record soft failure
            if exc_label is not None and match is not None:
                self._exc.add_note(_build_exception_message(
                    f"Expected exception: '{exc_label}' with match: '{match}', but nothing was raised", msg)
                )
            if exc_label is not None and match is None:
                self._exc.add_note(_build_exception_message(
                    f"Expected exception: '{exc_label}', but nothing was raised", msg)
                )
            if exc_label is None and match is not None:
                self._exc.add_note(_build_exception_message(
                    f"Expected exception with match: '{match}', but nothing was raised", msg)
                )

        # Verify match in exception constructor argument(s) and notes
        if check_match and not _search_matches(excinfo, match):
            # No match → record as soft failure
            notes = hasattr(excinfo.value, '__notes__')
            exc_repr = f"the exception representation '{excinfo.value}'"
            if notes:
                exc_repr += f" or notes {notes}"
            self._exc.add_note(_build_exception_message(
                f"Match '{match}' not found in {exc_repr}'", msg)
            )

    @contextmanager
    def does_not_raise(
        self,
        unexpected_exception: type[Exception] | tuple[type[Exception]] = None,
        match: str = None,
        msg: str = None
    ) -> ExceptionInfo:
        """
        Verify that a code block raises does not raise an exception type or one of its subclasses.

        Args:
            unexpected_exception (type[Exception] | tuple[type[Exception]]): The exception(s) to verify.
            match (str): The text or regular expression to verify in the exception string representation and its notes.
            msg (str): The message to display if the verification fails.

        Yields:
            Exceptioninfo: The information about the captured exception.
        """
        # Make the first argument a tuple
        if unexpected_exception is None:
            unexpected_exception = tuple()
        if type(unexpected_exception) is not tuple:
            unexpected_exception = (unexpected_exception, )
        excinfo = pytest.ExceptionInfo.for_later()
        check_match = False
        exc_raised = None
        match_found = False
        matched_exc = None
        try:
            yield excinfo
        except Exception as e:
            excinfo.fill_unfilled((type(e), e, e.__traceback__))
            matched_exc = _get_matching_type(type(e), unexpected_exception)
            if matched_exc:
                # Unexpected exception was raised → check match later
                exc_raised = type(e).__name__
                check_match = True and match not in (None, "", r'^$')
            if len(unexpected_exception) == 0:
                # First parameter not provided → check match later
                check_match = True and match not in (None, "", r'^$')
            # Check match
            match_found = check_match and _search_matches(excinfo, match)

        # Include super class in exception name for assertion message, if necessary
        if matched_exc and exc_raised != matched_exc:
            exc_raised = f"{exc_raised}({matched_exc})"

        # Record soft failure
        if exc_raised and len(unexpected_exception) > 0 and match is None:
            self._exc.add_note(_build_exception_message(
                f"Unexpected exception: '{exc_raised}'", msg)
            )

        if match_found:
            notes = getattr(excinfo.value, "__notes__", None)
            exc_repr = f"the exception representation '{excinfo.value}'"
            if notes:
                exc_repr += f" or notes {notes}"
            if (exc_raised is None or len(unexpected_exception) == 0):
                self._exc.add_note(_build_exception_message(
                    f"Unexpected match '{match}' found in {exc_repr}", msg)
                )
            else:
                self._exc.add_note(_build_exception_message(
                    f"Unexpected exception: '{exc_raised}' and match: '{match}' found in {exc_repr}", msg)
                )
                

def _get_matching_type(arg: type[Exception], collection: Iterable[type[[Exception]]]) -> str:
    """
    Get the name of the matching exception class or super class type in a collection.
    
    Returns:
        str: The name of the matching exception class or super class type. Otherwise, None.
    """
    for elem in collection:
        if arg is elem or issubclass(arg, elem):
            return elem.__name__
    return None


def _build_exception_message(reason: str = None, msg: str = None) -> str:
    """
    Build the soft assertion failure message.
    """
    message = f"SoftAssertionError: {reason}" if reason else "SoftAssertionError"
    message = f"{message}\n    {msg}" if msg else message
    return message


def _search_matches(excinfo: ExceptionInfo, match: str | re.Pattern[str]) -> bool:
    """
    Utility function to find a match in the exception constructor arguments or in its notes.
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
