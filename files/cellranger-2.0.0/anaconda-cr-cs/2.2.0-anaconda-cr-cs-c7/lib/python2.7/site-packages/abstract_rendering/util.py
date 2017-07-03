from __future__ import print_function, division, absolute_import


class EmptyList(object):
    """
    Utility that can be numerically indexed, but
    always returns None.

    If a no length or a negative length are passed at construction,
    the list will ALWAYS return None.

    If a non-negative length is passsed at construction,
    an indexed 0 <= index < length will return None.
    Others raise an IndexError
    """

    def __init__(self, length=-1):
        self.length = length

    def __getitem__(self, idx):
        if self.length < 0:
            return None

        if idx >= self.length or idx < 0:
            raise IndexError

        return None


class Color(list):
    def __init__(self, r, g, b, a):
        list.__init__(self, [r, g, b, a])
        self.r = r
        self.g = g
        self.b = b
        self.a = a

        if ((r > 255 or r < 0)
                or (g > 255 or g < 0)
                or (b > 255 or b < 0)
                or (a > 255 or a < 0)):
            raise ValueError


def zoom_fit(screen, bounds, balanced=True):
    """What affine transform will zoom-fit the given items?
         screen: (w,h) of the viewing region
         bounds: (x,y,w,h) of the items to fit
         balance: Should the x and y scales match?
         returns: [translate x, translate y, scale x, scale y]
    """
    (sw, sh) = screen
    (gx, gy, gw, gh) = bounds
    x_scale = sw/gw
    y_scale = sh/gh
    if (balanced):
        x_scale = min(x_scale, y_scale)
        y_scale = x_scale
    return [-gx*x_scale, -gy*y_scale, x_scale, y_scale]
