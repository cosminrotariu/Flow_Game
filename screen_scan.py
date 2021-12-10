import json
from dataclasses import dataclass
from typing import List, Optional, Tuple

from PIL import Image, ImageGrab


def is_border(colour: Tuple[int, int, int]) -> bool:
    red, green, blue = colour
    return 77 <= red <= 124 and 77 <= green <= 124 and 38 <= blue <= 61


def is_background(colour: Tuple[int, int, int]) -> bool:
    red, green, blue = colour
    return red <= 20 and green <= 20 and blue <= 20


@dataclass
class Bounds:
    top_left: Tuple[int, int]
    bot_right: Tuple[int, int]


def find_bounds(image: Image) -> Bounds:
    top_left: Optional[Tuple[int, int]] = None
    bot_right: Optional[Tuple[int, int]] = None
    width, height = image.size
    for x in range(0, width):
        for y in range(0, height):
            if is_border(image.getpixel((x, y))):
                if top_left is None or (x <= top_left[0] and y <= top_left[1]):
                    top_left = (x, y)
                if bot_right is None or (
                    x >= bot_right[0] and y >= bot_right[1]
                ):
                    bot_right = (x, y)
    assert top_left is not None
    assert bot_right is not None
    return Bounds(top_left, bot_right)


ColourGrid = List[List[Optional[Tuple[int, int, int]]]]


def find_colours(image: Image, bounds: Bounds, size: int) -> ColourGrid:
    result: List[List[Optional[Tuple[int, int, int]]]] = []
    tile_size = (bounds.bot_right[0] - bounds.top_left[0]) // size
    for row in range(0, size):
        result.append([])
        for col in range(0, size):
            middle = (
                bounds.top_left[0] + tile_size * col + tile_size // 2,
                bounds.top_left[1] + tile_size * row + tile_size // 2,
            )
            colour = image.getpixel(middle)
            if is_background(colour):
                result[-1].append(None)
            else:
                result[-1].append(colour)
    return result


size = 5
output: List[ColourGrid] = []
while True:
    print("Change size (1)\nTake screenshot (2)\nQuit (3)")
    option = int(input())
    if option == 1:
        size = int(input("Size: "))
    elif option == 2:
        image = ImageGrab.grab()
        bounds = find_bounds(image)
        output.append(find_colours(image, bounds, size))
        image.close()
    elif option == 3:
        break

with open("colours.json", "x") as file:
    json.dump(output, file)
