import ast
from typing import List, Dict, Any


class ASTAnalyzer:
    def __init__(self, source_code: str):
        self.tree = ast.parse(source_code)
        self.issues = []

    def analyze(self) -> List[Dict[str, Any]]:
        self._check_dead_code()
        self._check_shadowed_variables()
        self._check_deep_nesting()
        return self.issues

    def _check_dead_code(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                has_return = False
                for stmt in node.body:
                    if has_return and not isinstance(stmt, ast.Return):
                        self.issues.append({
                            'type': 'Dead Code',
                            'message': f'Unreachable code after return in function "{node.name}"',
                            'line': stmt.lineno
                        })
                        break
                    if isinstance(stmt, ast.Return):
                        has_return = True

    def _check_shadowed_variables(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                outer_names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name) and target.id in outer_names:
                                self.issues.append({
                                    'type': 'Shadowed Variable',
                                    'message': f'Variable "{target.id}" may shadow outer scope variable',
                                    'line': target.lineno
                                })

    def _check_deep_nesting(self, max_depth=3):
        def get_nesting_depth(node, depth=0):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    new_depth = depth + 1
                    if new_depth > max_depth:
                        self.issues.append({
                            'type': 'Deep Nesting',
                            'message': f'Deep nesting detected at depth {new_depth}',
                            'line': getattr(child, 'lineno', 0)
                        })
                    get_nesting_depth(child, new_depth)
                else:
                    get_nesting_depth(child, depth)

        for top_level in ast.iter_child_nodes(self.tree):
            if isinstance(top_level, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                for stmt in top_level.body:
                    if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With)):
                        get_nesting_depth(stmt, 1)