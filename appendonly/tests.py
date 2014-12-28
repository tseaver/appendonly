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
import unittest


class _LayerTestBase(object):

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        layer = self._makeOne()
        self.assertEqual(layer._max_length, 100)
        self.assertTrue(type(layer._stack) is list)
        self.assertEqual(layer._generation, 0)

    def test_ctor_w_positional(self):
        layer = self._makeOne(4, 14)
        self.assertEqual(layer._max_length, 4)
        self.assertTrue(type(layer._stack) is list)
        self.assertEqual(layer._generation, 14)

    def test_ctor_w_max_length(self):
        layer = self._makeOne(max_length=14)
        self.assertEqual(layer._max_length, 14)

    def test_ctor_w_generation(self):
        layer = self._makeOne(generation=12)
        self.assertEqual(layer._generation, 12)

    def test___iter___empty(self):
        layer = self._makeOne()
        self.assertEqual(list(layer), [])

    def test_newer_empty(self):
        layer = self._makeOne()
        self.assertEqual(list(layer.newer(0)), [])


class LayerTests(unittest.TestCase, _LayerTestBase):

    def _getTargetClass(self):
        from appendonly import _Layer
        return _Layer

    def test___iter___filled(self):
        layer = self._makeOne()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        layer.push(OBJ3)
        self.assertEqual(list(layer), [(2, OBJ3), (1, OBJ2), (0, OBJ1)])

    def test_newer_miss(self):
        layer = self._makeOne()
        layer.push(object())
        self.assertEqual(list(layer.newer(0)), [])

    def test_newer_hit(self):
        layer = self._makeOne()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        layer.push(OBJ3)
        self.assertEqual(list(layer.newer(0)),
                         [(2, OBJ3), (1, OBJ2)])

    def test_push_one(self):
        layer = self._makeOne()
        OBJ = object()
        layer.push(OBJ)
        self.assertEqual(list(layer), [(0, OBJ)])

    def test_push_many(self):
        layer = self._makeOne()
        OBJ1, OBJ2, OBJ3 = object(), object(), object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        layer.push(OBJ3)
        self.assertEqual(list(layer), [(2, OBJ3),
                                       (1, OBJ2),
                                       (0, OBJ1),
                                      ])

    def test_push_overflow(self):
        layer = self._makeOne(2)
        OBJ1, OBJ2, OBJ3 = object(), object(), object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        self.assertRaises(ValueError, layer.push, OBJ3)
        self.assertEqual(list(layer), [(1, OBJ2),
                                       (0, OBJ1),
                                      ])


