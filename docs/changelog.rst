=========
Changelog
=========


1.0.0
=====

**Initial release**


1.0.1
=====

Improvement
------------

- ``raises`` and ``does_not_raise`` methods can receive a parameter containing a string or a regular expression that is verified in the exception string representation and its notes ([PEP 678](https://peps.python.org/pep-0678/)).

  This improvement makes these two methods closer to the ``pytest.raises`` function.
