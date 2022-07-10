import src.ply.yacc
from src.lexer import PascalLexer, Token
from src.syntax_tree import Node, BinaryExpression, UnaryExpression, TerminalExpression, Program, Declarations, \
    Declaration, Procedures, Procedure, Parameters, CompoundStatement, AssignmentStatement, WhileStatement, \
    ProcedureCallStatement, IfStatement, IfElseStatement, Arguments, PrintStatement


class PascalParser:
    precedence = (
        ("nonassoc", "RELATIONAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "EQUAL", "NOT_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"),
        ("left", "ADDITIVE", "PLUS", "MINUS", "OR"),
        ("left", "MULTIPLICATIVE", "TIMES", "DIVIDE", "DIV", "MOD", "AND"),
        ("right", "UNARY", "NOT"),
    )

    def __init__(self):
        self.reductions = []

    def log(self, reduction):
        self.reductions.append(reduction)

    def p_program(self, p):
        """program : PROGRAM ID declarations procedures compound_statement"""
        p[0] = Program(p[2], p[3], p[4], p[5])
        self.log(self.p_program.__doc__)

    def p_declarations(self, p):
        """declarations : VAR declaration_list SEMICOLON
                        | empty"""
        if len(p) > 2:
            p[0] = p[2]
            self.log("declarations : VAR declaration_list SEMICOLON")
        else:
            p[0] = Declarations()
            self.log("declarations : empty")

    def p_declaration_list(self, p):
        """declaration_list : declaration_list SEMICOLON declaration
                            | declaration"""
        if len(p) > 2:
            p[0] = p[1]
            p[1].add_children(p[3])
            self.log("declaration_list : declaration_list SEMICOLON declaration")
        else:
            p[0] = Declarations(p[1])
            self.log("declaration_list : declaration")

    def p_declaration(self, p):
        """declaration : identifier_list COLON data_type"""
        p[0] = p[1]
        declaration: Declaration = p[1]
        declaration.set_data_type(p[3])
        self.log(self.p_declaration.__doc__)

    def p_identifier_list(self, p):
        """identifier_list : identifier_list COMMA ID
                           | ID"""
        if len(p) > 2:
            p[0] = p[1]
            p[1].add_identifier(p[3])
            self.log("identifier_list : identifier_list COMMA ID")
        else:
            p[0] = Declaration(p[1])
            self.log("identifier_list : ID")

    def p_data_type(self, p):
        """data_type : INTEGER
                     | REAL"""
        p[0] = p[1]
        self.log(f"type : {p[1].type}")

    def p_procedures(self, p):
        """procedures : procedure_list
                      | empty"""
        if p[1].tag == "empty":
            p[0] = Procedures()
            self.log("procedures : empty")
        else:
            p[0] = p[1]
            self.log("procedures : procedure_list")

    def p_procedure_list(self, p):
        """procedure_list : procedure_list procedure
                          | procedure"""
        if len(p) > 2:
            p[0] = p[1]
            p[1].add_children(p[2])
            self.log("procedure_list : procedure_list procedure")
        else:
            p[0] = Procedures(p[1])
            self.log("procedure_list : procedure")

    def p_procedure(self, p):
        """procedure : PROCEDURE ID parameters SEMICOLON declarations compound_statement SEMICOLON"""
        p[0] = Procedure(p[2], p[3], p[5], p[6])
        self.log(self.p_procedure.__doc__)

    def p_parameters(self, p):
        """parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS
                      | empty"""
        if len(p) > 2:
            p[0] = Parameters(p[2])
            self.log("parameters : LEFT_PARENTHESIS declaration_list RIGHT_PARENTHESIS")
        else:
            p[0] = Parameters(Declarations())
            self.log("parameters : empty")

    def p_compound_statement(self, p):
        """compound_statement : BEGIN statement_list END"""
        p[0] = p[2]
        self.log(self.p_compound_statement.__doc__)

    def p_statement_list(self, p):
        """statement_list : statement_list SEMICOLON statement
                          | statement"""
        if len(p) > 2:
            p[0] = p[1]
            p[1].add_children(p[3])
            self.log("statement_list : statement_list SEMICOLON statement")
        else:
            p[0] = CompoundStatement(p[1])
            self.log("statement_list : statement")

    def p_statement_print(self, p):
        """statement : PRINT LEFT_PARENTHESIS expression RIGHT_PARENTHESIS"""
        p[0] = PrintStatement(p[3])
        self.log(self.p_statement_print.__doc__)

    def p_statement_assignment(self, p):
        """statement : ID ASSIGN expression"""
        p[0] = AssignmentStatement(p[1], p[3])
        self.log(self.p_statement_assignment.__doc__)

    def p_statement_while(self, p):
        """statement : WHILE expression DO statement"""
        p[0] = WhileStatement(p[2], p[4])
        self.log(self.p_statement_while.__doc__)

    def p_statement_procedure_call(self, p):
        """statement : ID arguments"""
        p[0] = ProcedureCallStatement(p[1], p[2])
        self.log(self.p_statement_procedure_call.__doc__)

    def p_statement_if(self, p):
        """statement : IF expression THEN statement"""
        p[0] = IfStatement(p[2], p[4])
        self.log(self.p_statement_if.__doc__)

    def p_statement_if_else(self, p):
        """statement : IF expression THEN statement ELSE statement"""
        p[0] = IfElseStatement(p[2], p[4], p[6])
        self.log(self.p_statement_if_else.__doc__)

    def p_statement_compound(self, p):
        """statement : compound_statement"""
        p[0] = p[1]
        self.log(self.p_statement_compound.__doc__)

    def p_arguments(self, p):
        """arguments : LEFT_PARENTHESIS actual_parameter_list RIGHT_PARENTHESIS
                     | empty"""
        if len(p) > 2:
            p[0] = p[2]
            self.log("arguments : LEFT_PARENTHESIS actual_parameter_list RIGHT_PARENTHESIS")
        else:
            p[0] = Arguments()
            self.log("arguments : empty")

    def p_actual_parameter_list(self, p):
        """actual_parameter_list : actual_parameter_list COMMA expression
                                 | expression"""
        if len(p) > 2:
            p[0] = p[1]
            p[1].add_children(p[3])
            self.log("actual_parameter_list : actual_parameter_list COMMA expression")
        else:
            p[0] = Arguments(p[1])
            self.log("actual_parameter_list : expression")

    def p_expression(self, p):
        """expression : expression additive_operator expression %prec ADDITIVE
                      | expression relational_operator expression %prec RELATIONAL
                      | expression multiplicative_operator expression %prec MULTIPLICATIVE
                      | LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
                      | unary_operator expression %prec UNARY
                      | identifier_or_constant"""
        # p[0] = node = Node("expression")
        if len(p) == 4:
            if isinstance(p[1], Token):  # ( E )
                p[0] = p[2]  # node.children.extend([p[2]])
                self.log("expression : ( expression )")
            else:  # E op E
                p[0] = BinaryExpression(p[2], p[1], p[3])  # node.children.extend([p[1], p[2], p[3]])
                self.log(f"expression : expression {p[2].type} expression")
        elif len(p) == 3:  # op E
            p[0] = UnaryExpression(p[1], p[2])  # node.children.extend([p[1], p[2]])
            self.log(f"expression : unary_operator expression")
        elif len(p) == 2:
            p[0] = p[1]  # node.children.append(p[1])
            self.log(f"expression : identifier_or_constant")

    def p_identifier_or_constant(self, p):
        """identifier_or_constant : INTEGER_CONSTANT
                                  | REAL_CONSTANT
                                  | ID
                                  | TRUE
                                  | FALSE"""
        p[0] = TerminalExpression(p[1])  # Node("identifier_or_constant", leaf=p[1])
        self.log(f"identifier_or_constant : {p[1].type}")

    def p_relational_operator(self, p):
        """relational_operator : LESS_THAN
                               | LESS_THAN_OR_EQUAL
                               | EQUAL
                               | NOT_EQUAL
                               | GREATER_THAN
                               | GREATER_THAN_OR_EQUAL"""
        p[0] = p[1]  # Node("relational_operator", leaf=p[1])
        self.log(f"relational_operator : {p[1].type}")

    def p_additive_operator(self, p):
        """additive_operator : PLUS
                             | MINUS
                             | OR"""
        p[0] = p[1]  # Node("additive_operator", leaf=p[1])
        self.log(f"additive_operator : {p[1].type}")

    def p_multiplicative_operator(self, p):
        """multiplicative_operator : TIMES
                                   | DIVIDE
                                   | DIV
                                   | MOD
                                   | AND"""
        p[0] = p[1]  # Node("multiplicative_operator", leaf=p[1])
        self.log(f"multiplicative_operator : {p[1].type}")

    def p_unary_operator(self, p):
        """unary_operator : PLUS
                          | MINUS
                          | NOT"""
        p[0] = p[1]  # Node("unary_operator", leaf=p[1])
        self.log(f"unary_operator : {p[1].type}")

    def p_empty(self, p):
        """empty :"""

    def p_error(self, p):
        error = f"Syntax error at token {p}"
        self.log(error)
        raise SyntaxError(error)

    def build(self, lexer: PascalLexer, **kwargs):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.engine = src.ply.yacc.yacc(module=self, **kwargs)

    def parse(self, **kwargs):
        return self.engine.parse(lexer=self.lexer, **kwargs)
