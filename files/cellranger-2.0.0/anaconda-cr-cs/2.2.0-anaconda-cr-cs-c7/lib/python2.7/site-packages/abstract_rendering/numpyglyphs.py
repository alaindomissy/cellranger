from __future__ import print_function, division, absolute_import
from six.moves import range
import numpy as np
from scipy.ndimage.filters import convolve
from abstract_rendering.fast_project import _projectRects
import abstract_rendering.glyphset as glyphset
import abstract_rendering.core as ar


class Glyphset(glyphset.Glyphset):
    # TODO: Default data is list of None (?)
    """
    points: Base array of points (x, y, w, h)
    data: Base array of data associated with points.
          points[n] is associated with data[n]
    vt: view transform
    clean_nan: Remove entries with nans in points?  Default is false.
    """
    def __init__(self, points, data, vt=(0, 0, 1, 1), clean_nan=False):
        if clean_nan:
            mask = ~np.isnan(points).any(axis=1)
            points = points[mask]
            data = data[mask]

        self._points = points
        self._data = data
        self.vt = vt
        self.shaper = glyphset.ToPoint(glyphset.idx(0), glyphset.idx(1))

        if not is_identity_transform(vt):
            self.projected = np.empty_like(points, dtype=np.int32)
            _projectRects(vt, points, self.projected)
            # points must be at least 1 wide for general compatability
            self.projected[:, 2] = self.projected[:, 0]+1
            self.projected[:, 3] = self.projected[:, 1]+1
        else:
            self.projected = points

    def data(self):
        return self._data

    def points(self):
        return self.projected

    def project(self, vt):
        """
        Project the points found in the glyphset with to the transform.

        vt -- convert canvas space to pixel space [tx,ty,sx,sy]
        returns a new glyphset with projected points and associated info values
        """
        nvt = (self.vt[0]+vt[0],
               self.vt[1]+vt[1],
               self.vt[2]*vt[2],
               self.vt[3]*vt[3])
        return Glyphset(self._points, self._data, nvt)

    def bounds(self):
        (xmax, ymax, _, _) = self.projected.max(axis=0)
        (xmin, ymin, _, _) = self.projected.min(axis=0)
        bounds = (xmin, ymin, xmax-xmin, ymax-ymin)
        return bounds


class PointCount(ar.Aggregator):
    def aggregate(self, glyphset, info, screen):
        sparse = glyphset.points()

        dense = np.histogram2d(sparse[:, 1], sparse[:, 0],
                               bins=(screen[1], screen[0]),
                               range=((0, screen[1]), (0, screen[0])))
        return dense[0]

    def rollup(self, *vals):
        return reduce(lambda x, y: x+y,  vals)


# TODO: IS there a faster option for the coder?  'vectorize' is only
#       a little better than a list comprehension
class PointCountCategories(ar.Aggregator):
    def aggregate(self, glyphset, info, screen):
        points = glyphset.points()
        coder = np.vectorize(info)
        coded = coder(glyphset.data())
        coded = np.array(coded)
        cats = coded.max()

        (width, height) = screen
        dims = (height, width, cats+1)

        # Need cats+1 to do proper categorization...
        ranges = ((0, screen[1]), (0, screen[0]), (0, cats+1))

        data = np.hstack([np.fliplr(points[:, 0:2]), coded[:, np.newaxis]])
        dense = np.histogramdd(data, bins=dims, range=ranges)
        return dense[0]

    def rollup(self, *vals):
        """NOTE: Assumes co-registration of categories..."""
        return reduce(lambda x, y: x+y,  vals)


