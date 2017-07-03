"""
Tools for working with counts from multiple categories of data at once.

Categories are modeled as stakced 2D arrays.    Each category is in its
own slice of the stack.
"""
from __future__ import print_function, division, absolute_import
from six.moves import reduce
import numpy as np
from math import log
import abstract_rendering.util as util
import abstract_rendering.core as core


# ------------ Aggregators -------------------
class CountCategories(core.GlyphAggregator):
    """
    Count the number of items that fall into a particular grid element.

    To operateo correctly, allocate must be called with infos representing
    all possible categories; that set of categories is used in combine
    to determine where to place values.  It is, therefore, important that
    any call to combine must in some way correspond to the most recent
    call to allocate.

    TODO: This seems convoluted...is there a better way?
    """
    out_type = np.int32
    identity = np.asarray([0])
    cats = None

    def allocate(self, glyphset, screen):
        """Allocates one array slice for each unique info passed.
           Output array shape is (#cats, height, width).

        """
        (width, height) = screen
        self.cats = np.unique(glyphset.data())
        return np.zeros((height, width, len(self.cats)), dtype=self.out_type)

    def combine(self, existing, points, shapecode, val):
        entry = np.zeros(len(self.cats))
        idx = np.nonzero(self.cats == val)[0][0]
        entry[idx] = 1
        update = self.glyphAggregates(points, shapecode, entry, self.identity)
        existing[points[1]:points[3], points[0]:points[2], :] \
                += update

    def rollup(self, *vals):
        """NOTE: Assumes co-registration of categories..."""
        return reduce(lambda x, y: x+y,  vals)


# ----------- Shaders -----------------------
class ToCounts(core.CellShader):
    """Convert from count-by-categories to just raw counts.
       Then data shader functions from the count module can be used.
    """
    @staticmethod
    def shade(grid, dtype=None):
        dtype = (grid.dtype if dtype is None else dtype)
        return grid.sum(axis=2, dtype=dtype)


class NonZeros(core.CellShader):
    "How many non-zero categories are there?"
    def shade(self, grid):
        mask = grid != 0
        nonzero = np.zeros_like(grid)
        nonzero[mask] = 1
        return nonzero.sum(axis=2)


class Ratio(core.CellShader):
    """
    Compute the ratio of one category to the sum of all cateogires.
    Any cell with sum of zero is propogated as a 'zero' in the sum
     * focus: The "one cateogry"
              Will pick the local 'max' cateogry if set to a negative
    """
    def __init__(self, focus=-1):
        self.focus = focus

    def shade(self, grid):
        if self.focus < 0:
            plane = grid.max(axis=2)
        else:
            plane = grid[:, :, self.focus]

        sum = grid.sum(axis=2)
        mask = (sum != 0)
        ratio = plane/sum
        ratio[~mask] = 0
        return ratio


class Select(core.CellShader):
    """Get the counts from just one category.

       Operates by taking a single plane of the count of categories.

       TODO: Consider changing shade to take a wrapper 'grid' that can carry
             info like a category-label-to-grid-slice mapping....
    """

    def __init__(self, slice):
        """slice -- Which slice of the aggregates grid should be returned"""
        self.slice = slice

    def shade(self, aggregates):
        return aggregates[:, :, self.slice]


class MinPercent(core.CellShader):
    """If the item in the specified bin represents more than a certain percent
     of the total number of items, color it as "above" otherwise, "below"

     TODO: Change from idx to category label, lookup idx for 'cat' parameter
     TODO: Extend to work with more than just colors

     * cutoff -- percent value to split above and below coloring
     * cat -- integer indicating which category number to use
     * above    -- color to paint above (default is a red)
     * below    -- color to paint below (default is a blue)
     * background -- color to paint when there are no values (default is clear)
    """

    def __init__(self,
                 cutoff,
                 cat=0,
                 above=util.Color(228, 26, 28, 255),
                 below=util.Color(55, 126, 184, 255),
                 background=util.Color(255, 255, 255, 0)):

        self.cutoff = cutoff
        self.cat = cat
        self.above = np.array(above, dtype=np.uint8)
        self.below = np.array(below, dtype=np.uint8)
        self.background = np.array(background, dtype=np.uint8)

    def shade(self, grid):
        (height, width, depth) = grid.shape
        outgrid = np.empty((height, width, 4), dtype=np.uint8)

        sums = ToCounts.shade(grid, dtype=np.float32)
        maskbg = (sums == 0)
        mask = (grid[:, :, self.cat]/sums) >= self.cutoff

        outgrid[mask] = self.above
        outgrid[~mask] = self.below
        outgrid[maskbg] = self.background
        return outgrid


class HDAlpha(core.CellShader):
    def __init__(self, colors, background=util.Color(255, 255, 255, 255),
                 alphamin=0, log=False, logbase=10):
        """
        colors -- a list of colors in cateogry-order.
        alphamin -- minimum alpha value when (default is 0)
        log -- Log-based interpolate? (default is false)
        logbase -- Base to use if log is true (default is 10)
        background -- Color for empty category list (default is white)

        If C categories and N colors are presented:
            * N == C: No problems
            * N >  C: Only the first C colors are used
            * N <  C: The last color is replicated to make N == C

        TODO: Change 'colors' to a dictionary of category-to-color mapping
        TODO: mask out zero-sum regions in alpha and opaque blend
        """
        self.catcolors = np.array([np.array(v, dtype=np.uint8) for v in colors])
        self.background = np.array(background, dtype=np.uint8)
        self.alphamin = alphamin
        self.log = log
        self.logbase = logbase

    def shade(self, grid):
        sums = ToCounts.shade(grid, dtype=np.float32)
        mask = (sums != 0)

        # Ensure category count and color count match
        cats = grid.shape[2]
        catcolors = self.catcolors
        if len(catcolors) > cats:
            catcolors = catcolors[:cats]
        elif len(catcolors) < cats:
            other = catcolors[-1]
            replicated = [other] * (cats-len(catcolors))
            catcolors = np.vstack([catcolors, replicated])

        colors = HDAlpha.opaqueblend(catcolors, grid, sums)
        colors[~mask] = self.background
        HDAlpha.alpha(colors, sums, mask, self.alphamin, self.log, self.logbase)
        return colors

    # ------------------- Utilities -----------------
    @staticmethod
    def alpha(colors, sums, mask, alphamin, dolog=False, base=10):
        maxval = sums.max()

        if (dolog):
            base = log(base)
            maxval = log(maxval)/base
            sums[mask] = np.log10(sums[mask])/base

        np.putmask(colors[:, :, 3],
                   mask,
                   ((alphamin + ((1-alphamin) * (sums/maxval)))*255).astype(np.uint8))

    @staticmethod
    def opaqueblend(catcolors, counts, sums):
        weighted = (counts/sums[:, :, np.newaxis]).astype(float)
        weighted = catcolors[np.newaxis, np.newaxis, :] * weighted[:, :, :, np.newaxis]
        colors = weighted.sum(axis=2).astype(np.uint8)
        return colors
