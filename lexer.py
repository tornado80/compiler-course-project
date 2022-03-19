import ply.lex


class Entry:
    def __init__(self, lexeme, attribute):
        self.lexeme = lexeme
        self.attribute = attribute


class PascalLexer:
    keywords = [
        "PROGRAM", "VAR", "BEGIN", "END",
        "IF", "THEN", "ELSE", "WHILE", "DO",
        "AND", "OR", "NOT", "MOD", "DIV",
        "INTEGER", "REAL", "PROCEDURE", "FUNCTION"
    ]
    reserved = {keyword.lower(): keyword for keyword in keywords}
    tokens = [
        "ID", "INTEGER_CONSTANT", "REAL_CONSTANT",
        "PLUS", "MINUS", "TIMES", "DIVIDE",
        "LESS_THAN", "GREATER_THAN", "NOT_EQUAL", "EQUAL",
        "LESS_THAN_OR_EQUAL", "GREATER_THAN_OR_EQUAL",
        "COMMA", "SEMICOLON", "COLON", "ASSIGN",
        "LEFT_PARENTHESIS", "RIGHT_PARENTHESIS"
    ] + keywords
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_ASSIGN = r':='
    t_EQUAL = r'='
    t_NOT_EQUAL = r'<>'
    t_LESS_THAN_OR_EQUAL = r'<='
    t_GREATER_THAN_OR_EQUAL = r'>='
    t_LESS_THAN = r'<'
    t_GREATER_THAN = r'>'
    t_LEFT_PARENTHESIS = r'\('
    t_RIGHT_PARENTHESIS = r'\)'
    t_ignore = ' \t'  # ignore white spaces

    def t_newline(self, token):
        r'\n+'
        token.lexer.lineno += len(token.value)

    def t_REAL_CONSTANT(self, token):
        r'([1-9][0-9]*|0)\.[0-9]+'
        token.value = Entry(token.value, float(token.value))
        return token

    def t_INTEGER_CONSTANT(self, token):
        r'[1-9][0-9]*|0'
        token.value = Entry(token.value, int(token.value))
        return token

    def t_ID(self, token):
        r'[a-zA-Z][a-zA-Z0-9_]*'
        token.type = self.reserved.get(token.value.lower(), 'ID')
        if token.type == 'ID':
            token.value = Entry(token.value, token.value)
        return token

    def build(self, **kwargs):
        self.engine = ply.lex.lex(module=self, **kwargs)

    def input(self, inp):
        self.engine.input(inp)

    def token(self):
        return self.engine.token()

    def t_error(self, token):
        print(f"Illegal character '{token.value[0]}'")
        token.lexer.skip(1)