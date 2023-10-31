#!/usr/bin/env python3

import ast
import os

class CheckVisitor(ast.NodeVisitor):

    def visit_Name(self,node):
        if node.id not in ['a', 'b']:
            raise ValueError(f"accessing {node.id} is not allowed" )
        ast.NodeVisitor.generic_visit(self, node)

    def generic_visit(self, node):
        if not (isinstance(node, ast.Module) or\
                isinstance(node, ast.Expr) or\
                isinstance(node, ast.BinOp) or\
                isinstance(node, ast.Add) or\
                isinstance(node, ast.Sub) or\
                isinstance(node, ast.Div) or\
                isinstance(node, ast.Mult) or\
                isinstance(node, ast.Load) or\
                isinstance(node, ast.Name) or\
                isinstance(node, ast.Constant)):
            raise ValueError(f"node {type(node)} is not allowed" )
        ast.NodeVisitor.generic_visit(self, node)


def main():
    code = input()

    visitor = CheckVisitor()
    visitor.visit(ast.parse(code))

    for a in range(256):
        assert (a ^ 42) == int(eval(code))

    print(os.getenv("FLAG"))


if __name__ == "__main__":
    main()
