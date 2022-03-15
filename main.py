import sys
from lexer import PascalLexer

pascal_lexer = PascalLexer()
pascal_lexer.build(debug=1)
with open("program.pas", "r") as f: # sys.argv[1]
    pascal_lexer.input(f.read())
while True:
    token = pascal_lexer.token()
    if not token:
        break
    print(token.type, token.value, token.lineno)