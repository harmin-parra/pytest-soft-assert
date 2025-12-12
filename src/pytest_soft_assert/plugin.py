import pytest
from .soft_assert import SoftAssert
from . import update_test_status


#
# Definition of test options
#
def pytest_addoption(parser):
    parser.addini(
        "soft_assert_mode",
        type="string",
        default="xfail",
        help="The mode soft assertion should fail. Accepted values: fail, xfail"
    )


def _fx_soft_assert_mode(config):
    """ The mode soft assertion should fail """
    value = config.getini("soft_assert_mode")
    return value if value in ('fail', 'xfail') else 'xfail'


#
# Fixture
#
@pytest.fixture(scope="function")
def soft(request):
    return SoftAssert(_fx_soft_assert_mode(request.config))


#
# Hooks
#
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report = update_test_status(report, item, call)
    outcome.force_result(report)
