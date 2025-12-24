# Resume Tailor - Project Overview

**Generated:** 2025-12-23
**Project Type:** Desktop Application (Python GUI)
**Primary Interface:** Windows Executable (.exe)
**Status:** Production - Active Use

---

## Executive Summary

Resume Tailor is an AI-powered desktop application that generates tailored resumes and cover letters using career data stored in supermemory. The tool emphasizes **zero hallucinations** through multi-layer validation and fact injection, ensuring all generated content is factually accurate and traceable to source data.

**Key Differentiator:** Multi-layer anti-hallucination architecture prevents AI from inventing facts, making it production-ready for real job applications.

---

## Project Classification

- **Repository Type:** Monolith (single cohesive codebase)
- **Application Type:** Desktop GUI Application
- **Primary Interface:** Windows executable (Resume_Tailor.exe - 36MB)
- **Secondary Interface:** CLI (resume_tailor.py)
- **Distribution:** Standalone .exe via PyInstaller
- **Target Platform:** Windows (primary), cross-platform capable

---

## Quick Reference

### Technology Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Language | Python | 3.13.3 | Core application |
| GUI Framework | tkinter | Built-in | Retro terminal-style interface |
| AI Model | Anthropic Claude | Sonnet 4 | Job parsing & content generation |
| PDF Generation | ReportLab | 4.0.0+ | Resume PDF output |
| DOCX Generation | python-docx | Latest | Cover letter Word docs |
| HTML Generation | markdown | Latest | Intermediate HTML format |
| Build Tool | PyInstaller | Latest | Executable packaging |
| Config Management | python-dotenv | Latest | Environment variables |

### Architecture Pattern

**Multi-Module Desktop Application** with:
- **GUI Layer:** tkinter-based retro terminal interface
- **Generation Layer:** Modular format generators (PDF, DOCX, HTML)
- **API Layer:** Claude Sonnet 4 integration with retry logic
- **Validation Layer:** Anti-hallucination checks and contact info injection
- **Data Layer:** Supermemory integration for career data retrieval

---

## Core Features

### 1. Zero-Hallucination Architecture ⭐
- **Contact Info Injection:** Guarantees accurate contact details
- **Placeholder Detection:** Validates output before saving
- **Fact-Only Generation:** Strict prompts prevent invention
- **Source Traceability:** All claims traceable to supermemory

### 2. AI-Powered Tailoring
- **Job Description Parsing:** Extracts requirements, skills, keywords
- **Smart Matching:** Maps relevant experience to job needs
- **ATS Optimization:** Incorporates keywords naturally
- **Voice Mimicking:** Matches user's writing style from examples

### 3. Multi-Format Output
- **Resume:** PDF only (ATS-optimized)
- **Cover Letter:** DOCX + PDF
- **Intermediate:** Markdown (auto-cleaned)
- **Clean Folders:** Only final formats kept

### 4. Professional Design
- **Modern PDF Layout:** Based on VisualCV/Enhancv research
- **Optimized Spacing:** 21% vertical space reduction
- **Unicode Symbols:** ★ ▶ ● for reliable rendering
- **WCAG Compliant:** Level AA accessibility

---

## Project Structure

```
resume-tailor/
├── Resume_Tailor.exe          # Primary entry (GUI executable)
├── resume_tailor_gui.py       # GUI application source
├── resume_tailor.py           # CLI entry point
├── generator.py               # Core generation orchestration
├── resume_parser.py           # Unified markdown parser
├── config.py                  # Centralized configuration
├── pdf_generator.py           # ReportLab PDF generation
├── docx_generator.py          # python-docx generation
├── html_template.py           # HTML generation
├── conflict_detector.py       # Data validation
├── import_career_data.py      # Career data import script
├── test_hallucination_detection.py  # Test suite (16 tests)
├── build_executable.bat       # PyInstaller build script
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not committed)
├── data/                      # Career data (in supermemory)
├── output/                    # Generated documents
├── dist/                      # Built executables
└── _bmad/                     # BMad methodology files
```

