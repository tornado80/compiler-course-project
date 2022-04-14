import ply.yacc
from lexer import PascalLexer


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

    @property
    def id(self):
        return str(id(self))

    def __str__(self):
        return f"{self.type} ({self.leaf})" if self.leaf else self.type


class PascalParser:
    def p_program(self, p):
        """program : PROGRAM ID declarations procedures compound_statement"""
        p[0] = Node("program", children=[p[3], p[4], p[5]], leaf=p[2])
        print(self.p_program.__doc__)

    def p_declarations(self, p):
        """declarations : VAR declaration_list SEMICOLON
                        | empty"""
        p[0] = node = Node("declarations")
        if len(p) > 2:
            node.children.append(p[2])
            print("declarations : VAR declaration_list SEMICOLON")
        else:
            print("declarations : empty")

    def p_declaration_list(self, p):
        """declaration_list : declaration_list SEMICOLON declaration
                            | declaration"""
        p[0] = node = Node("declaration_list", children=[p[1]])
        if len(p) > 2:
            node.children.append(p[3])
            print("declaration_list : declaration_list SEMICOLON declaration")
        else:
            print("declaration_list : declaration")

    def p_declaration(self, p):
        """declaration : identifier_list COLON type"""
        p[0] = Node("declaration", children=[p[1]], leaf=p[3])
        print(self.p_declaration.__doc__)

    def p_identifier_list(self, p):
        """identifier_list : identifier_list COMMA ID
                           | ID"""
        p[0] = node = Node("identifier_list")
        if len(p) > 2:
            node.children.extend([p[1], Node("token", leaf=p[3])])
            print("identifier_list : identifier_list COMMA ID")
        else:
            node.children.append(Node("token", leaf=p[1]))
            print("identifier_list : ID")

    def p_type(self, p):
        """type : INTEGER
                | REAL"""
        p[0] = Node("type", leaf=p[1])
        print("type :", p[1].type)

    def p_procedures(self, p):
        """procedures : procedure_list
                      | empty"""
        p[0] = Node("procedures", children=[p[1]])
        if p[1].type == "empty":
            print("procedures : empty")
        else:
            print("procedures : procedure_list")

    def p_procedure_list(self, p):
        """procedure_list : procedure_list procedure
                          | procedure"""
        p[0] = node = Node("procedure_list", children=[p[1]])
        if len(p) > 2:
            node.children.append(p[2])
            print("procedure_list : procedure_list procedure")
        else:
            print("procedure_list : procedure")

    def p_procedure(self, p):
        """procedure : PROCEDURE ID parameters SEMICOLON declarations compound_statement SEMICOLON"""
        p[0] = Node("procedure", children=[p[3], p[5], p[6]], leaf=p[2])
        print(self.p_procedure.__doc__)

    def p_parameters(self, p):
        """parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS
                      | empty"""
        p[0] = node = Node("parameters")
        if len(p) > 2:
            node.children.append(p[2])
            print("parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS")
        else:
            node.children.append(p[1])
            print("parameters : empty")

    def p_compound_statement(self, p):
        """compound_statement : BEGIN statement_list END"""
        p[0] = Node("compound_statement", children=[p[2]])
        print(self.p_compound_statement.__doc__)

    def p_statement_list(self, p):
        """statement_list : statement_list SEMICOLON statement
                          | statement"""
        p[0] = node = Node("statement_list", children=[p[1]])
        if len(p) > 2:
            node.children.append(p[3])
            print("statement_list : statement_list SEMICOLON statement")
        else:
            print("statement_list : statement")

    def p_statement_assignment(self, p):
        """statement : ID ASSIGN expression"""
        p[0] = Node("assignment", children=[p[3]], leaf=p[1])
        print(self.p_statement_assignment.__doc__)

    def p_statement_while(self, p):
        """statement : WHILE expression DO statement"""
        p[0] = Node("while", children=[p[2], p[4]])
        print(self.p_statement_while.__doc__)

    def p_statement_procedure_call(self, p):
        """statement : ID arguments"""
        p[0] = Node("procedure_call", children=[p[2]], leaf=p[1])
        print(self.p_statement_procedure_call.__doc__)

    def p_statement_if(self, p):
        """statement : IF expression THEN statement"""
        p[0] = Node("if", children=[p[2], p[4]])
        print(self.p_statement_if.__doc__)

    def p_statement_if_else(self, p):
        """statement : IF expression THEN statement ELSE statement"""
        p[0] = Node("if_else", children=[p[2], p[4], p[6]])
        print(self.p_statement_if_else.__doc__)

    def p_statement_compound(self, p):
        """statement : compound_statement"""
        p[0] = Node("compound", children=[p[1]])
        print(self.p_statement_compound.__doc__)

    def p_arguments(self, p):
        """arguments : LEFT_PARENTHESIS actual_parameters RIGHT_PARENTHESIS"""
        p[0] = Node("arguments", children=[p[2]])
        print(self.p_arguments.__doc__)

    def p_actual_parameters(self, p):
        """actual_parameters : actual_parameter_list
                             | empty"""
        p[0] = Node("actual_parameters", children=[p[1]])
        if p[1].type == "empty":
            print("actual_parameters : empty")
        else:
            print("actual_parameters : actual_parameter_list")

    def p_actual_parameter_list(self, p):
        """actual_parameter_list : actual_parameter_list COMMA expression
                                 | expression"""
        p[0] = node = Node("actual_parameter_list", children=[p[1]])
        if len(p) > 2:
            node.children.append(p[3])
            print("actual_parameter_list : actual_parameter_list COMMA expression")
        else:
            print("actual_parameter_list : expression")

    def p_expression(self, p):
        """expression : expression relational_operator additive_expression
                      | additive_expression"""
        p[0] = node = Node("expression", children=[p[1]])
        if len(p) > 2:
            node.children.extend([p[2], p[3]])
            print("expression : expression relational_operator additive_expression")
        else:
            print("expression : additive_expression")

    def p_relational_operator(self, p):
        """relational_operator : LESS_THAN
                               | LESS_THAN_OR_EQUAL
                               | EQUAL
                               | NOT_EQUAL
                               | GREATER_THAN
                               | GREATER_THAN_OR_EQUAL"""
        p[0] = Node("relational_operator", leaf=p[1])
        print("relational_operator :", p[1].type)

    def p_additive_expression(self, p):
        """additive_expression : additive_expression additive_operator multiplicative_expression
                               | multiplicative_expression"""
        p[0] = node = Node("additive_expression", children=[p[1]])
        if len(p) > 2:
            node.children.extend([p[2], p[3]])
            print("additive_expression : additive_expression additive_operator multiplicative_expression")
        else:
            print("additive_expression : multiplicative_expression")

    def p_additive_operator(self, p):
        """additive_operator : PLUS
                             | MINUS
                             | OR"""
        p[0] = Node("additive_operator", leaf=p[1])
        print("additive_operator :", p[1].type)

    def p_multiplicative_expression(self, p):
        """multiplicative_expression : multiplicative_expression multiplicative_operator unary_expression
                                     | unary_expression"""
        p[0] = node = Node("multiplicative_expression", children=[p[1]])
        if len(p) > 2:
            node.children.extend([p[2], p[3]])
            print("multiplicative_expression : multiplicative_expression multiplicative_operator unary_expression")
        else:
            print("multiplicative_expression : unary_expression")

    def p_multiplicative_operator(self, p):
        """multiplicative_operator : TIMES
                                   | DIVIDE
                                   | DIV
                                   | MOD
                                   | AND"""
        p[0] = Node("multiplicative_operator", leaf=p[1])
        print("multiplicative_operator :", p[1].type)

    def p_unary_expression(self, p):
        """unary_expression : unary_operator unary_expression
                            | primary_expression"""
        p[0] = node = Node("unary_expression", children=[p[1]])
        if len(p) > 2:
            node.children.append(p[2])
            print("unary_expression : unary_operator unary_expression")
        else:
            print("unary_expression : primary_expression")

    def p_unary_operator(self, p):
        """unary_operator : PLUS
                          | MINUS
                          | NOT"""
        p[0] = Node("unary_operator", leaf=p[1])
        print("unary_operator :", p[1].type)

    def p_primary_expression(self, p):
        """primary_expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
                              | ID
                              | INTEGER_CONSTANT
                              | REAL_CONSTANT"""
        p[0] = node = Node("primary_expression")
        if len(p) > 2:
            node.children.append(p[2])
            print("primary_expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS")
        else:
            node.children.append(Node("token", leaf=p[1]))
            print("primary_expression :", p[1].type)

    def p_empty(self, p):
        """empty :"""
        p[0] = Node("empty")

    def p_error(self, p):
        print("Syntax error at line", p.lineno, "for token", p.type, "with value", p.value)

    def build(self, lexer: PascalLexer, **kwargs):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.engine = ply.yacc.yacc(module=self, **kwargs)

    def parse(self, debug=False):
        return self.engine.parse(lexer=self.lexer, debug=debug)
