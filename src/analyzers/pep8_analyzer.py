import pycodestyle
from typing import List, Dict, Any
import tempfile
import os


class PEP8Analyzer:
    def __init__(self, source_code: str):
        self.source = source_code

    def analyze(self) -> List[Dict[str, Any]]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(self.source)
            temp_path = f.name

        # Create custom reporter to capture errors
        issues = []
        
        class CaptureReport(pycodestyle.BaseReport):
            def error(self, line_number, offset, text, check):
                code = text[:4]
                message = text[5:]
                issues.append({
                    'file': os.path.basename(temp_path),
                    'line': line_number,
                    'col': offset,
                    'code': code,
                    'message': message
                })
                return super().error(line_number, offset, text, check)

        # Run pycodestyle with custom reporter
        style_guide = pycodestyle.StyleGuide(quiet=True, reporter=CaptureReport)
        style_guide.check_files([temp_path])

        os.unlink(temp_path)
        return issues