import os
import pytest
from _pytest.outcomes import Failed, Skipped, XFailed
from .soft_assert import SoftAssert
from .exception import SoftAssertionError


# DEBUG = os.getenv("PYTEST_SOFT_ASSERT_DEBUG", "false").lower() == "true"


def update_test_status(
    report: pytest.TestReport,
    item: pytest.Item,
    call: pytest.CallInfo,
    external_call: bool = True
) -> pytest.TestReport:
    """
    Modify the test result status according to the soft assertion verifications.
    """
    if call.when != "call" or "soft_assert" not in item.funcargs:
        return report
    try:
        request = item.funcargs["request"]
        fx_soft: SoftAssert = request.getfixturevalue("soft_assert")
    except Exception:
        return report

    # if external_call:
    #     _debug_message(report, "Called by another plugin\n")

    if len(fx_soft.errors) > 0:
        report.softexcinfo = fx_soft.get_excinfo()
    if fx_soft.already_failed or len(fx_soft.errors) == 0:
        # _debug_message(report, "Nothing to do. Soft assertion passed or failed during test execution\n")
        return report

    # _debug_before(report, item, call)

    fx_soft.already_failed = True

    is_fail_mode = fx_soft.fail_mode == "fail"
    has_wasxfail = getattr(report, "wasxfail", None) is not None
    has_xfail_marker = item.get_closest_marker("xfail") is not None

    exc = Failed() if is_fail_mode else XFailed()
    excinfo = pytest.ExceptionInfo.from_exc_info((type(exc), exc, ""))

    if report.outcome == "passed":
        if has_wasxfail:
            report.outcome = "skipped"
        else:
            if is_fail_mode:
                report.outcome = "failed"
            else:
                report.outcome = "skipped"
                report.wasxfail = ""
                call.excinfo = excinfo

    if report.outcome == "skipped":
        if not call.excinfo:
            call.excinfo = excinfo

        if is_fail_mode:
            if has_wasxfail:
                if not has_xfail_marker:
                    report.outcome = "failed"
                    delattr(report, "wasxfail")
            else:
                if has_xfail_marker:
                    report.outcome = "skipped"
                    report.wasxfail = ""
                else:
                    report.outcome = "failed"
        else:
            if not has_wasxfail:
                report.wasxfail = ""

    # _debug_after(report, item, call)
    return report


"""
def _debug_message(
    report: pytest.TestReport,
    msg: str
) -> None:
    if not DEBUG:
        return
    current_msg = getattr(report, "soft_assert_message", None)
    msg = msg if current_msg is None else current_msg + '\n' + msg
    setattr(report, "soft_assert_message", msg)


def _debug(
    report: pytest.TestReport,
    item: pytest.Item,
    call: pytest.CallInfo
) -> str:
    debug = []
    if call.when == "call":
        debug.append(f"outcome: {report.outcome}")
        if hasattr(report, "wasxfail"):
            debug.append(f"wasxfail: {report.wasxfail}")
        if hasattr(call.excinfo, "value"):
            debug.append(f"exc.type: {call.excinfo.type}")
            debug.append(f"exc.value: {call.excinfo.value}")
            if hasattr(call.excinfo.value, "output"):
                debug.append(f"exc.msg: {call.excinfo.value.msg}")
        if item.get_closest_marker("xfail"):
            debug.append(f"mark.xfail: {item.get_closest_marker('xfail')}")
    return debug


def _debug_before(
    report: pytest.TestReport,
    item: pytest.Item,
    call: pytest.CallInfo
) -> None:
    if not DEBUG:
        return
    debug = _debug(report, item, call)
    if len(debug) > 0:
        setattr(report, "soft_assert_before_update", '\n'.join(debug))


def _debug_after(
    report: pytest.TestReport,
    item: pytest.Item,
    call: pytest.CallInfo
) -> None:
    if not DEBUG:
        return
    debug = _debug(report, item, call)
    if len(debug) > 0:
        setattr(report, "soft_assert_after_update", '\n'.join(debug))
"""


__all__ = ['update_test_status', 'SoftAssertionError']
