import os
from src import utils
from src.compiler import compile_, prepare_lexer, prepare_parser


def tokenizer(input_file_path, lexer):
    with open(input_file_path, "r") as f:
        lexer.input(f.read())
    with open(f"{utils.get_output_file_path(input_file_path, 'tests/out')}.tokens", "w") as f:
        while True:
            token = lexer.token()
            if not token:
                break
            f.write(f"{token.value}\n")


for test in os.listdir("tests/in"):
    input_file_path = f"tests/in/{test}"
    if test.endswith(".expression"):
        tokenizer(input_file_path, prepare_lexer())
        lexer = prepare_lexer()
        parser = prepare_parser(lexer, start="expression")
        compile_(input_file_path, "tests/out", lexer, parser, code_generation=True)
    if test.endswith(".program"):
        tokenizer(input_file_path, prepare_lexer())
        compile_(input_file_path, "tests/out", code_generation=False)
