from enum import Enum


class Operator(Enum):
    pass


class BinaryOperator(Operator):
    pass


class BinaryArithmeticOperator(BinaryOperator):
    PLUS = 1
    MINUS = 2
    TIMES = 3
    DIVIDE = 4
    DIV = 5
    MOD = 6


class BinaryLogicalOperator(BinaryOperator):
    AND = 7
    OR = 8


class UnaryOperator(Operator):
    NOT = 9
    UNARY_PLUS = 10
    UNARY_MINUS = 11


class RelationalOperator(Operator):
    LESS_THAN = 12
    GREATER_THAN = 13
    EQUAL = 14
    NOT_EQUAL = 15
    LESS_THAN_OR_EQUAL = 16
    GREATER_THAN_OR_EQUAL = 17
