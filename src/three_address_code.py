from src.operator_enum import Operator, BinaryOperator, RelationalOperator, UnaryOperator


class ThreeAddressOperator(Operator):
    ASSIGN = 18
    UNCONDITIONAL_JUMP = 19
    CONDITIONAL_JUMP = 20
    PARAMETER = 21
    CALL = 22


class ThreeAddressCode:
    def __init__(self, operator: Operator, address1, address2=None, address3=None):
        self.operator = operator
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3


class BinaryAssignment(ThreeAddressCode):
    def __init__(self, binary_operator: BinaryOperator, arg1, arg2, result):
        super().__init__(binary_operator, arg1, arg2, result)


class UnaryAssignment(ThreeAddressCode):
    def __init__(self, unary_operator: UnaryOperator, arg, result):
        super().__init__(unary_operator, arg, None, result)


class BareAssignment(ThreeAddressCode):
    def __init__(self, src, dest):
        super().__init__(ThreeAddressOperator.ASSIGN, src, None, dest)


class ConditionalJump(ThreeAddressCode):
    def __init__(self, relational_operator: RelationalOperator, arg1, arg2, label):
        self.relational_operator = relational_operator
        super().__init__(ThreeAddressOperator.CONDITIONAL_JUMP, arg1, arg2, label)


class UnconditionalJump(ThreeAddressCode):
    def __init__(self, label):
        super().__init__(ThreeAddressOperator.UNCONDITIONAL_JUMP, label)


class Parameter(ThreeAddressCode):
    def __init__(self, parameter):
        super().__init__(ThreeAddressOperator.PARAMETER, parameter)


class Call(ThreeAddressCode):
    def __init__(self, procedure, arity):
        super().__init__(ThreeAddressOperator.CALL, procedure, arity)
