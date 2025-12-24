# Resume Tailor - Documentation Index

**Generated:** 2025-12-23
**Project Type:** Desktop Application (Python GUI)
**Primary Entry:** Resume_Tailor.exe (Windows Executable)
**Status:** Production - Active Use

---

## Quick Reference

### Project Overview
- **Type:** Monolith - Single cohesive Python codebase
- **Primary Language:** Python 3.13.3
- **Framework:** tkinter (retro terminal aesthetic)
- **Architecture:** Layered multi-module desktop application
- **Distribution:** PyInstaller standalone executable (36MB)
- **AI Model:** Anthropic Claude Sonnet 4

### Tech Stack Summary
| Component | Technology |
|-----------|-----------|
| GUI | tkinter |
| AI/API | Anthropic Claude Sonnet 4 |
| PDF Generation | ReportLab 4.0.0+ |
| DOCX Generation | python-docx |
| HTML Generation | markdown |
| Build Tool | PyInstaller |
| Testing | Python unittest (16 tests) |

### Entry Points
- **Primary:** `Resume_Tailor.exe` (dist/) - Windows GUI executable ⭐
- **GUI Source:** `resume_tailor_gui.py` - Retro terminal interface
- **CLI:** `resume_tailor.py` - Command-line alternative

### Core Architecture Pattern
**Multi-Layer Desktop Application:**
1. **GUI Layer** - tkinter retro terminal interface
2. **Orchestration Layer** - generator.py (main pipeline)
3. **Format Generation Layer** - PDF, DOCX, HTML generators
4. **Validation Layer** - Anti-hallucination checks
5. **API Layer** - Claude Sonnet 4 integration with retry logic
6. **Data Layer** - Supermemory career data (29 entries)

---

## Generated Documentation

### Core Documentation
- **[Project Overview](./project-overview.md)** - Executive summary, features, metrics
- **[Architecture](./architecture.md)** - System design, component breakdown, anti-hallucination architecture ⭐
- **[Source Tree Analysis](./source-tree-analysis.md)** - Annotated directory structure, file breakdown
- **[Development Guide](./development-guide.md)** - Setup, build process, testing, troubleshooting

### Component Documentation
#### GUI Components
- **ResumeTailorGUI** (resume_tailor_gui.py) - Main GUI class
  - Job description text area
  - Company name entry
  - AI model selector (Sonnet-4 / Haiku)
  - Output checkboxes (Resume / Cover Letter)
  - Generate button
  - Status log panel

#### Core Modules
- **ResumeGenerator** (generator.py) - Orchestration engine ⭐
- **config.py** - Centralized configuration (contact info, API settings, output prefs) ⭐
- **resume_parser.py** - Unified markdown parser (single source of truth) ⭐

#### Format Generators
- **pdf_generator.py** - ReportLab PDF generation (modern professional layout)
- **docx_generator.py** - python-docx Word generation (ATS-optimized)
- **html_template.py** - markdown HTML generation (intermediate format)

#### Data & Utilities
- **import_career_data.py** - Career data import script (29 entries)
- **conflict_detector.py** - Data validation and consistency checks
- **JobDescriptionParser** (generator.py) - Job requirement extraction

---

## Existing Documentation

- **[README.md](../README.md)** - User-facing project documentation
- **[STATUS.md](../STATUS.md)** - Project status and next steps
- **[GUI_README.md](../GUI_README.md)** - GUI quick start guide
- **[ATS_OPTIMIZATION_GUIDE.md](../ATS_OPTIMIZATION_GUIDE.md)** - ATS optimization best practices
- **[.claude/skills/resume-tailor/README.md](../.claude/skills/resume-tailor/README.md)** - Custom Claude skill documentation

---

## Getting Started

### For New Developers
1. Read [Project Overview](./project-overview.md) (5 min)
2. Review [Architecture](./architecture.md) - Focus on anti-hallucination architecture (15 min)
3. Follow [Development Guide](./development-guide.md) - Installation & setup (10 min)
4. Run test suite: `python test_hallucination_detection.py`
5. Generate test resume: `python resume_tailor.py --job test_job.txt --verbose`

### For Planning New Features
1. **Read Architecture First:** [architecture.md](./architecture.md) - Understand constraints ⭐
2. **Check Retrospective Learnings:** See "Critical Learnings" in [project-overview.md](./project-overview.md)
3. **Review Anti-Hallucination System:** Critical constraint for any new features
4. **Consult Git History:** Recent commits show evolution and fixes

### For Bug Fixes
1. Check [architecture.md](./architecture.md) - Component responsibilities
2. Run tests: `python test_hallucination_detection.py`
3. Check git history: `git log --oneline -10`
4. Review recent fixes in commit messages

---

## Key Architectural Constraints

