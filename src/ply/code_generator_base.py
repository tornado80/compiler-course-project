from abc import ABC, abstractmethod
from src.lexer import Token
from src.symbol_table import DataType, EntryType, SymbolTable, Entry
from src.three_address_code import ThreeAddressCode


class CodeGeneratorBase(ABC):
    @abstractmethod
    def emit(self, tac: ThreeAddressCode) -> ThreeAddressCode:
        pass

    @abstractmethod
    def newlabel(self):
        pass

    @abstractmethod
    def insert_quadruple(self, index: int, tac: ThreeAddressCode):
        pass

    @abstractmethod
    def newtemp(self, data_type: DataType):
        pass

    @abstractmethod
    def freetemp(self, data_type: DataType):
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

    @abstractmethod
    def log(self, log):
        pass

    @property
    @abstractmethod
    def nextquad(self):
        pass

    @abstractmethod
    def backpatch(self, quadruples, label):
        pass
