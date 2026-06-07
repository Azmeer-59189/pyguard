import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzers.ast_analyzer import ASTAnalyzer
from analyzers.complexity_analyzer import ComplexityAnalyzer
from analyzers.pep8_analyzer import PEP8Analyzer
from reporters.terminal_reporter import TerminalReporter
from reporters.pdf_reporter import PDFReporter


class PyGuard:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')

        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.source_code = f.read()

    def analyze(self, output_format='terminal'):
        ast_analyzer = ASTAnalyzer(self.source_code)
        ast_issues = ast_analyzer.analyze()

        complexity_analyzer = ComplexityAnalyzer(self.source_code)
        complexity = complexity_analyzer.get_cyclomatic_complexity()
        mi = complexity_analyzer.get_maintainability_index()
        quality = complexity_analyzer.get_code_quality_score()

        pep8_analyzer = PEP8Analyzer(self.source_code)
        pep8_issues = pep8_analyzer.analyze()

        if output_format == 'pdf':
            reporter = PDFReporter()
            reporter.generate_report(
                str(self.file_path),
                ast_issues,
                complexity,
                mi,
                quality,
                pep8_issues
            )
        else:
            reporter = TerminalReporter()
            reporter.generate_report(
                str(self.file_path),
                ast_issues,
                complexity,
                mi,
                quality,
                pep8_issues
            )


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py <path_to_python_file> [--pdf]')
        sys.exit(1)

    file_path = sys.argv[1]
    output_format = 'terminal'
    
    if '--pdf' in sys.argv:
        output_format = 'pdf'

    try:
        pyguard = PyGuard(file_path)
        pyguard.analyze(output_format=output_format)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()