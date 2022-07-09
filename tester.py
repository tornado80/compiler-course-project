import os
from src.compiler import compile_, prepare_lexer, prepare_parser


for test in os.listdir("tests/in"):
    print(test)
    input_file_path = f"tests/in/{test}"
    start_variable = test.split(".")[1]
    compile_(input_file_path, "tests/out",
             semantic_analysis_relaxed= True if start_variable != "program" else False,
             start=start_variable)
