``appendonly``
==============

.. image:: https://travis-ci.org/tseaver/appendonly.png?branch=master
        :target: https://travis-ci.org/tseaver/appendonly

This package provides a set of data structures for use in ZODB applications
where standard BTrees are poor fits for an application's requirements.

In particular, these data structures are designed to minimize conflict
errors when doing frequent "append" operations to queues and stacks.

`Read the docs online <http://appendonly.rtfd.org/>`_
