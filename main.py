import sys
from lexer import PascalLexer, Entry

pascal_lexer = PascalLexer()
pascal_lexer.build()
with open(sys.argv[1], "r") as f:
    pascal_lexer.input(f.read())
while True:
    token = pascal_lexer.token()
    if not token:
        break
    if isinstance(token.value, Entry):
        print(f"TOKEN: {token.type}, LEXEME: '{token.value.lexeme}', "
              f"ATTRIBUTE: {token.value.attribute}, LINE NUMBER: {token.lineno}")
    else:
        print(f"TOKEN: {token.type}, LEXEME: '{token.value}', LINE NUMBER: {token.lineno}")