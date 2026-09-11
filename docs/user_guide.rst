=====
Usage
=====


Options
=======

These are the options that can be added to the ``pytest.ini`` file:

* ``soft_assert_mode``

The soft assertion failure mode

Accepted values:

* ``fail``: Failed soft assertions will trigger a **failed** test status.

* ``xfail``: Failed soft assertions will trigger a **xfailed** test status.

Default value: ``fail``


API
===

The function scoped fixture ``soft_assert`` provides the following methods:

Method-style verifications
--------------------------

.. code-block:: python

  verify(self, condition: bool, msg: str = None)
  """
  Verify a condition.
  Args:
      condition (bool): The condition to verify.
      msg (str): The message to display if the verification fails.
  """

  equal(self, actual: object, expected: object, msg: str = None)
  """
  Verify two values are equals.
  Args:
      actual (object): The first value to compare.
      expected (object): The second value to compare.
      msg (str): The message to display if the verification fails.
  """

  not_equal(self, actual: object, unexpected: object, msg: str = None)
  """
  Verify two values are different.
  Args:
      actual (object): The first value to compare.
      unexpected (object): The second value to compare.
      msg (str): The message to display if the verification fails.
  """

  true(self, condition: bool, msg: str = None)
  """
  Verify a condition is true.
  Args:
      condition (bool): The condition to verify.
      msg (str): The message to display if the verification fails.
  """

  false(self, condition: bool, msg: str = None)
  """
  Verify a condition is false.
  Args:
      condition (bool): The condition to verify.
      msg (str): The message to display if the verification fails.
  """

  none(self, obj: object, msg: str = None)
  """
  Verify a value is None.
  Args:
      obj (object): The value to verify.
      msg (str): The message to display if the verification fails.
  """

  not_none(self, obj: object, msg: str = None)
  """
  Verify a value is not None.
  Args:
      obj (object): The value to verify.
      msg (str): The message to display if the verification fails.
  """

  instance_of(self, obj: object, clazz: type, msg=None)
  """
  Verify a value is an instance of class.
  Args:
      obj (object): The value to verify.
      clazz (type):  The expected class-type.
      msg (str): The message to display if the verification fails.
  """

  not_instance_of(self, obj: object, clazz: type, msg: str = None)
  """
  Verify a value is not an instance of class.
  Args:
      obj (object): The value to verify.
      clazz (type):  The unexpected class-type.
      msg (str): The message to display if the verification fails.
  """

Raise context manager
---------------------

.. code-block:: python

  raises(self, expected_exception: Exception = Exception, msg: str = None)
  """
  Verify that a block raises a given exception.
  Args:
      expected_exception (Exception): The exception to verify.
      msg (str): The message to display if the verification fails.
  """

  does_not_raise(self, unexpected_exception: Exception = Exception, msg: str = None)
  """
  Verify that a block raises does not raise a given exception.
  Args:
      unexpected_exception (Exception): The exception to verify.
      msg (str): The message to display if the verification fails.
  """

~~~~

To assert all collected verifications before the end of the text:

.. code-block:: python

  assert_all()
  """ Verify that all supplied verifications are true. """

To modify the soft assertion mode at runtime:

.. code-block:: python

  set_fail_mode(fail_mode: Literal['fail', 'xfail'])
  """
  Set the soft assertion mode.
  A soft_assertion failure will result in the following test status:
    - Failed if the soft assertion mode is 'fail'.
    - XFailed if the soft assertion mode is 'xfail'.
  Args:
      fail_mode (str): The soft assertion mode. Possible values: 'fail' or 'xfail'.
  """


Examples
========


Methos-style verifications:

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
      print("The exception type: ", excinfo.type)
      print("The exception value: ", excinfo.value)

To assert all collected verifications before the end of the test:

.. code-block:: python

  def test_example_03(soft_assert):
      soft_assert.verify(5 > 0)
      soft_assert.true(x)
      soft_assert.assert_all()
      soft_assert.false(False)
      soft_assert.verify(5 == 0)


Warning
=======

This plugin modifies the status of test results.

If other plugins need to read test execution status, those plugins need explicitly call pytest_soft_assert plugin to get the updated test result status.

This is a code snippet that other plugins can include:
 
.. code-block:: python

  # If pytest-soft-assert is loaded, update test result status
  if call.when == "call" and item.config.pluginmanager.has_plugin("pytest_soft_assert"):
      try:
          soft_assert = item.config.pluginmanager.getplugin("pytest_soft_assert")
          report = soft_assert.update_test_status(report, item, call)
      except Exception:
          pass
