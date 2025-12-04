# interpreter.py — Intérprete oficial de Inp v1

class Environment:
    """Tabla de símbolos con soporte para scopes anidados."""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Variable '{name}' no está definida")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise Exception(f"Variable '{name}' no está definida")

    def declare(self, name, value):
        if name in self.vars:
            raise Exception(f"Variable '{name}' ya existe en este scope")
        self.vars[name] = value


class ReturnSignal(Exception):
    """Se usa para cortar ejecución interna de una función."""
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}

    # =========================
    # EJECUCIÓN DEL PROGRAMA
    # =========================
    def run(self, program):
        try:
            self.exec_block(program.statements, self.global_env)
        except ReturnSignal:
            raise Exception("ERROR: 'return' espera estar dentro de una función.")

    # =========================
    # BLOQUES
    # =========================
    def exec_block(self, statements, env):
        for stmt in statements:
            self.exec(stmt, env)

    # =========================
    # EJECUCIÓN DE NODOS
    # =========================
    def exec(self, node, env):

        from parser import (
            VarDeclNode, AssignNode, DisplayNode,
            FunctionDefNode, IfNode, WhileNode,
            ForNode, ReturnNode, BlockNode, FunctionCallNode, ListNode,
            DictNode, IndexAccessNode, IndexAssignNode
        )

        # Declaración de variable
        if isinstance(node, VarDeclNode):
            value = self.eval(node.expr, env)
            env.declare(node.name, value)
            return

        # Asignación
        if isinstance(node, AssignNode):
            value = self.eval(node.expr, env)
            env.set(node.name, value)
            return

        # display(expr)
        if isinstance(node, DisplayNode):
            value = self.eval(node.expr, env)
            print(value)
            return

        # return
        if isinstance(node, ReturnNode):
            value = self.eval(node.expr, env)
            raise ReturnSignal(value)

        # función definida por el usuario
        if isinstance(node, FunctionDefNode):
            self.functions[node.name] = node
            return

        # if
        if isinstance(node, IfNode):
            cond = self.eval(node.cond, env)
            if cond:
                self.exec(node.then_block, Environment(env))
            elif node.else_block:
                self.exec(node.else_block, Environment(env))
            return

        # while
        if isinstance(node, WhileNode):
            while self.eval(node.cond, env):
                try:
                    self.exec(node.body, Environment(env))
                except ReturnSignal as r:
                    raise r
            return

        # for clásico
        if isinstance(node, ForNode):
            # init
            self.exec(node.init, env)

            while self.eval(node.cond, env):
                try:
                    self.exec(node.body, Environment(env))
                except ReturnSignal as r:
                    raise r

                self.exec(node.step, env)
            return

        # bloque
        if isinstance(node, BlockNode):
            self.exec_block(node.statements, Environment(env))
            return

        # llamada a función como statement
        if isinstance(node, FunctionCallNode):
            self.call_function(node, env)
            return
        if isinstance(node, ListNode):
            return [self.visit(e) for e in node.elements]
        if isinstance(node, DictNode):
            result = {}
            for key_node, value_node in node.pairs:
                key = self.visit(key_node)
                value = self.visit(value_node)
                result[key] = value
            return result
        if isinstance(node, IndexAccessNode):
            collection = self.visit(node.collection)
            index = self.visit(node.index)

            if isinstance(collection, list):
                if not isinstance(index, int):
                    raise Exception("Error: índice de lista debe ser Int.")
                try:
                    return collection[index]
                except:
                    raise Exception("Error: índice fuera de rango.")

            if isinstance(collection, dict):
                if index not in collection:
                    raise Exception(f"Error: clave '{index}' no existe.")
                return collection[index]

            raise Exception("No se puede indexar este tipo.")
        if isinstance(node, IndexAssignNode):
            collection = self.visit(node.collection)
            index = self.visit(node.index)
            value = self.visit(node.expr)

            if isinstance(collection, list):
                if not isinstance(index, int):
                    raise Exception("Índice de lista debe ser Int.")
                try:
                    collection[index] = value
                    return value
                except:
                    raise Exception("Índice fuera de rango.")

            if isinstance(collection, dict):
                collection[index] = value
                return value

            raise Exception("No se puede asignar índices en este tipo.")


        raise Exception(f"I can't evalue this node: {type(node)}")

    # =========================
    # LLAMADAS A FUNCIONES
    # =========================
    def call_function(self, node, env):

        if node.name not in self.functions:
            raise Exception(f"Function '{node.name}' doesn't exist.")

        fn = self.functions[node.name]

        # nuevo entorno local
        local = Environment(self.global_env)

        # parámetros
        if len(fn.params) != len(node.args):
            raise Exception(f"Function '{fn.name}' expects {len(fn.params)} arguments.")

        for (ptype, pname), arg_expr in zip(fn.params, node.args):
            local.declare(pname, self.eval(arg_expr, env))

        # ejecutar cuerpo
        try:
            self.exec(fn.body, local)
            return None  # si no hay return
        except ReturnSignal as r:
            return r.value

    # =========================
    # EVALUACIÓN DE EXPRESIONES
    # =========================
    def eval(self, node, env):

        from parser import (
            LiteralNode, IdentifierNode, BinOpNode, UnaryOpNode, FunctionCallNode
        )

        if isinstance(node, LiteralNode):
            return node.value

        if isinstance(node, IdentifierNode):
            return env.get(node.name)

        # llamados a función como expresión
        if isinstance(node, FunctionCallNode):
            return self.call_function(node, env)

        # operaciones binarias
        if isinstance(node, BinOpNode):
            left = self.eval(node.left, env)
            right = self.eval(node.right, env)
            op = node.op

            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '<': return left < right
            if op == '>': return left > right
            if op == '<=': return left <= right
            if op == '>=': return left >= right

            raise Exception(f"Unknown operator: {op}")

        # unarios
        if isinstance(node, UnaryOpNode):
            val = self.eval(node.expr, env)
            if node.op == '-': return -val
            if node.op == '+': return +val

        raise Exception(f"I cant't evalue: {type(node)}")
