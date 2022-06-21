import os
from src.compiler import compile_, prepare_lexer, prepare_parser


for test in os.listdir("tests/in"):
    print(test)
    input_file_path = f"tests/in/{test}"
    if test.endswith(".expression"):
        lexer = prepare_lexer()
        parser = prepare_parser(lexer, start="expression")
        compile_(input_file_path, "tests/out", lexer, parser, semantic_analysis_relaxed=True)
    if test.endswith(".program"):
        compile_(input_file_path, "tests/out")
