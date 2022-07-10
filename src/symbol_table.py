from enum import Enum
from typing import Tuple, Optional, List, Dict

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
                 symbol_table: 'SymbolTable'):
        self.token: Token = token
        self.offset: int = offset
        self.width: int = data_type.value[1]
        self.data_type: DataType = data_type
        self.entry_type = entry_type
        self.symbol_table = symbol_table

    def __str__(self):
        if self.entry_type == EntryType.CONSTANT:
            return str(self.token.attribute)
        if self.symbol_table.parent is None:  # entry in program
            if self.entry_type == EntryType.TEMPORARY:
                return f"temporary_{self.data_type.name}[{self.token.attribute - 1}]"
            elif self.entry_type == EntryType.DECLARATION:  # declaration
                return self.token.lexeme
        else:  # entry in procedure should use current activation record
            common = f"((ActivationRecordPtr_{self.symbol_table.header.lexeme})current_activation_record)->"
            if self.entry_type == EntryType.TEMPORARY:
                return f"{common}temporary_{self.data_type.name}[{self.token.attribute - 1}]"
            elif self.entry_type == EntryType.DECLARATION:
                return f"({common}locals).{self.token.lexeme}"
            elif self.entry_type == EntryType.PARAMETER:
                return f"({common}parameters).{self.token.lexeme}"

    def to_string(self):
        return f"Entry(token: {self.token}, offset: {self.offset}, width: {self.width}, " \
               f"data_type: {self.data_type}, entry_type: {self.entry_type})"


class SymbolTable:
    def __init__(self, header: Token, parent: 'SymbolTable' = None):
        self.header = header
        self.parent = parent
        self.begin_code_label = None
        self.entries: Dict[str, Entry] = {}
        self.procedures: Dict[str, SymbolTable] = {}
        self.parameters: List[Entry] = None
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

    def set_begin_code_label(self, label):
        self.begin_code_label = label

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
                return current.entries[lexeme]
            current = current.parent
        return None

    def lookup_procedure(self, identifier: Token):
        lexeme = identifier.lexeme
        current = self
        while current is not None:
            if lexeme in current.procedures:
                return current.procedures[lexeme]
            current = current.parent
        return None
