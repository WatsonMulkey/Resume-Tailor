"""
Advanced PDF generation for resumes with two-column layout and professional styling.
Matches the style of Watson's original resume.
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Frame, PageTemplate, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io


class SectionDivider(Flowable):
    """Horizontal line divider for sections."""
    def __init__(self, width, color=HexColor('#000000'), thickness=2):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


class CompanyIcon(Flowable):
    """Colored box icon for company."""
    def __init__(self, color, size=20):
        Flowable.__init__(self)
        self.color = color
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.size, self.size, fill=1, stroke=0)


def create_two_column_resume(markdown_file: Path, output_pdf: Path):
    """
    Create a two-column resume PDF matching Watson's original style.

    Left column: Experience, Education
    Right column: Achievements, Skills, Certifications
    """
    # Read markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Parse content
    sections = parse_resume_sections(md_content)

    # Create PDF with custom page template
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # Define styles
    styles = create_resume_styles()

    # Build story
    story = []

    # Header section (full width)
    story.extend(build_header(sections.get('header', {}), styles))

    # Create two-column layout
    # Split content between left and right columns
    left_content = []
    right_content = []

    # Left column: Experience, Education
    if 'experience' in sections:
        left_content.extend(build_experience_section(sections['experience'], styles))

    if 'education' in sections:
        left_content.extend(build_education_section(sections['education'], styles))

    # Right column: Achievements, Skills, Certifications
    if 'achievements' in sections:
        right_content.extend(build_achievements_section(sections['achievements'], styles))

    if 'skills' in sections:
        right_content.extend(build_skills_section(sections['skills'], styles))

    if 'certifications' in sections:
        right_content.extend(build_certifications_section(sections['certifications'], styles))

    # Create two-column table
    # Calculate widths
    page_width = letter[0] - 1*inch  # Total usable width
    left_width = page_width * 0.58  # 58% for experience
    right_width = page_width * 0.38  # 38% for achievements/skills
    gap = page_width * 0.04  # 4% gap

    # For now, let's use a simplified single-column approach with better styling
    # (Full two-column layout requires more complex frame management)

    story.extend(left_content)
    story.extend(right_content)

    # Build PDF
    doc.build(story)

    return output_pdf


def create_resume_styles():
    """Create custom styles matching Watson's resume."""
    styles = getSampleStyleSheet()

    # Colors
    blue = HexColor('#2563EB')
    dark_gray = HexColor('#1a1a1a')
    gray = HexColor('#666666')
    light_gray = HexColor('#999999')

    # Name style
    styles.add(ParagraphStyle(
        name='Name',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=dark_gray,
        spaceAfter=2,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=36
    ))

    # Title under name
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Normal'],
        fontSize=14,
        textColor=blue,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))

    # Contact info
    styles.add(ParagraphStyle(
        name='Contact',
        parent=styles['Normal'],
        fontSize=9,
        textColor=gray,
        spaceAfter=16,
        leading=11
    ))

    # Section headers (EXPERIENCE, SKILLS, etc.)
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=12,
        textColor=dark_gray,
        spaceAfter=8,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        leading=14,
        keepWithNext=True
    ))

    # Job title
    styles.add(ParagraphStyle(
        name='JobTitle',
        fontSize=11,
        textColor=dark_gray,
        spaceAfter=2,
        fontName='Helvetica-Bold',
        keepWithNext=True
    ))

    # Company name
    styles.add(ParagraphStyle(
        name='Company',
        fontSize=10,
        textColor=blue,
        spaceAfter=2,
        fontName='Helvetica-Bold'
    ))

    # Date and location
    styles.add(ParagraphStyle(
        name='DateLocation',
        fontSize=9,
        textColor=gray,
        spaceAfter=6,
        fontName='Helvetica'
    ))

    # Job description bullets
    styles.add(ParagraphStyle(
        name='JobBullet',
        fontSize=9,
        textColor=dark_gray,
        leftIndent=12,
        spaceAfter=3,
        leading=12
    ))

    # Achievement title
    styles.add(ParagraphStyle(
        name='AchievementTitle',
        fontSize=10,
        textColor=dark_gray,
        spaceAfter=3,
        fontName='Helvetica-Bold',
        leading=12
    ))

    # Achievement description
    styles.add(ParagraphStyle(
        name='AchievementDesc',
        fontSize=9,
        textColor=dark_gray,
        spaceAfter=10,
        leading=11
    ))

    # Skill tag
    styles.add(ParagraphStyle(
        name='SkillTag',
        fontSize=9,
        textColor=dark_gray,
        fontName='Helvetica'
    ))

    return styles


