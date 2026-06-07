from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
from typing import List, Dict, Any
import ast


class ComplexityAnalyzer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.tree = ast.parse(source_code)

    def get_cyclomatic_complexity(self) -> List[Dict[str, Any]]:
        results = cc_visit(self.source)
        complexity_data = []
        for item in results:
            if item.__class__.__name__ != 'Class':
                complexity_data.append({
                    'name': item.name,
                    'type': 'function',
                    'complexity': item.complexity,
                    'rank': self._get_rank(item.complexity),
                    'lineno': item.lineno
                })
        return complexity_data

    def get_maintainability_index(self) -> Dict[str, Any]:
        mi_score = mi_visit(self.source, multi=True)
        return {
            'score': round(mi_score, 2),
            'rank': 'A' if mi_score > 85 else 'B' if mi_score > 70 else 'C' if mi_score > 50 else 'D'
        }

    def get_code_quality_score(self) -> Dict[str, Any]:
        """Calculate overall code quality based on multiple factors"""
        score = 100
        issues = []

        # Check 1: Global variables usage
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Global):
                score -= 15
                issues.append({
                    'category': 'Globals',
                    'message': 'Using global variables makes code unpredictable',
                    'severity': 'High'
                })
                break

        # Check 2: Single letter variable names
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and len(node.id) == 1 and node.id.islower():
                if node.id not in ['i', 'j', 'k', 'x', 'y', 'z']:
                    continue
                score -= 5
                issues.append({
                    'category': 'Naming',
                    'message': f'Single letter variable "{node.id}" is not descriptive',
                    'severity': 'Medium'
                })
                break

        # Check 3: Missing type hints
        func_count = 0
        typed_func_count = 0
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_count += 1
                if node.returns or any(
                    isinstance(arg, ast.arg) and arg.annotation 
                    for arg in node.args.args + node.args.kwonlyargs
                ):
                    typed_func_count += 1
        
        if func_count > 0 and typed_func_count == 0:
            score -= 10
            issues.append({
                'category': 'Type Safety',
                'message': 'No type hints found - code is harder to maintain',
                'severity': 'Medium'
            })

        # Check 4: Missing docstrings
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    score -= 3
                    issues.append({
                        'category': 'Documentation',
                        'message': f'Function "{node.name}" missing docstring',
                        'severity': 'Low'
                    })
                    break

        # Check 5: Bare except clauses
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    score -= 15
                    issues.append({
                        'category': 'Error Handling',
                        'message': 'Bare except clause catches all errors silently',
                        'severity': 'High'
                    })
                    break

        # Check 6: String concatenation instead of f-strings
        for node in ast.walk(self.tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    if isinstance(node.right, ast.Call) and isinstance(node.right.func, ast.Name) and node.right.func.id == 'str':
                        score -= 5
                        issues.append({
                            'category': 'Style',
                            'message': 'Use f-strings instead of str() concatenation',
                            'severity': 'Low'
                        })
                        break

        # Check 7: Using list instead of tuple for constants
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.List):
                    score -= 3
                    issues.append({
                        'category': 'Performance',
                        'message': 'Use tuple for immutable constant data',
                        'severity': 'Low'
                    })
                    break

        # Check 8: No error handling in risky operations
        has_try = any(isinstance(node, ast.Try) for node in ast.walk(self.tree))
        has_raise = any(isinstance(node, ast.Raise) for node in ast.walk(self.tree))
        
        if not has_try and not has_raise:
            score -= 5
            issues.append({
                'category': 'Robustness',
                'message': 'No error handling found - add try/except for safety',
                'severity': 'Medium'
            })

        # Deduplicate issues
        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue['category'], issue['message'])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        final_score = max(0, score)
        
        if final_score >= 85:
            rank = 'A (Excellent)'
        elif final_score >= 70:
            rank = 'B (Good)'
        elif final_score >= 50:
            rank = 'C (Average)'
        elif final_score >= 30:
            rank = 'D (Poor)'
        else:
            rank = 'F (Critical)'

        return {
            'score': final_score,
            'rank': rank,
            'issues': unique_issues
        }

    def _get_rank(self, complexity: int) -> str:
        if complexity <= 5:
            return 'A (Low)'
        elif complexity <= 10:
            return 'B (Moderate)'
        elif complexity <= 20:
            return 'C (High)'
        else:
            return 'D (Very High)'