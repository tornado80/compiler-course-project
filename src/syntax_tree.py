from abc import ABC, abstractmethod
from typing import List, Union
from src.lexer import Token
from src.operator_enum import UnaryOperator, BinaryOperator
from src.ply.code_generator_base import CodeGeneratorBase
from src.symbol_table import DataType, EntryType
from src.three_address_code import UnaryAssignment, BinaryAssignment, Label


class Node(ABC):
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

    @abstractmethod
    def visit(self, code_generator: CodeGeneratorBase):
        pass

    def __str__(self):
        return f"{self.tag} ({self.leaf})" if self.leaf else self.tag


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


class Statement(Node):
    def __init__(self, tag, children=None, leaf=None):
        super().__init__(tag, children, leaf)
        self.nextlist = []

    def visit(self, code_generator):
        pass


class AssignmentStatement(Statement):
    def __init__(self, lvalue: Token, rvalue: Expression):
        super().__init__("assignment", children=[rvalue], leaf=lvalue)
        self.rvalue = rvalue
        self.lvalue = lvalue

    def visit(self, code_generator):
        pass


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        super().__init__("while", children=[condition, body])
        self.condition = condition
        self.body = body

    def visit(self, code_generator):
        pass


class IfStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        super().__init__("if", children=[condition, body])
        self.condition = condition
        self.body = body

    def visit(self, code_generator):
        pass


class IfElseStatement(Statement):
    def __init__(self, condition: Expression, then_body: Statement, else_body: Statement):
        super().__init__("if_else", children=[condition, then_body, else_body])
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def visit(self, code_generator):
        pass


class Arguments(Node):
    def __init__(self, first_expression: Expression = None):
        super().__init__("arguments")
        if first_expression:
            self.add_children(first_expression)

    def visit(self, code_generator):
        pass


class ProcedureCallStatement(Statement):
    def __init__(self, procedure_name: Token, arguments: Arguments):
        super().__init__("procedure_call", children=[arguments], leaf=procedure_name)
        self.procedure_name = procedure_name
        self.arguments = arguments

    def visit(self, code_generator):
        pass


class CompoundStatement(Statement):
    def __init__(self, first_statement: Statement):
        super().__init__("compound_statement", children=[first_statement])

    def visit(self, code_generator):
        pass


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
        elif token.type == "BOOLEAN":
            self.data_type = DataType.BOOLEAN
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
        del self.declarations.entrylist


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
        symbol_table = code_generator.insert_procedure(self.name)
        code_generator.emit(Label(symbol_table))
        code_generator.set_symbol_table(symbol_table)
        self.parameters.visit(code_generator)
        self.declarations.visit(code_generator)
        self.compound_statement.visit(code_generator)
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
                 declarations: Declaration,
                 procedures: Procedures,
                 compound_statement: CompoundStatement):
        super().__init__("program", children=[declarations, procedures, compound_statement], leaf=name)
        self.declarations = declarations
        self.procedures = procedures
        self.compound_statement = compound_statement
        self.name = name

    def visit(self, code_generator):
        self.declarations.visit(code_generator)
        self.procedures.visit(code_generator)
        code_generator.emit(Label(code_generator.symbol_table))
        self.compound_statement.visit(code_generator)
