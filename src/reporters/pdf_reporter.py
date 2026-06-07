from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List, Dict, Any
import datetime
import os


class PDFReporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, file_path: str, ast_issues: List[Dict],
                       complexity: List[Dict], mi: Dict, quality: Dict, pep8_issues: List[Dict]):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pyguard_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("PyGuard Code Quality Report", title_style))
        story.append(Spacer(1, 20))

        # File Info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=12
        )
        story.append(Paragraph(f"<b>File Analyzed:</b> {file_path}", info_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
        story.append(Spacer(1, 20))

        # Maintainability Index
        mi_color = colors.green if mi['rank'] == 'A' else colors.orange if mi['rank'] == 'B' else colors.red
        story.append(Paragraph(f"<b>Maintainability Index:</b> {mi['score']} (Rank: <font color='{mi_color.hexval()}'>{mi['rank']}</font>)", styles['Heading3']))
        story.append(Spacer(1, 15))

        # Code Quality Score
        q_rank = quality['rank'].split()[0]
        q_color = colors.green if q_rank == 'A' else colors.orange if q_rank == 'B' else colors.red if q_rank == 'C' else colors.HexColor('#8B0000')
        story.append(Paragraph(f"<b>Code Quality Score:</b> {quality['score']}/100 (Rank: <font color='{q_color.hexval()}'>{quality['rank']}</font>)", styles['Heading3']))
        
        if quality['issues']:
            story.append(Paragraph(f"<b>Quality Issues ({len(quality['issues'])} found):</b>", styles['Heading4']))
            q_data = [['Category', 'Severity', 'Message']]
            for issue in quality['issues']:
                q_data.append([issue['category'], issue['severity'], issue['message']])

            q_table = Table(q_data, colWidths=[1.5*inch, 1*inch, 4*inch])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5eef8')]),
            ]))
            story.append(q_table)
        story.append(Spacer(1, 20))

        # Complexity Heatmap
        story.append(Paragraph("<b>Complexity Heatmap</b>", styles['Heading3']))
        if complexity:
            comp_data = [['Function/Method', 'Complexity', 'Rank', 'Line']]
            for c in complexity:
                comp_data.append([
                    c['name'],
                    str(c['complexity']),
                    c['rank'],
                    str(c['lineno'])
                ])

            comp_table = Table(comp_data, colWidths=[3*inch, 1.2*inch, 1.5*inch, 0.8*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8e8e8')]),
            ]))
            story.append(comp_table)
        else:
            story.append(Paragraph("No functions/classes found.", styles['Normal']))
        story.append(Spacer(1, 20))

        # Structural Issues
        story.append(Paragraph(f"<b>Structural Issues ({len(ast_issues)} found)</b>", styles['Heading3']))
        if ast_issues:
            issue_data = [['Type', 'Line', 'Message']]
            for issue in ast_issues:
                issue_data.append([issue['type'], str(issue['line']), issue['message']])

            issue_table = Table(issue_data, colWidths=[1.5*inch, 0.8*inch, 4*inch])
            issue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffe6e6')]),
            ]))
            story.append(issue_table)
        else:
            story.append(Paragraph("No structural issues found.", styles['Normal']))
        story.append(Spacer(1, 20))

        # PEP-8 Violations
        story.append(Paragraph(f"<b>PEP-8 Violations ({len(pep8_issues)} found)</b>", styles['Heading3']))
        if pep8_issues:
            pep8_data = [['Line', 'Column', 'Code', 'Message']]
            for issue in pep8_issues:
                pep8_data.append([
                    str(issue['line']),
                    str(issue['col']),
                    issue['code'],
                    issue['message']
                ])

            pep8_table = Table(pep8_data, colWidths=[0.8*inch, 0.8*inch, 1*inch, 4*inch])
            pep8_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e6f2ff')]),
            ]))
            story.append(pep8_table)
        else:
            story.append(Paragraph("No PEP-8 violations found.", styles['Normal']))

        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph("Generated by PyGuard - Automated Code Quality Analyzer", footer_style))

        doc.build(story)
        print(f"\n PDF Report saved to: {filepath}")
        return filepath