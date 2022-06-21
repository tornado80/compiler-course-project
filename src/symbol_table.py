from enum import Enum
from src.lexer import Token


class DataType(Enum):
    REAL = ("REAL", 8)
    INTEGER = ("INTEGER", 4)
    BOOLEAN = ("BOOLEAN", 1)


class EntryType(Enum):
    TEMPORARY = "TEMPORARY"
    DECLARATION = "DECLARATION"
    PARAMETER = "PARAMETER"


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
        return f"Entry(token: {self.token}, offset: {self.offset}, width: {self.width}, " \
               f"data_type: {self.data_type}, entry_type: {self.entry_type})"


class SymbolTable:
    def __init__(self, header: Token, parent=None):
        self.header = header
        self.parent = parent
        self.entries = {}
        self.procedures = {}
        self.offset = 0

    def __str__(self):
        lines = [f"SymbolTable(header: {self.header}):"]
        for lexeme, entry in self.entries.items():
            lines.append(f"\tentry: {lexeme} -> {entry}")
        for lexeme, procedure in self.procedures.items():
            lines.append(f"\tprocedure: {lexeme} -> ")
            lines.extend(f"\t\t{line}" for line in str(procedure).splitlines())
        return "\n".join(lines)

    def insert_entry(self, identifier: Token, data_type: DataType, entry_type: EntryType):
        lexeme = identifier.lexeme
        if lexeme in self.entries:
            return None
        entry = Entry(identifier, self.offset, data_type, entry_type, self)
        self.entries[lexeme] = entry
        self.offset += entry.width
        return entry

    def insert_procedure(self, identifier: Token):
        lexeme = identifier.lexeme
        if lexeme in self.procedures:
            return None
        symbol_table = SymbolTable(identifier, self)
        self.procedures[lexeme] = symbol_table
        return symbol_table

    def lookup_entries(self, identifier: Token):
        lexeme = identifier.lexeme
        current = self
        while current is not None:
            if lexeme in current.entries:
                return self.entries[lexeme]
            current = self.parent
        return None

    def lookup_procedure(self, identifier: Token):
        lexeme = identifier.lexeme
        current = self
        while current is not None:
            if lexeme in current.procedures:
                return self.procedures[lexeme]
            current = self.parent
        return None
