# Resume Tailor - Source Tree Analysis

**Generated:** 2025-12-23
**Project:** Resume Tailor Desktop Application

---

## Annotated Directory Structure

```
resume-tailor/                     # Project root
│
├── 📦 EXECUTABLES & BUILD
│   ├── Resume_Tailor.exe          # ⭐ PRIMARY ENTRY - Windows executable (36MB)
│   ├── build_executable.bat      # PyInstaller build script
│   ├── Resume_Tailor.spec         # PyInstaller configuration
│   ├── dist/                      # Built executables directory
│   └── build/                     # PyInstaller temp build files
│
├── 🎨 USER INTERFACE
│   ├── resume_tailor_gui.py       # ⭐ GUI APPLICATION - Retro terminal interface
│   └── resume_tailor.py           # CLI alternative entry point
│
├── ⚙️ CORE GENERATION LOGIC
│   ├── generator.py               # ⭐ ORCHESTRATION - Main generation pipeline
│   ├── resume_parser.py           # ⭐ UNIFIED PARSER - Markdown → structured data
│   └── config.py                  # ⭐ CONFIGURATION - Single source of truth
│
├── 📄 FORMAT GENERATORS
│   ├── pdf_generator.py           # ReportLab PDF generation
│   ├── docx_generator.py          # python-docx Word generation
│   └── html_template.py           # Markdown HTML generation
│
├── 🗄️ DATA & UTILITIES
│   ├── import_career_data.py      # Career data import script (29 entries)
│   ├── conflict_detector.py       # Data validation and consistency checks
│   └── data/                      # Career data storage (in supermemory)
│
├── 🧪 TESTING
│   ├── test_hallucination_detection.py  # Test suite (16 tests)
│   └── .pytest_cache/             # Pytest cache directory
│
├── 📝 DOCUMENTATION
│   ├── README.md                  # Main project documentation
│   ├── STATUS.md                  # Project status and next steps
│   ├── GUI_README.md              # GUI quick start guide
│   ├── ATS_OPTIMIZATION_GUIDE.md  # ATS best practices
│   └── _bmad-output/              # BMad methodology documentation
│       ├── bmm-workflow-status.yaml
│       ├── project-overview.md
│       ├── architecture.md
│       └── source-tree-analysis.md  # This file
│
├── 📂 OUTPUT & SAMPLES
│   ├── output/                    # Generated resumes & cover letters
│   ├── test_debug.pdf             # PDF generation test sample
│   ├── test_direct_call.pdf       # Direct PDF call test sample
│   └── test_sharebite_job.txt     # Test job description
│
├── 📋 JOB DESCRIPTION SAMPLES
│   ├── classdojo_job.txt          # ClassDojo PM job posting
│   ├── metabase_job.txt           # Metabase PM job posting
│   └── test_job.txt               # Generic test job posting
│
├── 📚 REFERENCE DATA
│   ├── ai_skills_assessment.txt   # AI/ML skills documentation
│   ├── linkedin_recommendations.txt  # LinkedIn recommendations export
│   └── new_skills_to_add.txt      # Skills to add to supermemory
│
├── ⚙️ CONFIGURATION
│   ├── .env                       # Environment variables (API keys) - NOT COMMITTED
│   ├── .gitignore                 # Git ignore rules
│   ├── requirements.txt           # Python dependencies
│   └── .claude/                   # Claude Code configuration
│       └── skills/
│           └── resume-tailor/     # Custom resume-tailor skill
│
└── 🔧 BMad METHODOLOGY
    └── _bmad/                     # BMad Method framework
        ├── bmm/                   # BMad Method Module
        ├── bmb/                   # BMad Builder Module
        └── core/                  # Core BMad components
```

---

## Critical Files Breakdown

### Primary Entry Points

#### **Resume_Tailor.exe** (dist/)
- **Type:** Windows Executable
- **Size:** 36MB standalone
- **Contents:** Bundled Python + all dependencies + .env
- **Purpose:** PRIMARY USER ENTRY - Double-click to launch
- **Build:** Created by `build_executable.bat`

#### **resume_tailor_gui.py**
- **Type:** Python GUI Application
- **Framework:** tkinter
- **Style:** Retro terminal aesthetic (green-on-black)
- **Purpose:** Main GUI interface source
- **Dependencies:** generator.py, tkinter
- **Lines:** ~400

#### **resume_tailor.py**
- **Type:** Python CLI Script
- **Purpose:** Alternative command-line interface
- **Usage:** `python resume_tailor.py --job job.txt --verbose`
- **Dependencies:** generator.py, argparse
- **Lines:** ~200

