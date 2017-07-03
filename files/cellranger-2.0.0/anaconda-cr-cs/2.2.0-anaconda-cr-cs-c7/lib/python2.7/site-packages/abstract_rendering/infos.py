"""
Each info function returns callable that can be used on a single
entry in the dataset.
"""
from __future__ import print_function, division, absolute_import


def const(v):
    """Return the value passed."""
    def f(data):
        return v
    return f


def val(default=None):
    """Return the entire data value. This is the info-version of 'id'.
    """
    def f(data):
        if data is None:
            return default
        else:
            return data
    return f


def valAt(i, default=None):
    """Return the value at a given index in the data part of the input.
         On error returns the default value.
    """
    def f(data):
        try:
            return data[i]
        except:
            return default
    return f


def key(att, default=None):
    "Return the value under a given key in the data part of the input."
    def f(data):
        return data.get(att, default)
    return f


def attribute(att, default=None):
    "Return the value under a given attribute in the data part of the input."
    def f(data):
        return getattr(data, att, default)
    return f


def encode(cats, defcat=-1):
    """Create a function that converts values to numbers.
    The index in the value list passed will be the code-number.
    * cats : Values to create codes for
    * defcat : Default category; defaults to length fo cats list
    """

    if defcat < 0:
        defcat = len(cats)
    codes = dict(zip(cats, xrange(len(cats))))

    def f(val):
        return codes.get(val, defcat)

    return f


class AutoEncode(object):
    """Encoded values as numeric codes.
    Builds up a category->code dictionary incrementally.
    """

    def __init__(self):
        self.next_code = 0
        self.mapping = {}

    def __call__(self, val):
        if val not in self.mapping:
            self.mapping[val] = self.next_code
            self.next_code = self.next_code + 1
        return self.mapping[val]
