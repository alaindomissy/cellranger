from __future__ import print_function
import os

__version__ = "-1.-1.-1"
try:
    version_file = os.path.join(os.path.dirname(__file__), '', '_version.txt')
    with open(version_file, 'r') as version_file:
        __version__ = version_file.read().strip()
except Exception as e:
    print("Error finding version info.")
    print(e)

__version_info__ = dict(zip(["major","minor","micro"], 
                            map(int, __version__.split("."))))
