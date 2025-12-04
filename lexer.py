# lexer.py — Inp Language Lexer (literals version, clean)

import ply.lex as lex

# ============================
# PALABRAS RESERVADAS
# ============================

reserved = {
'fn': 'FN',
'if': 'IF',
'else': 'ELSE',
'while': 'WHILE',
'for': 'FOR',
'in': 'IN',
'return': 'RETURN',
'true': 'TRUE',
'false': 'FALSE',
'display': 'DISPLAY',
'input': 'INPUT',
'r_int': 'R_INT',
'r_float': 'R_FLOAT',
'r_rn': 'R_RN',
'Int': 'TYPE',
'Float': 'TYPE',
'String': 'TYPE',
'Bool': 'TYPE',
'List': 'TYPE',
'Dict': 'TYPE'
}

# ============================
# LITERALES (NO SERÁN TOKENS)
# ============================
literals = ['+', '-', '*', '/', '=', 
        '<', '>', 
        '(', ')', '{', '}', 
        '[', ']', 
        ',', ';', ':']

# ============================
# TOKENS
# ============================

tokens = [
'ID', 'INT', 'FLOAT', 'STRING',
'DOT',
# operadores de comparación multi-char
'EQ',   # ==
'NE',   # !=
'LE',   # <=
'GE',   # >=
] + list(set(reserved.values()))


# ============================
# IGNORAR ESPACIO, TAB Y RETORNO
# ============================

t_ignore = " \t\r"
t_DOT = r"\."

# ============================
# TOKENS MULTI-CARÁCTER
# ============================

t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='


# ============================
# NÚMEROS
# ============================

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t


# ============================
# STRINGS
# ============================

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t


# ============================
# IDENTIFICADORES Y RESERVED
# ============================

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# ============================
# NEWLINE
# ============================

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# ============================
# COMENTARIOS
# ============================

def t_comment_multiline(t):
    r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    pass

def t_comment_singleline(t):
    r'//.*'
    pass    


# ============================
# ERRORES
# ============================

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()
