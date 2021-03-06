from typing import List

import src.ply.lex


class Token:
    def __init__(self, type, lexeme, attribute, lineno):
        self.type = type
        self.lexeme = lexeme
        self.attribute = attribute
        self.lineno = lineno

    def __repr__(self):
        return f"Token(type: {self.type}, lexeme: '{self.lexeme}', attribute: {self.attribute}, lineno: {self.lineno})"


class PascalLexer:
    states = (
        ('comment', 'exclusive'),
    )
    keywords = [
        "PROGRAM", "VAR", "BEGIN", "END",
        "IF", "THEN", "ELSE", "WHILE", "DO",
        "AND", "OR", "NOT", "MOD", "DIV",
        "INTEGER", "REAL", "PROCEDURE",
        "TRUE", "FALSE", "PRINT"
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
    t_comment_ignore = ' \t\n'  # ignore white spaces in comments

    def __init__(self):
        self.comment_level = 0
        self.engine = None
        self.comment_start = 0
        self.generated_tokens: List[Token] = []

    def t_inline_comment(self, token):
        r'//.*'
        pass

    def t_comment(self, token):
        r'\{'
        self.comment_start = token.lexer.lexpos
        self.comment_level = 1
        token.lexer.begin('comment')

    def t_comment_lbrace(self, token):
        r'\{'
        self.comment_level += 1

    def t_comment_rbrace(self, token):
        r'\}'
        self.comment_level -= 1
        if self.comment_level == 0:
            comment = token.lexer.lexdata[self.comment_start:token.lexer.lexpos]
            token.lexer.lineno += comment.count('\n')
            token.lexer.begin('INITIAL')

    def t_comment_error(self, token):
        token.lexer.skip(1)

    def t_newline(self, token):
        r'\n+'
        token.lexer.lineno += len(token.value)

    def t_REAL_CONSTANT(self, token):
        r'([1-9][0-9]*|0)\.[0-9]+'
        token.value = Token(token.type, token.value, float(token.value), token.lineno)
        return token

    def t_INTEGER_CONSTANT(self, token):
        r'[1-9][0-9]*|0'
        token.value = Token(token.type, token.value, int(token.value), token.lineno)
        return token

    def t_ID(self, token):
        r'[a-zA-Z][a-zA-Z0-9_]*'
        token.type = self.reserved.get(token.value.lower(), 'ID')
        if token.type == "TRUE":
            token.value = Token(token.type, token.value, True, token.lineno)
        if token.type == "FALSE":
            token.value = Token(token.type, token.value, False, token.lineno)
        if token.type == 'ID':
            token.value = Token(token.type, token.value, None, token.lineno)
        return token

    def build(self, **kwargs):
        self.engine = src.ply.lex.lex(module=self, **kwargs)

    def input(self, inp):
        self.engine.input(inp)

    def token(self):
        token = self.engine.token()
        if token:
            if not isinstance(token.value, Token):
                token.value = Token(token.type, token.value, None, token.lineno)
            self.generated_tokens.append(token.value)
        return token

    def t_error(self, token):
        print(f"Illegal character '{token.value[0]}'")
        token.lexer.skip(1)
