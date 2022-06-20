from enum import Enum

from src.lexer import Token
from src.operator_enum import UnaryOperator, BinaryOperator
from src.three_address_code import UnaryAssignment, BinaryAssignment


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

    def visit(self, code_generator):
        pass

    def __str__(self):
        return f"{self.tag} ({self.leaf})" if self.leaf else self.tag


class DataType(Enum):
    REAL = 0
    INTEGER = 1
    BOOLEAN = 2


class Expression(Node):
    def __init__(self, tag, children=None, leaf=None):
        super().__init__(tag, children, leaf)
        self.place = None # TODO: Entry
        self.type = None


class BinaryExpression(Expression):
    def __init__(self, binary_operator: Token, left_operand: Expression, right_operand: Expression):
        super().__init__("binary_expression", children=[left_operand, right_operand], leaf=binary_operator)
        self.binary_operator = binary_operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def visit(self, code_generator):
        self.left_operand.visit(code_generator)
        self.right_operand.visit(code_generator)
        self.place = code_generator.newtemp()
        # TODO: for all operators and type checking
        if self.binary_operator.type == "TIMES":
            code_generator.emit(BinaryAssignment(
                BinaryOperator.TIMES,
                self.left_operand.place,
                self.right_operand.place,
                self.place
            ))
        elif self.binary_operator.type == "PLUS":
            code_generator.emit(BinaryAssignment(
                BinaryOperator.PLUS,
                self.left_operand.place,
                self.right_operand.place,
                self.place
            ))
        elif self.binary_operator.type == "MINUS":
            code_generator.emit(BinaryAssignment(
                BinaryOperator.MINUS,
                self.left_operand.place,
                self.right_operand.place,
                self.place
            ))


class SemanticError(Exception):
    pass


class UnaryExpression(Expression):
    def __init__(self, unary_operator: Token, operand: Expression):
        super().__init__("unary_expression", children=[operand], leaf=unary_operator)
        self.unary_operator = unary_operator
        self.operand = operand

    def visit(self, code_generator):
        self.operand.visit(code_generator)
        self.place = code_generator.newtemp()
        self.type = self.operand.type
        if self.unary_operator.type == "NOT":
            if self.operand.type != DataType.BOOLEAN:
                raise SemanticError("Incompatible types: expected boolean got numeric")
            # TODO: backpatching
        elif self.unary_operator.type == "PLUS":
            code_generator.emit(UnaryAssignment(UnaryOperator.UNARY_PLUS, self.operand.place, self.place))
        elif self.unary_operator.type == "MINUS":
            code_generator.emit(UnaryAssignment(UnaryOperator.UNARY_MINUS, self.operand.place, self.place))


class TerminalExpression(Expression):
    def __init__(self, terminal: Token):
        super().__init__("identifier_or_constant", leaf=terminal)
        self.terminal = terminal

    def visit(self, code_generator):
        # TODO : lookup symbol table for type and place
        self.place = self.terminal.lexeme
        if self.terminal.type == "ID":
            self.type = DataType.INTEGER
        elif self.terminal.type == "INTEGER_CONSTANT":
            self.type = DataType.INTEGER
        elif self.terminal.type == "REAL_CONSTANT":
            self.type = DataType.REAL
        elif self.terminal.type == "TRUE":
            self.type = DataType.BOOLEAN
        elif self.terminal.type == "FALSE":
            self.type = DataType.BOOLEAN