### 1. **Zero-Hallucination Requirement** ⚠️ CRITICAL
All new features MUST maintain multi-layer validation:
- Layer 1: Retrieval-only data (supermemory facts only)
- Layer 2: Contact info injection (hardcoded fallback)
- Layer 3: Placeholder detection (regex validation)
- Layer 4: Error surfacing (no silent failures)

**See:** [architecture.md](./architecture.md) - "Anti-Hallucination Architecture" section

### 2. **Centralized Configuration** ⚠️ CRITICAL
All configuration goes through `config.py`:
- Contact information (single source of truth)
- API settings (model, tokens, retries)
- Output preferences (formats, cleanup)

**Impact:** Never duplicate config - always import from config.py

### 3. **Unified Parser Pattern** ⚠️ CRITICAL
All format generators use `resume_parser.py`:
- Single source of truth for markdown parsing
- Returns `ResumeData` dataclass
- Eliminates code duplication

**Impact:** Parser changes automatically apply to all formats

### 4. **PyInstaller Bundling Rules** ⚠️ IMPORTANT
- Use `--add-data` (NOT `--hidden-import`) for local .py files
- Bundle .env file for API key
- Use `--windowed` to hide console

**See:** [development-guide.md](./development-guide.md) - "Building Executable" section

### 5. **Clean Output Requirement**
- Resume: PDF only (no DOCX clutter)
- Cover Letter: DOCX + PDF
- Auto-cleanup intermediate .md and .html files

**User Preference:** Clean folders, no clutter

---

## Critical Learnings (From Retrospective)

### ✅ Proven Approaches
- **Sample First:** Get user review of sample output before expanding scope
- **Multi-Layer Validation:** 4-layer anti-hallucination system works reliably
- **Code Centralization:** config.py and resume_parser.py reduced ~340 lines
- **Retry Logic:** Exponential backoff essential for API reliability
- **ReportLab:** Proven reliable for professional PDF generation

### ❌ Mistakes to Avoid
- **Placeholder Templates:** CRITICAL - validate before saving to prevent hallucinations
- **PyInstaller --hidden-import:** Doesn't work for local files, use --add-data
- **Output Clutter:** User wants only final .pdf and .docx files
- **Silent Failures:** All errors must surface in GUI log

### 👤 User Preferences
- **GUI Over CLI:** Primarily uses Resume_Tailor.exe, not command line
- **Bug Fixes First:** Prioritize fixing issues before adding features
- **Semicolons:** Writing style uses semicolons, not em-dashes
- **Quality Over Speed:** Prefers Sonnet-4 accuracy over Haiku speed

**See:** [project-overview.md](./project-overview.md) - "Critical Learnings (Retro)" section

---

## Architecture Decision Records

### ADR-001: Centralized Configuration (config.py)
**Date:** 2025-12-17
**Decision:** Create config.py as single source of truth
**Impact:** Eliminated 340 lines of duplication

### ADR-002: Unified Parser (resume_parser.py)
**Date:** 2025-12-17
**Decision:** Single parser for all format generators
**Impact:** Eliminated ~200 lines, bug fixes apply universally

### ADR-003: PyInstaller --add-data Pattern
**Date:** 2025-12-17
**Decision:** Use --add-data for local modules, not --hidden-import
**Impact:** Executable correctly bundles all generators

### ADR-004: PDF-Only for Resumes
**Date:** 2025-12-18
**Decision:** Only generate PDF for resumes (no DOCX)
**Impact:** Cleaner output, faster generation, user preference

### ADR-005: Multi-Layer Hallucination Prevention
**Date:** 2025-12-17
**Decision:** Implement 4-layer validation system
**Impact:** Zero hallucinations in production use

**See:** [architecture.md](./architecture.md) - "Architecture Decision Records" section

---

## Data Architecture

### Career Data in Supermemory (29 Entries)
- **Job History:** 6 entries (companies, titles, responsibilities)
- **Achievements:** 6 entries (metrics, context, methods, scope)
- **Skills:** 7 entries (evidence-based, tool-specific examples)
- **Writing Style:** 1 entry (tone patterns, common phrases)
- **Personal Values:** 3 entries (mission alignment, stories)
- **Education:** Degrees, certifications

**Storage Location:** Supermemory (external MCP server)
**Import Script:** `import_career_data.py`

### Job Description Data Model
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

**See:** [architecture.md](./architecture.md) - "Data Architecture" section

---

## Testing

### Test Suite: test_hallucination_detection.py
**Coverage:** 16 automated tests
**Command:** `python test_hallucination_detection.py`

**Test Categories:**
1. Contact info validation
2. Placeholder detection (anti-hallucination)
3. API integration and retry logic
4. Format generation (PDF, DOCX)
5. Data validation and consistency

**Status:** All passing ✅

**See:** [development-guide.md](./development-guide.md) - "Testing" section

---

## Build & Deployment

### Building the Executable
```bash
# One-click build
build_executable.bat

# Output
dist\Resume Tailor.exe  # 36MB standalone
```

