# Resume Tailor Skill

AI-powered resume and cover letter customization tool that generates tailored application documents with zero hallucinations by using your career data stored in supermemory.

## What This Skill Does

This skill helps you:
1. **Store your career history** in supermemory with structured, factual information
2. **Parse job descriptions** to extract requirements, skills, and keywords
3. **Generate tailored resumes** that highlight relevant experience
4. **Create personalized cover letters** that match your writing style
5. **Ensure zero hallucinations** by only using facts from your stored data

## Key Features

- **Zero Hallucinations**: Only uses factual information from supermemory
- **Voice Mimicking**: Learns from your past cover letters to match your tone
- **CLI Interface**: Fast, efficient command-line tool
- **Smart Matching**: Maps your experience to job requirements
- **Multiple Formats**: Markdown, PDF, DOCX (planned)

## Architecture

### Data Storage (Supermemory)
Your career data is stored in supermemory with these categories:
- **Achievements** (6 entries): Quantifiable wins with metrics, context, and methods
- **Job History** (6 entries): Detailed role information with responsibilities
- **Skills** (7 entries): Evidence-based skills with specific examples
- **Writing Style** (1 entry): Patterns from past cover letters
- **Personal Values** (3 entries): Mission alignment and motivations
- **Education & Certifications**

### Anti-Hallucination Strategy
1. **Retrieval-Only**: Claude only uses information retrieved from supermemory
2. **Explicit Instructions**: Prompts include strict "no invention" guidelines
3. **Structured Context**: Career data passed as structured facts
4. **Basic Fallback**: Works in offline mode with templates when API unavailable

### Components

```
resume-tailor/
├── resume_tailor.py          # Main CLI entry point
├── generator.py              # Core generation logic
├── import_career_data.py     # Data import script (29 entries)
├── requirements.txt          # Dependencies
├── test_job.txt             # Sample job description
└── output/                   # Generated documents
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Anthropic API Key
```powershell
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

```bash
# Mac/Linux
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 3. Import Your Career Data

The skill comes pre-configured with data structure. To customize with your own data:

1. Edit `import_career_data.py` with your:
   - Job history and responsibilities
   - Quantifiable achievements with metrics
   - Skills with evidence
   - Past cover letter examples
   - Personal values and stories

2. Run the import (structure is ready, data populates supermemory)

### 4. Add Your Documents

Place your career documents for import:
- Current resume (PDF/DOCX)
- Past cover letters (2-3 examples)
- LinkedIn export (optional)

## Usage

### Basic Usage

Generate from a job description file:
```bash
python resume_tailor.py --job job_description.txt
```

Interactive paste mode:
```bash
python resume_tailor.py --paste
```

### Advanced Options

With company name and custom output:
```bash
python resume_tailor.py --job job.txt --company-name "Acme Corp" --output-dir ./applications/acme
```

Generate only cover letter:
```bash
python resume_tailor.py --job job.txt --cover-letter-only
```

Verbose output for debugging:
```bash
python resume_tailor.py --job job.txt --verbose
```

### Offline Mode

Works without API key using basic templates:
- Uses simple keyword extraction for job parsing
- Generates documents with your factual data
- Good for testing or when API unavailable

### Full Mode (with API key)

With API key set, enables:
- Intelligent job requirement extraction
- Contextual supermemory searches
- Tailored content generation
- Voice-matched cover letters

## Example Output

### Generated Resume Features
- Your actual career data (no hallucinations)
- Metrics prominently displayed (32% engagement increase, 50% efficiency gains)
- Formatted to match your current resume style
- Tailored footer with company name

### Generated Cover Letter Features
- Opens with your style (personal story or enthusiastic greeting)
- Maps job requirements to your specific achievements
- Uses your common phrases and tone
- Quantifies outcomes prominently

## Data Structure

### Achievement Entry Example
```
ACHIEVEMENT: Improved user engagement by 32% YoY
Company: Discovery Education
Context: Overhauled teacher-side app to remove friction points
Metrics: 32% Year-over-Year increase
Scope: 1M+ MAU, 50M global users
Methods: User interviews, UX overhaul, friction point removal
```

### Skill Entry Example
```
SKILL: Cross-functional Team Leadership
Evidence:
- Led team of 4-7 at Discovery Education (15% delivery increase)
- Managed projects of 20+ people across 5 teams
- Created consensus between sales, engineering, clients
```

### Writing Style Example
```
WRITING STYLE:
- Opens with personal connection when mission-aligned
- Uses bullet-point structure for requirement mapping
- Quantifies achievements prominently
- Warm and enthusiastic tone
- Common phrases: "I'd love an opportunity to...", "Here's why I'm a great fit..."
```

## Customization

### Adding New Career Data

Use the import script structure to add:
- New job roles
- Recent achievements
- Additional skills
- Updated cover letter examples

### Modifying Templates

Edit `generator.py` to customize:
- Resume formatting and sections
- Cover letter structure
- Output file naming

### Adding Output Formats

Extend `generator.py` to support:
- PDF generation (requires reportlab or similar)
- DOCX generation (requires python-docx)
- HTML output for web portfolios

## Best Practices

1. **Keep Data Factual**: Only store true, verifiable information in supermemory
2. **Quantify Everything**: Include metrics for all achievements
3. **Update Regularly**: Add new achievements and skills as you gain them
4. **Review Outputs**: Always review generated documents before submission
5. **Verify Facts**: Check that all claims are accurate and traceable

## Troubleshooting

### API Key Issues
- Verify key is set: `echo $env:ANTHROPIC_API_KEY` (PowerShell)
- Check key format: Should start with `sk-ant-`
- Ensure credits in Anthropic account

### Unicode Errors
- System uses ASCII-safe output (no emojis)
- If issues persist, check terminal encoding

### Empty Output
- Verify supermemory has data (29 entries expected)
- Check job description file exists and is readable
- Run with `--verbose` flag for debugging

## Future Enhancements

- [ ] Web interface for non-technical use
- [ ] Batch processing for multiple jobs
- [ ] Interview prep from resume data
- [ ] Salary negotiation talking points
- [ ] LinkedIn profile optimizer
- [ ] PDF/DOCX output formatting
- [ ] Integration with application tracking systems

## Security & Privacy

- All career data stored locally in supermemory
- API calls only send: job description + retrieved context
- No external data storage beyond Anthropic API
- Generated documents saved locally only

## Version History

### v1.0.0 (2025-12-17)
- Initial release
- 29 career data entries in supermemory
- CLI tool with full argument parsing
- Job description parsing (basic + AI modes)
- Resume and cover letter generation
- Anti-hallucination architecture
- Offline mode support
