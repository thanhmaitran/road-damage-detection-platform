def box_is_valid(box, w, h) -> bool:
    """0 <= xmin < xmax <= W and 0 <= ymin < ymax <= H."""
    x0, y0, x1, y1 = box
    return 0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h
