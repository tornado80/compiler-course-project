from typing import List
from src.syntax_tree import Node
from src.three_address_code import *


class CodeGenerator:
    def __init__(self, syntax_tree_root: Node):
        self.symbol_table = None
        self.syntax_tree_root = syntax_tree_root
        self.quadruples: List[ThreeAddressCode] = []

    def generate(self, semantic_analysis: bool):
        pass
