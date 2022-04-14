import sys
from lexer import PascalLexer, Token
from parser import PascalParser


def tokenizer():
    while True:
        token = pascal_lexer.token()
        if not token:
            break
        print(token.value)


pascal_lexer = PascalLexer()
pascal_lexer.build()
pascal_parser = PascalParser()
pascal_parser.build(pascal_lexer)
with open("program.pas", "r") as f: # sys.argv[1]
    pascal_lexer.input(f.read())
#tokenizer()
pascal_parser.parse()
