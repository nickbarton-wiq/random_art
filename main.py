from PIL import Image
import math
import random
import numpy as np

WIDTH = 400
HEIGHT = 400
GEN_RULE_MAX_ATTEMPTS = 100


class GrammarBranch:
    def __init__(self, node, probability=1.0):
        self.node = node
        self.probability = probability


class Grammar:
    def __init__(self):
        self.rules = []

    def add_rule(self, branches: list[GrammarBranch]):
        self.rules.append(branches)


class NodeKind:
    NK_X = 'x'
    NK_Y = 'y'
    NK_RANDOM = 'random'
    NK_RULE = 'rule'
    NK_NUMBER = 'number'
    NK_BOOLEAN = 'boolean'
    NK_SQRT = 'sqrt'
    NK_ADD = 'add'
    NK_MULT = 'mult'
    NK_MOD = 'mod'
    NK_GT = 'gt'
    NK_LT = 'lt'
    NK_TRIPLE = 'triple'
    NK_IF = 'if'


class Node:
    def __init__(self, kind, as_data):
        self.kind = kind
        self.as_data = as_data  # Can be number, boolean, binop, triple, if structure, etc.

    def __repr__(self):
        match self.kind:
            case NodeKind.NK_X:
                return "x"
            case NodeKind.NK_Y:
                return "y"
            case NodeKind.NK_NUMBER:
                return f"{self.as_data:.6f}"
            case NodeKind.NK_RANDOM:
                return "random"
            case NodeKind.NK_RULE:
                return f"rule({self.as_data})"
            case NodeKind.NK_SQRT:
                return f"sqrt({self.as_data['unop']})"
            case NodeKind.NK_ADD:
                return f"add({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_MULT:
                return f"mult({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_MOD:
                return f"mod({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_BOOLEAN:
                return f"{self.as_data}"
            case NodeKind.NK_GT:
                return f"gt({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_LT:
                return f"lt({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_TRIPLE:
                return f"(\nR: {self.as_data['first']},\nG: {self.as_data['second']},\nB: {self.as_data['third']}\n)"
            case NodeKind.NK_IF:
                return f"if({self.as_data['cond']}, {self.as_data['then']}, {self.as_data['elze']})"
            case _:
                raise ValueError("Unknown node type")


def node_rule(rule_index=1):  # random.randint(0, 1) + 1):
    return Node(NodeKind.NK_RULE, as_data=rule_index)


# NUMBERS
def node_x():
    return Node(NodeKind.NK_X, as_data=None)


def node_y():
    return Node(NodeKind.NK_Y, as_data=None)


def node_number(number):
    return Node(NodeKind.NK_NUMBER, as_data=number)


def node_random():
    return Node(NodeKind.NK_RANDOM, as_data=random.uniform(-1.0, 1.0))


# UNOPS
def node_unop(kind, operand):
    return Node(kind, as_data={'unop': operand})


def node_sqrt(operand):
    return node_unop(NodeKind.NK_SQRT, operand)


# BINOPS
def node_binop(kind, lhs, rhs):
    return Node(kind, as_data={'lhs': lhs, 'rhs': rhs})


def node_add(lhs, rhs):
    return node_binop(NodeKind.NK_ADD, lhs, rhs)


def node_mult(lhs, rhs):
    return node_binop(NodeKind.NK_MULT, lhs, rhs)


def node_mod(lhs, rhs):
    return node_binop(NodeKind.NK_MOD, lhs, rhs)


def node_gt(lhs, rhs):
    return node_binop(NodeKind.NK_GT, lhs, rhs)


def node_lt(lhs, rhs):
    return node_binop(NodeKind.NK_LT, lhs, rhs)


# BOOLEAN
def node_boolean(boolean):
    return Node(NodeKind.NK_BOOLEAN, as_data=boolean)


# TRIPLE
def node_triple(first, second, third):
    return Node(NodeKind.NK_TRIPLE, as_data={'first': first, 'second': second, 'third': third})


# IF
def node_if(cond, then, elze):
    return Node(NodeKind.NK_IF, as_data={'cond': cond, 'then': then, 'elze': elze})


def eval_node(expr, x, y) -> Node:
    match expr.kind:
        case NodeKind.NK_X:
            return node_number(x)
        case NodeKind.NK_Y:
            return node_number(y)
        case NodeKind.NK_NUMBER | NodeKind.NK_BOOLEAN:
            return expr
        case NodeKind.NK_SQRT:
            unop = eval_node(expr.as_data['unop'], x, y)
            return node_number(math.sqrt(unop.as_data) if unop.as_data > 0 else 0)
        case NodeKind.NK_ADD:
            lhs = eval_node(expr.as_data['lhs'], x, y)
            rhs = eval_node(expr.as_data['rhs'], x, y)
            return node_number(lhs.as_data + rhs.as_data)
        case NodeKind.NK_MULT:
            lhs = eval_node(expr.as_data['lhs'], x, y)
            rhs = eval_node(expr.as_data['rhs'], x, y)
            return node_number(lhs.as_data * rhs.as_data)
        case NodeKind.NK_MOD:
            lhs = eval_node(expr.as_data['lhs'], x, y)
            rhs = eval_node(expr.as_data['rhs'], x, y)
            return node_number(math.fmod(lhs.as_data, rhs.as_data) if rhs.as_data != 0 else 0)
        case NodeKind.NK_GT:
            lhs = eval_node(expr.as_data['lhs'], x, y)
            rhs = eval_node(expr.as_data['rhs'], x, y)
            return node_boolean(lhs.as_data > rhs.as_data)
        case NodeKind.NK_LT:
            lhs = eval_node(expr.as_data['lhs'], x, y)
            rhs = eval_node(expr.as_data['rhs'], x, y)
            return node_boolean(lhs.as_data < rhs.as_data)
        case NodeKind.NK_TRIPLE:
            first = eval_node(expr.as_data['first'], x, y)
            second = eval_node(expr.as_data['second'], x, y)
            third = eval_node(expr.as_data['third'], x, y)
            return node_triple(first, second, third)
        case NodeKind.NK_IF:
            cond = eval_node(expr.as_data['cond'], x, y)
            then = eval_node(expr.as_data['then'], x, y)
            elze = eval_node(expr.as_data['elze'], x, y)
            return then if cond.as_data else elze
        case _:
            raise ValueError("Unknown node type")


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


