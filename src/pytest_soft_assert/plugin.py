import os
import pytest
from . import update_test_status
from .soft_assert import SoftAssert


#
# Definition of test options
#
def pytest_addoption(parser):
    parser.addini(
        "soft_assert_mode",
        type="string",
        default="fail",
        help="How a soft assertion should fail. Accepted values: fail, xfail. Default value: fail."
    )


#
# Fixtures
#
def _fx_soft_assert_mode(config):
    """ The mode soft assertion should fail """
    value = config.getini("soft_assert_mode")
    return value if value in ('fail', 'xfail') else 'fail'


@pytest.fixture(scope="function")
def soft_assert(request):
    return SoftAssert(_fx_soft_assert_mode(request.config))


#
# Hooks
#
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report = update_test_status(report, item, call, False)
    outcome.force_result(report)
    if hasattr(report, "softexcinfo") and hasattr(report.softexcinfo.value, "__notes__"):
        report.sections.append(("Captured soft assertions", "\n\n".join(report.softexcinfo.value.__notes__)))

    """
    DEBUG = os.getenv("PYTEST_SOFT_ASSERT_DEBUG", "false").lower() == "true"
    if DEBUG:
        debug = []
        if hasattr(report, "soft_assert_message"):
            debug.append(report.soft_assert_message)
            delattr(report, "soft_assert_message")
        if hasattr(report, "soft_assert_before_update"):
            debug.append(f"Before result update\n{report.soft_assert_before_update}")
            delattr(report, "soft_assert_before_update")
        if hasattr(report, "soft_assert_after_update"):
            debug.append(f"After result update\n{report.soft_assert_after_update}")
            delattr(report, "soft_assert_after_update")
        if len(debug) > 0:
            report.sections.append(("Debug", '\n\n'.join(debug)))
    """
