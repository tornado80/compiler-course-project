from abc import ABC, abstractmethod
from typing import List, Union
from src.errors import SemanticError
from src.lexer import Token
from src.operator_enum import UnaryOperator, BinaryOperator
from src.ply.code_generator_base import CodeGeneratorBase
from src.symbol_table import DataType, EntryType, Entry
from src.three_address_code import UnaryAssignment, BinaryAssignment, BareAssignment, ConditionalJump, \
    UnconditionalJump, Call, BeginProgram, EndProgram, Label, ThreeAddressCode, Definition, Temporary, \
    ActivationRecordDefinition, Return, Print


class Node(ABC):
    def __init__(self, tag=None, children: List['Node'] = None, leaf=None, parent: 'Node'=None):
        self.tag = tag
        self.children: List['Node'] = []
        if children:
            self.add_children(*children)
        self.leaf = leaf
        self.parent: 'Node' = parent

    @property
    def id(self):
        return str(id(self))

    def add_children(self, *args):
        for child in args:
            child.parent = self
            self.children.append(child)

    @abstractmethod
    def visit(self, code_generator: CodeGeneratorBase):
        pass

    def __str__(self):
        return f"{self.tag} ({self.leaf})" if self.leaf else self.tag


class Expression(Node):
    @abstractmethod
    def __init__(self, tag, children=None, leaf=None):
        super().__init__(tag, children, leaf)
        self.place: Entry = None
        self.type: DataType = None
        self.truelist: List[ThreeAddressCode] = []
        self.falselist: List[ThreeAddressCode] = []


class BinaryExpression(Expression):
    def __init__(self, binary_operator: Token, left_operand: Expression, right_operand: Expression):
        super().__init__("binary_expression", children=[left_operand, right_operand], leaf=binary_operator)
        self.binary_operator = binary_operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def visit(self, code_generator: CodeGeneratorBase):
        self.left_operand.visit(code_generator)
        if self.binary_operator.type in ["AND", "OR"]:
            # marker = code_generator.nextquad
            marker = Label(code_generator.newlabel())
            code_generator.emit(marker)
        self.right_operand.visit(code_generator)
        arithmetic_types = [DataType.REAL, DataType.INTEGER]
        if self.binary_operator.type in ["LESS_THAN", "GREATER_THAN", "NOT_EQUAL",
            "EQUAL", "LESS_THAN_OR_EQUAL", "GREATER_THAN_OR_EQUAL"]:
            # type checking
            if self.left_operand.type not in arithmetic_types or self.right_operand.type not in arithmetic_types:
                code_generator.log(
                    SemanticError(f"Incompatible types: relational operators only apply to arithmetic types.")
                )
            # free temporary
            if self.left_operand.place.entry_type == EntryType.TEMPORARY:
                code_generator.freetemp(self.left_operand.place.data_type)
            if self.right_operand.place.entry_type == EntryType.TEMPORARY:
                code_generator.freetemp(self.right_operand.place.data_type)
            # find the type of result
            self.type = DataType.BOOLEAN
            # TODO: convert to Relational Operator Enum. we have just relaxed restricting types :)
            # code generation
            conditional_jump = code_generator.emit(ConditionalJump(
                self.binary_operator.lexeme,
                self.left_operand.place,
                self.right_operand.place,
                None  # None label is to be backpatched
            ))
            unconditional_jump = code_generator.emit(UnconditionalJump(None))
            # backpatching
            # nextquad = code_generator.nextquad
            self.truelist = [conditional_jump]  # [nextquad]
            self.falselist = [unconditional_jump]  # [nextquad + 1]
        if self.binary_operator.type in ["PLUS", "MINUS", "TIMES", "DIVIDE", "MOD", "DIV"]:
            # type checking
            if self.left_operand.type not in arithmetic_types or self.right_operand.type not in arithmetic_types:
                code_generator.log(
                    SemanticError(f"Incompatible types: arithmetic operators only apply to arithmetic types.")
                )
            # TODO: type checking right and left of MOD and DIV
            # free temporary
            if self.left_operand.place.entry_type == EntryType.TEMPORARY:
                code_generator.freetemp(self.left_operand.place.data_type)
            if self.right_operand.place.entry_type == EntryType.TEMPORARY:
                code_generator.freetemp(self.right_operand.place.data_type)
            # find the type of result and allocate temporary
            if self.left_operand.type == DataType.REAL or self.right_operand.type == DataType.REAL:
                self.type = DataType.REAL
                self.place = code_generator.newtemp(self.type)
            if self.left_operand.type == DataType.INTEGER and self.right_operand.type == DataType.INTEGER:
                self.type = DataType.INTEGER
                self.place = code_generator.newtemp(self.type)
            # code generation
            code_generator.emit(BinaryAssignment(
                self.binary_operator.lexeme,
                self.left_operand.place,
                self.right_operand.place,
                self.place
            ))
        if self.binary_operator.type in ["AND", "OR"]:
            # type checking
            if self.left_operand.type != DataType.BOOLEAN or self.left_operand.type != DataType.BOOLEAN:
                code_generator.log(
                    SemanticError(f"Incompatible types: logical operators only apply to boolean types.")
                )
            # find the type of result
            self.type = DataType.BOOLEAN
            # backpatching
            if self.binary_operator.type == "OR":
                code_generator.backpatch(self.left_operand.falselist, marker)
                self.truelist = self.left_operand.truelist + self.right_operand.truelist
                self.falselist = self.right_operand.falselist
            if self.binary_operator.type == "AND":
                code_generator.backpatch(self.left_operand.truelist, marker)
                self.truelist = self.right_operand.truelist
                self.falselist = self.left_operand.falselist + self.right_operand.falselist


