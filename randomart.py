import random

from src.image import render_pixels_to_image
from src.grammar import build_grammar
from src.node import Node, NodeKind, NodeFactory
from src.node import node_if, node_triple, terminal_node


GEN_RULE_MAX_ATTEMPTS = 100


class ExpressionGenerationError(Exception):
    pass


class UnknownNode(Exception):
    pass


def gen_expr(grammar, index, depth) -> Node:
    if depth <= 0:
        return gen_node(grammar, terminal_node(), depth)
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
        raise ExpressionGenerationError(f"Failed to generate a node after {GEN_RULE_MAX_ATTEMPTS} attempts")
    else:
        return node


def gen_node(grammar, node, depth):
    match node.kind:
        case NodeKind.NK_RULE:
            return gen_expr(grammar, node.as_data, depth - 1)

        case NodeKind.NK_X | NodeKind.NK_Y | NodeKind.NK_T | NodeKind.NK_NUMBER | NodeKind.NK_BOOLEAN:
            return node

        case NodeKind.NK_RANDOM:
            return NodeFactory.node_number(random.uniform(-1.0, 1.0))

        case NodeKind.NK_SQRT:
            unop = gen_node(grammar, node.as_data['unop'], depth)
            return NodeFactory.node_unop(node.kind, unop)

        case NodeKind.NK_ADD | NodeKind.NK_MULT | NodeKind.NK_MOD | NodeKind.NK_GT | NodeKind.NK_LT:
            lhs = gen_node(grammar, node.as_data['lhs'], depth)
            rhs = gen_node(grammar, node.as_data['rhs'], depth)
            return NodeFactory.node_binop(node.kind, lhs, rhs)

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
            raise UnknownNode(f"Unknown node type: {node.kind}")


def gen_fragment_expr(node: Node) -> str:
    """Generates a fragment shader expression from a node

    Args:
        node (Node): the node to generate the expression from

    Raises:
        ValueError: if the node kind is unknown

    Returns:
        str: the fragment shader expression
    """
    match node.kind:
        case NodeKind.NK_X:
            return "x"
        case NodeKind.NK_Y:
            return "y"
        case NodeKind.NK_T:
            return "t"
        case NodeKind.NK_NUMBER:
            return f"{node.as_data:.6f}"
        case NodeKind.NK_ADD:
            return f"({gen_fragment_expr(node.as_data['lhs'])} + {gen_fragment_expr(node.as_data['rhs'])})"
        case NodeKind.NK_MULT:
            return f"({gen_fragment_expr(node.as_data['lhs'])} * {gen_fragment_expr(node.as_data['rhs'])})"
        case NodeKind.NK_MOD:
            return f"mod({gen_fragment_expr(node.as_data['lhs'])}, {gen_fragment_expr(node.as_data['rhs'])})"
        case NodeKind.NK_GT:
            return f"({gen_fragment_expr(node.as_data['lhs'])} > {gen_fragment_expr(node.as_data['rhs'])})"
        case NodeKind.NK_LT:
            return f"({gen_fragment_expr(node.as_data['lhs'])} < {gen_fragment_expr(node.as_data['rhs'])})"
        case NodeKind.NK_SQRT:
            return f"sqrt({gen_fragment_expr(node.as_data['unop'])})"
        case NodeKind.NK_TRIPLE:
            return f"vec3({gen_fragment_expr(node.as_data['first'])}, {gen_fragment_expr(node.as_data['second'])}, {gen_fragment_expr(node.as_data['third'])})" # noqa
        case NodeKind.NK_IF:
            return f"({gen_fragment_expr(node.as_data['cond'])} ? {gen_fragment_expr(node.as_data['then'])} : {gen_fragment_expr(node.as_data['elze'])})" # noqa
        case _:
            raise UnknownNode("Unknown node type")


def get_fragment_shader() -> str:
    """Generates a randomart fragment shader expression

    Returns:
        str: the fragment shader expression
    """
    grammar = build_grammar()
    generated_expr = gen_expr(
        grammar=grammar,
        index=0,
        depth=30
        )
    print(f"\nGenerated rule: {generated_expr}")
    fragment_expression = gen_fragment_expr(generated_expr)
    print(f"\nFragment expression:\n{fragment_expression}")
    return fragment_expression


def get_randomart_image():
    """Generates a randomart image. Saves the image to disk as `output.png`
    """
    grammar = build_grammar()
    generated_expr = gen_expr(
        grammar=grammar,
        index=0,
        depth=30
        )
    print(f"\nGenerated rule: {generated_expr}")
    print("\nRendering...")
    render_pixels_to_image(generated_expr)


if __name__ == "__main__":
    get_randomart_image()
