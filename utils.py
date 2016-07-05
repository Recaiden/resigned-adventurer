def size_to_scale(size):
    scale = 0.4
    while size >= 1024:
        scale += 0.2
        size /= 2.0
    return scale
