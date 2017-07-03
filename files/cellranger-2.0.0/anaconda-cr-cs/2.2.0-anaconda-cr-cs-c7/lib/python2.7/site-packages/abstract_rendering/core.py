""" Core abstract rendering abstractions. This includes the main drivers of
execution and the base clases for shared data representations.
"""
from __future__ import print_function, division, absolute_import
from six.moves import range

import numpy as np
import abstract_rendering.geometry as geometry
import abstract_rendering.glyphset as glyphset


# ------------------- Basic process function --------------------------------
def render(glyphs, info, aggregator, shader, screen, vt):
    """
    Render a set of glyphs to the described canvas.

    * glyphs -- Glyphs to render
    * info -- For each glyph, the piece of information that will be aggregated
    * aggregator -- Combines a set of info values into a single aggregate value
    * shader -- Converts aggregates to other aggregates (often colors)
    * screen -- (width,height) of the canvas
    * vt -- View transform (converts canvas to pixels)
    """
    projected = glyphs.project(vt)
    aggregates = aggregator.aggregate(projected, info, screen)
    # TODO: Add shader specialization here
    rslt = shader(aggregates)
    return rslt


# -------------------------  Aggregators and related utilities ----------------
class Aggregator(object):
    out_type = None
    in_type = None
    identity = None

    def aggregate(self, glyphset, info, screen):
        """
        Produce a set of aggregates

        glyphset -- glyphs to process
        screen -- (width, height) of the output grid
        info -- info function to invoke
        """

        raise NotImplementedError()

    def rollup(self, *vals):
        """
        Combine multiple sets of aggregates.

        * vals - list of numpy arrays with type out_type
        """
        raise NotImplementedError()


class GlyphAggregator(Aggregator):
    """
    Aggregator tha tworks on one glyph at a time.

    Aggregators need to eventually process all glyphs.
    This class provides on workflow for realzing that.
    Each glyph is turned into its own set of aggregates,
    then combine dinto a larger set of aggregates for the
    whole glyphset.

    High-level overview of the control flow:
        * 'allocate' is used to make an empty set of aggregates
          for the whole glyphset
        * 'aggregate' calls 'combine' to include a single glyph
          into that allocated set of aggregates.
        * 'aggregate' repeats until all glyphs have been processed
        * 'glyphAggregates' is a utility for combine
          to convert a glyph into a set of aggregates.  Most instances
          of 'combine' call 'glyphAggregates' though it is not always
          required

    Sub-classes need to implement allocate and combine.
    """

    def allocate(self, glyphset, screen):
        """
        Create an array suitable for processing the passed dataset
        into the requested grid size.

        * glyphset - The points that will be processed (already projected)
        * screen -- The size of the bin-grid to produce
        """
        raise NotImplementedError()

    def combine(self, existing, points, shapecode, val):
        """Add a new point to an existing set of aggregates.

        * existing - out_type numpy array, aggregate values for all glyphs seen
        * points - points that define a shape
        * shapecode - Code that determines how points are interpreted
        * val -- Info value associated with the current set of points
        """
        raise NotImplementedError()

    def aggregate(self, glyphset, info, screen):
        # TODO: vectorize pretty much this whole method...
        (width, height) = screen

        # co-iterating on number of points in case glyphset.data() is a non-length-carrying placeholder
        # TODO: Should the default placeholder carry length?
        infos = [info(data) for (data, _)
                 in zip(glyphset.data(), range(len(glyphset.points())))]
        aggregates = self.allocate(glyphset, screen)
        for idx, points in enumerate(glyphset.points()):
            self.combine(aggregates,
                         points,
                         glyphset.shaper.code,
                         infos[idx])
        return aggregates

    def glyphAggregates(self, glyph, shapeCode, val, default):
        """Create a set of aggregates for a single glyph. The set of aggregates will be
           tight to the bound box of the shape but may not be completely filled
           (thus the need for both 'val' and 'default').

           * glyph -- Points that define the glyph
           * shapeCode -- Code that indicates how to interpret the glyph
           * val -- Value to place in bins that are hit by the shape
           * default -- Value to place in bins not hit by the shape
        """

        def scalar(array, val):
            array.fill(val)

        def nparray(array, val):
            array[:] = val

        if type(val) == np.ndarray:
            fill = nparray
            extShape = val.shape
        else:
            fill = scalar
            extShape = ()

        # TODO: These are selectors...rename and move this somewhere else
        if shapeCode == glyphset.ShapeCodes.POINT:
            array = np.copy(val)  # TODO: Not sure this is always an array...verify
        elif shapeCode == glyphset.ShapeCodes.RECT:
            array = np.empty((glyph[3]-glyph[1], glyph[2]-glyph[0])+extShape,
                             dtype=np.int32)
            fill(array, val)
        elif shapeCode == glyphset.ShapeCodes.LINE:
            array = np.empty((glyph[3]-glyph[1], glyph[2]-glyph[0])+extShape,
                             dtype=np.int32)
            fill(array, default)
            glyph = [0, 0, array.shape[1]-1, array.shape[0]-1]  # Translate shape to be in the corner of the update canvas
            geometry.bressenham(array, glyph, val)

        return array


