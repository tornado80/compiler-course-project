from src.lexer import Token
from src.operator_enum import BinaryOperator, UnaryOperator


class Node:
    def __init__(self, tag=None, children: list = None, leaf=None, parent=None):
        self.tag = tag
        self.children = []
        if children:
            self.add_children(*children)
        self.leaf = leaf
        self.parent = parent

    @property
    def id(self):
        return str(id(self))

    def add_children(self, *args):
        for child in args:
            child.parent = self
            self.children.append(child)

    def visit(self):
        pass

    def __str__(self):
        return f"{self.tag} ({self.leaf})" if self.leaf else self.tag


class Expression(Node):
    def __init__(self, tag, children=None, leaf=None):
        super().__init__(tag, children, leaf)
        self.place = None
        self.type = None


class BinaryExpression(Expression):
    def __init__(self, binary_operator: BinaryOperator, left_operand: Expression, right_operand: Expression):
        super().__init__("binary_expression", children=[left_operand, right_operand], leaf=binary_operator)
        self.binary_operator = binary_operator
        self.left_operand = left_operand
        self.right_operand = right_operand


class UnaryExpression(Expression):
    def __init__(self, unary_operator: UnaryOperator, operand: Expression):
        super().__init__("unary_expression", children=[operand], leaf=unary_operator)
        self.unary_operator = unary_operator
        self.operand = operand


class TerminalExpression(Expression):
    def __init__(self, terminal: Token):
        super().__init__("identifier_or_constant", leaf=terminal)
        self.terminal = terminal
