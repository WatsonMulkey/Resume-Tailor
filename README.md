# Resume Tailor

AI-powered resume and cover letter customization tool that uses your career data stored in supermemory to generate tailored application documents with zero hallucinations.

## Features

- **Zero Hallucinations**: Only uses factual information retrieved from your supermemory career data
- **Tailored Content**: Analyzes job descriptions and matches your relevant experience
- **Writing Style Mimicking**: Learns from your past cover letters to match your tone and voice
- **CLI Interface**: Fast and efficient command-line tool
- **Multiple Output Formats**: Markdown, PDF, and DOCX (planned)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. Make the script executable (optional):
```bash
chmod +x resume_tailor.py
```

## Usage

### Basic Usage

Generate from a job description file:
```bash
python resume_tailor.py --job job_description.txt
```

Paste job description interactively:
```bash
python resume_tailor.py --paste
```

### Advanced Options

Specify company name and output directory:
```bash
python resume_tailor.py --job job_description.txt --company-name "Acme Corp" --output-dir ./applications/acme
```

Generate only cover letter:
```bash
python resume_tailor.py --job job_description.txt --cover-letter-only
```

Generate only resume:
```bash
python resume_tailor.py --job job_description.txt --resume-only
```

Verbose output:
```bash
python resume_tailor.py --job job_description.txt --verbose
```

## Career Data in Supermemory

Your career data is stored in supermemory with the following structure:

- **Achievements**: Quantifiable wins with context, metrics, and methods
- **Job History**: Detailed role information with responsibilities
- **Skills**: Evidence-based skills with specific examples
- **Writing Style**: Patterns from your past cover letters
- **Personal Values**: Mission alignment and motivations

## Data Population

To populate your career data, run:
```bash
python import_career_data.py
```

This imports data from:
- Current resume
- Past cover letters
- LinkedIn profile (when available)
- Additional career documents

## Anti-Hallucination Strategy

1. **Retrieval-Only**: Claude only uses information retrieved from supermemory
2. **Explicit Instructions**: Prompts include strict "no invention" guidelines
3. **Structured Context**: Career data passed as structured facts
4. **Verification**: Optional second-pass verification (planned)

## Current Status

✅ Career data structured and imported to supermemory (29 entries)
✅ CLI tool skeleton created
✅ Job description parser implemented
🚧 Supermemory integration (in progress)
🚧 Claude API anti-hallucination prompts (in progress)
🚧 Resume formatting (basic template ready)
🚧 Cover letter formatting (basic template ready)
⏳ PDF/DOCX export (planned)
⏳ LinkedIn data import (waiting for export)

## Next Steps

1. Add LinkedIn recommendations when data is ready
2. Complete supermemory retrieval integration
3. Enhance Claude prompts with anti-hallucination instructions
4. Add resume style preservation (matching current resume format)
5. Implement PDF/DOCX export

## File Structure

```
resume-tailor/
├── resume_tailor.py        # Main CLI entry point
├── generator.py            # Core generation logic
├── import_career_data.py   # Career data import script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # Career data (stored in supermemory)
└── output/                # Generated documents
```

## Privacy & Security

- All career data stays in your local supermemory instance
- API calls to Claude only send: job description + retrieved context
- No data is stored externally beyond Anthropic's standard API usage
- Generated documents are saved locally only

## License

Personal use tool - not for distribution