class AppendStackTests(unittest.TestCase):

    def _getTargetClass(self):
        from appendonly import AppendStack
        return AppendStack

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_IAppendStack(self):
        from zope.interface.verify import verifyClass
        from appendonly.interfaces import IAppendStack
        verifyClass(IAppendStack, self._getTargetClass())

    def test_instance_conforms_to_IAppendStack(self):
        from zope.interface.verify import verifyObject
        from appendonly.interfaces import IAppendStack
        verifyObject(IAppendStack, self._makeOne())

    def test_ctor_defaults(self):
        stack = self._makeOne()
        self.assertEqual(stack._max_layers, 10)
        self.assertEqual(stack._max_length, 100)

    def test_ctor_w_max_layers(self):
        stack = self._makeOne(max_layers=37)
        self.assertEqual(stack._max_layers, 37)

    def test_ctor_w_max_length(self):
        stack = self._makeOne(max_length=14)
        self.assertEqual(stack._max_length, 14)

    def test___iter___empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack), [])

    def test_newer_empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack.newer(0, 0)), [])

    def test_newer_miss(self):
        stack = self._makeOne()
        stack.push(object())
        self.assertEqual(list(stack.newer(0, 0)), [])

    def test_newer_hit(self):
        stack = self._makeOne()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        stack.push(OBJ1)
        stack.push(OBJ2)
        stack.push(OBJ3)
        self.assertEqual(list(stack.newer(0, 0)),
                         [(0, 2, OBJ3), (0, 1, OBJ2)])

    def test_newer_hit_across_layers(self):
        stack = self._makeOne(max_length=2)
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        stack.push(OBJ1)
        stack.push(OBJ2)
        stack.push(OBJ3)
        self.assertEqual(list(stack.newer(0, 0)),
                         [(1, 0, OBJ3), (0, 1, OBJ2)])

    def test_push_one(self):
        stack = self._makeOne()
        OBJ = object()
        stack.push(OBJ)
        self.assertEqual(list(stack), [(0, 0, OBJ)])
        self.assertEqual(len(stack._layers), 1)

    def test_push_many(self):
        stack = self._makeOne(max_length=2)
        OBJ1, OBJ2, OBJ3 = object(), object(), object()
        stack.push(OBJ1)
        stack.push(OBJ2)
        stack.push(OBJ3)
        self.assertEqual(list(stack), [(1, 0, OBJ3),
                                       (0, 1, OBJ2),
                                       (0, 0, OBJ1),
                                      ])
        self.assertEqual(len(stack._layers), 2)
        self.assertEqual(stack._layers[0]._generation, 1)
        self.assertEqual(stack._layers[1]._generation, 0)

    def test_push_trimming_layers(self):
        stack = self._makeOne(max_layers=4)
        for obj in range(1001):
            stack.push(obj)
        found = list(stack)
        self.assertEqual(len(found), 301)
        self.assertEqual(found[0], (10, 0, 1000))
        self.assertEqual(found[-1], (7, 0, 700))
        self.assertEqual(len(stack._layers), 4)
        self.assertEqual(stack._layers[0]._generation, 10)
        self.assertEqual(stack._layers[1]._generation, 9)
        self.assertEqual(stack._layers[2]._generation, 8)
        self.assertEqual(stack._layers[3]._generation, 7)

    def test_push_trimming_layers_with_archive_utility(self):
        _pruned = {}
        def _prune(generation, items):
            _pruned[generation] = items
        stack = self._makeOne(max_layers=4)
        for obj in range(1001):
            stack.push(obj, pruner=_prune)
        found = list(stack)
        self.assertEqual(len(found), 301)
        self.assertEqual(found[0], (10, 0, 1000))
        self.assertEqual(found[-1], (7, 0, 700))
        self.assertEqual(len(stack._layers), 4)
        self.assertEqual(stack._layers[0]._generation, 10)
        self.assertEqual(stack._layers[1]._generation, 9)
        self.assertEqual(stack._layers[2]._generation, 8)
        self.assertEqual(stack._layers[3]._generation, 7)
        self.assertEqual(len(_pruned), 7)
        self.assertEqual(_pruned[0], list(range(0, 100)))
        self.assertEqual(_pruned[1], list(range(100, 200)))
        self.assertEqual(_pruned[2], list(range(200, 300)))
        self.assertEqual(_pruned[3], list(range(300, 400)))
        self.assertEqual(_pruned[4], list(range(400, 500)))
        self.assertEqual(_pruned[5], list(range(500, 600)))
        self.assertEqual(_pruned[6], list(range(600, 700)))

    def test___getstate___empty(self):
        stack = self._makeOne()
        self.assertEqual(stack.__getstate__(), (10, 100, [(0, [])]))

    def test___getstate___filled(self):
        stack = self._makeOne(2, 3)
        for i in range(10):
            stack.push(i)
        self.assertEqual(stack.__getstate__(),
                        (2, 3, [(3, [9]), (2, [6, 7, 8])]))

    def test___setstate___(self):
        stack = self._makeOne()
        STATE = (2,                 # _max_layers
                 3,                 # _max_length
                 [(3, [9]),        # _layers[0] as (generation, list)
                  (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                 ],
                )
        stack.__setstate__(STATE)
        self.assertEqual(stack._max_layers, 2)
        self.assertEqual(stack._max_length, 3)
        self.assertEqual(list(stack), [(3, 0, 9),
                                       (2, 2, 8),
                                       (2, 1, 7),
                                       (2, 0, 6),
                                      ])

    def test__p_resolveConflict_mismatched_max_layers(self):
        from appendonly import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (3,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_mismatched_max_length(self):
        from appendonly import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   4,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_old_latest_commited_earliest(self):
        from appendonly import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(5, [29]),        # _layers[0] as (generation, list)
                    (4, [26, 27, 28]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 10]),    # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_old_latest_new_earliest(self):
        from appendonly import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 10]),    # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(5, [29]),        # _layers[0] as (generation, list)
                    (4, [26, 27, 28]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_no_added_layers(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 10]),    # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 11]),    # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 10, 11]),# _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

    def test__p_resolveConflict_added_committed_layer(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4, [12]),       # _layers[0] as (generation, list)
                    (3, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 13]),    # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4, [12, 13]),   # _layers[0] as (generation, list)
                    (3, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

    def test__p_resolveConflict_added_new_layer(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9]),        # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3, [9, 10]),    # _layers[0] as (generation, list)
                    (2, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4, [13, 14]),   # _layers[0] as (generation, list)
                    (3, [9, 11, 12]),# _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4, [12, 13, 14]),# _layers[0] as (generation, list)
                    (3, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)


