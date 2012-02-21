##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from persistent import Persistent
from ZODB.POSException import ConflictError
from zope.interface import implements

from appendonly.interfaces import IAppendStack

class _LayerFull(ValueError):
    pass


class _LayerBase(object):
    """ Base for both _Layer and _ArchiveLayer.
    """
    def __init__(self, max_length=100, generation=0):
        self._stack = []
        self._max_length = max_length
        self._generation = generation

    def __iter__(self):
        at = len(self._stack)
        while at > 0:
            at = at - 1
            yield at, self._stack[at]

    def newer(self, latest_index):
        """ Yield items appended after `latest_index`.
        
        Implemented as a method on the layer to work around lack of generator
        expressions in Python 2.5.x.
        """
        for index, obj in self:
            if index <= latest_index:
                break
            yield index, obj


class _Layer(_LayerBase):
    """ Append-only list with maximum length.

    - Raise `_LayerFull` on attempts to exceed that length.

    - Iteration occurs in reverse order of appends, and yields (index, object)
      tuples.

    - Hold generation (a sequence number) on behalf of `AppendStack`.
    """

    def push(self, obj):
        if len(self._stack) >= self._max_length:
            raise _LayerFull()
        self._stack.append(obj)


class AppendStack(Persistent):
    """ Append-only stack w/ garbage collection.

    - Append items to most recent layer until full;  then add a new layer.
    
    - Discard "oldest" layer starting a new one.

    - Invariant:  the sequence of (generation, id) increases monotonically.

    - Iteration occurs in reverse order of appends, and yields
      (generation, index, object) tuples.
    """
    implements(IAppendStack)

    def __init__(self, max_layers=10, max_length=100):
        self._max_layers = max_layers
        self._max_length = max_length
        self._layers = [_Layer(max_length, generation=0L)]

    def __iter__(self):
        """ See IAppendStack.
        """
        for layer in self._layers:
            for index, item in layer:
                yield layer._generation, index, item

    def newer(self, latest_gen, latest_index):
        """ See IAppendStack.
        """
        for gen, index, obj in self:
            if (gen, index) <= (latest_gen, latest_index):
                break
            yield gen, index, obj

    def push(self, obj, pruner=None):
        """ See IAppendStack.
        """
        layers = self._layers
        max = self._max_layers
        try:
            layers[0].push(obj)
        except _LayerFull:
            new_layer = _Layer(self._max_length,
                              generation=layers[0]._generation+1L)
            new_layer.push(obj)
            self._layers.insert(0, new_layer)
        self._layers, pruned = layers[:max], layers[max:]
        if pruner is not None:
            for layer in pruned:
                pruner(layer._generation, layer._stack)

    def __getstate__(self):
        layers = [(x._generation, x._stack) for x in self._layers]
        return (self._max_layers, self._max_length, layers)

    def __setstate__(self, state):
        self._max_layers, self._max_length, layer_data = state
        self._layers = []
        for generation, items in layer_data:
            layer = _Layer(self._max_length, generation)
            for item in items:
                layer.push(item)
            self._layers.append(layer)

    #
    # ZODB Conflict resolution
    #
    # The overall approach here is to compute the 'delta' from old -> new
    # (objects added in new, not present in old), and push them onto the
    # committed state to create a merged state.
    # Unresolvable errors include:
    # - any difference between O <-> C <-> N on the non-layers attributes.
    # - either C or N has its oldest layer in a later generation than O's
    #   newest layer.
    # Compute the O -> N diff via the following:
    # - Find the layer, N' in N whose generation matches the newest generation
    #   in O, O'.
    # - Compute the new items in N` by slicing it using the len(O').
    # - That slice, plus any newer layers in N, form the set to be pushed
    #   onto C.
    #   
    def _p_resolveConflict(self, old, committed, new):
        o_m_layers, o_m_length, o_layers = old
        c_m_layers, c_m_length, c_layers = committed
        m_layers = [x[:] for x in c_layers]
        n_m_layers, n_m_length, n_layers = new
        
        if not o_m_layers == n_m_layers == n_m_layers:
            raise ConflictError('Conflicting max layers')

        if not o_m_length == c_m_length == n_m_length:
            raise ConflictError('Conflicting max length')

        o_latest_gen = o_layers[0][0]
        o_latest_items = o_layers[0][1]
        c_earliest_gen = c_layers[-1][0]
        n_earliest_gen = n_layers[-1][0]

        if o_latest_gen < c_earliest_gen:
            raise ConflictError('Committed obsoletes old')

        if o_latest_gen < n_earliest_gen:
            raise ConflictError('New obsoletes old')

        new_objects = []
        for n_generation, n_items in n_layers:
            if n_generation > o_latest_gen:
                new_objects[:0] = n_items
            elif n_generation == o_latest_gen:
                new_objects[:0] = n_items[len(o_latest_items):]
            else:
                break

        while new_objects:
            to_push, new_objects = new_objects[0], new_objects[1:]
            if len(m_layers[0][1]) == c_m_length:
                m_layers.insert(0, (m_layers[0][0]+1L, []))
            m_layers[0][1].append(to_push)

        return c_m_layers, c_m_length, m_layers[:c_m_layers]


class _ArchiveLayer(Persistent, _LayerBase):
    """ Allow saving layer info in separate persistent sub-objects.

    Archive layers don't support 'push' (they are conceptually immuatble).

    These layers will be kept in a linked list in an archive.
    """
    _next = None

    @classmethod
    def fromLayer(klass, layer):
        copy = klass(layer._max_length, layer._generation)
        copy._stack[:] = layer._stack
        return copy


class Archive(Persistent):
    """ Manage layers discarded from an AppendStack as a persistent linked list.
    """
    _head = None
    _generation = -1

    def __iter__(self):
        current = self._head
        while current is not None:
            for index, item in current:
                yield current._generation, index, item
            current = current._next

    def addLayer(self, generation, items):
        if generation <= self._generation:
            raise ValueError(
                    "Cannot add older layers to an already-populated archive")
        copy = _ArchiveLayer(generation=generation)
        copy._stack[:] = items
        self._head, copy._next = copy, self._head
        self._generation = generation

    #
    # ZODB Conflict resolution
    #
    # Archive is a simpler problem, because the only mutation occurs when
    # adding a layer.  We can resolve IFF the committed version and the new
    # version have the same generation:  in that case, we can just keep the
    # committed version, because the two layers are equivalent.
    #
    # This neglects the case of independently-constructed layers:  we presume
    # that the source layers are coming from the same AppendStack, in which
    # case they will be identical.
    #
    def _p_resolveConflict(self, old, committed, new):
        if committed['_generation'] == new['_generation']:
            return committed
        raise ConflictError('Conflicting generations')
