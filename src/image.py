import math

import numpy as np
from PIL import Image

from src.node import Node, NodeKind, NodeFactory

WIDTH = 400
HEIGHT = 400


class Color:
    def __init__(self, r, g, b, a=255):
        self.r = self.scale(r)
        self.g = self.scale(g)
        self.b = self.scale(b)
        self.a = self.scale(a)

    def scale(self, value: float) -> int:
        """scales a value between -inf and inf to 0-255

        Args:
            value (float): value to scale

        Returns:
            int: scaled value
        """
        return self.check_rgb(int((math.tanh(value) + 1) / 2 * 255))

    def check_rgb(self, rgb: int) -> int:
        """Checks if the RGB value is within bounds of 0-255

        Args:
            rgb (int): RGB value

        Returns:
            int: RGB value
        """
        if rgb < 0 or rgb > 255:
            raise ValueError(f"Out of bounds: {self}")
        return rgb

    def rgb(self) -> tuple[int, int, int]:
        """Returns the color as an RGBA tuple

        Returns:
            tuple[int, int, int, int]: RGBA tuple
        """
        return self.r, self.g, self.b

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


class Pixel:
    def __init__(self, x: int, y: int, expr):
        """Initializes a pixel at x, y with and passes an expression to evaluate on the pixel

        Args:
            x (int): the x coordinate of the pixel
            y (int): the y coordinate of the pixel
            expr: the expression to evaluate on the pixel
        """
        self.x = x
        self.y = y
        self.expr = expr
        self.normalize_xy()

    def normalize_xy(self):
        """normalize the x and y values to -1 to 1
        """
        self.nx = float(self.x) / WIDTH * 2.0 - 1
        self.ny = float(self.y) / HEIGHT * 2.0 - 1

    def eval(self) -> Node:
        """Evaluates the expression

        Returns:
            Node: the evaluated node
        """
        return eval_node(self.expr, self.nx, self.ny, 0.0)

    @property
    def color(self):
        return Color(
            r=self.eval().as_data['first'].as_data,
            g=self.eval().as_data['second'].as_data,
            b=self.eval().as_data['third'].as_data,
        ).rgb()


def eval_node(expr, x, y, t) -> Node:
    match expr.kind:
        case NodeKind.NK_X:
            return NodeFactory.node_number(x)
        case NodeKind.NK_Y:
            return NodeFactory.node_number(y)
        case NodeKind.NK_T:
            return NodeFactory.node_number(t)
        case NodeKind.NK_NUMBER | NodeKind.NK_BOOLEAN:
            return expr
        case NodeKind.NK_SQRT | NodeKind.NK_SIN | NodeKind.NK_COS:
            unop = eval_node(expr.as_data['unop'], x, y, t)
            return NodeFactory.node_number(math.sqrt(unop.as_data) if unop.as_data > 0 else 0)
        case NodeKind.NK_ADD:
            lhs = eval_node(expr.as_data['lhs'], x, y, t)
            rhs = eval_node(expr.as_data['rhs'], x, y, t)
            return NodeFactory.node_number(lhs.as_data + rhs.as_data)
        case NodeKind.NK_MULT:
            lhs = eval_node(expr.as_data['lhs'], x, y, t)
            rhs = eval_node(expr.as_data['rhs'], x, y, t)
            return NodeFactory.node_number(lhs.as_data * rhs.as_data)
        case NodeKind.NK_MOD:
            lhs = eval_node(expr.as_data['lhs'], x, y, t)
            rhs = eval_node(expr.as_data['rhs'], x, y, t)
            return NodeFactory.node_number(math.fmod(lhs.as_data, rhs.as_data) if rhs.as_data != 0 else 0)
        case NodeKind.NK_GT:
            lhs = eval_node(expr.as_data['lhs'], x, y, t)
            rhs = eval_node(expr.as_data['rhs'], x, y, t)
            return NodeFactory.node_boolean(lhs.as_data > rhs.as_data)
        case NodeKind.NK_LT:
            lhs = eval_node(expr.as_data['lhs'], x, y, t)
            rhs = eval_node(expr.as_data['rhs'], x, y, t)
            return NodeFactory.node_boolean(lhs.as_data < rhs.as_data)
        case NodeKind.NK_TRIPLE:
            first = eval_node(expr.as_data['first'], x, y, t)
            second = eval_node(expr.as_data['second'], x, y, t)
            third = eval_node(expr.as_data['third'], x, y, t)
            return NodeFactory.node_triple(first, second, third)
        case NodeKind.NK_IF:
            cond = eval_node(expr.as_data['cond'], x, y, t)
            then = eval_node(expr.as_data['then'], x, y, t)
            elze = eval_node(expr.as_data['elze'], x, y, t)
            return then if cond.as_data else elze
        case _:
            raise ValueError("Unknown node type")


def render_pixels_to_image(expr):
    pixel_array = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pixel_array[y, x] = Pixel(x, y, expr).color

    image = Image.fromarray(pixel_array, 'RGB')
    image.save("output.png")
    print("Image saved as chatgpt.png")
