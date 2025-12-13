import pytest
from _pytest._code.code import ExceptionInfo
from .soft_assert import SoftAssert, SoftAssertionError


def update_test_status(report: pytest.TestReport, item, call) -> pytest.TestReport:
    if call.when == "call" and "soft" in item.funcargs:
        try:
            feature_request = item.funcargs["request"]
            fx_soft = feature_request.getfixturevalue("soft")
        except Exception:
            return
        if fx_soft.errors:
            msg = "\n".join(fx_soft.errors)
            exc = SoftAssertionError(msg)
            excinfo = ExceptionInfo.from_exc_info((type(exc), exc, exc.__traceback__))
            report.softexcinfo = excinfo
            if not fx_soft.already_failed:
                call.excinfo = excinfo
                fx_soft.already_failed = True
                if fx_soft.failure_mode == "fail":
                    report.outcome = "failed"
                else:
                    report.outcome = "skipped"
                    report.wasxfail = 'SoftAssertionError'

    return report


__all__ = ['update_test_status']
