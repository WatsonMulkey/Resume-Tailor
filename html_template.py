"""
HTML/CSS template generator for resumes matching Watson's original style.
"""

from pathlib import Path
from string import Template


def generate_html_resume(resume_data: dict, output_html: Path):
    """
    Generate HTML resume with inline CSS matching Watson's original design.

    Args:
        resume_data: Dictionary with resume sections
        output_html: Path to save HTML file
    """

    css_styles = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Calibri', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
            font-size: 10.5pt;
            line-height: 1.5;
            color: #2c3e50;
            background: #f5f5f5;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .page {
            width: 8.5in;
            min-height: 11in;
            margin: 20px auto;
            padding: 0.6in;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        /* Header */
        .header {
            margin-bottom: 24px;
            border-bottom: 3px solid #2563EB;
            padding-bottom: 16px;
        }

        .name {
            font-size: 28pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }

        .title {
            font-size: 13pt;
            font-weight: 600;
            color: #2563EB;
            margin-bottom: 10px;
        }

        .contact-info {
            font-size: 9.5pt;
            color: #666;
            margin-top: 8px;
        }

        .contact-info a {
            color: #2563EB;
            text-decoration: none;
        }

        .contact-info a:hover {
            text-decoration: underline;
        }

        /* Section divider */
        .section-divider {
            border-bottom: 1.5px solid #e0e0e0;
            margin: 8px 0 14px 0;
        }

        /* Two column layout */
        .content-wrapper {
            display: flex;
            gap: 30px;
        }

        .left-column {
            flex: 1.4;
        }

        .right-column {
            flex: 1;
        }

        /* Section headers */
        .section-header {
            font-size: 11pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-top: 20px;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .section-header:first-child {
            margin-top: 0;
        }

        /* Job entry */
        .job-entry {
            margin-bottom: 20px;
            position: relative;
            padding-left: 28px;
        }

        .company-icon {
            position: absolute;
            left: 0;
            top: 2px;
            width: 18px;
            height: 18px;
            border-radius: 3px;
        }

        .job-title {
            font-size: 10.5pt;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 3px;
            line-height: 1.3;
        }

        .company-name {
            font-size: 10pt;
            font-weight: 600;
            color: #2563EB;
            margin-bottom: 3px;
        }

        .job-meta {
            font-size: 9pt;
            color: #777;
            margin-bottom: 8px;
            font-style: italic;
        }

        .job-bullets {
            list-style: none;
            padding-left: 0;
        }

        .job-bullets li {
            font-size: 9.5pt;
            color: #333;
            margin-bottom: 5px;
            padding-left: 14px;
            position: relative;
            line-height: 1.5;
        }

        .job-bullets li:before {
            content: "▪";
            position: absolute;
            left: 0;
            color: #2563EB;
            font-weight: bold;
        }

        /* Achievements */
        .achievement {
            margin-bottom: 16px;
            padding-left: 24px;
            position: relative;
        }

        .achievement-icon {
            position: absolute;
            left: 0;
            top: 1px;
            font-size: 13pt;
            color: #2563EB;
        }

        .achievement-title {
            font-size: 10pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 4px;
        }

        .achievement-desc {
            font-size: 9.5pt;
            color: #555;
            line-height: 1.5;
        }

        /* Skills */
        .skills-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 6px;
            margin-top: 8px;
        }

        .skill-item {
            font-size: 9.5pt;
            color: #333;
            padding: 6px 0;
            border-left: 3px solid #2563EB;
            padding-left: 10px;
        }

        /* Certifications */
        .cert-item {
            margin-bottom: 12px;
        }

        .cert-title {
            font-size: 10pt;
            font-weight: bold;
            color: #2563EB;
            margin-bottom: 2px;
        }

        .cert-desc {
            font-size: 9pt;
            color: #555;
            line-height: 1.3;
        }

        /* Education */
        .education-item {
            margin-bottom: 10px;
        }

        .degree {
            font-size: 10pt;
            font-weight: bold;
            color: #1a1a1a;
        }

        .school {
            font-size: 10pt;
            color: #2563EB;
            font-weight: bold;
        }

        .edu-dates {
            font-size: 9pt;
            color: #666;
        }

        /* Print styles */
        @media print {
            body {
                background: white;
            }

            .page {
                width: 100%;
                margin: 0;
                padding: 0.5in;
                box-shadow: none;
            }

            .header {
                page-break-after: avoid;
            }

            .section-header {
                page-break-after: avoid;
            }

            .job-entry, .achievement, .cert-item {
                page-break-inside: avoid;
            }

            /* Ensure colors print */
            * {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color-adjust: exact;
            }
        }

        @page {
            size: Letter;
            margin: 0;
        }

        /* Screen-only: subtle hover effects */
        @media screen {
            .job-entry:hover {
                background-color: #f8f9fa;
                transition: background-color 0.2s;
            }
        }
    </style>
    """

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${name} - Resume</title>
        ${css_styles}
    </head>
    <body>
        <div class="page">
            <!-- Header -->
            <div class="header">
                <div class="name">${name}</div>
                <div class="title">${job_title}</div>
                <div class="contact-info">
                    ${contact_info}
                </div>
                <div class="section-divider"></div>
            </div>

            <!-- Two column content -->
            <div class="content-wrapper">
                <!-- Left column: Experience & Education -->
                <div class="left-column">
                    <div class="section-header">EXPERIENCE</div>
                    <div class="section-divider"></div>
                    ${experience_html}

                    <div class="section-header">EDUCATION</div>
                    <div class="section-divider"></div>
                    ${education_html}
                </div>

                <!-- Right column: Achievements, Skills, Certs -->
                <div class="right-column">
                    <div class="section-header">HEADLINE ACHIEVEMENTS</div>
                    <div class="section-divider"></div>
                    ${achievements_html}

                    <div class="section-header">SKILLS</div>
                    <div class="section-divider"></div>
                    ${skills_html}

                    <div class="section-header">CERTIFICATIONS</div>
                    <div class="section-divider"></div>
                    ${certifications_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Build HTML from resume data
    template = Template(html_template)

    html_content = template.substitute(
        css_styles=css_styles,
        name=resume_data.get('name', 'M. WATSON MULKEY'),
        job_title=resume_data.get('title', 'Senior Product Manager'),
        contact_info=resume_data.get('contact_info', ''),
        experience_html=build_experience_html(resume_data.get('experience', [])),
        education_html=build_education_html(resume_data.get('education', {})),
        achievements_html=build_achievements_html(resume_data.get('achievements', [])),
        skills_html=build_skills_html(resume_data.get('skills', [])),
        certifications_html=build_certifications_html(resume_data.get('certifications', []))
    )

    # Save HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_html


def build_experience_html(jobs):
    """Build HTML for experience section."""
    if not jobs:
        return ""

    html_parts = []

    # Company colors (cycling through nice colors)
    colors = ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#8B5CF6']

    for i, job in enumerate(jobs):
        color = colors[i % len(colors)]

        bullets_html = ""
        if job.get('bullets'):
            bullets = '\n'.join([f'<li>{b}</li>' for b in job['bullets']])
            bullets_html = f'<ul class="job-bullets">{bullets}</ul>'

        html_parts.append(f"""
        <div class="job-entry">
            <div class="company-icon" style="background-color: {color};"></div>
            <div class="job-title">{job.get('title', '')}</div>
            <div class="company-name">{job.get('company', '')}</div>
            <div class="job-meta">{job.get('dates', '')} • {job.get('location', '')}</div>
            {bullets_html}
        </div>
        """)

    return '\n'.join(html_parts)


def build_education_html(education):
    """Build HTML for education section."""
    if not education:
        return ""

    return f"""
    <div class="education-item">
        <div class="degree">{education.get('degree', 'Bachelor of Arts - English')}</div>
        <div class="school">{education.get('school', 'Hampden-Sydney College')}</div>
        <div class="edu-dates">{education.get('dates', '08/2004 - 04/2008')}</div>
    </div>
    """


def build_achievements_html(achievements):
    """Build HTML for achievements section."""
    if not achievements:
        return ""

    icons = ['⭐', '🚀', '🎯', '📈', '💡']
    html_parts = []

    for i, ach in enumerate(achievements):
        icon = icons[i % len(icons)]
        html_parts.append(f"""
        <div class="achievement">
            <div class="achievement-icon">{icon}</div>
            <div class="achievement-title">{ach.get('title', '')}</div>
            <div class="achievement-desc">{ach.get('description', '')}</div>
        </div>
        """)

    return '\n'.join(html_parts)


def build_skills_html(skills):
    """Build HTML for skills section."""
    if not skills:
        return ""

    skills_items = '\n'.join([f'<div class="skill-item">{s}</div>' for s in skills])
    return f'<div class="skills-grid">{skills_items}</div>'


def build_certifications_html(certs):
    """Build HTML for certifications section."""
    if not certs:
        return ""

    html_parts = []
    for cert in certs:
        html_parts.append(f"""
        <div class="cert-item">
            <div class="cert-title">{cert.get('title', '')}</div>
            <div class="cert-desc">{cert.get('description', '')}</div>
        </div>
        """)

    return '\n'.join(html_parts)


if __name__ == '__main__':
    # Test with sample data
    sample_data = {
        'name': 'M. WATSON MULKEY',
        'title': 'Senior Product Manager',
        'contact_info': '4348082493 • watsonmulkey@gmail.com • Denver, Colorado',
        'experience': [
            {
                'title': 'Senior Product Manager - ID/Onboarding/Platform',
                'company': 'Registria',
                'dates': '01/2024 - 03/2025',
                'location': 'Denver, Colorado',
                'bullets': [
                    'Delivered comprehensive reporting suite for flagship product',
                    'Developed multi-vertical dependency roadmap'
                ]
            }
        ],
        'education': {
            'degree': 'Bachelor of Arts - English',
            'school': 'Hampden-Sydney College',
            'dates': '08/2004 - 04/2008'
        },
        'achievements': [
            {
                'title': '32% YoY engagement increase',
                'description': 'Overhauled teacher-side app based on user research'
            }
        ],
        'skills': ['Product Strategy', 'User Research', 'A/B Testing'],
        'certifications': [
            {
                'title': 'Pragmatic Marketing - Focus',
                'description': 'Strategic business opportunities and roadmaps'
            }
        ]
    }

    output = Path('test_resume.html')
    generate_html_resume(sample_data, output)
    print(f"Test HTML generated: {output}")
