from abc import ABC

from src.operator_enum import Operator, BinaryOperator, RelationalOperator, UnaryOperator
from src.symbol_table import SymbolTable, DataType, EntryType, Entry


class ThreeAddressOperator(Operator):
    ASSIGN = "ASSIGN"
    UNCONDITIONAL_JUMP = "UNCONDITIONAL_JUMP"
    CONDITIONAL_JUMP = "CONDITIONAL_JUMP"
    PARAMETER = "PARAMETER"
    CALL = "CALL"
    LABEL = "LABEL"
    PRINT = "PRINT"
    RETURN = "RETURN"
    BEGIN_PROGRAM = "BEGIN_PROGRAM"
    END_PROGRAM = "END_PROGRAM"
    STRUCT_DEFINITION = "STRUCT_DEFINITION"
    VARIABLE_DEFINITION = "VARIABLE_DEFINITION"
    TEMPORARY_DEFINITION = "TEMPORARY_DEFINITION"


CDataTypes = {
    DataType.INTEGER: "int",
    DataType.REAL: "float"
}


def to_c_operators(operator_lexeme):
    if operator_lexeme == '=':
        return '=='
    if operator_lexeme == '<>':
        return '!='
    if operator_lexeme == 'mod':
        return '%'
    if operator_lexeme == 'div':
        return '/'
    return operator_lexeme


class ThreeAddressCode(ABC):
    def __init__(self, operator: Operator, address1=None, address2=None, address3=None):
        self.operator = operator
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3


class Print(ThreeAddressCode):
    def __init__(self, place: Entry):
        super().__init__(ThreeAddressOperator.PRINT, place)

    def __str__(self):
        return f"printf(\"%{'d' if self.address1.data_type == DataType.INTEGER else 'f'}\\n\", {self.address1});"


class Temporary(ThreeAddressCode):
    def __init__(self, data_type: DataType, count: int):
        super().__init__(ThreeAddressOperator.TEMPORARY_DEFINITION, data_type, count)

    def __str__(self):
        return f"{CDataTypes[self.address1]} temporary_{self.address1.name}[{self.address2}] = {{ 0 }};"


class Definition(ThreeAddressCode):
    def __init__(self, entry: Entry):
        super().__init__(ThreeAddressOperator.VARIABLE_DEFINITION, entry)

    def __str__(self):
        return f"{CDataTypes[self.address1.data_type]} {self.address1};"


class BeginProgram(ThreeAddressCode):
    def __init__(self):
        super().__init__(ThreeAddressOperator.BEGIN_PROGRAM)

    def __str__(self):
        return "\n".join([
            "#include<string.h>",
            "#include<stdlib.h>",
            "#include<stdio.h>",
            "int main() {",
            "void *current_activation_record = NULL, *tmp_activation_record = NULL;"
        ])


class EndProgram(ThreeAddressCode):
    def __init__(self):
        super().__init__(ThreeAddressOperator.END_PROGRAM)

    def __str__(self):
        return "}"


class Label(ThreeAddressCode):
    def __init__(self, name: int):
        super().__init__(ThreeAddressOperator.LABEL, name)

    @property
    def name(self) -> str:
        return f"l{self.address1}"

    def __str__(self):
        return f"{self.name}: ;"


class BinaryAssignment(ThreeAddressCode):
    def __init__(self, binary_operator: BinaryOperator, arg1, arg2, result):
        super().__init__(binary_operator, arg1, arg2, result)

    def __str__(self):
        return f"{self.address3} = {self.address1} {to_c_operators(self.operator)} {self.address2};"


class UnaryAssignment(ThreeAddressCode):
    def __init__(self, unary_operator: UnaryOperator, arg, result):
        super().__init__(unary_operator, arg, None, result)

    def __str__(self):
        return f"{self.address3} = {self.operator} {self.address1};"


