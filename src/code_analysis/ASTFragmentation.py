from code_analysis import AST

fragmentTypes = [
    "FunctionStatement",
    "MethodStatement",
    "PublicMethodStatement",
    "PrivateMethodStatement",
    "ProtectedMethodStatement",
    "AbstractPublicMethodStatement",
    "AbstractProtectedMethodStatement",
    "AbstractPrivateMethodStatement",
    "ClosureExpression"
]


class ASTFragmentation:
    def __init__(self):
        self.__fragments = []

    def fragment(self, ast: AST) -> list:
        self.__fragments = [ast.get_root()]  # Root node is our first fragment
        self.__fragment(ast, ast.get_root())
        return self.__fragments

    def __fragment(self, ast: AST, node: int):
        if ast.get_type(node) in fragmentTypes:  # New fragment found: add to the list and remove edge with parent
            self.__fragments.append(node)
            parents = ast.get_parents(node).copy()
            for p in parents:
                ast.get_children(p).remove(node)
            ast.get_parents(node).clear()
        for c in ast.get_children(node):  # Recursive call
            self.__fragment(ast, c)