class ArchiveLayerTests(unittest.TestCase, _LayerTestBase):

    def _getTargetClass(self):
        from appendonly import _ArchiveLayer
        return _ArchiveLayer

    def test_is_persistent(self):
        from persistent import Persistent
        self.assertTrue(issubclass(self._getTargetClass(), Persistent))

    def test_fromLayer(self):
        from appendonly import _Layer
        klass = self._getTargetClass()
        source = _Layer(max_length=42, generation=13)
        for i in range(25):
            obj = object()
            source.push(obj)
        copied = klass.fromLayer(source)
        self.assertEqual(copied._max_length, 42)
        self.assertEqual(copied._generation, 13)
        self.assertEqual(len(copied._stack), len(source._stack))
        for s_obj, c_obj in zip(source._stack, copied._stack):
            self.assertTrue(s_obj is c_obj)

    def test___iter___filled(self):
        from appendonly import _Layer
        klass = self._getTargetClass()
        source = _Layer()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        source.push(OBJ1)
        source.push(OBJ2)
        source.push(OBJ3)
        copied = klass.fromLayer(source)
        self.assertEqual(list(copied), [(2, OBJ3), (1, OBJ2), (0, OBJ1)])

    def test_newer_miss(self):
        from appendonly import _Layer
        klass = self._getTargetClass()
        source = _Layer()
        source.push(object())
        copied = klass.fromLayer(source)
        self.assertEqual(list(copied.newer(0)), [])

    def test_newer_hit(self):
        from appendonly import _Layer
        klass = self._getTargetClass()
        source = _Layer()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        source.push(OBJ1)
        source.push(OBJ2)
        source.push(OBJ3)
        copied = klass.fromLayer(source)
        self.assertEqual(list(copied.newer(0)),
                         [(2, OBJ3), (1, OBJ2)])


class ArchiveTests(unittest.TestCase):

    def _getTargetClass(self):
        from appendonly import Archive
        return Archive

    def _makeOne(self):
        return self._getTargetClass()()

    def test_ctor(self):
        archive = self._makeOne()
        self.assertTrue(archive._head is None)
        self.assertEqual(archive._generation, -1)

    def test___iter___empty(self):
        archive = self._makeOne()
        self.assertEqual(list(archive), [])

    def test___iter___filled(self):
        archive = self._makeOne()
        created = []
        layer0 = []
        for i in range(3):
            obj = object()
            created.append(obj)
            layer0.append(obj)
        archive.addLayer(0, layer0)
        layer1 = []
        for i in range(2):
            obj = object()
            created.append(obj)
            layer1.append(obj)
        archive.addLayer(1, layer1)
        found = []
        gen_ndx = []
        for generation, index, obj in archive:
            gen_ndx.append((generation, index))
            found.append(obj)
        self.assertEqual(gen_ndx, [(1, 1), (1, 0), (0, 2), (0, 1), (0, 0)])
        self.assertEqual(found, list(reversed(created)))

    def test_addLayer_older(self):
        archive = self._makeOne()
        archive.addLayer(0, [])
        self.assertRaises(ValueError, archive.addLayer, 0, [])

    def test__p_resolveConflict_w_same_generation(self):
        O_STATE = {'_generation': -1, '_head': None}
        c_obj = object()
        C_STATE = {'_generation': 0, '_head': c_obj}
        n_obj = object()
        N_STATE = {'_generation': 0, '_head': n_obj}
        archive = self._makeOne()
        resolved = archive._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, C_STATE)

    def test__p_resolveConflict_w_different_generation(self):
        from appendonly import ConflictError
        O_STATE = {'_generation': -1, '_head': None}
        c_obj = object()
        C_STATE = {'_generation': 0, '_head': c_obj}
        n_obj = object()
        N_STATE = {'_generation': 1, '_head': n_obj}
        archive = self._makeOne()
        self.assertRaises(ConflictError, archive._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)


