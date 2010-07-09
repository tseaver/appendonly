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

from zope.interface import Interface

class IAppendStack(Interface):
    """ Append-only stack w/ garbage collection.

    - Append items to most recent layer until full;  then add a new layer.
    
    - When max layers reached, discard "oldest" layer starting a new one.

    - Invariant:  the sequence of (generation, id) increases monotonically.

    - Iteration occurs in reverse order of appends, and yields
      (generation, index, object) tuples.
    """
    def __iter__():
        """ Yield (generation, index, object) in most-recent first order.
        """

    def newer(latest_gen, latest_index):
        """ Yield items newer than (`latest_gen`, `latest_index`).
        
        Implemented as a method on the layer to work around lack of generator
        expressions in Python 2.5.x.
        """

    def push(obj, pruner=None):
        """ Append an item to the stack.

        - If `pruner` is passed, call it with the generation and items of
          any pruned layer.
        """
