"""
PDF generation for resumes with professional styling using ReportLab.
Matches the HTML template design with two-column layout and modern styling.
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
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


def generate_pdf_from_data(resume_data: dict, output_pdf: Path):
    """
    Generate PDF resume with two-column layout matching HTML design.
    Uses structured data format (same as HTML generator).

    Args:
        resume_data: Dictionary with resume sections (name, title, contact_info,
                     experience, education, achievements, skills, certifications)
        output_pdf: Path for output PDF file
    """
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch
    )

    # Define custom styles matching HTML design (with Dec 18 UX optimizations)
    styles = getSampleStyleSheet()

    # Name style (34pt, bold, black) - Updated from 28pt per UX optimization
    styles.add(ParagraphStyle(
        name='Resume2Name',  # Unique name to avoid conflicts
        parent=styles['Heading1'],
        fontSize=34,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=4,
        spaceBefore=0,
        fontName='Helvetica-Bold',
        leading=37,  # line-height: 1.1
        alignment=TA_LEFT
    ))

    # Title style (13pt, blue, bold)
    styles.add(ParagraphStyle(
        name='Resume2Title',
        parent=styles['Normal'],
        fontSize=13,
        textColor=HexColor('#2563EB'),
        spaceAfter=6,
        fontName='Helvetica-Bold',
        leading=16,  # line-height: 1.2
        alignment=TA_LEFT
    ))

    # Contact info (9.5pt, gray)
    styles.add(ParagraphStyle(
        name='Resume2Contact',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=HexColor('#666666'),
        spaceAfter=10,
        leading=12,  # line-height: 1.3
        alignment=TA_LEFT
    ))

    # Section headers (11pt, bold, uppercase)
    styles.add(ParagraphStyle(
        name='Resume2Section',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=3,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        leading=13,
        alignment=TA_LEFT
    ))

    # Job title (10.5pt, bold)
    styles.add(ParagraphStyle(
        name='Resume2JobTitle',
        parent=styles['Normal'],
        fontSize=10.5,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=2,
        fontName='Helvetica-Bold',
        leading=14,  # line-height: 1.3
        alignment=TA_LEFT
    ))

    # Company name (10pt, blue, bold)
    styles.add(ParagraphStyle(
        name='Resume2Company',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#2563EB'),
        spaceAfter=2,
        fontName='Helvetica-Bold',
        leading=12,
        alignment=TA_LEFT
    ))

    # Job meta (9pt, italic, gray)
    styles.add(ParagraphStyle(
        name='Resume2Meta',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#777777'),
        spaceAfter=6,
        fontName='Helvetica-Oblique',
        leading=11,
        alignment=TA_LEFT
    ))

    # Bullet points (9.5pt) - Optimized spacing
    styles.add(ParagraphStyle(
        name='Resume2Bullet',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=HexColor('#333333'),
        spaceAfter=3,  # Tightened from 5px per UX optimization
        leftIndent=0,
        leading=14,  # line-height: 1.4
        alignment=TA_LEFT
    ))

    # Achievement title (10pt, bold)
    styles.add(ParagraphStyle(
        name='Resume2AchTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=4,
        fontName='Helvetica-Bold',
        leading=12,
        alignment=TA_LEFT
    ))

    # Achievement description (9.5pt)
    styles.add(ParagraphStyle(
        name='Resume2AchDesc',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=HexColor('#555555'),
        spaceAfter=12,
        leading=14,  # line-height: 1.5
        alignment=TA_LEFT
    ))

    # Skill item (9.5pt)
    styles.add(ParagraphStyle(
        name='Resume2Skill',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=HexColor('#333333'),
        spaceAfter=4,
        leading=13,
        alignment=TA_LEFT
    ))

    # Cert title (10pt, blue, bold)
    styles.add(ParagraphStyle(
        name='Resume2CertTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#2563EB'),
        spaceAfter=2,
        fontName='Helvetica-Bold',
        leading=12,
        alignment=TA_LEFT
    ))

    # Cert description (9pt)
    styles.add(ParagraphStyle(
        name='Resume2CertDesc',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#555555'),
        spaceAfter=10,
        leading=11,  # line-height: 1.3
        alignment=TA_LEFT
    ))

    # Build document story (simple single-column layout)
    story = []

    # Header section with horizontal line
    story.append(Paragraph(resume_data.get('name', 'M. WATSON MULKEY'), styles['Resume2Name']))
    story.append(Paragraph(resume_data.get('title', 'Senior Product Manager'), styles['Resume2Title']))
    story.append(Paragraph(resume_data.get('contact_info', ''), styles['Resume2Contact']))

    # Horizontal line separator (3px solid blue border)
    line_table = Table([['']], colWidths=[7*inch])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 3, HexColor('#2563EB')),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 8))

    # Experience section
    story.append(Paragraph('EXPERIENCE', styles['Resume2Section']))
    divider = Table([['']], colWidths=[7*inch])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, HexColor('#e0e0e0')),
    ]))
    story.append(divider)
    story.append(Spacer(1, 8))

    # Company colors matching HTML
    colors = ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#8B5CF6']

    for i, job in enumerate(resume_data.get('experience', [])):
        color = colors[i % len(colors)]
        icon_text = f'<font color="{color}">■</font> '

        if job.get('title'):
            story.append(Paragraph(icon_text + job['title'], styles['Resume2JobTitle']))
        if job.get('company'):
            story.append(Paragraph(job['company'], styles['Resume2Company']))

        meta_parts = []
        if job.get('dates'):
            meta_parts.append(job['dates'])
        if job.get('location'):
            meta_parts.append(job['location'])
        if meta_parts:
            story.append(Paragraph(' • '.join(meta_parts), styles['Resume2Meta']))

        for bullet in job.get('bullets', []):
            bullet_text = f'<font color="#2563EB">▪</font> {bullet}'
            story.append(Paragraph(bullet_text, styles['Resume2Bullet']))

        story.append(Spacer(1, 10))

    # Achievements section
    story.append(Spacer(1, 4))
    story.append(Paragraph('HEADLINE ACHIEVEMENTS', styles['Resume2Section']))
    divider2 = Table([['']], colWidths=[7*inch])
    divider2.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, HexColor('#e0e0e0')),
    ]))
    story.append(divider2)
    story.append(Spacer(1, 8))

    symbols = ['★', '▶', '●']
    for i, ach in enumerate(resume_data.get('achievements', [])):
        symbol = symbols[i % len(symbols)]
        icon_text = f'<font color="#2563EB">{symbol}</font> '

        if ach.get('title'):
            story.append(Paragraph(icon_text + ach['title'], styles['Resume2AchTitle']))
        if ach.get('description'):
            story.append(Paragraph(ach['description'], styles['Resume2AchDesc']))

    # Skills section
    story.append(Spacer(1, 4))
    story.append(Paragraph('SKILLS', styles['Resume2Section']))
    divider3 = Table([['']], colWidths=[7*inch])
    divider3.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, HexColor('#e0e0e0')),
    ]))
    story.append(divider3)
    story.append(Spacer(1, 8))

    for skill in resume_data.get('skills', []):
        skill_text = f'<font color="#2563EB">│</font> {skill}'
        story.append(Paragraph(skill_text, styles['Resume2Skill']))

    # Education section
    story.append(Spacer(1, 4))
    story.append(Paragraph('EDUCATION', styles['Resume2Section']))
    divider4 = Table([['']], colWidths=[7*inch])
    divider4.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, HexColor('#e0e0e0')),
    ]))
    story.append(divider4)
    story.append(Spacer(1, 8))

    edu = resume_data.get('education', {})
    if edu:
        if edu.get('degree'):
            story.append(Paragraph(edu['degree'], styles['Resume2JobTitle']))
        if edu.get('school'):
            story.append(Paragraph(edu['school'], styles['Resume2Company']))
        if edu.get('dates'):
            story.append(Paragraph(edu['dates'], styles['Resume2Meta']))

    # Certifications section
    story.append(Spacer(1, 8))
    story.append(Paragraph('CERTIFICATIONS', styles['Resume2Section']))
    divider5 = Table([['']], colWidths=[7*inch])
    divider5.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, HexColor('#e0e0e0')),
    ]))
    story.append(divider5)
    story.append(Spacer(1, 8))

    for cert in resume_data.get('certifications', []):
        if cert.get('title'):
            story.append(Paragraph(cert['title'], styles['Resume2CertTitle']))
        if cert.get('description'):
            story.append(Paragraph(cert['description'], styles['Resume2CertDesc']))

    # Build PDF
    doc.build(story)

    return output_pdf


def generate_cover_letter_pdf(markdown_file: Path, output_pdf: Path):
    """
    Generate professional cover letter PDF with proper formatting.

    Watson's requirements:
    - Contact info bold and left-aligned at top
    - No centered name heading (redundant)
    - Letter positioned higher on page

    Args:
        markdown_file: Path to markdown file
        output_pdf: Path for output PDF file
    """
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Create PDF with more top margin to position letter higher
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1.25*inch,  # More space at top
        bottomMargin=0.75*inch
    )

    # Define styles
    styles = getSampleStyleSheet()

    # Contact info - bold, left-aligned, at top
    styles.add(ParagraphStyle(
        name='CoverLetterContact',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#1a1a1a'),
        fontName='Helvetica-Bold',  # Bold
        alignment=TA_LEFT,  # Left-aligned
        spaceAfter=16,
        leading=14
    ))

    # Letter body paragraphs
    styles.add(ParagraphStyle(
        name='CoverLetterBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        leading=16,
        alignment=TA_LEFT
    ))

    # Greeting and closing
    styles.add(ParagraphStyle(
        name='CoverLetterGreeting',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        leading=16,
        alignment=TA_LEFT
    ))

    # Parse content and build story
    lines = md_content.strip().split('\n')
    story = []

    # Skip first line if it's just the name (redundant)
    start_idx = 0
    if lines and not '@' in lines[0] and not 'linkedin' in lines[0].lower():
        start_idx = 1  # Skip name line

    # Extract contact info (lines with @ or linkedin)
    contact_lines = []
    body_start = start_idx

    for i in range(start_idx, min(start_idx + 3, len(lines))):
        if i < len(lines):
            line = lines[i].strip()
            if '@' in line or 'linkedin' in line.lower() or any(c.isdigit() for c in line):
                contact_lines.append(line)
                body_start = i + 1
            elif line:  # Hit non-contact content
                break

    # Add contact info as bold header
    if contact_lines:
        contact_text = '<br/>'.join(contact_lines)
        story.append(Paragraph(contact_text, styles['CoverLetterContact']))

    # Add rest of letter
    for i in range(body_start, len(lines)):
        line = lines[i].strip()
        if not line:
            continue

        # Convert markdown bold
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)

        story.append(Paragraph(line, styles['CoverLetterBody']))

    # Build PDF
    doc.build(story)
    return output_pdf


def markdown_to_pdf(markdown_file: Path, output_pdf: Path):
    """
    Convert a markdown resume to a professionally styled PDF.

    DEPRECATED for cover letters - use generate_cover_letter_pdf() instead.

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
