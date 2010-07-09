``appendonly`` README
=====================

This package provides a set of data structures for use in ZODB applications
where standard BTrees are poor fits for an application's requirements.

In particular, these data structures are designed to minimize conflict
errors when doing frequent "append" operations to queues and stacks.


``appendonly.AppendStack``
--------------------------

This class provides a LIFO stack of separately-persisted objects:

- The stack manages a set of "layer" objects, with a configurable limit
  on the number of layers.  Each layer has a configurable maximum length,
  and a sequential generation number.

- The stack appends items to most recent layer until the layer is filled;
  it then adds a new layer.

- If the number of layers then exceeds the configured maximum, the stack
  pruneds the oldest layer(s) to conform to that limit.

- When pruning, the stack calls an application-supplied callback for
  archiving / cleanup of the pruned layer.

- Iteration over the stack yields (generation, index, object) tuples.
  in reverse order to that in which the objects were appended.

The stack is implemented as a single persistent record, with custom
ZODB conflict resolution code.