### Deployment
1. Copy `Resume Tailor.exe` to desktop
2. Double-click to launch
3. No Python installation required on target machine

**See:** [development-guide.md](./development-guide.md) - "Building Executable" section

---

## Common Development Workflows

### Adding New Career Data
1. Edit `import_career_data.py` - Add achievement/job/skill
2. Run: `python import_career_data.py`
3. Verify in supermemory

### Modifying PDF Layout
1. Edit `pdf_generator.py` - Adjust spacing constants
2. Test: `python resume_tailor.py --job test_job.txt --resume-only`
3. Compare with baseline

### Changing AI Prompts
1. Edit `generator.py` - Search for `content": f"""`
2. Test with validation: `python test_hallucination_detection.py`
3. Verify no placeholders in output

### Updating Contact Info
1. Edit `config.py` - DEFAULT_CONTACT dictionary
2. Rebuild if using .exe: `build_executable.bat`

**See:** [development-guide.md](./development-guide.md) - "Common Development Tasks" section

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "No module named 'anthropic'" | `pip install -r requirements.txt` |
| "API key not found" | Create `.env` with `ANTHROPIC_API_KEY=sk-ant-...` |
| Placeholder text detected | Expected! AI tried to hallucinate - add more supermemory data |
| .exe doesn't generate PDF | Rebuild with `build_executable.bat` |
| GUI window too small | Edit `resume_tailor_gui.py`: `self.root.geometry("1000x850")` |

**Full Troubleshooting:** [development-guide.md](./development-guide.md) - "Troubleshooting" section

---

## Git Repository Info

### Recent Commits
```
cf0e94f - PDF design optimization (spacing, Unicode symbols)
5ec0d6b - Refactoring (config.py, resume_parser.py)
af13866 - Semicolons, remove DOCX, verify metrics
345a243 - Add cover letter formats, cleanup
41d0485 - CRITICAL FIX: Placeholder detection
```

### Branch Structure
- **main** - Production branch (current)

### Ignored Files
- `.env` (API keys)
- `dist/` (executables)
- `output/` (generated files)
- `__pycache__/` (Python cache)

---

## Project Metrics

- **Total Lines of Code:** ~4,500 (core codebase)
- **Test Coverage:** 16 automated tests
- **Career Data:** 29 entries in supermemory
- **Executable Size:** 36MB
- **Generation Time:** 10-15 seconds per application
- **Cost per Generation:** ~$0.10 (Sonnet-4), ~$0.01 (Haiku)
- **Code Duplication Eliminated:** ~340 lines (via refactoring)

---

## Next Steps (From STATUS.md)

### Current Focus
- ✅ Core generation working
- ✅ GUI functional
- ✅ Executable builds correctly
- ✅ Zero hallucinations achieved
- ✅ Multi-format output (PDF, DOCX)

### Future Enhancements (Post-MVP)
- [ ] Web interface for non-technical use
- [ ] Batch processing for multiple jobs
- [ ] Interview prep from resume data
- [ ] Salary negotiation talking points
- [ ] LinkedIn profile optimizer

**See:** [STATUS.md](../STATUS.md) for complete status

---

## BMad Workflow Status

**Current Phase:** Prerequisite - Documentation ✅
**Next Phase:** Phase 1 - Planning (PRD)

**Workflow File:** `bmm-workflow-status.yaml`
**Track:** BMad Method (brownfield)
**Project Type:** Desktop Application

**See:** `bmm-workflow-status.yaml` for full workflow tracking

---

## Documentation Usage Guide

### For AI-Assisted Development
**Primary Entry Point:** This file (index.md)

**Recommended Reading Order:**
1. index.md (this file) - Quick reference and navigation
2. architecture.md - System design and constraints ⭐
3. project-overview.md - Executive summary and learnings
4. development-guide.md - Practical development tasks

### For Writing PRDs (Next Phase)
**Critical Reading:**
1. architecture.md - Anti-hallucination constraints
2. project-overview.md - Success criteria and user preferences
3. Git commit messages - Evolution and fixes

**Key Constraints to Remember:**
- Multi-layer validation required
- Centralized configuration pattern
- Unified parser for all formats
- Clean output requirement

### For Implementation Planning
**Reference:**
1. architecture.md - Component responsibilities
2. source-tree-analysis.md - Where to make changes
3. development-guide.md - Build and test procedures

---

## Contact & Support

**Developer:** Watson Mulkey
**Project Location:** `C:\Users\watso\Dev\resume-tailor`
**Documentation Location:** `C:\Users\watso\Dev\resume-tailor\_bmad-output`

**Issue Tracking:** Git commit messages track all fixes and enhancements

---

**Generated by BMad Method Document-Project Workflow**
**Scan Level:** Deep
**Scan Date:** 2025-12-23
**Documentation Completeness:** Comprehensive ✅

**This index serves as the primary entry point for AI-assisted development. All other documentation files are linked from here.**
