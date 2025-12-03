# main.py — Runtime oficial de Inp v1

from lexer import lexer
from parser import parser
from interpreter import Interpreter

import sys

def run_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filename}'")
        return

    # 1. Parsear
    ast = parser.parse(code, lexer=lexer)

    if not ast:
        print("Error: no se pudo generar el AST")
        return

    # 2. Ejecutar
    interp = Interpreter()
    interp.run(ast)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python main.py archivo.inp")
        sys.exit(1)

    run_file(sys.argv[1])
