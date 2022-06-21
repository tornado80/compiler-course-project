from typing import List
from src.lexer import Token
from src.ply.code_generator_base import CodeGeneratorBase
from src.symbol_table import SymbolTable, DataType, EntryType
from src.syntax_tree import Node, Program
from src.three_address_code import ThreeAddressCode


class CodeGenerator(CodeGeneratorBase):
    def __init__(self, syntax_tree_root: Node):
        self.syntax_tree_root = syntax_tree_root
        if isinstance(syntax_tree_root, Program):
            self._symbol_table = SymbolTable(syntax_tree_root.name)
        else:
            self._symbol_table = SymbolTable(Token("ID", "DEFAULT", None, 0))
        self.quadruples: List[ThreeAddressCode] = []
        self.last_temporary_variable = 0
        self.semantic_analysis: bool

    def emit(self, tac: ThreeAddressCode):
        self.quadruples.append(tac)

    def newtemp(self):
        # TODO: free temp
        self.last_temporary_variable += 1
        return f"({self.last_temporary_variable})"

    def generate(self, semantic_analysis_relaxed: bool):
        self.semantic_analysis_relaxed = semantic_analysis_relaxed
        self.syntax_tree_root.visit(self)
        return self.quadruples

    @property
    def symbol_table(self) -> SymbolTable:
        return self._symbol_table

    def set_symbol_table(self, symbol_table: SymbolTable):
        self._symbol_table = symbol_table

    def insert_entry(self, identifier: Token, data_type: DataType, entry_type: EntryType):
        return self._symbol_table.insert_entry(identifier, data_type, entry_type)

    def insert_procedure(self, identifier: Token):
        return self._symbol_table.insert_procedure(identifier)

    def lookup_entries(self, identifier: Token):
        if self.semantic_analysis_relaxed:
            entry = self._symbol_table.lookup_entries(identifier)
            if not entry:
                entry = self._symbol_table.insert_entry(identifier, DataType.INTEGER, EntryType.DECLARATION)
            return entry
        return self._symbol_table.lookup_entries(identifier)

    def lookup_procedures(self, identifier: Token):
        if self.semantic_analysis_relaxed:
            procedure = self._symbol_table.insert_procedure(identifier)
            if not procedure:
                procedure = self._symbol_table.insert_procedure(identifier)
            return procedure
        return self._symbol_table.lookup_procedure(identifier)
