# Resume Tailor - Architecture Documentation

**Generated:** 2025-12-23
**Project:** Resume Tailor Desktop Application
**Architecture Pattern:** Layered Multi-Module Desktop App

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Architecture](#data-architecture)
5. [Anti-Hallucination Architecture](#anti-hallucination-architecture)
6. [API Design](#api-design)
7. [Build & Deployment](#build--deployment)
8. [Testing Strategy](#testing-strategy)

---

## Executive Summary

Resume Tailor implements a **layered architecture** with clear separation of concerns between GUI, generation logic, format processors, and external integrations. The system is designed around a **zero-hallucination constraint**, requiring multi-layer validation and fact injection.

**Key Architectural Decisions:**
- Modular format generators (PDF, DOCX, HTML) for extensibility
- Centralized configuration (config.py) to eliminate duplication
- Unified parser (resume_parser.py) as single source of truth
- Retry logic with exponential backoff for API resilience
- PyInstaller bundling with --add-data for standalone distribution

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                    │
│  ┌─────────────────────┐      ┌────────────────────────┐  │
│  │  Resume_Tailor.exe  │      │  resume_tailor.py      │  │
│  │  (GUI - Primary)    │      │  (CLI - Secondary)     │  │
│  └──────────┬──────────┘      └──────────┬─────────────┘  │
└─────────────┼────────────────────────────┼────────────────┘
              │                            │
┌─────────────┴────────────────────────────┴────────────────┐
│                  GENERATION ORCHESTRATION                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              generator.py (ResumeGenerator)          │ │
│  │  • Job description parsing                           │ │
│  │  • Supermemory retrieval orchestration               │ │
│  │  • Claude API calls with retry logic                 │ │
│  │  • Anti-hallucination validation                     │ │
│  │  • Format generator delegation                       │ │
│  └────────────┬─────────────────┬─────────────┬─────────┘ │
└───────────────┼─────────────────┼─────────────┼───────────┘
                │                 │             │
┌───────────────┴─────────────────┴─────────────┴───────────┐
│               FORMAT GENERATION LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐│
│  │pdf_generator │  │docx_generator│  │html_template.py  ││
│  │   .py        │  │    .py       │  │                  ││
│  │ (ReportLab)  │  │(python-docx) │  │  (markdown)      ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────┘│
│         └─────────────────┴──────────────────┘            │
│                            │                               │
│                   ┌────────┴────────┐                     │
│                   │ resume_parser.py │                     │
│                   │(Unified Parser)  │                     │
│                   └──────────────────┘                     │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────────┐
│              SHARED SERVICES & UTILITIES                   │
│  ┌──────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │config.py │  │conflict_detector│  │ JobDescription  │  │
│  │          │  │     .py         │  │    Parser       │  │
│  └──────────┘  └─────────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────────┐
│                  EXTERNAL INTEGRATIONS                     │
│  ┌────────────────┐            ┌────────────────────────┐ │
│  │  Anthropic API │            │   Supermemory          │ │
│  │ (Claude Sonnet │            │  (Career Data Store)   │ │
│  │      4)        │            │                        │ │
│  └────────────────┘            └────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Core Components

#### 1. **resume_tailor_gui.py** (GUI Layer)
**Responsibility:** Retro terminal-style user interface

**Key Features:**
- ASCII art branding
- Green-on-black terminal aesthetic
- Tkinter-based UI components
- Background threading for generation
- Real-time status logging

**UI Components:**
- Job Description Text Area (scrolledtext)
- Company Name Entry
- AI Model Selector (Sonnet-4 / Haiku)
- Output Checkboxes (Resume / Cover Letter)
- Generate Button
- Status Log (scrolledtext)

**Threading Model:**
```python
def generate_in_background():
    """Runs generation in separate thread to keep GUI responsive."""
    thread = threading.Thread(target=self.run_generation)
    thread.daemon = True
    thread.start()
```

---

#### 2. **generator.py** (Orchestration Layer)
**Responsibility:** Core generation logic and API orchestration

**Class:** `ResumeGenerator`

**Key Methods:**
```python
class ResumeGenerator:
    def __init__(log_callback=None, verbose=False):
        """Initialize with optional GUI logging callback."""

    def generate_resume(job_description, company_name, output_dir):
        """Main resume generation pipeline."""

    def generate_cover_letter(job_description, company_name, output_dir):
        """Main cover letter generation pipeline."""

    def _generate_with_claude(prompt, max_tokens):
        """Call Claude API with retry logic."""

    def validate_generated_content(content):
        """Check for placeholder text (anti-hallucination)."""
```

**Generation Pipeline:**
1. Parse job description → structured data
2. Search supermemory for relevant career data
3. Build context-rich prompt
4. Call Claude API with strict anti-hallucination instructions
5. Validate output (no placeholders)
6. Inject contact info (guarantees accuracy)
7. Generate formats (PDF, DOCX)
8. Clean up intermediate files
9. Return file paths

---

#### 3. **resume_parser.py** (Parsing Layer)
**Responsibility:** Unified markdown-to-structured-data conversion

**Why Created:** Eliminated ~200 lines of duplicate parsing logic across format generators

**Data Structure:**
```python
@dataclass
class Job:
    title: str
    company: str
    dates: str
    location: str
    bullets: List[str]

@dataclass
class ResumeData:
    name: str
    title: str
    contact_info: str
    summary: str
    experience: List[Job]
    achievements: List[str]
    skills: Dict[str, str]
    education: Dict[str, str]
    certifications: List[str]
```

**Single Source of Truth:** All format generators (PDF, DOCX, HTML) use this parser.

---

#### 4. **config.py** (Configuration Layer)
**Responsibility:** Centralized configuration and contact info

**Eliminates:** 4 duplicate contact info definitions

**Configuration Domains:**
- Contact Information (with fallback)
- API Settings (model, tokens, retries)
- Output Preferences (formats, cleanup)
- Optional Dependency Checks

**Key Functions:**
```python
get_contact_info() -> dict  # Prefers CAREER_DATA, falls back to DEFAULT
get_output_formats(content_type) -> list
should_cleanup_intermediate(content_type) -> bool
check_optional_dependency(module_name) -> bool
```

---

#### 5. **Format Generators**

##### **pdf_generator.py** (ReportLab)
- Modern professional layout
- Optimized spacing (21% reduction)
- Unicode symbols (★ ▶ ●)
- WCAG Level AA compliant
- Company-specific footer

##### **docx_generator.py** (python-docx)
- ATS-friendly Word documents
- Markdown formatting support
- Cover letter + resume variants
- Uses shared resume_parser.py

##### **html_template.py** (markdown)
- Intermediate HTML generation
- Auto-cleaned after PDF/DOCX creation
- Fallback format option

---

## Data Architecture

### Career Data Storage (Supermemory)

**Total Entries:** 29

**Categories:**
- **Job History:** 6 entries (companies, titles, dates, responsibilities)
- **Achievements:** 6 entries (metrics, context, methods, scope)
- **Skills:** 7 entries (evidence-based, tool-specific)
- **Writing Style:** 1 entry (patterns, tone, phrases)
- **Personal Values:** 3 entries (mission alignment, stories)
- **Education:** Degrees, certifications

**Storage Format:**
```
JOB: [Title] at [Company] ([Dates])
Context: [What company does]
Responsibilities:
- [Responsibility 1]
- [Responsibility 2]

ACHIEVEMENT: [Brief with metric]
Company: [Company]
Context: [Problem solved]
Metrics: [Quantified results]
Scope: [Scale/impact]
Methods: [How accomplished]

SKILL: [Skill name]
Evidence:
- [Example 1]
- [Example 2]
Tools: [Specific tools]
```

### Job Description Data Model

Parsed by `JobDescriptionParser` into:
```python
{
    "company": str,
    "title": str,
    "required_skills": List[str],
    "preferred_skills": List[str],
    "responsibilities": List[str],
    "qualifications": List[str],
    "keywords": List[str],
    "company_mission": Optional[str],
    "team_size": Optional[str],
    "remote_policy": Optional[str]
}
```

---

## Anti-Hallucination Architecture

### Multi-Layer Prevention System

#### **Layer 1: Retrieval-Only Data**
```python
# Strict prompt instructions
"ONLY use the provided facts from supermemory.
DO NOT invent any information.
If information is not provided, do not include it."
```

#### **Layer 2: Contact Info Injection**
```python
# config.py
DEFAULT_CONTACT = {
    "name": "M. Watson Mulkey",
    "email": "watsonmulkey@gmail.com",
    "phone": "434-808-2493",
    "linkedin": "linkedin.com/in/watsonmulkey",
    "location": "Denver, Colorado"
}

# Injected post-generation
resume_text = inject_contact_info(generated_text)
```

#### **Layer 3: Placeholder Detection**
```python
def validate_generated_content(content):
    """
    Check for placeholder patterns that indicate hallucination.

    Raises ValueError if placeholders detected.
    """
    placeholder_patterns = [
        r'\[relevant .*?\]',
        r'\[Key Requirement.*?\]',
        r'\[Specific.*?\]',
        r'\[metric\]',
        r'\[Capitalized Text\]'
    ]

    for pattern in placeholder_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            raise ValueError(f"CRITICAL: Placeholder text detected: {pattern}")
```

#### **Layer 4: Error Surfacing**
```python
# No silent failures
if validation_failed:
    raise ValueError("Generation failed validation")

# GUI sees all errors
generator = ResumeGenerator(log_callback=self.log_status, verbose=False)

# Force-log critical errors
self._log("CRITICAL: Generation failed", force=True)
```

---

## API Design

### Claude API Integration

**Model:** claude-sonnet-4-20250514 (Sonnet 4)

**Retry Logic with Exponential Backoff:**
```python
def call_claude_with_retry(client, model, max_tokens, messages, max_retries=3):
    """
    Call Claude API with exponential backoff retry logic.

    Handles:
    - Rate limits (wait and retry)
    - Network errors (exponential backoff)
    - API errors (log and reraise)
    """
    delay = 1.0  # Initial delay

    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise RuntimeError(f"API call failed after {max_retries} attempts") from e
```

**Token Limits:**
- Resume: 2500 tokens max
- Cover Letter: 1500 tokens max

**Cost per Generation:**
- Sonnet-4: ~$0.10 per application
- Haiku: ~$0.01 per application (faster, lower quality)

---

## Build & Deployment

### PyInstaller Configuration

**Build Script:** `build_executable.bat`

**Critical Flags:**
```batch
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
    --add-data ".env;." ^
    --hidden-import anthropic ^
    --hidden-import reportlab ^
    resume_tailor_gui.py
```

**Key Learnings:**
- Use `--add-data` (NOT `--hidden-import`) for local .py files
- `--windowed` prevents console window
- Final .exe size: 36MB

**Output:** `dist\Resume Tailor.exe`

---

## Testing Strategy

### Test Suite: `test_hallucination_detection.py`

**Coverage:** 16 automated tests

**Test Categories:**
1. **Contact Info Validation**
   - Correct info injected
   - No placeholder contact details

2. **Placeholder Detection**
   - Catches [bracketed text]
   - Catches [Capitalized Text]
   - Catches common placeholder patterns

3. **API Integration**
   - Retry logic works
   - Exponential backoff verified
   - Error handling tested

4. **Format Generation**
   - PDF generation succeeds
   - DOCX generation succeeds
   - Markdown parsing correct

5. **Data Validation**
   - Career data structure valid
   - Conflict detection works

**Running Tests:**
```bash
python test_hallucination_detection.py
```

---

## Deployment Architecture

### User Workflow
```
Desktop/Resume_Tailor.exe
         ↓
   Embedded Python + Dependencies
         ↓
   Reads: .env (API key)
         ↓
   Writes: C:\Users\watso\OneDrive\Desktop\Jobs\[Company]\
         ↓
   Output Files:
   - Watson_Mulkey_Resume_[Company].pdf
   - Watson_Mulkey_[Company]_CoverLetter.docx
   - Watson_Mulkey_[Company]_CoverLetter.pdf
```

### Environment Configuration
```
ANTHROPIC_API_KEY=sk-ant-...
RESUME_OUTPUT_DIR=C:\Users\watso\OneDrive\Desktop\Jobs  # Optional
```

---

## Architecture Decision Records

### ADR-001: Centralized Configuration (config.py)
**Decision:** Create config.py as single source of truth
**Rationale:** Eliminated 340 lines of duplicate code
**Impact:** Easier maintenance, single place to update contact info
**Date:** 2025-12-17

### ADR-002: Unified Parser (resume_parser.py)
**Decision:** Single parser for all format generators
**Rationale:** Eliminated ~200 lines of duplicate parsing logic
**Impact:** Bug fixes apply to all formats, consistent data model
**Date:** 2025-12-17

### ADR-003: PyInstaller --add-data (not --hidden-import)
**Decision:** Use --add-data for local Python modules
**Rationale:** --hidden-import only works for installed packages
**Impact:** Executable correctly bundles all generators
**Date:** 2025-12-17

### ADR-004: PDF-Only for Resumes
**Decision:** Only generate PDF for resumes (no DOCX)
**Rationale:** User preference - DOCX not needed, reduces clutter
**Impact:** Cleaner output folders, faster generation
**Date:** 2025-12-18

### ADR-005: Multi-Layer Hallucination Prevention
**Decision:** Implement 4-layer validation system
**Rationale:** Single-layer insufficient, placeholders were slipping through
**Impact:** Zero hallucinations in production use
**Date:** 2025-12-17

---

## Component Dependencies

```
resume_tailor_gui.py
└── generator.py
    ├── config.py
    ├── resume_parser.py
    ├── pdf_generator.py
    │   └── reportlab
    ├── docx_generator.py
    │   ├── python-docx
    │   └── resume_parser.py
    ├── html_template.py
    │   └── markdown
    ├── conflict_detector.py
    └── anthropic (Claude API)

resume_tailor.py (CLI)
└── generator.py
    └── (same dependencies as above)

build_executable.bat
└── PyInstaller
    └── Bundles all above + .env
```

---

## Performance Characteristics

- **Generation Time:** 10-15 seconds per application
- **API Calls:** 2-3 per generation (job parsing + resume + cover letter)
- **File I/O:** Minimal (markdown intermediate, final PDF/DOCX)
- **Memory Usage:** ~50MB during generation
- **Executable Size:** 36MB standalone
- **Startup Time:** ~2 seconds (GUI)

---

## Security Considerations

1. **API Key Storage:** .env file (not committed to git)
2. **Data Privacy:** All career data in local supermemory
3. **No External Storage:** Only Anthropic API receives data
4. **Local File Generation:** All outputs saved locally
5. **No Telemetry:** No usage tracking or analytics

---

**Generated by BMad Method Document-Project Workflow**
**Scan Level:** Deep
**Date:** 2025-12-23