---

## Development Workflow

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Run GUI
python resume_tailor_gui.py

# Run CLI
python resume_tailor.py --job job.txt --verbose
```

### Building Executable
```bash
# One-click build
build_executable.bat

# Output: dist\Resume Tailor.exe
```

### Testing
```bash
# Run test suite (16 tests)
python test_hallucination_detection.py
```

---

## Key Metrics

- **Career Data:** 29 entries in supermemory
- **Test Coverage:** 16 automated tests
- **Executable Size:** 36MB standalone
- **Code Quality:** ~340 lines reduced via refactoring
- **Output Formats:** 3 (PDF, DOCX, Markdown)
- **Generation Time:** ~10-15 seconds per application
- **Cost per Generation:** ~$0.10 (Sonnet 4)

---

## Success Criteria

✅ **Zero Hallucinations:** Every fact traceable to supermemory
✅ **Voice Match:** Cover letters sound like user examples
✅ **ATS Optimization:** Keywords naturally incorporated
✅ **Production Ready:** Used for real job applications
✅ **Clean Output:** Only final formats (.pdf, .docx)
✅ **Error Handling:** All failures surface immediately
✅ **Executable Works:** GUI runs standalone without Python

---

## User Workflow

1. **Launch** Resume_Tailor.exe from desktop
2. **Paste** job description from company website
3. **Enter** company name (e.g., "ClassDojo")
4. **Select** AI model (Sonnet-4 recommended)
5. **Choose** outputs (Resume + Cover Letter)
6. **Click** GENERATE
7. **Review** generated files in output folder
8. **Verify** facts before submission

**Output Location:** `C:\Users\watso\OneDrive\Desktop\Jobs\[Company]\`

---

## Anti-Hallucination Layers

### Layer 1: Retrieval-Only Data
- All facts from supermemory
- No invention in prompts
- Structured context passing

### Layer 2: Contact Info Injection
- Hardcoded fallback in config.py
- Injected post-generation
- Guarantees accuracy

### Layer 3: Placeholder Validation
- Regex pattern detection
- Pre-save validation
- Raises error on placeholders

### Layer 4: Error Surfacing
- No silent failures
- All errors visible in GUI
- Logs force-displayed

---

## Critical Learnings (Retro)

### Proven Approaches ✓
- Sample output first, user review before expanding
- Multi-layer hallucination prevention works
- Code centralization (config.py) saves maintenance
- ReportLab reliable for PDF generation
- Retry logic with exponential backoff essential

### Mistakes Avoided ✗
- Placeholder template generation (CRITICAL FIX applied)
- PyInstaller --hidden-import (use --add-data instead)
- Cluttered output folders (cleanup implemented)
- Silent GUI failures (log_callback added)

### User Preferences 👤
- GUI over CLI (uses .exe primarily)
- Bug fixes before features
- Semicolons over em-dashes
- Clean output folders
- Quality over speed

---

## Future Roadmap (Post-MVP)

- [ ] Web interface for non-technical use
- [ ] Batch processing for multiple jobs
- [ ] Interview prep from resume data
- [ ] Salary negotiation talking points
- [ ] LinkedIn profile optimizer
- [ ] Application tracking integration

---

## Documentation Files

- [Architecture](./architecture.md) - System design and component overview
- [Source Tree Analysis](./source-tree-analysis.md) - Annotated directory structure
- [Development Guide](./development-guide.md) - Setup and build instructions
- [Component Inventory](./component-inventory.md) - UI components and generators
- README.md - User-facing documentation
- STATUS.md - Project status tracking
- GUI_README.md - GUI quick start guide
- ATS_OPTIMIZATION_GUIDE.md - ATS optimization best practices

---

**Generated by BMad Method Document-Project Workflow**
**Scan Level:** Deep
**Date:** 2025-12-23
