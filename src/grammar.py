from src.node import node_rule, node_triple, node_x, node_y, node_t, node_add, node_mult


class GrammarBranch:
    def __init__(self, node, probability=1.0):
        self.node = node
        self.probability = probability


class Grammar:
    def __init__(self):
        self.rules = []

    def add_rule(self, branches: list[GrammarBranch]):
        self.rules.append(branches)


def build_grammar() -> Grammar:
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
        # GrammarBranch(node_if(node_lt(node_rule(), node_rule()), node_rule(), node_rule())),
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
        GrammarBranch(node_t(), 1.0 / 3.0),
        GrammarBranch(node_x(), 1.0 / 3.0),
        GrammarBranch(node_y(), 1.0 / 3.0),
        # GrammarBranch(node_random(), 1.0 / 4.0),
    ])
    return grammar