def parse_resume_sections(md_content):
    """Parse markdown into structured sections."""
    sections = {
        'header': {},
        'experience': [],
        'education': [],
        'achievements': [],
        'skills': [],
        'certifications': []
    }

    lines = md_content.split('\n')
    current_section = None
    current_job = None

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            continue

        # Name (H1)
        if line.startswith('# '):
            sections['header']['name'] = line[2:].strip()

        # Contact info (usually second or third line)
        elif '|' in line and '@' in line:
            sections['header']['contact'] = line

        # Section headers
        elif line.startswith('## '):
            section_name = line[3:].strip().lower()
            if 'experience' in section_name:
                current_section = 'experience'
            elif 'education' in section_name:
                current_section = 'education'
            elif 'achievement' in section_name:
                current_section = 'achievements'
            elif 'skill' in section_name:
                current_section = 'skills'
            elif 'certification' in section_name:
                current_section = 'certifications'

        # Job title (H3)
        elif line.startswith('### '):
            if current_section == 'experience':
                if current_job:
                    sections['experience'].append(current_job)
                current_job = {
                    'title': line[4:].strip(),
                    'company': '',
                    'dates': '',
                    'location': '',
                    'bullets': []
                }

        # Company/dates/location or bullets
        elif current_section == 'experience' and current_job:
            if line.startswith('**') and line.endswith('**'):
                # Company line
                current_job['company'] = line.strip('*')
            elif '|' in line:
                # Dates and location
                parts = line.split('|')
                if len(parts) >= 2:
                    current_job['dates'] = parts[0].strip()
                    current_job['location'] = parts[1].strip()
            elif line.startswith('- '):
                current_job['bullets'].append(line[2:])

    # Add last job
    if current_job:
        sections['experience'].append(current_job)

    return sections


def build_header(header, styles):
    """Build header section."""
    story = []

    if 'name' in header:
        story.append(Paragraph(header['name'], styles['Name']))

    story.append(Paragraph('Senior Product Manager', styles['Title']))

    if 'contact' in header:
        # Clean up contact info
        contact = header['contact'].replace('|', ' • ')
        story.append(Paragraph(contact, styles['Contact']))

    # Divider line
    story.append(SectionDivider(width=7*inch, color=HexColor('#000000'), thickness=2))
    story.append(Spacer(1, 0.1*inch))

    return story


def build_experience_section(jobs, styles):
    """Build experience section."""
    story = []

    story.append(Paragraph('<b>EXPERIENCE</b>', styles['SectionHeader']))
    story.append(SectionDivider(width=7*inch, color=HexColor('#000000'), thickness=2))
    story.append(Spacer(1, 0.1*inch))

    for job in jobs:
        # Job title
        story.append(Paragraph(job['title'], styles['JobTitle']))

        # Company
        if job.get('company'):
            story.append(Paragraph(f'<font color="#2563EB"><b>{job["company"]}</b></font>', styles['Company']))

        # Dates and location
        if job.get('dates') or job.get('location'):
            date_loc = f"{job.get('dates', '')} • {job.get('location', '')}".strip(' •')
            story.append(Paragraph(date_loc, styles['DateLocation']))

        # Bullets
        for bullet in job.get('bullets', []):
            # Convert markdown bold to reportlab
            bullet = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', bullet)
            story.append(Paragraph(f'• {bullet}', styles['JobBullet']))

        story.append(Spacer(1, 0.15*inch))

    return story


def build_education_section(education, styles):
    """Build education section."""
    story = []
    story.append(Paragraph('<b>EDUCATION</b>', styles['SectionHeader']))
    story.append(SectionDivider(width=7*inch, color=HexColor('#000000'), thickness=2))
    # Add education content here
    return story


def build_achievements_section(achievements, styles):
    """Build achievements section."""
    story = []
    story.append(Paragraph('<b>HEADLINE ACHIEVEMENTS</b>', styles['SectionHeader']))
    story.append(SectionDivider(width=7*inch, color=HexColor('#000000'), thickness=2))
    # Add achievements content here
    return story


def build_skills_section(skills, styles):
    """Build skills section."""
    story = []
    story.append(Paragraph('<b>SKILLS</b>', styles['SectionHeader']))
    story.append(SectionDivider(width=7*inch, color=HexColor('#000000'), thickness=2))
    # Add skills as tags/pills
    return story


def build_certifications_section(certs, styles):
    """Build certifications section."""
    story = []
    story.append(Paragraph('<b>CERTIFICATIONS</b>', styles['SectionHeader']))
    story.append(SectionDivider(width=7*inch, color=HexColor('#000000'), thickness=2))
    # Add certifications content here
    return story


def markdown_to_pdf(markdown_file: Path, output_pdf: Path):
    """
    Main entry point - create advanced PDF from markdown.
    """
    return create_two_column_resume(markdown_file, output_pdf)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        md_file = Path(sys.argv[1])
        pdf_file = md_file.with_suffix('.pdf')
        markdown_to_pdf(md_file, pdf_file)
        print(f"PDF generated: {pdf_file}")
    else:
        print("Usage: python pdf_generator_advanced.py <markdown_file>")
