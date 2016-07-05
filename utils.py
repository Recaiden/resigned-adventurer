def size_to_scale(size):
    scale = 0.9
    while size >= 1024:
        scale += 0.1
        size /= 2.0