class BareAssignment(ThreeAddressCode):
    def __init__(self, src, dest):
        super().__init__(ThreeAddressOperator.ASSIGN, src, None, dest)

    def __str__(self):
        return f"{self.address3} = {self.address1};"


class ConditionalJump(ThreeAddressCode):
    def __init__(self, relational_operator: RelationalOperator, arg1, arg2, label: Label):
        self.relational_operator = relational_operator
        super().__init__(ThreeAddressOperator.CONDITIONAL_JUMP, arg1, arg2, label)

    def __str__(self):
        return f"if ({self.address1} {self.relational_operator} {self.address2}) goto {self.address3.name if self.address3 else None};"


class UnconditionalJump(ThreeAddressCode):
    def __init__(self, label: Label):
        super().__init__(ThreeAddressOperator.UNCONDITIONAL_JUMP, None, None, label)

    def __str__(self):
        return f"goto {self.address3.name if self.address3 else None};"


class Call(ThreeAddressCode):
    def __init__(self, procedure: SymbolTable, return_label: Label):
        super().__init__(ThreeAddressOperator.CALL, procedure, return_label)
        self.common = f"((ActivationRecordPtr_{procedure.header.lexeme})tmp_activation_record)"

    def prepare_temporaries(self):
        result = []
        for data_type, count in self.address1.max_count_of_temporary.items():
            if count > 0:
                result.append(f"memset(&{self.common}->temporary_{data_type.name}, 0, {count});")
        return "\n".join(result)

    def __str__(self):
        return "\n".join([
            f"tmp_activation_record = malloc(sizeof(ActivationRecord_{self.address1.header.lexeme}));",
            self.prepare_temporaries(),
            f"{self.common}->control_link = current_activation_record;",
            f"{self.common}->return_address = &&{self.address2.name};",
            f"current_activation_record = tmp_activation_record;"
        ])


class Return(ThreeAddressCode):
    def __init__(self, procedure: SymbolTable):
        super().__init__(ThreeAddressOperator.RETURN, procedure)
        self.common = f"((ActivationRecordPtr_{procedure.header.lexeme})tmp_activation_record)"

    def __str__(self):
        return "\n".join([
            "tmp_activation_record = current_activation_record;",
            f"current_activation_record = {self.common}->control_link;",
            "free(tmp_activation_record);",
            f"goto *{self.common}->return_address;"
        ])


class ActivationRecordDefinition(ThreeAddressCode):
    def __init__(self, procedure: SymbolTable):
        super().__init__(ThreeAddressOperator.STRUCT_DEFINITION, procedure)

    def prepare_parameters(self):
        result = ["struct {"]
        for entry in self.address1.parameters:
            result.append(f"\t{CDataTypes[entry.data_type]} {entry.token.lexeme};")
        result.append("} parameters;")
        return "\n".join(result)

    def __str__(self):
        return "\n".join([
            f"struct activation_record_{self.address1.header.lexeme} {{",
            f"struct activation_record_{self.address1.header.lexeme}* control_link;",
            "void* return_address;",
            self.prepare_parameters(),
            self.prepare_temporaries(),
            self.prepare_locals(),
            "};",
            f"typedef struct activation_record_{self.address1.header.lexeme} "
            f"ActivationRecord_{self.address1.header.lexeme};",
            f"typedef ActivationRecord_{self.address1.header.lexeme}* "
            f"ActivationRecordPtr_{self.address1.header.lexeme};"
        ])

    def prepare_temporaries(self):
        result = []
        for data_type, count in self.address1.max_count_of_temporary.items():
            if count > 0:
                result.append(f"{CDataTypes[data_type]} temporary_{data_type.name}[{count}];")
        return "\n".join(result)

    def prepare_locals(self):
        result = ["struct {"]
        for entry in self.address1.entries.values():
            if entry.entry_type == EntryType.DECLARATION:
                result.append(f"\t{CDataTypes[entry.data_type]} {entry.token.lexeme};")
        result.append("} locals;")
        return "\n".join(result)
