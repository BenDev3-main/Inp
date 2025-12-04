# parser.py — CLEAN version for Inp (compatible with literals)

import ply.yacc as yacc
from lexer import tokens

# ============================
# AST NODES
# ============================

class ProgramNode:
    def __init__(self, statements): self.statements = statements

class BlockNode:
    def __init__(self, statements): self.statements = statements

class VarDeclNode:
    def __init__(self, vtype, name, expr):
        self.vtype = vtype
        self.name = name
        self.expr = expr

class AssignNode:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class DisplayNode:
    def __init__(self, expr): self.expr = expr

class ReturnNode:
    def __init__(self, expr): self.expr = expr

class FunctionDefNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class IfNode:
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block

class WhileNode:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
class ForNode:
    def __init__(self, init, cond, step, body):
        self.init = init
        self.cond = cond
        self.step = step
        self.body = body

class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class LiteralNode:
    def __init__(self, value): self.value = value

class IdentifierNode:
    def __init__(self, name): self.name = name
class ListNode:
    def __init__(self, elements):
        self.elements = elements


class DictNode:
    def __init__(self, pairs):
        self.pairs = pairs


class IndexAccessNode:
    def __init__(self, collection, index):
        self.collection = collection
        self.index = index


class IndexAssignNode:
    def __init__(self, collection, index, expr):
        self.collection = collection
        self.index = index
        self.expr = expr


# ============================
# PROGRAMA
# ============================

def p_program(p):
    "program : statement_list"
    p[0] = ProgramNode(p[1])


def p_statement_list(p):
    """statement_list : statement_list statement
                      | statement"""
    if len(p) == 2: p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]


def p_statement(p):
    """statement : declaration
                 | assignment
                 | function_def
                 | function_call ';'
                 | display_call
                 | return_statement
                 | if_statement
                 | while_statement
                 | for_statement
                 | block"""
    p[0] = p[1]
# ============================
# BLOQUES
# ============================

def p_block(p):
    "block : '{' statement_list '}'"
    p[0] = BlockNode(p[2])


# ============================
# VARIABLES
# ============================

def p_declaration(p):
    "declaration : TYPE ID '=' expression ';'"
    p[0] = VarDeclNode(p[1], p[2], p[4])


def p_assignment(p):
    "assignment : ID '=' expression ';'"
    p[0] = AssignNode(p[1], p[3])


# ============================
# DISPLAY
# ============================

def p_display_call(p):
    "display_call : DISPLAY '(' expression ')' ';'"
    p[0] = DisplayNode(p[3])


# ============================
# RETURN
# ============================

def p_return_statement(p):
    "return_statement : RETURN expression ';'"
    p[0] = ReturnNode(p[2])


# ============================
# FUNCIONES
# ============================

def p_function_def(p):
    "function_def : FN ID '(' params_opt ')' block"
    p[0] = FunctionDefNode(p[2], p[4], p[6])


def p_params_opt(p):
    """params_opt : params
                  | empty"""
    p[0] = p[1] if p[1] else []


def p_params(p):
    """params : TYPE ID
              | params ',' TYPE ID"""
    if len(p) == 3: p[0] = [(p[1], p[2])]
    else:
        p[1].append((p[3], p[4]))
        p[0] = p[1]


def p_function_call(p):
    "function_call : ID '(' args_opt ')'"
    p[0] = FunctionCallNode(p[1], p[3])


def p_args_opt(p):
    """args_opt : args
                | empty"""
    p[0] = p[1] if p[1] else []


def p_args(p):
    """args : expression
            | args ',' expression"""
    if len(p) == 2: p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


# ============================
# IF / ELSE
# ============================

def p_if_statement(p):
    """if_statement : IF '(' expression ')' block
                    | IF '(' expression ')' block ELSE block"""
    if len(p) == 6: p[0] = IfNode(p[3], p[5])
    else: p[0] = IfNode(p[3], p[5], p[7])


# ============================
# WHILE
# ============================

def p_while_statement(p):
    "while_statement : WHILE '(' expression ')' block"
    p[0] = WhileNode(p[3], p[5])


# ============================
# FOR CLÁSICO
# ============================

def p_for_statement(p):
    "for_statement : FOR '(' declaration expression ';' assignment ')' block"
    p[0] = ForNode(p[3], p[4], p[6], p[8])


# ============================
# EXPRESIONES
# ============================

def p_expression_binop(p):
    """expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression EQ expression
                  | expression NE expression
                  | expression '<' expression
                  | expression '>' expression
                  | expression LE expression
                  | expression GE expression"""
    p[0] = BinOpNode(p[1], p[2], p[3])

def p_expression_list(p):
    "expression : LBRACKET list_elements RBRACKET"
    p[0] = ListNode(p[2])

def p_list_elements_multiple(p):
    "list_elements : list_elements COMMA expression"
    p[0] = p[1] + [p[3]]

def p_list_elements_single(p):
    "list_elements : expression"
    p[0] = [p[1]]

def p_list_elements_empty(p):
    "list_elements : "
    p[0] = []
def p_expression_dict(p):
    "expression : LBRACE dict_pairs RBRACE"
    p[0] = DictNode(p[2])

def p_dict_pairs_multiple(p):
    "dict_pairs : dict_pairs COMMA dict_pair"
    p[0] = p[1] + [p[3]]

def p_dict_pairs_single(p):
    "dict_pairs : dict_pair"
    p[0] = [p[1]]

def p_dict_pairs_empty(p):
    "dict_pairs : "
    p[0] = []

def p_dict_pair(p):
    "dict_pair : expression COLON expression"
    p[0] = (p[1], p[2])
    
def p_expression_index_access(p):
    "expression : expression LBRACKET expression RBRACKET"
    p[0] = IndexAccessNode(p[1], p[3])

def p_expression_unary(p):
    """expression : '-' expression
                  | '+' expression"""
    p[0] = UnaryOpNode(p[1], p[2])


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_literal(p):
    """expression : INT
                  | FLOAT
                  | STRING
                  | TRUE
                  | FALSE"""
    p[0] = LiteralNode(p[1])


def p_expression_id(p):
    "expression : ID"
    p[0] = IdentifierNode(p[1])


def p_expression_call(p):
    "expression : function_call"
    p[0] = p[1]


def p_empty(p):
    "empty :"
    pass


def p_error(p):
    if p:
        print(f"[Parser] Error de sintaxis en '{p.value}' (token {p.type})")
    else:
        print("[Parser] Error: fin inesperado del archivo")


parser = yacc.yacc()
