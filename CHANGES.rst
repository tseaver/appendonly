``appendonly`` Changelog
========================

After 1.0.1
-----------

- Added ``Accumulator.extend`` method to enhance list-ness.

- Added support for PyPy.

- Added support for Python 3.2 / 3.3.

1.0.1 (2013-02-25)
------------------

- Fixed brown-bag in 1.0 release ('Accumulator.append' changes were not
  persisted).

1.0 (2013-02-25)
----------------

- Added a conflict-free 'Accumulator' class: manages a queue of items which
  can be iterated, appended to, or conumed entirely (no partial / pop).

- Automated tests for supported Python versions via 'tox'.

- Dropped support for Python 2.4 / 2.5.


0.10 (2012-02-21)
------------------

- Added an 'Archive' class, intended to support long-term storage of the
  layer data pruned from an 'AppendStack'.


0.9 (2010-08-09)
----------------

- Initial public release.