# ---------------------- Shaders and related utilities --------------------
class Shader(object):
    """Shaders take grids and analize them.
       This interface asserts that instances are callable
       and accept a grid as their input.
    """

    def __add__(self, other):
        """Extend this shader by executing another transfer in sequence."""
        if (not isinstance(other, Shader)):
                raise TypeError("Can only extend with Shaders.  Received a {0}"
                                .format(str(type(other))))
        return Seq(self, other)


class ShapeShader(Shader):
    "Convert a grid into a set of shapes (instead of another grid)."

    def fuse(self, grid):
        "Convert aggregates grid into geometry"
        raise NotImplementedError

    def __call__(self, grid):
        return self.fuse(grid)


# TODO: Add specialization to Shaders....
class CellShader(Shader):
    """Cell shaders take a grid and produce a new grid."""

    def shade(self, grid):
        """Execute the actual data shader operation."""
        raise NotImplementedError

    def __call__(self, grid):
        """Execute shading (by default)."""
        return self.shade(grid)


class Seq(Shader):
    "Shader that does a sequence of shaders."

    def __init__(self, *args):
        self._parts = args

    def __add__(self, other):
        if (other is None):
            return self
        elif not isinstance(self._parts[-1], CellShader):
            raise ValueError("Cannot extend: Sequence terminated by non-CellShader.")
        elif (not isinstance(other, Shader)):
            raise TypeError("Can only extend with Shaders. Received a "
                            .format(str(type(other))))
        return Seq(*(self._parts + (other,)))

    def __call__(self, grid):
        for t in self._parts:
            grid = t(grid)
        return grid


class SequentialShader(Shader):
    "Data shader that does non-vectorized per-pixel shading."

    def _pre(self, grid):
        "Executed exactly once before pixelfunc is called on any cell. "
        pass

    def __call__(self, grid):
        """Execute shading."""
        return self.shade(grid)

    def cellfunc(grid, x, y):
        """
        This method will be called for each pixel in the outgrid.
        Must be implemented in subclasses.
        """
        raise NotImplementedError

    def makegrid(self, grid):
        """Create an output grid.

           Default implementation creates one of the same width/height
           of the input suitable for colors (dept 4, unit8).
        """
        (width, height) = grid.shape[0], grid.shape[1]
        return np.ndarray((width, height, 4), dtype=np.uint8)

    def shade(self, grid):
        """Access each element in the out grid sequentially"""
        outgrid = self.makegrid(grid)
        self._pre(grid)
        (height, width) = outgrid.shape
        for x in range(0, width):
            for y in range(0, height):
                outgrid[y, x] = self.cellfunc(grid, x, y)

        return outgrid
