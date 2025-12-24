import pytest
from _pytest.outcomes import Failed, Skipped, XFailed
from .soft_assert import SoftAssert
from .exception import SoftAssertionError


def update_test_status(
    report: pytest.TestReport,
    item: pytest.Item,
    call: pytest.CallInfo
) -> pytest.TestReport:
    if call.when != "call" or "soft" not in item.funcargs:
        return report
    try:
        request = item.funcargs["request"]
        fx_soft: SoftAssert = request.getfixturevalue("soft")
    except Exception:
        return report
    if len(fx_soft.errors) > 0:
        report.softexcinfo = fx_soft.get_excinfo()
    if fx_soft.already_failed or len(fx_soft.errors) == 0:
        return report

    # _debug(report, item, call)
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

    return report


def _debug(
    report: pytest.TestReport,
    item: pytest.Item,
    call: pytest.CallInfo
) -> pytest.TestReport:
    if call.when == "call":
        print()
        print(item.name)
        print("outcome: ", report.outcome)
        if hasattr(report, "wasxfail"):
            print("wasxfail: ", report.wasxfail)
        if hasattr(call.excinfo, "value"):
            print("exc.type: ", call.excinfo.type)
            print("exc.value: ", call.excinfo.value)
            if hasattr(call.excinfo.value, "msg"):
                print("exc.msg: ", call.excinfo.value.msg)
        if item.get_closest_marker("xfail"):
            print("mark.xfail: ", item.get_closest_marker("xfail"))
        print()


__all__ = ['update_test_status', 'SoftAssertionError']
