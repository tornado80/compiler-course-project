from abc import ABC

from src.operator_enum import Operator, BinaryOperator, RelationalOperator, UnaryOperator
from src.symbol_table import SymbolTable


class ThreeAddressOperator(Operator):
    ASSIGN = "ASSIGN"
    UNCONDITIONAL_JUMP = "UNCONDITIONAL_JUMP"
    CONDITIONAL_JUMP = "CONDITIONAL_JUMP"
    PARAMETER = "PARAMETER"
    CALL = "CALL"
    LABEL = "LABEL"


class ThreeAddressCode(ABC):
    def __init__(self, operator: Operator, address1, address2=None, address3=None):
        self.operator = operator
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3


class StartLabel(ThreeAddressCode):
    def __init__(self, scope: SymbolTable):
        super().__init__(ThreeAddressOperator.LABEL, scope.header)

    def __str__(self):
        return f"Start of {self.address1}:"


class EndLabel(ThreeAddressCode):
    def __init__(self, scope: SymbolTable):
        super().__init__(ThreeAddressOperator.LABEL, scope.header)

    def __str__(self):
        return f"End of {self.address1}:"

class BinaryAssignment(ThreeAddressCode):
    def __init__(self, binary_operator: BinaryOperator, arg1, arg2, result):
        super().__init__(binary_operator, arg1, arg2, result)

    def __str__(self):
        return f"{self.address3} := {self.address1} {self.operator} {self.address2}"


class UnaryAssignment(ThreeAddressCode):
    def __init__(self, unary_operator: UnaryOperator, arg, result):
        super().__init__(unary_operator, arg, None, result)

    def __str__(self):
        return f"{self.address3} := {self.operator} {self.address1}"


class BareAssignment(ThreeAddressCode):
    def __init__(self, src, dest):
        super().__init__(ThreeAddressOperator.ASSIGN, src, None, dest)

    def __str__(self):
        return f"{self.address3} := {self.address1}"


class ConditionalJump(ThreeAddressCode):
    def __init__(self, relational_operator: RelationalOperator, arg1, arg2, label):
        self.relational_operator = relational_operator
        super().__init__(ThreeAddressOperator.CONDITIONAL_JUMP, arg1, arg2, label)

    def __str__(self):
        return f"if {self.address1} {self.relational_operator} {self.address2} goto {self.address3}"


class UnconditionalJump(ThreeAddressCode):
    def __init__(self, label):
        super().__init__(ThreeAddressOperator.UNCONDITIONAL_JUMP, None, None, label)

    def __str__(self):
        return f"goto {self.address3}"


class Parameter(ThreeAddressCode):
    def __init__(self, parameter):
        super().__init__(ThreeAddressOperator.PARAMETER, parameter)

    def __str__(self):
        return f"param {self.address1}"


class Call(ThreeAddressCode):
    def __init__(self, procedure: SymbolTable, arity):
        super().__init__(ThreeAddressOperator.CALL, procedure, arity)

    def __str__(self):
        return f"call {self.address1.header.lexeme} {self.address2}"