class UnaryExpression(Expression):
    def __init__(self, unary_operator: Token, operand: Expression):
        super().__init__("unary_expression", children=[operand], leaf=unary_operator)
        self.unary_operator = unary_operator
        self.operand = operand

    def visit(self, code_generator):
        self.operand.visit(code_generator)
        # find the type of result
        self.type = self.operand.type
        if self.unary_operator.type == "NOT":
            # type checking
            if self.operand.type != DataType.BOOLEAN:
                code_generator.log(SemanticError(f"Incompatible types: expected {DataType.BOOLEAN} got {self.operand.type}"))
            # backpatching
            self.truelist = self.operand.falselist
            self.falselist = self.operand.truelist
        else:
            # allocate temporary
            self.place = code_generator.newtemp(self.type)
            expected = [DataType.REAL, DataType.INTEGER]
            # type checking
            if self.operand.type not in expected:
                code_generator.log(SemanticError(f"Incompatible types: expected {expected} got {self.operand.type}"))
            # code generation
            code_generator.emit(UnaryAssignment(self.unary_operator.lexeme, self.operand.place, self.place))


class TerminalExpression(Expression):
    def __init__(self, terminal: Token):
        super().__init__("identifier_or_constant", leaf=terminal)
        self.terminal: Token = terminal

    def visit(self, code_generator):
        if self.terminal.type == "ID":
            entry = code_generator.lookup_entries(self.terminal)
            if not entry:
                code_generator.log(SemanticError(f"Identifier {self.terminal} is used before declaration."))
            self.place = entry
            self.type = entry.data_type
        elif self.terminal.type == "INTEGER_CONSTANT":
            entry = code_generator.insert_entry(self.terminal, DataType.INTEGER, EntryType.CONSTANT)
            self.place = entry
            self.type = entry.data_type
        elif self.terminal.type == "REAL_CONSTANT":
            entry = code_generator.insert_entry(self.terminal, DataType.REAL, EntryType.CONSTANT)
            self.place = entry
            self.type = entry.data_type
        elif self.terminal.type == "TRUE":
            entry = code_generator.insert_entry(self.terminal, DataType.BOOLEAN, EntryType.CONSTANT)
            #self.place = entry # note that this is not necessary because we don't have boolean data types at all
            self.type = entry.data_type
            # backpatching
            unconditional_jump = code_generator.emit(UnconditionalJump(None))  # None label is to be backpatched
            self.truelist = [unconditional_jump]
        elif self.terminal.type == "FALSE":
            entry = code_generator.insert_entry(self.terminal, DataType.BOOLEAN, EntryType.CONSTANT)
            #self.place = entry # note that this is not necessary
            self.type = entry.data_type
            # backpatching
            unconditional_jump = code_generator.emit(UnconditionalJump(None))  # None label is to be backpatched
            self.falselist = [unconditional_jump]


class Statement(Node):
    def __init__(self, tag, children=None, leaf=None):
        super().__init__(tag, children, leaf)
        self.nextlist: List[ThreeAddressCode] = []

    @abstractmethod
    def visit(self, code_generator):
        pass


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        super().__init__("print", leaf=expression)
        self.expression = expression

    def visit(self, code_generator):
        self.expression.visit(code_generator)
        code_generator.emit(Print(self.expression.place))
        if self.expression.place.entry_type == EntryType.TEMPORARY:
            code_generator.freetemp(self.expression.place.data_type)


