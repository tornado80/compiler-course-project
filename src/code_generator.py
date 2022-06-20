from typing import List
from src.syntax_tree import Node
from src.three_address_code import *


class CodeGenerator:
    def __init__(self, syntax_tree_root: Node):
        self.symbol_table = None
        self.syntax_tree_root = syntax_tree_root
        self.quadruples: List[ThreeAddressCode] = []
        self.last_temporary_variable = 0
        self.semantic_analysis = True

    def emit(self, tac: ThreeAddressCode):
        self.quadruples.append(tac)

    def newtemp(self):
        # TODO: free temp
        self.last_temporary_variable += 1
        return f"({self.last_temporary_variable})"

    def generate(self, semantic_analysis: bool):
        self.semantic_analysis = semantic_analysis
        self.syntax_tree_root.visit(self)
        return self.quadruples
