=====
Usage
=====


Options
=======

These are the options that can be added to the ``pytest.ini`` file:

.. confval:: soft_assert_mode

   Type: ``str``

   Default value: ``fail``

The soft assertion failure mode.

* ``fail``: Failed soft assertions will trigger a **failed** test status.
* ``xfail``: Failed soft assertions will trigger a **xfailed** test status.


API
===

The function scoped fixture ``soft_assert`` provides the following methods:

Method-style verifications
--------------------------

soft_assert.verify
~~~~~~~~~~~~~~~~~~

``verify(condition: bool, msg: str = None)``

Verify a condition.

PARAMETERS:

* **condition**: The condition to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.verify(x > 5)
  soft_assert.verify(x > 5, msg="Verify variable x")

soft_assert.equal
~~~~~~~~~~~~~~~~~

``equal(actual: object, expected: object, msg: str = None)``

Verify two values are equals.

PARAMETERS:

* **actual**: The first value to compare.
* **expected**: The second value to compare.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.equal(x, y)
  soft_assert.equal(x, y, msg="Verify x == y")

soft_assert.not_equal
~~~~~~~~~~~~~~~~~~~~~

``not_equal(actual: object, unexpected: object, msg: str = None)``

Verify two values are different.

PARAMETERS:

* **actual**: The first value to compare.
* **expected**: The second value to compare.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.not_equal(x, y)
  soft_assert.not_equal(x, y, msg="Verify x != y")

soft_assert.true
~~~~~~~~~~~~~~~~

``true(value: bool, msg: str = None)``

Verify a value is ``True``.

PARAMETERS:

* **value**: The value to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.true(x)
  soft_assert.true(x, "Verify x is True")

soft_assert.false
~~~~~~~~~~~~~~~~~

``false(value: bool, msg: str = None)``

Verify a value is ``False``.

PARAMETERS:

* **value**: The value to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.false(x)
  soft_assert.false(x, msg="Verify x is False")

soft_assert.none
~~~~~~~~~~~~~~~~

``none(value: object, msg: str = None)``

Verify a value is ``None``.

PARAMETERS:

* **value**: The value to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.none(x)
  soft_assert.none(x, "Verify x is None")

soft_assert.not_none
~~~~~~~~~~~~~~~~~~~~

``not_none(value: object, msg: str = None)``

Verify a value is not ``None``.

PARAMETERS:

* **value**: The value to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.not_none(x)
  soft_assert.not_none(x, msg="Verify x is not None")

soft_assert.instance_of
~~~~~~~~~~~~~~~~~~~~~~~

``instance_of(value: object, clazz: type, msg=None)``

Verify a value is an instance of class.

PARAMETERS:

* **value**: The value to verify.
* **clazz**: The expected class-type.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.instance_of(x, int)
  soft_assert.instance_of(x, int, msg="Verify x is of type int")

soft_assert.not_instance_of
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``not_instance_of(value: object, clazz: type, msg: str = None)``

Verify a value is not an instance of class.

PARAMETERS:

* **value**: The value to verify.
* **clazz**: The unexpected class-type.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  soft_assert.instance_of(x, str)
  soft_assert.instance_of(x, str, msg="Verify x is not of type str")

Raise context manager
---------------------

soft_assert.raises
~~~~~~~~~~~~~~~~~~

``raises(expected_exception: Exception = Exception, msg: str = None)``

Verify that a block raises a given exception.

PARAMETERS:

* **expected_exception**: The exception to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  with soft_assert.raises(ArithmeticError):
      x / 0
  with soft_assert.raises(match="division by zero"):
      y / 0
  with soft_assert.raises(match="note"):
      e = Exception("Exception message")
      e.add_note("note")
      e.add_note("another note")
      raise e


soft_assert.does_not_raise
~~~~~~~~~~~~~~~~~~~~~~~~~~

``does_not_raise(unexpected_exception: Exception = Exception, msg: str = None)``

Verify that a block raises does not raise a given exception.

PARAMETERS:

* **unexpected_exception**: The exception to verify.
* **msg**: The message to display if the verification fails. (*optional*)

.. code-block:: python

  with soft_assert.does_not_raise(ArithmeticError):
      5 / 2

Other functions
---------------

soft_assert.assert_all
~~~~~~~~~~~~~~~~~~~~~~

``assert_all()``

Assert that all collected verifications are true.

.. code-block:: python

  soft_assert.assert_all()

soft_assert.set_fail_mode
~~~~~~~~~~~~~~~~~~~~~~~~~

``set_fail_mode(fail_mode: Literal['fail', 'xfail'])``

Modify the soft assertion mode at runtime.

A soft_assertion failure will result in the following test status:

* **failed** if the soft assertion mode is ``fail``.
* **xfailed** if the soft assertion mode is ``xfail``.

PARAMETERS:

* **fail_mode**: The soft assertion mode. Possible values: ``fail`` or ``xfail``.

.. code-block:: python

  soft_assert.set_fail_mode('xfail')


Examples
========


Method-style verifications:

.. code-block:: python

  def test_example_01(soft_assert):
      soft_assert.verify(5 > 0, "Verify a condition is true")
      soft_assert.true(x, "Verify variable x is true")
      soft_assert.equal(a, b, "Verify a and b are equal")
      soft_assert.not_none(y, "Verify variable y is not none")
      soft_assert.instance_of(5, int, "Verify a variable is instance of int")

Raise context manager:

.. code-block:: python

  def test_example_02(soft_assert):
      with soft_assert.raises(ArithmeticError) as excinfo:
          5 / 0
      # Examine the raised Exception (type and message)
      print("The exception type: ", excinfo.type)
      print("The exception value: ", excinfo.value)

To assert all collected verifications before the end of the test:

.. code-block:: python

  def test_example_03(soft_assert):
      soft_assert.verify(5 < 0)
      soft_assert.none(None)
      # Assert verifications and stop test execution if a verification fails.
      soft_assert.assert_all()
      # Continue the test with other soft assertions
      soft_assert.false(False)
      soft_assert.verify(5 == 0)
      soft_assert.assert_all()


To modify the soft assertion mode for one particular test:

.. code-block:: python

  def test_example_04(soft_assert):
      soft_assert.set_fail_mode('xfail')
      soft_assert.verify(5 > 0)
      soft_assert.true(x)


Warning
=======

This plugin modifies the status of test results.

If other Pytest plugins need to read test result status, those plugins need to explicitly call **pytest_soft_assert** plugin to get the updated test result status.

This is a code snippet that other plugins can include:
 
.. code-block:: python

  @pytest.hookimpl(hookwrapper=True)
  def pytest_runtest_makereport(item, call):
      outcome = yield
      report = outcome.get_result()

      # If pytest-soft-assert is loaded, update test result status
      if call.when == "call" and item.config.pluginmanager.has_plugin("pytest_soft_assert"):
          try:
              soft_assert = item.config.pluginmanager.getplugin("pytest_soft_assert")
              report = soft_assert.update_test_status(report, item, call)
          except Exception:
              pass