class AccumulatorTests(unittest.TestCase):

    def _getTargetClass(self):
        from appendonly import Accumulator
        return Accumulator

    def _makeOne(self, value=None):
        if value is None:
            return self._getTargetClass()()
        return self._getTargetClass()(value)

    def test_ctor_wo_value(self):
        aclist = self._makeOne()
        self.assertEqual(aclist._list, [])

    def test_ctor_w_value(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne(VALUE)
        self.assertEqual(aclist._list, VALUE)
        self.assertFalse(aclist._list is VALUE)

    def test___iter___empty(self):
        aclist = self._makeOne()
        self.assertEqual(list(aclist), [])

    def test___iter___filled(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne(VALUE)
        self.assertEqual(list(aclist), VALUE)

    def test_append(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne()
        for value in VALUE:
            aclist.append(value)
        self.assertEqual(list(aclist), VALUE)

    def test_extend(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne()
        aclist.extend(VALUE)
        self.assertEqual(list(aclist), VALUE)

    def test_consume(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne(VALUE)
        result = aclist.consume()
        self.assertEqual(result, VALUE)
        self.assertEqual(list(aclist), [])

    def test___getstate___empty(self):
        aclist = self._makeOne()
        self.assertEqual(aclist.__getstate__(), [])

    def test___getstate___filled(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne(VALUE)
        self.assertEqual(aclist.__getstate__(), VALUE)

    def test___setstate___empty(self):
        aclist = self._makeOne([0, 1, 2])
        aclist.__setstate__([])
        self.assertEqual(list(aclist), [])

    def test___setstate___filled(self):
        VALUE = [0, 1, 2]
        aclist = self._makeOne()
        aclist.__setstate__(VALUE)
        self.assertEqual(list(aclist), VALUE)

    def test__p_resolveConflict_w_both_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4]
        N_STATE = [1, 2, 3, 5]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [1, 2, 3, 4, 5])

    def test__p_resolveConflict_w_both_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4, 6]
        N_STATE = [1, 2, 3, 5, 7]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [1, 2, 3, 4, 6, 5, 7])

    def test__p_resolveConflict_w_c_consume_n_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = []
        N_STATE = [1, 2, 3, 4]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4])

    def test__p_resolveConflict_w_c_consume_n_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = []
        N_STATE = [1, 2, 3, 4, 5]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5])

    def test__p_resolveConflict_w_n_consume_c_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4]
        N_STATE = []
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4])

    def test__p_resolveConflict_w_n_consume_c_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4, 5]
        N_STATE = []
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5])

    def test__p_resolveConflict_w_both_consume(self):
        O_STATE = [1, 2, 3]
        C_STATE = []
        N_STATE = []
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [])

    def test__p_resolveConflict_w_c_append_n_consume_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4]
        N_STATE = [5]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5])

    def test__p_resolveConflict_w_c_extend_n_consume_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4, 6]
        N_STATE = [5, 7]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 6, 5, 7])

    def test__p_resolveConflict_w_n_append_c_consume_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4]
        N_STATE = [5]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5])

    def test__p_resolveConflict_w_n_extend_c_consume_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = [1, 2, 3, 4, 6]
        N_STATE = [5, 7]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 6, 5, 7])

    def test__p_resolveConflict_w_c_consume_n_consume_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = []
        N_STATE = [4]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4])

    def test__p_resolveConflict_w_c_consume_n_consume_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = []
        N_STATE = [4, 5]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5])

    def test__p_resolveConflict_w_n_consume_c_consume_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = [4]
        N_STATE = []
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4])

    def test__p_resolveConflict_w_n_consume_c_consume_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = [4, 5]
        N_STATE = []
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5])

    def test__p_resolveConflict_w_both_consume_append(self):
        O_STATE = [1, 2, 3]
        C_STATE = [4, 5]
        N_STATE = [6]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5, 6])

    def test__p_resolveConflict_w_both_consume_extend(self):
        O_STATE = [1, 2, 3]
        C_STATE = [4, 5]
        N_STATE = [6, 7]
        aclist = self._makeOne()
        resolved = aclist._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(resolved, [4, 5, 6, 7])
