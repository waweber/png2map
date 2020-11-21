#!/usr/bin/env python
# png2map - convert a png image to a minecraft map data file
# Requires pypng and PyNBT (pip install pypng pynbt)
# usage: png2map.py < input.png > map_X.dat
#
# Standard input should be an exactly 128x128 PNG image.
# The data file is written to stdout.

from pynbt import *
import png
import sys
import gzip
import functools

# Minecraft color mapping
# https://minecraft.gamepedia.com/Map_item_format
COLORS = {
    4: [89, 125, 39],
    5: [109, 153, 48],
    6: [127, 178, 56],
    7: [67, 94, 29],
    8: [174, 164, 115],
    9: [213, 201, 140],
    10: [247, 233, 163],
    11: [130, 123, 86],
    12: [140, 140, 140],
    13: [171, 171, 171],
    14: [199, 199, 199],
    15: [105, 105, 105],
    16: [180, 0, 0],
    17: [220, 0, 0],
    18: [255, 0, 0],
    19: [135, 0, 0],
    20: [112, 112, 180],
    21: [138, 138, 220],
    22: [160, 160, 255],
    23: [84, 84, 135],
    24: [117, 117, 117],
    25: [144, 144, 144],
    26: [167, 167, 167],
    27: [88, 88, 88],
    28: [0, 87, 0],
    29: [0, 106, 0],
    30: [0, 124, 0],
    31: [0, 65, 0],
    32: [180, 180, 180],
    33: [220, 220, 220],
    34: [255, 255, 255],
    35: [135, 135, 135],
    36: [115, 118, 129],
    37: [141, 144, 158],
    38: [164, 168, 184],
    39: [86, 88, 97],
    40: [106, 76, 54],
    41: [130, 94, 66],
    42: [151, 109, 77],
    43: [79, 57, 40],
    44: [79, 79, 79],
    45: [96, 96, 96],
    46: [112, 112, 112],
    47: [59, 59, 59],
    48: [45, 45, 180],
    49: [55, 55, 220],
    50: [64, 64, 255],
    51: [33, 33, 135],
    52: [100, 84, 50],
    53: [123, 102, 62],
    54: [143, 119, 72],
    55: [75, 63, 38],
    56: [180, 177, 172],
    57: [220, 217, 211],
    58: [255, 252, 245],
    59: [135, 133, 129],
    60: [152, 89, 36],
    61: [186, 109, 44],
    62: [216, 127, 51],
    63: [114, 67, 27],
    64: [125, 53, 152],
    65: [153, 65, 186],
    66: [178, 76, 216],
    67: [94, 40, 114],
    68: [72, 108, 152],
    69: [88, 132, 186],
    70: [102, 153, 216],
    71: [54, 81, 114],
    72: [161, 161, 36],
    73: [197, 197, 44],
    74: [229, 229, 51],
    75: [121, 121, 27],
    76: [89, 144, 17],
    77: [109, 176, 21],
    78: [127, 204, 25],
    79: [67, 108, 13],
    80: [170, 89, 116],
    81: [208, 109, 142],
    82: [242, 127, 165],
    83: [128, 67, 87],
    84: [53, 53, 53],
    85: [65, 65, 65],
    86: [76, 76, 76],
    87: [40, 40, 40],
    88: [108, 108, 108],
    89: [132, 132, 132],
    90: [153, 153, 153],
    91: [81, 81, 81],
    92: [53, 89, 108],
    93: [65, 109, 132],
    94: [76, 127, 153],
    95: [40, 67, 81],
    96: [89, 44, 125],
    97: [109, 54, 153],
    98: [127, 63, 178],
    99: [67, 33, 94],
    100: [36, 53, 125],
    101: [44, 65, 153],
    102: [51, 76, 178],
    103: [27, 40, 94],
    104: [72, 53, 36],
    105: [88, 65, 44],
    106: [102, 76, 51],
    107: [54, 40, 27],
    108: [72, 89, 36],
    109: [88, 109, 44],
    110: [102, 127, 51],
    111: [54, 67, 27],
    112: [108, 36, 36],
    113: [132, 44, 44],
    114: [153, 51, 51],
    115: [81, 27, 27],
    116: [17, 17, 17],
    117: [21, 21, 21],
    118: [25, 25, 25],
    119: [13, 13, 13],
    120: [176, 168, 54],
    121: [215, 205, 66],
    122: [250, 238, 77],
    123: [132, 126, 40],
    124: [64, 154, 150],
    125: [79, 188, 183],
    126: [92, 219, 213],
    127: [48, 115, 112],
    128: [52, 90, 180],
    129: [63, 110, 220],
    130: [74, 128, 255],
    131: [39, 67, 135],
    132: [0, 153, 40],
    133: [0, 187, 50],
    134: [0, 217, 58],
    135: [0, 114, 30],
    136: [91, 60, 34],
    137: [111, 74, 42],
    138: [129, 86, 49],
    139: [68, 45, 25],
    140: [79, 1, 0],
    141: [96, 1, 0],
    142: [112, 2, 0],
    143: [59, 1, 0],
    144: [147, 124, 113],
    145: [180, 152, 138],
    146: [209, 177, 161],
    147: [110, 93, 85],
    148: [112, 57, 25],
    149: [137, 70, 31],
    150: [159, 82, 36],
    151: [84, 43, 19],
    152: [105, 61, 76],
    153: [128, 75, 93],
    154: [149, 87, 108],
    155: [78, 46, 57],
    156: [79, 76, 97],
    157: [96, 93, 119],
    158: [112, 108, 138],
    159: [59, 57, 73],
    160: [131, 93, 25],
    161: [160, 114, 31],
    162: [186, 133, 36],
    163: [98, 70, 19],
    164: [72, 82, 37],
    165: [88, 100, 45],
    166: [103, 117, 53],
    167: [54, 61, 28],
    168: [112, 54, 55],
    169: [138, 66, 67],
    170: [160, 77, 78],
    171: [84, 40, 41],
    172: [40, 28, 24],
    173: [49, 35, 30],
    174: [57, 41, 35],
    175: [30, 21, 18],
    176: [95, 75, 69],
    177: [116, 92, 84],
    178: [135, 107, 98],
    179: [71, 56, 51],
    180: [61, 64, 64],
    181: [75, 79, 79],
    182: [87, 92, 92],
    183: [46, 48, 48],
    184: [86, 51, 62],
    185: [105, 62, 75],
    186: [122, 73, 88],
    187: [64, 38, 46],
    188: [53, 43, 64],
    189: [65, 53, 79],
    190: [76, 62, 92],
    191: [40, 32, 48],
    192: [53, 35, 24],
    193: [65, 43, 30],
    194: [76, 50, 35],
    195: [40, 26, 18],
    196: [53, 57, 29],
    197: [65, 70, 36],
    198: [76, 82, 42],
    199: [40, 43, 22],
    200: [100, 42, 32],
    201: [122, 51, 39],
    202: [142, 60, 46],
    203: [75, 31, 24],
    204: [26, 15, 11],
    205: [31, 18, 13],
    206: [37, 22, 16],
    207: [19, 11, 8],
}


