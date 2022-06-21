from src import utils
from src.lexer import PascalLexer
from src.parser import PascalParser
from src.pydot_generator import PyDotGenerator
from src.code_generator import CodeGenerator


def prepare_lexer(**kwargs):
    pascal_lexer = PascalLexer()
    pascal_lexer.build(**kwargs)
    return pascal_lexer


def prepare_parser(pascal_lexer: PascalLexer, **kwargs):
    pascal_parser = PascalParser()
    pascal_parser.build(pascal_lexer, **kwargs)
    return pascal_parser


def compile_(
        input_file_path: str,
        output_path: str,
        pascal_lexer: PascalLexer = None,
        pascal_parser: PascalParser = None,
        debug=False,
        semantic_analysis_relaxed=False,
        code_generation=True):
    output_file_path = utils.get_output_file_path(input_file_path, output_path)
    if not pascal_lexer:
        pascal_lexer = prepare_lexer()
    if not pascal_parser:
        pascal_parser = prepare_parser(pascal_lexer, debug=debug)
    with open(input_file_path, "r") as f:
        pascal_lexer.input(f.read())
    root = pascal_parser.parse(debug=debug)
    with open(f"{output_file_path}.tokens", "w") as f:
        for token in pascal_lexer.generated_tokens:
            f.write(f"{token}\n")
    with open(f"{output_file_path}.reductions", "w") as f:
        for reduction in pascal_parser.reductions:
            f.write(f"{reduction}\n")
    tree = PyDotGenerator("Syntax Tree", root).generate()
    tree.write_svg(f"{output_file_path}.syntax.svg")
    if code_generation:
        code_generator = CodeGenerator(root)
        quadruples = code_generator.generate(semantic_analysis_relaxed)
        with open(f"{output_file_path}.symbols", "w") as f:
            f.write(str(code_generator.symbol_table))
        with open(f"{output_file_path}.compiled", "w") as f:
            f.writelines([f"{quadruple}\n" for quadruple in quadruples])