class AssignmentStatement(Statement):
    def __init__(self, lvalue: Token, rvalue: Expression):
        super().__init__("assignment", children=[rvalue], leaf=lvalue)
        self.rvalue = rvalue
        self.lvalue = lvalue

    def visit(self, code_generator):
        self.rvalue.visit(code_generator)
        entry = code_generator.lookup_entries(self.lvalue)
        if not entry:
            code_generator.log(SemanticError(f"Identifier {self.lvalue} is used before declaration."))
        if entry.data_type != self.rvalue.type:
            code_generator.log(SemanticError(f"Type mismatch, {entry.data_type} could not be mixed with {self.rvalue.type}."))
        code_generator.emit(BareAssignment(self.rvalue.place, entry))
        if self.rvalue.place.entry_type == EntryType.TEMPORARY:
            code_generator.freetemp(self.rvalue.place.data_type)


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        super().__init__("while", children=[condition, body])
        self.condition = condition
        self.body = body

    def visit(self, code_generator):
        marker1 = code_generator.emit(Label(code_generator.newlabel()))  # code_generator.nextquad
        self.condition.visit(code_generator)
        if self.condition.type != DataType.BOOLEAN:
            code_generator.log(
                SemanticError(f"Type mismatch, conditional expressions have to be boolean."))
        marker2 = code_generator.emit(Label(code_generator.newlabel()))  # code_generator.nextquad
        self.body.visit(code_generator)
        code_generator.backpatch(self.body.nextlist, marker1)
        code_generator.backpatch(self.condition.truelist, marker2)
        self.nextlist = self.condition.falselist
        code_generator.emit(UnconditionalJump(marker1))  # f"l{marker1}"


class IfStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        super().__init__("if", children=[condition, body])
        self.condition = condition
        self.body = body

    def visit(self, code_generator):
        self.condition.visit(code_generator)
        if self.condition.type != DataType.BOOLEAN:
            code_generator.log(
                SemanticError(f"Type mismatch, conditional expressions have to be boolean."))
        marker = code_generator.emit(Label(code_generator.newlabel()))  # code_generator.nextquad
        self.body.visit(code_generator)
        code_generator.backpatch(self.condition.truelist, marker)
        self.nextlist = self.condition.falselist + self.body.nextlist


class IfElseStatement(Statement):
    def __init__(self, condition: Expression, then_body: Statement, else_body: Statement):
        super().__init__("if_else", children=[condition, then_body, else_body])
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def visit(self, code_generator):
        self.condition.visit(code_generator)
        if self.condition.type != DataType.BOOLEAN:
            code_generator.log(
                SemanticError(f"Type mismatch, conditional expressions have to be boolean."))
        marker1 = code_generator.emit(Label(code_generator.newlabel()))  # code_generator.nextquad
        self.then_body.visit(code_generator)
        # marker2 = code_generator.nextquad
        unconditional_jump = code_generator.emit(UnconditionalJump(None))
        marker3 = code_generator.emit(Label(code_generator.newlabel()))  # code_generator.nextquad  # could be marker2 + 1?
        self.else_body.visit(code_generator)
        code_generator.backpatch(self.condition.truelist, marker1)
        code_generator.backpatch(self.condition.falselist, marker3)
        self.nextlist = self.then_body.nextlist + self.else_body.nextlist + [unconditional_jump]


class CompoundStatement(Statement):
    def __init__(self, first_statement: Statement):
        super().__init__("compound_statement", children=[first_statement])

    def visit(self, code_generator):
        for statement in self.children[:-1]:
            statement.visit(code_generator)
            if len(statement.nextlist) > 0:
                marker = code_generator.emit(Label(code_generator.newlabel()))  # code_generator.nextquad
                code_generator.backpatch(statement.nextlist, marker)
        self.children[-1].visit(code_generator)
        self.nextlist = self.children[-1].nextlist


class Arguments(Node):
    def __init__(self, first_expression: Expression = None):
        super().__init__("arguments")
        if first_expression:
            self.add_children(first_expression)
        self.queue = []

    def visit(self, code_generator):
        for expression in self.children:
            expression.visit(code_generator)
            self.queue.append(expression.place)


class ProcedureCallStatement(Statement):
    def __init__(self, procedure_name: Token, arguments: Arguments):
        super().__init__("procedure_call", children=[arguments], leaf=procedure_name)
        self.procedure_name = procedure_name
        self.arguments = arguments

    def visit(self, code_generator):
        self.arguments.visit(code_generator)
        procedure = code_generator.lookup_procedures(self.procedure_name)
        if len(procedure.parameters) != len(self.arguments.queue):
            code_generator.log(SemanticError("Procedure call arity does not match the procedure parameter counts."))
        marker = Label(code_generator.newlabel())
        code_generator.emit(Call(procedure, marker))
        for place, parameter in zip(self.arguments.queue, procedure.parameters):
            if place.data_type != parameter.data_type:
                code_generator.log(SemanticError("Type mismatch when passing arguments to procedure."))
            code_generator.emit(BareAssignment(place, parameter))
            if place.entry_type == EntryType.TEMPORARY:
                code_generator.freetemp(place.data_type)
        code_generator.emit(UnconditionalJump(procedure.begin_code_label))
        code_generator.emit(marker)