def render_pixels(expr):
    pixel_array = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
    for y in range(HEIGHT):
        ny = float(y) / HEIGHT * 2.0 - 1
        for x in range(WIDTH):
            nx = float(x) / WIDTH * 2.0 - 1
            result = eval_node(expr, nx, ny)
            pixel_array[y, x] = (
                Color(
                    r=result.as_data['first'].as_data,
                    g=result.as_data['second'].as_data,
                    b=result.as_data['third'].as_data,
                ).rgb()
            )

    image = Image.fromarray(pixel_array, 'RGB')
    image.save("output.png")
    print("Image saved as chatgpt.png")


def gen_expr(grammar, index, depth):
    if depth <= 0:
        return gen_node(grammar, gen_terminal_node(), depth)
    assert index < len(grammar.rules), "Rule index out of bounds"
    branches = grammar.rules[index]
    assert len(branches) > 0, "No branches available for this rule"
    node = None
    attempts = 0
    while node is None and attempts < GEN_RULE_MAX_ATTEMPTS:
        attempts += 1
        p = random.uniform(0.0, 1.0)
        t = 0.0
        for branch in branches:
            t += branch.probability
            if t >= p:
                node = gen_node(grammar, branch.node, depth - 1)
                break
    if node is None:
        print(f"Failed to generate a node for grammar {index} after {GEN_RULE_MAX_ATTEMPTS} attempts")
    return node


def gen_terminal_node():
    return random.choice([node_x(), node_y(), node_random()])


def gen_node(grammar, node, depth):
    match node.kind:
        case NodeKind.NK_RULE:
            return gen_expr(grammar, node.as_data, depth - 1)

        case NodeKind.NK_X | NodeKind.NK_Y | NodeKind.NK_NUMBER | NodeKind.NK_BOOLEAN:
            return node

        case NodeKind.NK_RANDOM:
            return node_number(random.uniform(-1.0, 1.0))

        case NodeKind.NK_SQRT:
            unop = gen_node(grammar, node.as_data['unop'], depth)
            return node_sqrt(unop)

        case NodeKind.NK_ADD | NodeKind.NK_MULT | NodeKind.NK_MOD | NodeKind.NK_GT | NodeKind.NK_LT:
            lhs = gen_node(grammar, node.as_data['lhs'], depth)
            rhs = gen_node(grammar, node.as_data['rhs'], depth)
            return node_binop(node.kind, lhs, rhs)

        case NodeKind.NK_IF:
            cond = gen_node(grammar, node.as_data['cond'], depth)
            then = gen_node(grammar, node.as_data['then'], depth)
            elze = gen_node(grammar, node.as_data['elze'], depth)
            return node_if(cond, then, elze)

        case NodeKind.NK_TRIPLE:
            first = gen_node(grammar, node.as_data['first'], depth)
            second = gen_node(grammar, node.as_data['second'], depth)
            third = gen_node(grammar, node.as_data['third'], depth)
            return node_triple(first, second, third)

        case _:
            raise ValueError("Unknown node type: {node.kind}")


def build_grammar():
    """The Grammar gives the generator choices on how to generate our node rules.  We need a triple to generate the RGB,
    so we pass grammar index 0 (triple) to the generator first.  From there, the generator will keep generating nodes
    given the grammar until it reaches a terminal node (x, y, or random) or the depth limit is reached.
    """
    grammar = Grammar()
    # Triple (Base rule)
    grammar.add_rule([
        GrammarBranch(node_triple(node_rule(1), node_rule(1), node_rule(1)), 1.0)
        ])

    # Operations nodes
    ops_rules = [
        GrammarBranch(node_rule(1)),
        GrammarBranch(node_add(node_rule(), node_rule())),
        GrammarBranch(node_mult(node_rule(), node_rule())),
        GrammarBranch(node_if(node_lt(node_rule(), node_rule()), node_rule(), node_rule())),
        # GrammarBranch(node_if(node_gt(node_rule(), node_rule()), node_rule(), node_rule())),
        # GrammarBranch(node_sqrt(node_rule())),
        # GrammarBranch(node_sqrt(node_add(node_mult(node_x(), node_x()),
        #                                  node_mult(node_y(), node_y())),
        #                         )),
        # GrammarBranch(node_mod(node_rule(), node_rule())),
    ]
    for rule in ops_rules:
        rule.probability = 1.0 / len(ops_rules)
    grammar.add_rule(ops_rules)

    # Terminal nodes
    grammar.add_rule([
        GrammarBranch(node_x(), 1.0 / 3.0),
        GrammarBranch(node_y(), 1.0 / 3.0),
        GrammarBranch(node_random(), 1.0 / 3.0),
    ])
    return grammar


if __name__ == "__main__":
    grammar = build_grammar()
    generated_expr = gen_expr(
        grammar=grammar,
        index=0,
        depth=20
        )
    print(f"\nGenerated rule: {generated_expr}")
    print("\nRendering...")
    render_pixels(generated_expr)