---

### Core Generation Pipeline

#### **generator.py** ⭐ CRITICAL
- **Type:** Core Orchestration Module
- **Class:** `ResumeGenerator`
- **Responsibilities:**
  - Job description parsing
  - Supermemory retrieval orchestration
  - Claude API calls with retry logic
  - Anti-hallucination validation
  - Format generator delegation
  - Contact info injection
- **Dependencies:** anthropic, config.py, all format generators
- **Lines:** ~1300
- **Key Methods:**
  - `generate_resume()`
  - `generate_cover_letter()`
  - `_generate_with_claude()`
  - `validate_generated_content()`

#### **resume_parser.py** ⭐ CRITICAL
- **Type:** Unified Data Parser
- **Purpose:** Single source of truth for markdown parsing
- **Created:** Refactoring on 2025-12-17
- **Impact:** Eliminated ~200 lines of duplicate code
- **Data Structures:**
  - `Job` dataclass
  - `ResumeData` dataclass
- **Used By:** pdf_generator.py, docx_generator.py, html_template.py
- **Lines:** ~190

#### **config.py** ⭐ CRITICAL
- **Type:** Configuration Module
- **Purpose:** Centralized settings and contact info
- **Created:** Refactoring on 2025-12-17
- **Impact:** Eliminated ~340 lines of duplication
- **Domains:**
  - Contact Information (with fallback)
  - API Settings (model, tokens, retries)
  - Output Preferences (formats, cleanup)
  - Dependency Checks
- **Lines:** ~105

---

### Format Generators

#### **pdf_generator.py**
- **Type:** PDF Generation Module
- **Library:** ReportLab 4.0.0+
- **Features:**
  - Modern professional layout
  - Optimized spacing (21% reduction from 2025-12-18)
  - Unicode symbols (★ ▶ ●)
  - WCAG Level AA compliant
  - Company-specific footer
- **Functions:**
  - `generate_pdf_from_data(resume_data)`
  - `generate_cover_letter_pdf(content, company)`
- **Dependencies:** reportlab, resume_parser.py
- **Lines:** ~550

#### **docx_generator.py**
- **Type:** Word Document Generation Module
- **Library:** python-docx
- **Features:**
  - ATS-friendly formatting
  - Markdown parsing support
  - Resume + cover letter variants
- **Functions:**
  - `generate_docx_resume(data)`
  - `generate_docx_cover_letter(content)`
- **Dependencies:** docx, resume_parser.py
- **Lines:** ~350

#### **html_template.py**
- **Type:** HTML Generation Module
- **Library:** markdown
- **Purpose:** Intermediate format (auto-cleaned)
- **Status:** Less used, mainly for debugging
- **Lines:** ~400

---

### Data & Utilities

#### **import_career_data.py**
- **Type:** Data Import Script
- **Purpose:** Populate supermemory with career data
- **Entries:** 29 total
  - 6 job history entries
  - 6 achievements with metrics
  - 7 skills with evidence
  - 3 personal values/stories
  - 2 cover letter examples
  - 1 writing style guide
  - Education & certifications
- **Usage:** Run once to populate supermemory
- **Lines:** ~600

#### **conflict_detector.py**
- **Type:** Data Validation Module
- **Purpose:** Detect inconsistencies in career data
- **Checks:**
  - Date overlaps
  - Duplicate achievements
  - Inconsistent metrics
  - Missing evidence
- **Lines:** ~350

---

### Testing

#### **test_hallucination_detection.py**
- **Type:** Automated Test Suite
- **Framework:** Python unittest
- **Coverage:** 16 tests
- **Categories:**
  - Contact info validation
  - Placeholder detection
  - API integration
  - Format generation
  - Data validation
- **Command:** `python test_hallucination_detection.py`
- **Status:** All passing ✅

---

## File Size Analysis

| File | Lines | Size | Criticality |
|------|-------|------|-------------|
| generator.py | ~1300 | 53KB | ⭐⭐⭐ CRITICAL |
| pdf_generator.py | ~550 | 20KB | ⭐⭐ HIGH |
| import_career_data.py | ~600 | 26KB | ⭐⭐ HIGH |
| resume_tailor_gui.py | ~400 | 17KB | ⭐⭐ HIGH |
| html_template.py | ~400 | 15KB | ⭐ MEDIUM |
| docx_generator.py | ~350 | 10KB | ⭐⭐ HIGH |
| conflict_detector.py | ~350 | 11KB | ⭐ MEDIUM |
| resume_tailor.py | ~200 | 8KB | ⭐ MEDIUM |
| resume_parser.py | ~190 | 7KB | ⭐⭐⭐ CRITICAL |
| config.py | ~105 | 3KB | ⭐⭐⭐ CRITICAL |

