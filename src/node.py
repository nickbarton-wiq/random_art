from typing import Any

import random

from dataclasses import dataclass
from enum import Enum


class NodeKind(Enum):
    NK_X = 'x'
    NK_Y = 'y'
    NK_T = 't'
    NK_RANDOM = 'random'
    NK_RULE = 'rule'
    NK_NUMBER = 'number'
    NK_BOOLEAN = 'boolean'
    NK_SQRT = 'sqrt'
    NK_SIN = 'sin'
    NK_COS = 'cos'
    NK_ADD = 'add'
    NK_MULT = 'mult'
    NK_MOD = 'mod'
    NK_GT = 'gt'
    NK_LT = 'lt'
    NK_TRIPLE = 'triple'
    NK_IF = 'if'


@dataclass
class Node:
    kind: NodeKind
    as_data: Any

    def __repr__(self) -> str:
        match self.kind:
            case NodeKind.NK_X: return "x"
            case NodeKind.NK_Y: return "y"
            case NodeKind.NK_T: return "t"
            case NodeKind.NK_NUMBER: return f"{self.as_data:.6f}"
            case NodeKind.NK_RANDOM: return "random"
            case NodeKind.NK_RULE: return f"rule({self.as_data})"
            case NodeKind.NK_BOOLEAN: return f"{self.as_data}"
            case NodeKind.NK_SQRT: return f"sqrt({self.as_data['unop']})"
            case NodeKind.NK_SIN: return f"sin({self.as_data['unop']})"
            case NodeKind.NK_COS: return f"cos({self.as_data['unop']})"
            case NodeKind.NK_ADD: return f"add({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_MULT: return f"mult({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_MOD: return f"mod({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_GT: return f"gt({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_LT: return f"lt({self.as_data['lhs']}, {self.as_data['rhs']})"
            case NodeKind.NK_TRIPLE: return f"(\nR: {self.as_data['first']},\nG: {self.as_data['second']},\nB: {self.as_data['third']}\n)"  # noqa
            case NodeKind.NK_IF: return f"if({self.as_data['cond']}, {self.as_data['then']}, {self.as_data['elze']})"
            case _: raise ValueError("Unknown node type")


class NodeFactory:
    """A low-level factory class for creating nodes that should not be accessed directly for creating grammar rules

    Returns:
        Node: a new node
    """
    @staticmethod
    def node_number(number):
        return Node(NodeKind.NK_NUMBER, as_data=number)

    @staticmethod
    def node_unop(kind, operand):
        return Node(kind, as_data={'unop': operand})

    @staticmethod
    def node_binop(kind, lhs, rhs):
        return Node(kind, as_data={'lhs': lhs, 'rhs': rhs})

    @staticmethod
    def node_boolean(boolean):
        return Node(NodeKind.NK_BOOLEAN, as_data=boolean)

    @staticmethod
    def node_triple(first, second, third):
        return Node(NodeKind.NK_TRIPLE, as_data={'first': first, 'second': second, 'third': third})


# TODO: Refactor this to an attribute of the Node
def terminal_node():
    return random.choice([node_x(), node_y(), node_t(), node_random()])


def node_rule(rule_index=1):  # random.randint(0, 1) + 1):
    return Node(NodeKind.NK_RULE, as_data=rule_index)


# NUMBERS
def node_x():
    return Node(NodeKind.NK_X, as_data=None)


def node_y():
    return Node(NodeKind.NK_Y, as_data=None)


def node_t():
    return Node(NodeKind.NK_T, as_data=None)


def node_random():
    return Node(NodeKind.NK_RANDOM, as_data=random.uniform(-1.0, 1.0))


# UNOPS
def node_sqrt(operand):
    return NodeFactory.node_unop(NodeKind.NK_SQRT, operand)


def node_sin(operand):
    return NodeFactory.node_unop(NodeKind.NK_SIN, operand)


def node_cos(operand):
    return NodeFactory.node_unop(NodeKind.NK_COS, operand)


# BINOPS
def node_add(lhs, rhs):
    return NodeFactory.node_binop(NodeKind.NK_ADD, lhs, rhs)


def node_mult(lhs, rhs):
    return NodeFactory.node_binop(NodeKind.NK_MULT, lhs, rhs)


def node_mod(lhs, rhs):
    return NodeFactory.node_binop(NodeKind.NK_MOD, lhs, rhs)


def node_gt(lhs, rhs):
    return NodeFactory.node_binop(NodeKind.NK_GT, lhs, rhs)


def node_lt(lhs, rhs):
    return NodeFactory.node_binop(NodeKind.NK_LT, lhs, rhs)


# TRIPLE
def node_triple(first, second, third):
    return NodeFactory.node_triple(first, second, third)


# IF
def node_if(cond, then, elze):
    return Node(NodeKind.NK_IF, as_data={'cond': cond, 'then': then, 'elze': elze})
