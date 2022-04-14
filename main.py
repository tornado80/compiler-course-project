import sys
from lexer import PascalLexer, Token
from parser import PascalParser, Node
import pydot


def tokenizer():
    while True:
        token = pascal_lexer.token()
        if not token:
            break
        print(token.value)


def traverse_ast(tree: pydot.Dot, parent: Node):
    for child in parent.children:
        tree.add_node(pydot.Node(child.id, label=str(child)))
        tree.add_edge(pydot.Edge(parent.id, child.id))
        traverse_ast(tree, child)


def get_ast(root: Node):
    tree = pydot.Dot("Abstract Syntax Tree (AST)", graph_type="graph")
    tree.add_node(pydot.Node(root.id, label=str(root)))
    traverse_ast(tree, root)
    return tree


pascal_lexer = PascalLexer()
pascal_lexer.build()
pascal_parser = PascalParser()
pascal_parser.build(pascal_lexer)
with open("program.pas", "r") as f: # sys.argv[1]
    pascal_lexer.input(f.read())
# tokenizer()
tree = get_ast(pascal_parser.parse())
tree.write_svg("program_ast.svg")

