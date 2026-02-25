# Resume Tailor - AI Resume Generator

## Tech Stack
- **Language**: Python 3.11+
- **AI**: Anthropic Claude API (via `anthropic` SDK)
- **Output**: DOCX (python-docx), HTML
- **GUI**: Tkinter (`resume_tailor_gui.py`)
- **Executable**: PyInstaller

## Architecture
- CLI entry point: `resume_tailor.py`
- GUI entry point: `resume_tailor_gui.py`
- Core generation: `generator.py` (ResumeGenerator class)
- Career data: `career_data_manager.py` + `career_data.json`
- Per-job bullet isolation: generates bullets for each job independently to prevent achievement misattribution
- Provenance tracing: `provenance.py` + `trace_validator.py`

## Key Files
- `resume_tailor.py` - CLI with `--job`, `--trace` flags
- `resume_tailor_gui.py` - Tkinter GUI with TRACE checkbox
- `generator.py` - Two-phase generation (per-job bullets then assembly)
- `career_data_manager.py` - Career data loading/retrieval
- `career_data.json` - Structured career history
- `trace_validator.py` - Validates achievements aren't misattributed
- `build_executable.bat` - PyInstaller build script

## Key Design Decisions
- **Per-job isolation**: Both resume bullets AND cover letter talking points generated with ONLY that job's context (prevents LLM cross-contamination)
- **Two-phase generation**: Phase 1 generates per-job content in isolation, Phase 2 assembles final document
- **Non-blocking validation**: Trace document warns but doesn't prevent generation
- **Provenance tracing on by default**: Use `--no-trace` to disable

## Dev Commands
```bash
# Generate resume (tracing enabled by default)
python resume_tailor.py --job path/to/job.txt

# Disable tracing
python resume_tailor.py --job path/to/job.txt --no-trace

# Run tests
pytest

# Build executable
.\build_executable.bat
```

## Current Status
- Provenance tracing fully implemented and enabled by default
- Achievement misattribution resolved for both resume AND cover letter
- Education/certifications loaded from CareerData (not hardcoded)
- Path validation on `--job` argument
- Filename sanitization for output files

## Known Issues
- GUI blocks during generation (no threading)
