from tabulate import tabulate
from typing import List, Dict, Any
import datetime


class TerminalReporter:
    def __init__(self):
        self.report_data = {}

    def generate_report(self, file_path: str, ast_issues: List[Dict],
                       complexity: List[Dict], mi: Dict, quality: Dict, pep8_issues: List[Dict]):
        import sys
        print('\n' + '=' * 70, flush=True)
        print('PYGUARD CODE QUALITY REPORT', flush=True)
        print(f'File: {file_path}', flush=True)
        print(f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', flush=True)
        print('=' * 70, flush=True)

        print(f'\n MAINTAINABILITY INDEX: {mi["score"]} (Rank: {mi["rank"]})', flush=True)

        # Code Quality Score
        print(f'\n CODE QUALITY SCORE: {quality["score"]}/100 (Rank: {quality["rank"]})', flush=True)
        if quality['issues']:
            print(f'\n QUALITY ISSUES ({len(quality["issues"])} found):', flush=True)
            headers = ['Category', 'Severity', 'Message']
            rows = [[i['category'], i['severity'], i['message']] for i in quality['issues']]
            print(tabulate(rows, headers=headers, tablefmt='grid'), flush=True)

        print('\n COMPLEXITY HEATMAP:', flush=True)
        if complexity:
            headers = ['Function/Class', 'Type', 'Complexity', 'Rank', 'Line']
            rows = [[c['name'], c['type'], c['complexity'], c['rank'], c['lineno']] for c in complexity]
            print(tabulate(rows, headers=headers, tablefmt='grid'), flush=True)
        else:
            print('No functions/classes found.', flush=True)

        print(f'\n STRUCTURAL ISSUES ({len(ast_issues)} found):', flush=True)
        if ast_issues:
            headers = ['Type', 'Line', 'Message']
            rows = [[i['type'], i['line'], i['message']] for i in ast_issues]
            print(tabulate(rows, headers=headers, tablefmt='grid'), flush=True)
        else:
            print('No structural issues found.', flush=True)

        print(f'\n PEP-8 VIOLATIONS ({len(pep8_issues)} found):', flush=True)
        if pep8_issues:
            headers = ['Line', 'Column', 'Code', 'Message']
            rows = [[i['line'], i['col'], i['code'], i['message']] for i in pep8_issues]
            print(tabulate(rows, headers=headers, tablefmt='grid'), flush=True)
        else:
            print('No PEP-8 violations found.', flush=True)

        print('\n' + '=' * 70, flush=True)
        print('END OF REPORT', flush=True)
        print('=' * 70 + '\n', flush=True)