**Total Core Codebase:** ~4,500 lines

---

## Critical Directories

### `/dist/`
- **Contains:** Built executables
- **Primary File:** Resume_Tailor.exe (36MB)
- **Build Process:** PyInstaller via build_executable.bat
- **Deployment:** Copy .exe to desktop

### `/output/`
- **Contains:** Generated resumes and cover letters
- **Structure:** `[Company]/` subdirectories
- **Files Per Company:**
  - `Watson_Mulkey_Resume_[Company].pdf`
  - `Watson_Mulkey_[Company]_CoverLetter.docx`
  - `Watson_Mulkey_[Company]_CoverLetter.pdf`
- **Cleanup:** Intermediate .md and .html files auto-deleted

### `/_bmad-output/`
- **Contains:** BMad methodology documentation
- **Files:**
  - `bmm-workflow-status.yaml` - Progress tracking
  - `project-overview.md` - Project summary
  - `architecture.md` - System design
  - `source-tree-analysis.md` - This file
- **Purpose:** Brownfield development planning

### `/.claude/`
- **Contains:** Claude Code configuration
- **Subdir:** `skills/resume-tailor/` - Custom skill
- **Files:**
  - `README.md` - Skill documentation
  - `instructions.md` - Usage instructions

---

## Integration Points

### External Dependencies
```
resume-tailor/
├── Anthropic API
│   └── Claude Sonnet 4 (job parsing + generation)
│
├── Supermemory
│   └── Career data storage (29 entries)
│
└── Local Filesystem
    ├── .env (API keys)
    ├── output/ (generated files)
    └── OneDrive/Desktop/Jobs/[Company]/ (default output)
```

### Data Flow
```
User Input (Job Description)
    ↓
GUI/CLI Entry Point
    ↓
generator.py (Orchestration)
    ↓
├─→ Job Description Parser → Claude API
├─→ Supermemory Search → Retrieve career data
├─→ Claude Generation → AI-generated content
├─→ Validation Layer → Anti-hallucination checks
├─→ Contact Info Injection → Guarantee accuracy
└─→ Format Generators
    ├─→ pdf_generator.py → .pdf file
    ├─→ docx_generator.py → .docx file
    └─→ Cleanup intermediate files
```

---

## Git Status

**Current State:** Local repository with commit history

**Recent Commits:**
1. `cf0e94f` - PDF design optimization (spacing, symbols)
2. `5ec0d6b` - Refactoring (config.py, resume_parser.py)
3. `af13866` - Semicolons, remove DOCX, verify metrics
4. `345a243` - Add cover letter formats, cleanup
5. `41d0485` - CRITICAL FIX: Placeholder detection
6. `d6170af` - Fix PyInstaller bundling
7. `9de67ec` - Fix hidden imports
8. `0d8106a` - Initial commit

**Ignored Files (.gitignore):**
- `.env` (API keys)
- `__pycache__/` (Python cache)
- `dist/` (executables)
- `build/` (build artifacts)
- `.pytest_cache/` (test cache)
- `output/` (generated documents)

---

## Entry Point Usage Patterns

### Primary Usage (GUI)
```
User: Double-click Resume_Tailor.exe
      ↓
GUI launches (resume_tailor_gui.py bundled)
      ↓
Paste job description
      ↓
Click Generate
      ↓
Files appear in output/[Company]/
```

### Secondary Usage (CLI)
```bash
# From command line
python resume_tailor.py --job classdojo_job.txt --company-name "ClassDojo" --verbose

# Or with paste mode
python resume_tailor.py --paste
```

---

## Module Dependency Graph

```
resume_tailor_gui.py
    └── generator.py
        ├── config.py
        ├── anthropic (external)
        ├── resume_parser.py
        ├── pdf_generator.py
        │   ├── reportlab (external)
        │   └── resume_parser.py
        ├── docx_generator.py
        │   ├── docx (external)
        │   └── resume_parser.py
        ├── html_template.py
        │   └── markdown (external)
        ├── import_career_data.py
        └── conflict_detector.py

resume_tailor.py (CLI)
    └── generator.py (same tree as above)

build_executable.bat
    └── PyInstaller (bundles all above)
```

---

**Generated by BMad Method Document-Project Workflow**
**Scan Level:** Deep
**Date:** 2025-12-23
