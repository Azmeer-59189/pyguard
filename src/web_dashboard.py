from flask import Flask, render_template_string, request, send_file
import os
import sys
import tempfile
import base64
from pathlib import Path
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzers.ast_analyzer import ASTAnalyzer
from analyzers.complexity_analyzer import ComplexityAnalyzer
from analyzers.pep8_analyzer import PEP8Analyzer
from reporters.pdf_reporter import PDFReporter


app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyGuard - Web Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #0f3460;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 3em;
            color: #e94560;
            text-shadow: 0 0 20px rgba(233, 69, 96, 0.3);
        }
        .header p { color: #a0a0a0; margin-top: 10px; }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }
        .tab-btn {
            background: rgba(255,255,255,0.1);
            color: #e0e0e0;
            border: 2px solid #e94560;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .tab-btn.active {
            background: #e94560;
            color: white;
        }
        .tab-btn:hover:not(.active) { background: rgba(233, 69, 96, 0.3); }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .upload-section, .paste-section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .upload-btn, .analyze-btn {
            background: #e94560;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            margin-top: 15px;
        }
        .upload-btn:hover, .analyze-btn:hover { background: #ff6b6b; transform: translateY(-2px); }
        
        .code-textarea {
            width: 100%;
            min-height: 300px;
            background: rgba(0,0,0,0.3);
            border: 2px solid #0f3460;
            border-radius: 10px;
            color: #e0e0e0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            padding: 15px;
            resize: vertical;
        }
        .code-textarea:focus {
            outline: none;
            border-color: #e94560;
        }
        
        .download-btn {
            background: #2ecc71;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            transition: all 0.3s;
            display: inline-block;
            text-decoration: none;
            margin: 20px 0;
        }
        .download-btn:hover { background: #27ae60; transform: translateY(-2px); }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-card h3 { color: #e94560; margin-bottom: 10px; }
        .metric-value { font-size: 2.5em; font-weight: bold; }
        .rank-a { color: #2ecc71; }
        .rank-b { color: #f39c12; }
        .rank-c { color: #e67e22; }
        .rank-d { color: #e74c3c; }
        .rank-f { color: #8B0000; }
        
        .section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .section h2 {
            color: #e94560;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0f3460;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th {
            background: #0f3460;
            color: #e0e0e0;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        tr:hover { background: rgba(255,255,255,0.03); }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .badge-low { background: #2ecc71; color: white; }
        .badge-moderate { background: #f39c12; color: white; }
        .badge-high { background: #e67e22; color: white; }
        .badge-very-high { background: #e74c3c; color: white; }
        
        .severity-high { border-left: 4px solid #e74c3c; }
        .severity-medium { border-left: 4px solid #f39c12; }
        .severity-low { border-left: 4px solid #3498db; }
        
        .no-issues { color: #2ecc71; font-style: italic; }
        
        .file-input {
            background: rgba(255,255,255,0.1);
            border: 2px dashed #e94560;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
        }
        
        .download-section {
            text-align: center;
            margin: 30px 0;
            padding: 30px;
            background: rgba(46, 204, 113, 0.1);
            border-radius: 15px;
            border: 2px solid #2ecc71;
        }
        
        .error-box {
            background: rgba(231, 76, 60, 0.2);
            border: 2px solid #e74c3c;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 PyGuard</h1>
            <p>Automated Code Quality & Metrics Analyzer</p>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('upload')">📁 Upload File</button>
            <button class="tab-btn" onclick="showTab('paste')">📝 Paste Code</button>
        </div>
        
        <div id="upload-tab" class="tab-content active">
            <div class="upload-section">
                <h2 style="margin-bottom: 20px;">Upload Python File</h2>
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="mode" value="upload">
                    <div class="file-input">
                        <input type="file" name="file" accept=".py" style="margin-bottom: 15px;">
                    </div>
                    <button type="submit" class="upload-btn">Analyze File</button>
                </form>
            </div>
        </div>
        
        <div id="paste-tab" class="tab-content">
            <div class="paste-section">
                <h2 style="margin-bottom: 20px;">Paste Python Code</h2>
                <form method="POST">
                    <input type="hidden" name="mode" value="paste">
                    <textarea name="code" class="code-textarea" placeholder="# Paste your Python code here...
# Example:
def hello():
    print('Hello World')"></textarea>
                    <button type="submit" class="analyze-btn">Analyze Code</button>
                </form>
            </div>
        </div>
        
        {% if error %}
        <div class="error-box">
            <h3>❌ Error</h3>
            <p>{{ error }}</p>
        </div>
        {% endif %}
        
        {% if results %}
        <div class="download-section">
            <h3 style="margin-bottom: 15px; color: #2ecc71;">Analysis Complete! 📊</h3>
            <form method="POST" action="/download_pdf">
                <input type="hidden" name="source_code_b64" value="{{ source_code_b64 }}">
                <input type="hidden" name="filename" value="{{ filename }}">
                <button type="submit" class="download-btn">📥 Download PDF Report</button>
            </form>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Maintainability Index</h3>
                <div class="metric-value rank-{{ results.mi.rank.lower().split(' ')[0] }}">{{ results.mi.score }}</div>
                <p>Rank: {{ results.mi.rank }}</p>
            </div>
            <div class="metric-card">
                <h3>Code Quality Score</h3>
                <div class="metric-value rank-{{ results.quality.rank.lower().split(' ')[0] }}">{{ results.quality.score }}</div>
                <p>Rank: {{ results.quality.rank }}</p>
            </div>
            <div class="metric-card">
                <h3>Functions Analyzed</h3>
                <div class="metric-value">{{ results.complexity|length }}</div>
            </div>
            <div class="metric-card">
                <h3>Total Issues</h3>
                <div class="metric-value" style="color: #e74c3c;">{{ results.total_issues }}</div>
            </div>
        </div>
        
        {% if results.quality.issues %}
        <div class="section">
            <h2>⚠️ Quality Issues</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th>Severity</th>
                    <th>Message</th>
                </tr>
                {% for issue in results.quality.issues %}
                <tr class="severity-{{ issue.severity.lower() }}">
                    <td><strong>{{ issue.category }}</strong></td>
                    <td>{{ issue.severity }}</td>
                    <td>{{ issue.message }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>🔥 Complexity Heatmap</h2>
            {% if results.complexity %}
            <table>
                <tr>
                    <th>Function/Method</th>
                    <th>Complexity</th>
                    <th>Rank</th>
                    <th>Line</th>
                </tr>
                {% for c in results.complexity %}
                <tr>
                    <td>{{ c.name }}</td>
                    <td>{{ c.complexity }}</td>
                    <td>
                        {% if 'A' in c.rank %}
                        <span class="badge badge-low">{{ c.rank }}</span>
                        {% elif 'B' in c.rank %}
                        <span class="badge badge-moderate">{{ c.rank }}</span>
                        {% elif 'C' in c.rank %}
                        <span class="badge badge-high">{{ c.rank }}</span>
                        {% else %}
                        <span class="badge badge-very-high">{{ c.rank }}</span>
                        {% endif %}
                    </td>
                    <td>{{ c.lineno }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p class="no-issues">No functions found.</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>🔍 Structural Issues</h2>
            {% if results.ast_issues %}
            <table>
                <tr>
                    <th>Type</th>
                    <th>Line</th>
                    <th>Message</th>
                </tr>
                {% for issue in results.ast_issues %}
                <tr class="severity-{{ 'high' if issue.type == 'Dead Code' else 'medium' }}">
                    <td><strong>{{ issue.type }}</strong></td>
                    <td>{{ issue.line }}</td>
                    <td>{{ issue.message }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p class="no-issues">No structural issues found! ✅</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>📏 PEP-8 Violations</h2>
            {% if results.pep8_issues %}
            <table>
                <tr>
                    <th>Line</th>
                    <th>Column</th>
                    <th>Code</th>
                    <th>Message</th>
                </tr>
                {% for issue in results.pep8_issues %}
                <tr>
                    <td>{{ issue.line }}</td>
                    <td>{{ issue.col }}</td>
                    <td><code>{{ issue.code }}</code></td>
                    <td>{{ issue.message }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p class="no-issues">No PEP-8 violations found! ✅</p>
            {% endif %}
        </div>
        {% endif %}
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""


def analyze_code(source_code, filename):
    """Run all analyzers and return results"""
    try:
        ast_analyzer = ASTAnalyzer(source_code)
        ast_issues = ast_analyzer.analyze()
    except SyntaxError as e:
        return None, f"Syntax Error in your code: {str(e)}"

    complexity_analyzer = ComplexityAnalyzer(source_code)
    complexity = complexity_analyzer.get_cyclomatic_complexity()
    mi = complexity_analyzer.get_maintainability_index()
    quality = complexity_analyzer.get_code_quality_score()

    pep8_analyzer = PEP8Analyzer(source_code)
    pep8_issues = pep8_analyzer.analyze()

    total_issues = len(ast_issues) + len(quality['issues']) + len(pep8_issues)

    results = {
        'ast_issues': ast_issues,
        'complexity': complexity,
        'mi': mi,
        'quality': quality,
        'pep8_issues': pep8_issues,
        'total_issues': total_issues
    }
    
    return results, None


@app.route('/', methods=['GET', 'POST'])
def dashboard():
    results = None
    error = None
    source_code = ""
    filename = "pasted_code.py"
    source_code_b64 = ""
    
    if request.method == 'POST':
        mode = request.form.get('mode', 'upload')
        
        if mode == 'upload':
            file = request.files.get('file')
            if file and file.filename.endswith('.py'):
                source_code = file.read().decode('utf-8')
                filename = file.filename
        elif mode == 'paste':
            source_code = request.form.get('code', '')
            filename = "pasted_code.py"
        
        if source_code:
            results, error = analyze_code(source_code, filename)
            if results:
                # Encode source code safely for form transmission
                source_code_b64 = base64.b64encode(source_code.encode('utf-8')).decode('ascii')

    return render_template_string(HTML_TEMPLATE, results=results, 
                                error=error,
                                source_code_b64=source_code_b64,
                                filename=filename)


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    source_code_b64 = request.form.get('source_code_b64', '')
    filename = request.form.get('filename', 'code.py')
    
    if not source_code_b64:
        return "No code to analyze", 400
    
    # Decode the base64 source code
    try:
        source_code = base64.b64decode(source_code_b64).decode('utf-8')
    except Exception as e:
        return f"Error decoding code: {str(e)}", 400
    
    # Run analysis
    results, error = analyze_code(source_code, filename)
    if error:
        return error, 400
    
    # Generate PDF to temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        reporter = PDFReporter(output_dir=tmpdir)
        report_path = reporter.generate_report(
            filename,
            results['ast_issues'],
            results['complexity'],
            results['mi'],
            results['quality'],
            results['pep8_issues']
        )
        
        # Read PDF into memory
        with open(report_path, 'rb') as f:
            pdf_data = f.read()
        
        # Create in-memory file for download
        pdf_buffer = BytesIO(pdf_data)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'pyguard_report_{filename.replace(".py", "")}.pdf'
        )


if __name__ == '__main__':
    print("Starting PyGuard Web Dashboard...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)