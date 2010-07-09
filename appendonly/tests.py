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

class LayerTests(unittest.TestCase):

    def _getTargetClass(self):
        from appendonly import _Layer
        return _Layer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        layer = self._makeOne()
        self.assertEqual(layer._max_length, 100)
        self.failUnless(type(layer._stack) is list)
        self.assertEqual(layer._generation, 0)

    def test_ctor_w_positional(self):
        layer = self._makeOne(4, 14)
        self.assertEqual(layer._max_length, 4)
        self.failUnless(type(layer._stack) is list)
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
        self.assertEqual(_pruned[0], range(0, 100))
        self.assertEqual(_pruned[1], range(100, 200))
        self.assertEqual(_pruned[2], range(200, 300))
        self.assertEqual(_pruned[3], range(300, 400))
        self.assertEqual(_pruned[4], range(400, 500))
        self.assertEqual(_pruned[5], range(500, 600))
        self.assertEqual(_pruned[6], range(600, 700))

    def test___getstate___empty(self):
        stack = self._makeOne()
        self.assertEqual(stack.__getstate__(), (10, 100, [(0L, [])]))

    def test___getstate___filled(self):
        stack = self._makeOne(2, 3)
        for i in range(10):
            stack.push(i)
        self.assertEqual(stack.__getstate__(),
                        (2, 3, [(3L, [9]), (2L, [6, 7, 8])]))

    def test___setstate___(self):
        stack = self._makeOne()
        STATE = (2,                 # _max_layers
                 3,                 # _max_length
                 [(3L, [9]),        # _layers[0] as (generation, list)
                  (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
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
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (3,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_mismatched_max_length(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   4,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_old_latest_commited_earliest(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(5L, [29]),        # _layers[0] as (generation, list)
                    (4L, [26, 27, 28]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 10]),    # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_old_latest_new_earliest(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 10]),    # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(5L, [29]),        # _layers[0] as (generation, list)
                    (4L, [26, 27, 28]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_no_added_layers(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 10]),    # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 11]),    # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 10, 11]),# _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

    def test__p_resolveConflict_added_committed_layer(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4L, [12]),       # _layers[0] as (generation, list)
                    (3L, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 13]),    # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4L, [12, 13]),   # _layers[0] as (generation, list)
                    (3L, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

    def test__p_resolveConflict_added_new_layer(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9]),        # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(3L, [9, 10]),    # _layers[0] as (generation, list)
                    (2L, [6, 7, 8]),  # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4L, [13, 14]),   # _layers[0] as (generation, list)
                    (3L, [9, 11, 12]),# _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [(4L, [12, 13, 14]),# _layers[0] as (generation, list)
                    (3L, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)
