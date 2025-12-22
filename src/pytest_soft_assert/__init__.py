import pytest
from _pytest._code.code import ExceptionInfo
from _pytest.outcomes import Failed, Skipped, XFailed
from .soft_assert import SoftAssert
from .exception import SoftAssertionError


SHORT_MSG = "Soft assertion error"


def update_test_status(report: pytest.TestReport, item, call) -> pytest.TestReport:
    # debug(report, item, call)
    if call.when == "call" and "soft" in item.funcargs:
        try:
            feature_request = item.funcargs["request"]
            fx_soft = feature_request.getfixturevalue("soft")
        except Exception:
            return report
        if fx_soft.errors:
            report.softexcinfo = fx_soft.get_excinfo()
            if fx_soft.failure_mode == "fail":
                exc = Failed()
            else:
                exc = XFailed()
            excinfo = ExceptionInfo.from_exc_info((type(exc), exc, ''))
            # Get original wasxfail attribute
            original_wasxfail = None
            if hasattr(report, "wasxfail") and report.wasxfail is not None:
                original_wasxfail = report.wasxfail

            if not fx_soft.already_failed:
                fx_soft.already_failed = True
                if report.outcome ==  "passed":
                    if original_wasxfail is not None:
                        report.outcome = "skipped"
                    else:
                        if fx_soft.failure_mode == "fail":
                            report.outcome = "failed"
                        else:
                            report.outcome = "skipped"
                            report.wasxfail = ""
                            call.excinfo = excinfo

                if report.outcome == "skipped":
                    if fx_soft.failure_mode == "fail":
                        if original_wasxfail is not None and item.get_closest_marker("xfail") is None:
                            report.outcome = "failed"
                            call.excinfo = excinfo
                            delattr(report, "wasxfail")
                        if original_wasxfail is not None and item.get_closest_marker("xfail") is not None:
                            report.outcome = "skipped"
                            call.excinfo = excinfo

                        if original_wasxfail is None:
                            call.excinfo = excinfo
                            if item.get_closest_marker("xfail"):
                                report.outcome = "skipped"
                                report.wasxfail = ""
                            else:
                                report.outcome = "failed"

                    else:
                        call.excinfo = excinfo
                        if original_wasxfail is None:
                            report.wasxfail = ""

    return report

def debug(report: pytest.TestReport, item, call) -> pytest.TestReport:
    if call.when == "call":
        print()
        print(item.name)
        print("outcome: ", report.outcome)
        if hasattr(report, "wasxfail"):
            print("wasxfail: ", report.wasxfail)
        if hasattr(call.excinfo, "value"):
            print("exc.type: ",call.excinfo.type)
            print("exc.value: ", call.excinfo.value)
            if hasattr(call.excinfo.value, "msg"):
                print("exc.msg: ", call.excinfo.value.msg)
        if item.get_closest_marker("xfail"):
            print("mark.xfail: ", item.get_closest_marker("xfail"))
        print()

__all__ = ['update_test_status', 'SoftAssertionError']
