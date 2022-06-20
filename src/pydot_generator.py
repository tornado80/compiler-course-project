import pydot
from src.syntax_tree import Node


class PyDotGenerator:
    def __init__(self, tree_name: str, tree_root: Node):
        self.tree_root: Node = tree_root
        self.pydot_tree: pydot.Dot = pydot.Dot(tree_name, graph_type="graph")

    def generate(self):
        self.pydot_tree.add_node(pydot.Node(self.tree_root.id, label=str(self.tree_root)))
        self.traverse_tree(self.tree_root)
        return self.pydot_tree

    def traverse_tree(self, parent: Node):
        for child in parent.children:
            self.pydot_tree.add_node(pydot.Node(child.id, label=str(child)))
            self.pydot_tree.add_edge(pydot.Edge(parent.id, child.id))
            self.traverse_tree(child)