def rgb2lab(inputColor):
    """Given an RGB color array, return the L*a*b representation."""
    # https://stackoverflow.com/a/16020102

    num = 0
    RGB = [0, 0, 0]

    for value in inputColor:
        value = float(value) / 255

        if value > 0.04045:
            value = ((value + 0.055) / 1.055) ** 2.4
        else:
            value = value / 12.92

        RGB[num] = value * 100
        num = num + 1

    XYZ = [
        0,
        0,
        0,
    ]

    X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505
    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)

    XYZ[0] = float(XYZ[0]) / 95.047  # ref_X =  95.047   Observer= 2°, Illuminant= D65
    XYZ[1] = float(XYZ[1]) / 100.0  # ref_Y = 100.000
    XYZ[2] = float(XYZ[2]) / 108.883  # ref_Z = 108.883

    num = 0
    for value in XYZ:

        if value > 0.008856:
            value = value ** (0.3333333333333333)
        else:
            value = (7.787 * value) + (16 / 116)

        XYZ[num] = value
        num = num + 1

    Lab = [0, 0, 0]

    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])

    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)

    return Lab

LAB_COLORS = {id_: rgb2lab(rgb) for id_, rgb in COLORS.items()}

@functools.lru_cache
def get_nearest_color(r, g, b):
    """Given an r, g, b color, find the nearest Minecraft map color ID.

    Selects the color with the closest distance in L*a*b space.

    Returns:
        int: The color ID.
    """
    nearest_id = None
    nearest_diff = None

    a = rgb2lab([r, g, b])

    for id_, b in LAB_COLORS.items():
        diff = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2) ** (1 / 2)

        if nearest_diff is None or nearest_diff > diff:
            nearest_diff = diff
            nearest_id = id_

    return nearest_id


# Read PNG
r = png.Reader(file=sys.stdin.buffer)
w, h, rows, meta = r.read()
if w != h or w != 128:
    print("error: width and height must be 128", file=sys.stderr)
    sys.exit(1)

if meta["greyscale"] is True:
    print("error: don't use grayscale images", file=sys.stderr)
    sys.exit(1)

# Write basic map NBT tags
nb = NBTFile()
data_tag = TAG_Compound()
nb["data"] = data_tag

data_tag.update(
    dict(
        scale=TAG_Byte(0),
        dimension=TAG_String("custom"),
        trackingPosition=TAG_Byte(0),
        unlimitedTracking=TAG_Byte(0),
        locked=TAG_Byte(1),
        xCenter=TAG_Int(5000),
        yCenter=TAG_Int(5000),
        banners=TAG_List(TAG_Compound),
        frames=TAG_List(TAG_Compound),
        DataVersion=TAG_Int(2584),
    )
)

# Map all colors
color_arr = bytearray()
px_size = 4 if meta["alpha"] is True else 3

for row in rows:
    for i in range(0, len(row) // px_size):
        px = [int(v) for v in row[i * px_size : (i + 1) * px_size]]
        color_id = get_nearest_color(px[0], px[1], px[2])
        color_arr.append(color_id)

data_tag["colors"] = TAG_Byte_Array(color_arr)

# Save
gz = gzip.GzipFile(fileobj=sys.stdout.buffer, mode="wb")
nb.save(io=gz)
