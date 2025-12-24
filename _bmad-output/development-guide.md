# Resume Tailor - Development Guide

**Generated:** 2025-12-23
**Project:** Resume Tailor Desktop Application

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Environment Setup](#environment-setup)
4. [Local Development](#local-development)
5. [Building Executable](#building-executable)
6. [Testing](#testing)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python:** 3.13.3 or newer
- **pip:** Latest version
- **Git:** For version control

### Optional Tools
- **Windows:** For building .exe (PyInstaller Windows-only)
- **Claude Code / VS Code:** For development

### API Keys
- **Anthropic API Key:** Required for AI generation
  - Get from: https://console.anthropic.com/
  - Cost: ~$0.10 per application with Sonnet-4

---

## Installation

### 1. Clone Repository
```bash
cd C:\Users\watso\Dev
# Repository already exists at resume-tailor/
```

### 2. Install Dependencies
```bash
cd resume-tailor
pip install -r requirements.txt
```

**Dependencies installed:**
```
anthropic>=0.39.0      # Claude API client
reportlab>=4.0.0       # PDF generation
python-dotenv          # Environment variable loading
python-docx            # Word document generation
markdown               # HTML generation
PyInstaller            # Executable building (optional)
```

### 3. Verify Installation
```bash
python -c "import anthropic, reportlab, docx, markdown; print('✅ All dependencies installed')"
```

---

## Environment Setup

### 1. Create .env File
```bash
# Create .env in project root
echo ANTHROPIC_API_KEY=sk-ant-your-key-here > .env
```

**Full .env template:**
```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Optional - custom output directory
RESUME_OUTPUT_DIR=C:\Users\watso\OneDrive\Desktop\Jobs
```

### 2. Verify API Key
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('ANTHROPIC_API_KEY')[:15] + '...')"
```

### 3. Configure Contact Info
Edit `config.py` if needed:
```python
DEFAULT_CONTACT = {
    "name": "M. Watson Mulkey",
    "email": "watsonmulkey@gmail.com",
    "phone": "434-808-2493",
    "linkedin": "linkedin.com/in/watsonmulkey",
    "location": "Denver, Colorado"
}
```

---

## Local Development

### Running the GUI
```bash
# Launch GUI application
python resume_tailor_gui.py
```

**Expected Output:**
- Retro terminal-style window opens
- ASCII art header displays
- Ready for job description input

### Running the CLI
```bash
# Basic usage with job file
python resume_tailor.py --job test_job.txt --verbose

# Paste mode (interactive)
python resume_tailor.py --paste

# With company name
python resume_tailor.py --job classdojo_job.txt --company-name "ClassDojo"

# Resume only
python resume_tailor.py --job test_job.txt --resume-only

# Cover letter only
python resume_tailor.py --job test_job.txt --cover-letter-only

# Custom output directory
python resume_tailor.py --job test_job.txt --output-dir ./custom_output
```

### CLI Options Reference
```
--job FILE           Job description file path
--paste              Paste job description interactively
--company-name NAME  Company name (for file organization)
--output-dir DIR     Custom output directory
--resume-only        Generate only resume
--cover-letter-only  Generate only cover letter
--output-format FMT  Output format (markdown, pdf, docx, all)
--verbose            Detailed logging
```

---

## Building Executable

### One-Click Build (Windows)
```bash
# Double-click or run:
build_executable.bat
```

**What it does:**
1. Checks PyInstaller installation
2. Installs if missing
3. Runs PyInstaller with correct flags
4. Creates `dist\Resume Tailor.exe`

### Manual Build
```bash
python -m PyInstaller --onefile ^
    --windowed ^
    --name "Resume Tailor" ^
    --add-data "import_career_data.py;." ^
    --add-data "generator.py;." ^
    --add-data "pdf_generator.py;." ^
    --add-data "html_template.py;." ^
    --add-data "docx_generator.py;." ^
    --add-data "conflict_detector.py;." ^
    --add-data "config.py;." ^
    --add-data "resume_parser.py;." ^
    --add-data ".env;." ^
    --hidden-import anthropic ^
    --hidden-import reportlab ^
    --hidden-import docx ^
    --hidden-import markdown ^
    resume_tailor_gui.py
```

### Build Output
```
dist/
└── Resume Tailor.exe  # 36MB standalone executable
```

### Critical Build Notes
- ⚠️ Use `--add-data` (NOT `--hidden-import`) for local .py files
- ⚠️ Include `.env` file in bundle for API key
- ⚠️ Use `--windowed` to hide console window
- ⚠️ Final .exe is portable (no Python installation needed)

### Build Troubleshooting
```bash
# Clear build cache
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Resume Tailor.spec" del "Resume Tailor.spec"

# Then rebuild
build_executable.bat
```

---

## Testing

### Run Full Test Suite
```bash
python test_hallucination_detection.py
```

**Expected Output:**
```
Ran 16 tests in 2.5s
OK
```

### Test Categories
1. **Contact Info Tests** - Validates correct info injection
2. **Placeholder Tests** - Catches hallucination patterns
3. **API Tests** - Retry logic and error handling
4. **Format Tests** - PDF/DOCX generation
5. **Validation Tests** - Data consistency checks

### Individual Test Run
```bash
# Run specific test
python -m unittest test_hallucination_detection.TestContactInfo

# Run with verbose output
python -m unittest test_hallucination_detection -v
```

### Manual Testing Workflow
1. **Prepare test job description:**
   ```bash
   # Use existing sample
   type test_job.txt
   ```

2. **Generate with GUI:**
   ```bash
   python resume_tailor_gui.py
   # Paste job description
   # Click Generate
   # Verify output in output/TestCo/
   ```

3. **Verify output files:**
   ```bash
   dir output\TestCo
   # Should show:
   # - Watson_Mulkey_Resume_TestCo.pdf
   # - Watson_Mulkey_TestCo_CoverLetter.docx
   # - Watson_Mulkey_TestCo_CoverLetter.pdf
   ```

4. **Check for hallucinations:**
   - Open PDF/DOCX files
   - Verify all facts match import_career_data.py
   - Check contact info is correct
   - Look for [placeholder text]

---

## Common Development Tasks

### Add New Career Achievement
1. Edit `import_career_data.py`:
   ```python
   {
       "type": "achievement",
       "title": "Increased conversion rate by 25%",
       "company": "NewCo",
       "context": "Redesigned checkout flow",
       "metrics": "25% conversion increase, $500K revenue",
       "scope": "10K daily users",
       "methods": "A/B testing, user research, iterative design"
   }
   ```

2. Re-import to supermemory:
   ```bash
   python import_career_data.py
   ```

### Update Contact Information
1. Edit `config.py`:
   ```python
   DEFAULT_CONTACT = {
       "name": "Your Name",
       "email": "your.email@example.com",
       "phone": "123-456-7890",
       "linkedin": "linkedin.com/in/yourname",
       "location": "City, State"
   }
   ```

2. Rebuild executable if needed:
   ```bash
   build_executable.bat
   ```

### Change AI Model
1. Edit `config.py`:
   ```python
   # Use faster/cheaper model
   CLAUDE_MODEL = "claude-haiku-20250514"  # ~$0.01 per application

   # Or most capable
   CLAUDE_MODEL = "claude-sonnet-4-20250514"  # ~$0.10 per application
   ```

### Modify PDF Layout
1. Edit `pdf_generator.py`:
   ```python
   # Adjust spacing
   NAME_SIZE = 34  # Name font size
   HEADER_SPACING = 22  # Header spacing in pixels
   LINE_HEIGHT = 1.35  # Line height multiplier
   ```

2. Test changes:
   ```bash
   python resume_tailor.py --job test_job.txt --resume-only
   ```

### Add New Output Format
1. Create new generator module (e.g., `latex_generator.py`)
2. Implement using `resume_parser.py`:
   ```python
   from resume_parser import parse_markdown_resume

   def generate_latex(markdown_text):
       data = parse_markdown_resume(markdown_text)
       # Generate LaTeX from data
       return latex_content
   ```

3. Register in `generator.py`:
   ```python
   if output_format == 'latex':
       from latex_generator import generate_latex
       generate_latex(markdown_resume)
   ```

---

## Project Structure for Development

### Core Files to Know
```
resume-tailor/
├── 🎨 GUI & CLI
│   ├── resume_tailor_gui.py   # Main GUI (edit for UI changes)
│   └── resume_tailor.py       # CLI (edit for new flags)
│
├── ⚙️ Generation Pipeline
│   ├── generator.py           # Orchestration (edit for workflow)
│   ├── config.py              # Settings (edit for config changes)
│   └── resume_parser.py       # Parser (edit for new sections)
│
├── 📄 Format Generators
│   ├── pdf_generator.py       # PDF (edit for layout changes)
│   ├── docx_generator.py      # DOCX (edit for Word format)
│   └── html_template.py       # HTML (rarely changed)
│
└── 🗄️ Data
    ├── import_career_data.py  # Career data (edit to add achievements)
    └── conflict_detector.py   # Validation (edit for new checks)
```

### Where to Make Changes

| Task | File to Edit |
|------|-------------|
| Change GUI layout | `resume_tailor_gui.py` |
| Add CLI option | `resume_tailor.py` |
| Modify AI prompts | `generator.py` (search for "content": f""") |
| Update contact info | `config.py` |
| Change PDF design | `pdf_generator.py` |
| Add career data | `import_career_data.py` |
| Adjust spacing | `pdf_generator.py` (constants at top) |
| Add validation check | `generator.py` (validate_generated_content) |
| Change output formats | `config.py` (OUTPUT_CONFIG) |

---

## Troubleshooting

### "No module named 'anthropic'"
```bash
pip install anthropic
```

### "ANTHROPIC_API_KEY not found"
1. Check .env file exists:
   ```bash
   dir .env
   ```

2. Verify contents:
   ```bash
   type .env
   # Should show: ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Ensure dotenv is installed:
   ```bash
   pip install python-dotenv
   ```

### GUI Window Too Small
Edit `resume_tailor_gui.py`:
```python
self.root.geometry("1000x850")  # Increase from 900x700
```

### Executable Doesn't Generate PDF/DOCX
Rebuild with all modules:
```bash
# Clean first
if exist dist rmdir /s /q dist

# Rebuild (use build_executable.bat)
build_executable.bat
```

### "Placeholder text detected" Error
This is **expected** - means AI tried to hallucinate!

**Fix:**
1. Check supermemory has relevant data
2. Rerun generation (retry with different prompt)
3. If persists, add more career data to `import_career_data.py`

### PDF Rendering Issues
Unicode symbols not rendering:
- Check `pdf_generator.py` uses: ★ ▶ ● (not emojis)
- Ensure ReportLab 4.0.0+ installed

### Output Files Not Found
Check output directory:
```bash
# Default location
dir "C:\Users\watso\OneDrive\Desktop\Jobs"

# Or check config
python -c "from config import DEFAULT_OUTPUT_DIR; print(DEFAULT_OUTPUT_DIR)"
```

### Executable Size Too Large (>36MB)
Expected! Includes:
- Python interpreter
- All libraries (anthropic, reportlab, docx)
- All source modules
- .env file

Cannot reduce significantly without breaking functionality.

---

## Development Workflow Best Practices

### Before Making Changes
1. Run tests: `python test_hallucination_detection.py`
2. Generate baseline sample: `python resume_tailor.py --job test_job.txt`
3. Save baseline PDF for comparison

### After Making Changes
1. Run tests again
2. Generate new sample
3. Compare output with baseline
4. Verify no hallucinations introduced
5. Rebuild executable if GUI/core changes

### Before Committing
```bash
# Run tests
python test_hallucination_detection.py

# Check git status
git status

# Don't commit:
# - .env (contains API key)
# - dist/ (executables)
# - output/ (generated files)
# - __pycache__/ (Python cache)

# Commit message format
git commit -m "Brief description

Detailed explanation of changes.
Impact on functionality.

🤖 Generated with Claude Code"
```

---

## Performance Optimization

### Speed Up Generation
1. **Use Haiku model** (10x faster, 10x cheaper):
   ```python
   # In config.py
   CLAUDE_MODEL = "claude-haiku-20250514"
   ```

2. **Reduce max tokens**:
   ```python
   MAX_RESUME_TOKENS = 2000  # Down from 2500
   MAX_COVER_LETTER_TOKENS = 1200  # Down from 1500
   ```

3. **Skip cover letter** (if only need resume):
   ```bash
   python resume_tailor.py --job job.txt --resume-only
   ```

### Reduce Executable Size
Not recommended - breaks functionality. Current 36MB is optimal for:
- Standalone distribution
- No external dependencies
- Includes all features

---

## Debugging Tips

### Enable Verbose Logging
```bash
# CLI
python resume_tailor.py --job test_job.txt --verbose

# GUI - check status log panel
```

### Print Debug Info
Add to `generator.py`:
```python
print(f"DEBUG: Job parsed as: {parsed_job}")
print(f"DEBUG: Supermemory retrieved: {len(results)} items")
print(f"DEBUG: Generated {len(markdown)} characters")
```

### Inspect API Responses
```python
# In generator.py, after API call
with open('debug_api_response.txt', 'w') as f:
    f.write(message.content[0].text)
```

### Check File Generation
```bash
# See what files were created
dir output\[Company] /b

# Check file sizes
dir output\[Company]
```

---

**Generated by BMad Method Document-Project Workflow**
**Scan Level:** Deep
**Date:** 2025-12-23