class Declaration(Node):
    def __init__(self, first_identifier: Token):
        super().__init__("declaration")  # leaf = <data_type, [identifiers]>
        self.identifiers: List[Token] = [first_identifier]
        self.data_type: DataType = DataType.INTEGER
        self.entrylist = []

    def set_data_type(self, token: Token):
        if token.type == "REAL":
            self.data_type = DataType.REAL
        elif token.type == "INTEGER":
            self.data_type = DataType.INTEGER
        self.leaf = (self.data_type, self.identifiers)

    def add_identifier(self, identifier: Token):
        self.identifiers.append(identifier)

    def visit(self, code_generator):
        for identifier in self.identifiers:
            self.entrylist.append(code_generator.insert_entry(identifier, self.data_type, EntryType.DECLARATION))


class Declarations(Node):
    def __init__(self, first_declaration: Declaration = None):
        super().__init__("declarations")
        if first_declaration:
            self.add_children(first_declaration)
        self.entrylist = []

    def visit(self, code_generator):
        for child in self.children:
            child.visit(code_generator)
            self.entrylist.extend(child.entrylist)


class Parameters(Node):
    def __init__(self, declarations: Declarations):
        super().__init__("parameters", children=[declarations])
        self.declarations = declarations

    def visit(self, code_generator):
        self.declarations.visit(code_generator)
        for entry in self.declarations.entrylist:
            entry.entry_type = EntryType.PARAMETER
        self.entrylist = self.declarations.entrylist


class Procedure(Node):
    def __init__(self,
                 name: Token,
                 parameters: Parameters,
                 declarations: Declarations,
                 compound_statement: CompoundStatement):
        super().__init__("procedure", children=[parameters, declarations, compound_statement], leaf=name)
        self.name = name
        self.parameters = parameters
        self.declarations = declarations
        self.compound_statement = compound_statement

    def visit(self, code_generator):
        # create a symbol table for the procedure
        symbol_table = code_generator.insert_procedure(self.name)
        # mark the beginning of code for the procedure
        begin_marker = Label(code_generator.newlabel())
        code_generator.emit(begin_marker)
        symbol_table.set_begin_code_label(begin_marker)
        # set current symbol table in code generator to the newly generated one
        code_generator.set_symbol_table(symbol_table)
        # visit parameters
        self.parameters.visit(code_generator)
        symbol_table.parameters = self.parameters.entrylist
        self.declarations.visit(code_generator)
        self.compound_statement.visit(code_generator)
        # insert procedure activation record struct at the beginning of program
        code_generator.insert_quadruple(1, ActivationRecordDefinition(symbol_table))
        # mark the end of code for the procedure
        if len(self.compound_statement.nextlist) > 0:
            end_marker = Label(code_generator.newlabel())
            code_generator.emit(end_marker)
            code_generator.backpatch(self.compound_statement.nextlist, end_marker)  # code_generator.nextquad
        code_generator.emit(Return(symbol_table))
        # restore enclosing scope symbol table
        code_generator.set_symbol_table(symbol_table.parent)


class Procedures(Node):
    def __init__(self, first_procedure: Procedure = None):
        super().__init__("procedures")
        if first_procedure:
            self.add_children(first_procedure)

    def visit(self, code_generator):
        for child in self.children:
            child.visit(code_generator)


class Program(Node):
    def __init__(self,
                 name: Token,
                 declarations: Declarations,
                 procedures: Procedures,
                 compound_statement: CompoundStatement):
        super().__init__("program", children=[declarations, procedures, compound_statement], leaf=name)
        self.declarations = declarations
        self.procedures = procedures
        self.compound_statement = compound_statement
        self.name = name

    def visit(self, code_generator):
        code_generator.emit(BeginProgram())
        self.declarations.visit(code_generator)
        for entry in self.declarations.entrylist:
            code_generator.emit(Definition(entry))
        unconditional_jump = code_generator.emit(UnconditionalJump(None))
        self.procedures.visit(code_generator)
        begin_marker = code_generator.emit(Label(code_generator.newlabel()))
        code_generator.backpatch([unconditional_jump], begin_marker)
        quad = code_generator.nextquad
        self.compound_statement.visit(code_generator)
        for data_type, count in code_generator.symbol_table.max_count_of_temporary.items():
            if count > 0:
                code_generator.insert_quadruple(quad - 1, Temporary(data_type, count))
        if len(self.compound_statement.nextlist) > 0:
            end_marker = code_generator.emit(Label(code_generator.newlabel()))
            code_generator.backpatch(self.compound_statement.nextlist, end_marker)
        code_generator.emit(EndProgram())
