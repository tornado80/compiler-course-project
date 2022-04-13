import sys
from lexer import PascalLexer, Entry
from parser import PascalParser


def tokenizer():
    while True:
        token = pascal_lexer.token()
        if not token:
            break
        if isinstance(token.value, Entry):
            print(f"TOKEN: {token.type}, LEXEME: '{token.value.lexeme}', "
                  f"ATTRIBUTE: {token.value.attribute}, LINE NUMBER: {token.lineno}")
        else:
            print(f"TOKEN: {token.type}, LEXEME: '{token.value}', LINE NUMBER: {token.lineno}")


pascal_lexer = PascalLexer()
pascal_lexer.build()
pascal_parser = PascalParser()
pascal_parser.build(pascal_lexer)
with open("program2.pas", "r") as f: # sys.argv[1]
    pascal_lexer.input(f.read())
pascal_parser.parse()
