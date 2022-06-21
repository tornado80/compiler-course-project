from typing import List
from src.lexer import Token
from src.ply.code_generator_base import CodeGeneratorBase
from src.symbol_table import SymbolTable, DataType, EntryType, Entry
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
        self.logs = []

    def backpatch(self, quadruples, label):
        for quadruple in quadruples:
            self.quadruples[quadruple - 1].address3 = label  # change goto
            # 'quadruple - 1' is for transforming to zero based

    @property
    def nextquad(self):
        return len(self.quadruples) + 1  # not zero based

    def log(self, log):
        self.logs.append(log)
        print(log)
        if isinstance(log, Exception):
            raise log

    def emit(self, tac: ThreeAddressCode):
        self.quadruples.append(tac)

    def newtemp(self, data_type: DataType) -> Entry:
        # Could we implement this method in symbol table?
        self._symbol_table.next_available_temporary[data_type] += 1
        maximum = self._symbol_table.max_count_of_temporary[data_type]
        current = self._symbol_table.next_available_temporary[data_type]
        if current > maximum:
            self._symbol_table.max_count_of_temporary[data_type] = current
            entry = self.insert_entry(
                Token("ID", f"({current}/{data_type.name})", None, 0),
                data_type,
                EntryType.TEMPORARY
            )
        else:
            entry = self.lookup_entries(Token("ID", f"({current}/{data_type.name})", None, 0))
        return entry

    def freetemp(self, data_type: DataType):
        self._symbol_table.next_available_temporary[data_type] -= 1

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
        entry, warning = self._symbol_table.insert_entry(identifier, data_type, entry_type)
        if warning:
            self.log(warning)
        return entry

    def insert_procedure(self, identifier: Token):
        entry, warning = self._symbol_table.insert_procedure(identifier)
        if warning:
            self.log(warning)
        return entry

    def lookup_entries(self, identifier: Token):
        if self.semantic_analysis_relaxed:
            entry = self._symbol_table.lookup_entries(identifier)
            if not entry:
                entry, _ = self._symbol_table.insert_entry(identifier, DataType.REAL, EntryType.DECLARATION)
            return entry
        return self._symbol_table.lookup_entries(identifier)

    def lookup_procedures(self, identifier: Token):
        if self.semantic_analysis_relaxed:
            procedure = self._symbol_table.lookup_procedure(identifier)
            if not procedure:
                procedure, _ = self._symbol_table.insert_procedure(identifier)
            return procedure
        return self._symbol_table.lookup_procedure(identifier)
