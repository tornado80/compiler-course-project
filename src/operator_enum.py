from enum import Enum


class Operator(Enum):
    pass


class BinaryOperator(Operator):
    PLUS = "PLUS"
    MINUS = "MINUS"
    TIMES = "TIMES"
    DIVIDE = "DIVIDE"
    DIV = "DIV"
    MOD = "MOD"
    AND = "AND"
    OR = "OR"


class UnaryOperator(Operator):
    NOT = "NOT"
    UNARY_PLUS = "UNARY_PLUS"
    UNARY_MINUS = "UNARY_MINUS"


class RelationalOperator(Operator):
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
