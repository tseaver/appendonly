``appendonly`` Changelog
========================

1.2 (2014-12-28)
----------------

- Add support for Python 3.4.

- Make ``ZODB`` dependency unconditional, now that it fully supports Py3k.

- Add support for testing on Travis.

1.1 (2013-11-28)
----------------

- Add ``Accumulator.extend`` method to enhance list-ness.

- Add support for PyPy.

- Add support for Python 3.2 / 3.3.

1.0.1 (2013-02-25)
------------------

- Fix brown-bag in 1.0 release (``Accumulator.append`` changes were not
  persisted).

1.0 (2013-02-25)
----------------

- Add a conflict-free 'Accumulator' class: manages a queue of items which
  can be iterated, appended to, or conumed entirely (no partial / pop).

- Automate tests for supported Python versions via 'tox'.

- Drop support for Python 2.4 / 2.5.


0.10 (2012-02-21)
------------------

- Add an 'Archive' class, intended to support long-term storage of the
  layer data pruned from an 'AppendStack'.


0.9 (2010-08-09)
----------------

- Initial public release.
