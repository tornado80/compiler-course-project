import ply.yacc
from lexer import PascalLexer


class PascalParser:
    def p_program(self, p):
        """program : PROGRAM ID declarations procedure_list compound_statement"""
        print(self.p_program.__doc__)

    def p_declarations(self, p):
        """declarations : VAR declaration_list SEMICOLON
                        | empty"""
        if len(p) > 2:
            print("declarations : VAR declaration_list SEMICOLON")
        else:
            print("declarations : empty")

    def p_declaration_list(self, p):
        """declaration_list : declaration_list SEMICOLON declaration
                            | declaration"""
        if len(p) > 2:
            print("declaration_list : declaration_list SEMICOLON declaration")
        else:
            print("declaration_list : declaration")

    def p_declaration(self, p):
        """declaration : identifier_list COLON type"""
        print(self.p_declaration.__doc__)

    def p_identifier_list(self, p):
        """identifier_list : identifier_list COMMA ID
                           | ID"""
        if len(p) > 2:
            print("identifier_list : identifier_list COMMA ID")
        else:
            print("identifier_list : ID")

    def p_type(self, p):
        """type : INTEGER
                | REAL"""
        print("type :", p[1].type)

    def p_procedure_list(self, p):
        """procedure_list : procedure_list procedure
                          | empty"""
        if len(p) > 2:
            print("procedure_list : procedure_list procedure")
        else:
            print("procedure_list : empty")

    def p_procedure(self, p):
        """procedure : PROCEDURE ID parameters SEMICOLON declarations compound_statement SEMICOLON"""
        print(self.p_procedure.__doc__)

    def p_parameters(self, p):
        """parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS
                      | empty"""
        if len(p) > 2:
            print("parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS")
        else:
            print("parameters : empty")

    def p_compound_statement(self, p):
        """compound_statement : BEGIN statement_list END"""
        print(self.p_compound_statement.__doc__)

    def p_statement_list(self, p):
        """statement_list : statement_list SEMICOLON statement
                          | statement"""
        if len(p) > 2:
            print("statement_list : statement_list SEMICOLON statement")
        else:
            print("statement_list : statement")

    def p_statement_assignment(self, p):
        """statement : ID ASSIGN expression"""
        print(self.p_statement_assignment.__doc__)

    def p_statement_while(self, p):
        """statement : WHILE expression DO statement"""
        print(self.p_statement_while.__doc__)

    def p_statement_procedure_call(self, p):
        """statement : ID arguments"""
        print(self.p_statement_procedure_call.__doc__)

    def p_statement_if(self, p):
        """statement : IF expression THEN statement"""
        print(self.p_statement_if.__doc__)

    def p_statement_if_else(self, p):
        """statement : IF expression THEN statement ELSE statement"""
        print(self.p_statement_if_else.__doc__)

    def p_statement_compound(self, p):
        """statement : compound_statement"""
        print(self.p_statement_compound.__doc__)

    def p_arguments(self, p):
        """arguments : LEFT_PARENTHESIS actual_parameters RIGHT_PARENTHESIS"""
        print(self.p_arguments.__doc__)

    def p_actual_parameters(self, p):
        """actual_parameters : actual_parameter_list
                             | empty"""
        if p[1]:
            print("actual_parameters : actual_parameter_list")
        else:
            print("actual_parameters : empty")

    def p_actual_parameter_list(self, p):
        """actual_parameter_list : actual_parameter_list COMMA expression
                                 | expression"""
        if len(p) > 2:
            print("actual_parameter_list : actual_parameter_list COMMA expression")
        else:
            print("actual_parameter_list : expression")

    def p_expression(self, p):
        """expression : expression relational_operator additive_expression
                      | additive_expression"""
        if len(p) > 2:
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
        print("relational_operator :", p[1].type)

    def p_additive_expression(self, p):
        """additive_expression : additive_expression additive_operator multiplicative_expression
                               | multiplicative_expression"""
        if len(p) > 2:
            print("additive_expression : additive_expression additive_operator multiplicative_expression")
        else:
            print("additive_expression : multiplicative_expression")

    def p_additive_operator(self, p):
        """additive_operator : PLUS
                             | MINUS
                             | OR"""
        print("additive_operator :", p[1].type)

    def p_multiplicative_expression(self, p):
        """multiplicative_expression : multiplicative_expression multiplicative_operator unary_expression
                                     | unary_expression"""
        if len(p) > 2:
            print("multiplicative_expression : multiplicative_expression multiplicative_operator unary_expression")
        else:
            print("multiplicative_expression : unary_expression")

    def p_multiplicative_operator(self, p):
        """multiplicative_operator : TIMES
                                   | DIVIDE
                                   | DIV
                                   | MOD
                                   | AND"""
        print("multiplicative_operator :", p[1].type)

    def p_unary_expression(self, p):
        """unary_expression : unary_operator unary_expression
                            | primary_expression"""
        if len(p) > 2:
            print("unary_expression : unary_operator unary_expression")
        else:
            print("unary_expression : primary_expression")

    def p_unary_operator(self, p):
        """unary_operator : PLUS
                          | MINUS
                          | NOT"""

    def p_primary_expression(self, p):
        """primary_expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
                              | ID
                              | INTEGER_CONSTANT
                              | REAL_CONSTANT"""
        if len(p) > 2:
            print("primary_expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS")
        else:
            print("primary_expression :", p[1].type)

    def p_empty(self, p):
        """empty :"""
        p[0] = None

    def p_error(self, p):
        print("Syntax error at line", p.lineno, "for token", p.type, "with value", p.value)

    def build(self, lexer: PascalLexer, **kwargs):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.engine = ply.yacc.yacc(module=self, **kwargs)

    def parse(self, debug=False):
        return self.engine.parse(lexer=self.lexer, debug=debug)
