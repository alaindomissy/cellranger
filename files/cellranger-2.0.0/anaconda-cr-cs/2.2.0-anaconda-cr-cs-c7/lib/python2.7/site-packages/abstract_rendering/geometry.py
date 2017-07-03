from __future__ import print_function, division, absolute_import


def bressenham(canvas, line, val):
    """
    based on 'optimized and simplified' version at
    http://en.wikipedia.org/wiki/Bresenham's_line_algorithm
    """
    (x0, y0, x1, y1) = line

    dx = abs(x1-x0)
    dy = abs(y1-y0)
    err = dx - dy

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    while True:
        canvas[y0, x0] = val

        if x0 == x1 and y0 == y1:
            break

        e2 = err * 2
        if e2 > -dy:
            err = err - dy
            x0 = x0 + sx

        if e2 < dx:
            err = err + dx
            y0 = y0 + sy
