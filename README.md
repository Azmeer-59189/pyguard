# PyGuard 🛡️ — Python Code Quality Analyzer

<div align="center">

![PyGuard Banner](https://img.shields.io/badge/PyGuard-Code%20Quality%20Analyzer-e94560?style=for-the-badge&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-e94560?style=flat-square)](LICENSE)

**A static code analysis tool for Python that detects bugs, measures complexity, checks style, and generates detailed PDF reports — via terminal or web dashboard.**

[Features](#features) · [Demo](#demo) · [Installation](#installation) · [Usage](#usage) · [Analysis Types](#analysis-types) · [Web Dashboard](#web-dashboard)

</div>

---

## What is PyGuard?

PyGuard analyzes Python source code and reports on:

- 🐛 **Code issues** — dead code, shadowed variables, deep nesting
- 📊 **Complexity metrics** — cyclomatic complexity, maintainability index, quality score
- 🎨 **Style violations** — PEP 8 compliance checks
- 📄 **PDF reports** — downloadable detailed analysis reports
- 🌐 **Web dashboard** — paste or upload code and analyze in the browser

---

## Features

### 🔍 AST Analysis (Abstract Syntax Tree)
- **Dead code detection** — finds unreachable code after return statements
- **Shadowed variable detection** — warns when inner scope variables shadow outer scope
- **Deep nesting detection** — flags code nested beyond 3 levels (configurable)

### 📈 Complexity Analysis
- **Cyclomatic complexity** — measures how many independent paths exist through code
- **Maintainability index** — industry-standard score for how maintainable code is
- **Code quality score** — overall quality rating

### ✅ PEP 8 Style Checking
- Line length violations
- Whitespace and indentation issues
- Naming convention checks
- Import ordering

### 📄 Reporting
- **Terminal reporter** — colored output directly in the console
- **PDF reporter** — professional downloadable PDF report
- **Web dashboard** — browser-based interface with file upload or paste

---

## Demo

```bash
# Analyze a file in terminal
python src/main.py myfile.py

# Generate PDF report
python src/main.py myfile.py --pdf

# Start web dashboard
python src/web_dashboard.py
# Open http://127.0.0.1:5000
```

---

## Installation

### Prerequisites
- Python 3.12+
- pip

### Steps

```bash
# Clone the repo
git clone https://github.com/Azmeer-59189/pyguard.git
cd pyguard

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
```
astunparse>=1.6.0    # AST unparsing utilities
radon>=6.0.1         # Cyclomatic complexity + maintainability index
tabulate>=0.9.0      # Terminal table formatting
pycodestyle>=2.11.0  # PEP 8 style checking
flask>=3.0.0         # Web dashboard
```

---

## Usage

### Command Line

```bash
# Terminal output
python src/main.py path/to/your_file.py

# PDF report output
python src/main.py path/to/your_file.py --pdf
```

### Web Dashboard

```bash
python src/web_dashboard.py
```

Open **http://127.0.0.1:5000** in your browser. You can:
- **Upload** a `.py` file
- **Paste** code directly into the editor
- View results instantly in the browser
- **Download** a PDF report

---

## Analysis Types

### 1. Dead Code Detection
Finds code that will never execute:
```python
# PyGuard will flag this
def calculate():
    return 42
    print("This never runs")  # ← Dead code detected
```

### 2. Shadowed Variables
Warns when variables hide outer scope names:
```python
x = 10
def my_func():
    x = 20  # ← Shadows outer 'x'
    return x
```

### 3. Deep Nesting
Flags excessively nested code (default max depth: 3):
```python
for i in range(10):
    if condition:
        for j in range(10):
            if other:
                while True:  # ← Deep nesting detected (depth 4)
                    pass
```

### 4. Cyclomatic Complexity
Measures the number of independent paths through code:

| Score | Rating |
|---|---|
| 1–5 | Simple — low risk |
| 6–10 | Moderate — manageable |
| 11–20 | Complex — review recommended |
| 21+ | Very complex — refactor advised |

### 5. Maintainability Index
Industry-standard metric (0–100):

| Score | Rating |
|---|---|
| 80–100 | Highly maintainable |
| 60–79 | Moderately maintainable |
| 40–59 | Difficult to maintain |
| 0–39 | Very difficult — needs refactoring |

---

## Project Structure

```
PyGuard/
├── src/
│   ├── main.py                      # CLI entry point
│   ├── web_dashboard.py             # Flask web interface
│   ├── analyzers/
│   │   ├── ast_analyzer.py          # Dead code, shadowing, nesting
│   │   ├── complexity_analyzer.py   # Cyclomatic complexity, MI score
│   │   └── pep8_analyzer.py         # PEP 8 style checks
│   └── reporters/
│       ├── terminal_reporter.py     # Console output
│       └── pdf_reporter.py          # PDF generation
├── tests/
│   └── sample_code/
│       └── test_file.py             # Sample Python file for testing
├── reports/                         # Generated PDF reports
├── requirements.txt
└── README.md
```

---

## How It Works

```
Python source file
        ↓
   ast.parse()          → builds Abstract Syntax Tree
        ↓
  ASTAnalyzer           → walks tree, detects issues
  ComplexityAnalyzer    → radon calculates CC + MI
  PEP8Analyzer          → pycodestyle checks style
        ↓
  TerminalReporter      → colored console output
  PDFReporter           → downloadable PDF
  Web Dashboard         → Flask + browser UI
```

---

## Sample Output

```
═══════════════════════════════════════
         PyGuard Analysis Report
═══════════════════════════════════════
File: mycode.py

📊 COMPLEXITY METRICS
─────────────────────
Cyclomatic Complexity : 4 (Simple)
Maintainability Index : 73.2 (Good)
Quality Score         : 85/100

🐛 AST ISSUES (2 found)
─────────────────────────
[Line 15] Dead Code      : Unreachable code after return in function "process"
[Line 28] Deep Nesting   : Deep nesting detected at depth 4

🎨 PEP 8 VIOLATIONS (3 found)
──────────────────────────────
[Line 5 ] E501: line too long (89 > 79 characters)
[Line 12] E302: expected 2 blank lines, found 1
[Line 34] W291: trailing whitespace
```

---

## Future Enhancements

- [ ] Support for analyzing entire directories/projects
- [ ] GitHub Actions integration for CI/CD pipelines
- [ ] VS Code extension
- [ ] Comparison between two versions of a file
- [ ] Historical tracking of code quality over time
- [ ] Support for additional languages (JavaScript, TypeScript)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Syed Azmeer**
- Student ID: 59189
- GitHub: [@Azmeer-59189](https://github.com/Azmeer-59189)

---

<div align="center">
Built with ❤️ as a Software Construction university project
</div>