class Spread(ar.CellShader):
    """
    Spreads the values out in a regular pattern.
    Spreads categories inside their category plane (not between planes).

    TODO: Spread beyond the bounds of the input plot?

    * shape: Shape of the spread.  Supports "rect" and "circle"
    * factor : How wide to spread?
    * anti_alias: Can a value be fractionally spread into a cell
                  (default is false)
    """
    def __init__(self, factor=1, anti_alias=False, shape="circle"):
        self.factor = factor
        self.anti_alias = anti_alias
        self.shape = shape

    def make_k(self):
        """Construct the weights matrix"""
        if self.shape == "rect":
            if not self.anti_alias or (self.factor % 2) == 1:
                kShape = (self.factor+1, self.factor+1)
                k = np.ones(kShape)
            else:
                kShape = (self.factor, self.factor)
                k = np.ones(kShape)
                k[0] = .5
                k[:, 0] = .5
                k[-1] = .5
                k[:, -1] = .5
            return k

        if self.shape == "circle":
            if not self.anti_alias or (self.factor % 2) == 1:
                kShape = (self.factor+1, self.factor+1)
                k = np.ones(kShape)
                r = self.factor//2
                rr = r**2
                for x in range(0, r):
                    for y in range(0, r):
                        if ((x - r)**2 + (y - r)**2) > rr:
                            k[x, y] = 0
                            k[x, -(y+1)] = 0
                            k[-(x+1), -(y+1)] = 0
                            k[-(x+1), y] = 0
                return k
            else:
                kShape = (self.factor+1, self.factor+1)
                k = np.ones(kShape)
                r = self.factor//2
                rr = r**2
                for x in range(0, r):
                    for y in range(0, r):
                        if ((x - r)**2 + (y - r)**2) == rr:
                            k[x, y] = .5
                            k[x, -(y+1)] = .5
                            k[-(x+1), -(y+1)] = .5
                            k[-(x+1), y] = .5
                        elif ((x - r)**2 + (y - r)**2) > rr:
                            k[x, y] = 0
                            k[x, -(y+1)] = 0
                            k[-(x+1), -(y+1)] = 0
                            k[-(x+1), y] = 0
                return k
            return k

    def shade(self, grid):
        k = self.make_k()

        out_dtype = grid.dtype if not self.anti_alias else np.float64
        out = np.empty_like(grid, dtype=out_dtype)
        if len(grid.shape) == 3:
            cats = grid.shape[2]
            for cat in range(cats):
                convolve(grid[:, :, cat], k, output=out[:, :, cat],
                         mode='constant', cval=0.0)
        else:
            convolve(grid, k, mode='constant', cval=0.0, output=out)

        return out


class Log10(ar.CellShader):
    def shade(self, grid):
        mask = (grid == 0)
        out = np.log10(grid)
        out[mask] = 0
        return out


def is_identity_transform(vt):
    return vt == (0, 0, 1, 1)


def load_csv(filename, skip, xc, yc, vc):
    """Turn a csv file into a glyphset.

    This is a fairly naive regulary-expression based parser
    (it doesn't handle quotes, blank lines or much else).
    It is useful for getting simple datasets into the system.
    """
    import re
    source = open(filename, 'r')
    points = []
    data = []

    for i in range(0, skip):
        source.readline()

    for line in source:
        line = re.split("\s*,\s*", line)
        x = float(line[xc].strip())
        y = float(line[yc].strip())
        v = float(line[vc].strip()) if vc >= 0 else 1
        g = [x, y, 0, 0]
        points.append(g)
        data.append(v)

    source.close()
    return Glyphset(np.array(points, order="F"), np.array(data))


def load_hdf(filename, node, xc, yc, vc=None):
    """
    Load a node from an HDF file.

    filename : HDF file to load
    node: Path to relevant HDF table
    xc: Name/index of the x column
    yc: Name/index of the y column
    vc: Name/index of the value column (if applicable)
    cats: List of expected categories.
        If cats is an empty list, a coding will be automatically generated
        Any value not on the list will be assigned category equal to
        list length. This parameter is ignored if vc is not supplied.
    """
    import pandas as pd
    table = pd.read_hdf(filename, node)
    points = table[[xc, yc]]
    a = np.zeros((len(points), 4), order="F")
    a[:, :2] = points

    data = table[vc] if vc else None
    print("Loaded %d items" % len(a))

    return Glyphset(a, data)
