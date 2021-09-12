from collections import OrderedDict

CARDINAL_DIRECTIONS = OrderedDict(
    [
        ("N", 0.0),
        ("NNE", 22.5),
        ("NE", 45.0),
        ("ENE", 67.5),
        ("E", 90.0),
        ("ESE", 112.5),
        ("SE", 135.0),
        ("SSE", 157.5),
        ("S", 180.0),
        ("SSW", 202.5),
        ("SW", 225.0),
        ("WSW", 247.5),
        ("W", 270.0),
        ("WNW", 292.5),
        ("NW", 315.0),
        ("NNW", 337.5),
    ]
)

MONTHS = OrderedDict(
    [
        (1, "Jan"),
        (2, "Feb"),
        (3, "Mar"),
        (4, "Apr"),
        (5, "May"),
        (6, "Jun"),
        (7, "Jul"),
        (8, "Aug"),
        (9, "Sep"),
        (10, "Oct"),
        (11, "Nov"),
        (12, "Dec"),
    ]
)

SEASONS = OrderedDict(
    [
        (1, "Win"),
        (2, "Spr"),
        (3, "Sum"),
        (4, "Aut"),
    ]
)
