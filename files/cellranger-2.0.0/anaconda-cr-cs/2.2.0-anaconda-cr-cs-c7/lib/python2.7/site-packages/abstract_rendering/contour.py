from __future__ import print_function, division, absolute_import
import numpy as np
import abstract_rendering.core as core
from abstract_rendering._cntr import Cntr


class Contour(core.ShapeShader):
    def __init__(self, x_range=None, y_range=None, levels=5, points=True):
        """
         x/y_range arguments determine the data values that correspond
         to the max/min values on the axes of the input grid.  It is assumed
         that the grid is linear between the two.

         levels as a scalar determines how many levels will be built
         levels as a list determines where the levels are built

         points -- Indicates if it should return values
                    as [[(x,y)...], [(x,y)...]] (default, True)
                    or as [[x,x...], [x,x...],[y,y...][y,y...]] (False)

        """

        self.x_range = x_range
        self.y_range = y_range
        self.levels = levels
        self.points = points

    def fuse(self, grid):
        x_range = self.x_range if self.x_range else (0, grid.shape[1]-1)
        y_range = self.y_range if self.y_range else (0, grid.shape[0]-1)

        xs = np.linspace(x_range[0], x_range[1], num=grid.shape[1])
        ys = np.linspace(y_range[0], y_range[1], num=grid.shape[0])
        xg, yg = np.meshgrid(xs, ys)

        c = Cntr(xg, yg, grid)

        if isinstance(self.levels, list):
            levels = self.levels
        else:
            levels = Contour.nlevels(grid, self.levels)

        isos = dict()
        for level in levels:
            points = c.trace(level, points=self.points)
            points = [[], []] if len(points) == 0 else points
            isos[level] = points

        return isos

    @classmethod
    def nlevels(cls, grid, n):
        "Given grid of values, pick out n values for iso contour levels"

        # The contouring library outlines places below the given value.
        # We do n+2 and drop the first and last values because they are
        # empty contours.
        return np.linspace(grid.min(), grid.max(), n+2)[1:-1]
