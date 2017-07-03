"""
Utilities that apply across a broad variety of categories.
"""

from __future__ import print_function, division, absolute_import
import abstract_rendering.core as core


class Id(core.CellShader):
    """ Return the input unchanged.

    This DOES NOT make a copy of the input
    It is usually used a zero-cost placeholder.
    """

    def makegrid(self, grid):
        return grid

    def shade(self, grid):
        return grid
