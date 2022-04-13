import ply.yacc
from lexer import PascalLexer


class PascalParser:
    def p_program(self, p):
        """program : PROGRAM ID declarations procedure_list compound_statement"""
        print(self.p_program.__doc__)

    def p_declarations(self, p):
        """declarations : VAR declaration_list SEMICOLON
                        | empty"""
        print(self.p_declarations.__doc__)

    def p_declaration_list(self, p):
        """declaration_list : declaration
                            | declaration_list SEMICOLON declaration"""
        print(self.p_declaration_list.__doc__)

    def p_declaration(self, p):
        """declaration : identifier_list COLON type"""
        print(self.p_declaration.__doc__)

    def p_identifier_list(self, p):
        """identifier_list : ID
                           | identifier_list COMMA ID"""
        print(self.p_declaration_list.__doc__)

    def p_type(self, p):
        """type : INTEGER
                | REAL"""
        print(self.p_type.__doc__)

    def p_procedure_list(self, p):
        """procedure_list : procedure_list procedure
                          | empty"""
        print(self.p_procedure_list.__doc__)

    def p_procedure(self, p):
        """procedure : PROCEDURE ID parameters SEMICOLON declarations compound_statement SEMICOLON"""
        print(self.p_procedure.__doc__)

    def p_parameters(self, p):
        """parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS
                      | empty"""
        print(self.p_parameters.__doc__)

    def p_compound_statement(self, p):
        """compound_statement : BEGIN statement_list END"""
        print(self.p_compound_statement.__doc__)

    def p_statement_list(self, p):
        """statement_list : statement
                          | statement_list SEMICOLON statement"""
        print(self.p_statement_list.__doc__)

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
        """statement : IF expression THEN statement ELSE statement
                     | IF expression THEN statement"""
        print(self.p_statement_list.__doc__)

    def p_statement_compound(self, p):
        """statement : compound_statement"""
        print(self.p_statement_compound.__doc__)

    def p_arguments(self, p):
        """arguments : LEFT_PARENTHESIS actual_parameters RIGHT_PARENTHESIS"""
        print(self.p_arguments.__doc__)

    def p_actual_parameters(self, p):
        """actual_parameters : actual_parameter_list
                             | empty"""
        print(self.p_actual_parameters.__doc__)

    def p_actual_parameter_list(self, p):
        """actual_parameter_list : actual_parameter_list COMMA expression
                                 | expression"""
        print(self.p_actual_parameter_list.__doc__)

    def p_expression(self, p):
        """expression : term
                      | expression PLUS term
                      | expression MINUS term"""
        print(self.lexer.current_token, p[1], self.p_expression_term.__doc__)

    def p_expression_term(self, p):
        """term : factor
                | term TIMES factor
                | term DIVIDE factor
                | term DIV factor
                | term MOD factor"""
        print(self.lexer.current_token, p[1], self.p_expression_factor.__doc__)

    def p_expression_factor(self, p):
        """factor : MINUS factor
                  | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
                  | INTEGER_CONSTANT
                  | REAL_CONSTANT
                  | ID"""
        print(self.lexer.current_token, p[1], self.p_expression_factor.__doc__)

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        print("Syntax error at", p.lineno, p.type, p.value)

    def build(self, lexer: PascalLexer, **kwargs):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.engine = ply.yacc.yacc(module=self, **kwargs)

    def parse(self):
        return self.engine.parse(lexer=self.lexer, debug=False)
