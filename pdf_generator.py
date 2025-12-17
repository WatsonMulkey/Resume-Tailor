"""
PDF generation for resumes with professional styling using ReportLab.
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def parse_markdown_to_paragraphs(md_content):
    """Convert markdown to list of (style, text) tuples."""
    lines = md_content.split('\n')
    paragraphs = []
    current_list = []

    for line in lines:
        line = line.rstrip()

        # Skip empty lines
        if not line:
            if current_list:
                paragraphs.extend(current_list)
                current_list = []
            continue

        # H1 header (name)
        if line.startswith('# '):
            text = line[2:].strip()
            paragraphs.append(('h1', text))

        # H2 section headers
        elif line.startswith('## '):
            text = line[3:].strip()
            paragraphs.append(('h2', text))

        # H3 subsection headers
        elif line.startswith('### '):
            text = line[4:].strip()
            paragraphs.append(('h3', text))

        # Bullet points
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Convert markdown bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            current_list.append(('bullet', text))

        # Horizontal rules
        elif line.strip() in ['---', '***', '___']:
            paragraphs.append(('hr', ''))

        # Regular paragraph
        else:
            # Convert markdown bold and italic
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            paragraphs.append(('p', text))

    # Add any remaining list items
    if current_list:
        paragraphs.extend(current_list)

    return paragraphs


def markdown_to_pdf(markdown_file: Path, output_pdf: Path):
    """
    Convert a markdown resume to a professionally styled PDF.

    Args:
        markdown_file: Path to markdown file
        output_pdf: Path for output PDF file
    """
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Create PDF
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles for resume
    styles.add(ParagraphStyle(
        name='ResumeName',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='ContactInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=HexColor('#2563eb'),
        spaceAfter=8,
        spaceBefore=14,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=HexColor('#2563eb'),
        borderPadding=2,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=4,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ResumeBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333'),
        spaceAfter=6,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333'),
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=4,
        leading=13,
        bulletFontName='Helvetica',
        bulletFontSize=8
    ))

    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#999999'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceBefore=20
    ))

    # Parse markdown and build story
    story = []
    paragraphs = parse_markdown_to_paragraphs(md_content)

    is_first_p = True  # Track if this is contact info

    for style_name, text in paragraphs:
        if style_name == 'h1':
            story.append(Paragraph(text, styles['ResumeName']))

        elif style_name == 'h2':
            story.append(Paragraph(text, styles['SectionHeader']))

        elif style_name == 'h3':
            story.append(Paragraph(text, styles['SubsectionHeader']))

        elif style_name == 'bullet':
            story.append(Paragraph(f'• {text}', styles['BulletPoint']))

        elif style_name == 'hr':
            story.append(Spacer(1, 0.1*inch))

        elif style_name == 'p':
            # First paragraph after name is usually contact info
            if is_first_p and not text.startswith('#'):
                story.append(Paragraph(text, styles['ContactInfo']))
                is_first_p = False
            # Last paragraph is usually footer
            elif 'tailored for' in text.lower() or 'this resume' in text.lower():
                story.append(Paragraph(text, styles['Footer']))
            else:
                story.append(Paragraph(text, styles['ResumeBody']))

    # Build PDF
    doc.build(story)

    return output_pdf


if __name__ == '__main__':
    # Quick test
    import sys
    if len(sys.argv) > 1:
        md_file = Path(sys.argv[1])
        pdf_file = md_file.with_suffix('.pdf')
        markdown_to_pdf(md_file, pdf_file)
        print(f"PDF generated: {pdf_file}")
    else:
        print("Usage: python pdf_generator.py <markdown_file>")
