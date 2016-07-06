import os

def size_to_scale(size):
    """returns logarithmic file size multipliers.  Base 2>.2, with 1024=0.6 centerpoint"""
    scale = 0.4
    while size >= 1024:
        scale += 0.2
        size /= 2.0
    return scale


# COMPATIBILITY: Windows only
def launch(nfile):
    """wrapper around os functionality to 'double-click' an entity and run its associated default program"""
    #this actually gives you basically no information and is not useful
    os.startfile(nfile)
