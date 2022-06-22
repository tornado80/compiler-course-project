from enum import Enum
from typing import Tuple, Optional, List

from src.lexer import Token


class DataType(Enum):
    REAL = ("REAL", 8)
    INTEGER = ("INTEGER", 4)
    # we don't support boolean data types. this is just for expressions types during code generation
    BOOLEAN = ("BOOLEAN", 1)


class EntryType(Enum):
    TEMPORARY = "TEMPORARY"
    DECLARATION = "DECLARATION"
    PARAMETER = "PARAMETER"
    CONSTANT = "CONSTANT"


class Entry:
    def __init__(self,
                 token: Token,
                 offset: int,
                 data_type: DataType,
                 entry_type: EntryType,
                 symbol_table):
        self.token: Token = token
        self.offset: int = offset
        self.width: int = data_type.value[1]
        self.data_type: DataType = data_type
        self.entry_type = entry_type
        self.symbol_table = symbol_table

    def __str__(self):
        return self.token.lexeme

    def to_string(self):
        return f"Entry(token: {self.token}, offset: {self.offset}, width: {self.width}, " \
               f"data_type: {self.data_type}, entry_type: {self.entry_type})"


class SymbolTable:
    def __init__(self, header: Token, parent=None):
        self.header = header
        self.parent = parent
        self.entries = {}
        self.procedures = {}
        self.parameters: List[Entry] = []
        self.next_available_temporary = {
            DataType.INTEGER: 0,
            DataType.REAL: 0
        }
        self.max_count_of_temporary = {  # maximum ever reached
            DataType.INTEGER: 0,
            DataType.REAL: 0
        }
        self.offset = 0

    def __str__(self):
        lines = [f"SymbolTable(header: {self.header}):"]
        for lexeme, entry in self.entries.items():
            lines.append(f"\tentry: {lexeme} -> {entry.to_string()}")
        for lexeme, procedure in self.procedures.items():
            lines.append(f"\tprocedure: {lexeme} -> ")
            lines.extend(f"\t\t{line}" for line in str(procedure).splitlines())
        return "\n".join(lines)

    def insert_entry(self, identifier: Token, data_type: DataType, entry_type: EntryType):
        lexeme = identifier.lexeme
        warning = None
        if lexeme in self.entries:
            entry = self.entries[lexeme]
            if entry.entry_type == EntryType.CONSTANT:
                return entry, None
            warning = Warning(f"Entry {entry.to_string()} already exists in the symbol table. "
                              f"Token {identifier} shadows it.")
        entry = Entry(identifier, self.offset, data_type, entry_type, self)
        self.entries[lexeme] = entry
        self.offset += entry.width
        return entry, warning

    def insert_procedure(self, identifier: Token):
        lexeme = identifier.lexeme
        warning = None
        if lexeme in self.procedures:
            warning = Warning(f"Warning: procedure '{self.procedures[lexeme]}' already exists in the symbol table. "
                              f"Token {identifier} shadows it.")
        symbol_table = SymbolTable(identifier, self)
        self.procedures[lexeme] = symbol_table
        return symbol_table, warning

    def lookup_entries(self, identifier: Token):
        lexeme = identifier.lexeme
        current = self
        while current is not None:
            if lexeme in current.entries:
                return self.entries[lexeme]
            current = current.parent
        return None

    def lookup_procedure(self, identifier: Token):
        lexeme = identifier.lexeme
        current = self
        while current is not None:
            if lexeme in current.procedures:
                return self.procedures[lexeme]
            current = current.parent
        return None
