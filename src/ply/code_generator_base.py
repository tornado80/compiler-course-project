from abc import ABC, abstractmethod
from src.lexer import Token
from src.symbol_table import DataType, EntryType, SymbolTable, Entry
from src.three_address_code import ThreeAddressCode


class CodeGeneratorBase(ABC):
    @abstractmethod
    def emit(self, tac: ThreeAddressCode):
        pass

    @abstractmethod
    def newtemp(self):
        pass

    @abstractmethod
    def insert_entry(self, identifier: Token, data_type: DataType, entry_type: EntryType) -> Entry:
        pass

    @abstractmethod
    def insert_procedure(self, identifier: Token) -> SymbolTable:
        pass

    @abstractmethod
    def lookup_entries(self, identifier: Token) -> Entry:
        pass

    @abstractmethod
    def lookup_procedures(self, identifier: Token) -> SymbolTable:
        pass


    @property
    @abstractmethod
    def symbol_table(self) -> SymbolTable:
        pass

    @abstractmethod
    def set_symbol_table(self, symbol_table: SymbolTable):
        pass
