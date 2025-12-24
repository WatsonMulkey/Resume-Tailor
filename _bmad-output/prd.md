---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - "_bmad-output/index.md"
  - "_bmad-output/project-overview.md"
  - "_bmad-output/architecture.md"
  - "_bmad-output/source-tree-analysis.md"
  - "_bmad-output/development-guide.md"
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 5
workflowType: 'prd'
lastStep: 6
project_name: 'Resume Tailor'
user_name: 'Watso'
date: '2025-12-23'
---

# Product Requirements Document - Resume Tailor

**Author:** Watso
**Date:** 2025-12-23

## Executive Summary

Resume Tailor is evolving from a personal productivity tool into a privacy-first, distributable desktop application for AI-powered resume and cover letter generation. This PRD defines two major feature additions that remove external dependencies and add interactive intelligence with provable anti-hallucination guarantees.

**Current State:** Production desktop app (Resume_Tailor.exe) with multi-layer anti-hallucination validation, generating ATS-optimized resumes and cover letters using career data stored in supermemory MCP server.

**New Features:**

1. **Local Career Data Storage** - Migrate from supermemory to JSON-based local file storage (`career_data.json`) with Pydantic schema validation, eliminating external dependencies and usage limits while maintaining zero-hallucination guarantees.

2. **Interactive Discovery Mode** - Comprehensive real-time skill/experience capture during generation. When job descriptions mention unknown capabilities, the app pauses to collect structured, validated data through a 5-layer anti-hallucination validation system, then enriches the local career data file with verified, concrete examples.

**Strategic Goal:** Transform Resume Tailor from a tool requiring MCP server setup into a standalone, self-contained application with local data storage and zero external dependencies beyond the Claude API.

### What Makes This Special

**Privacy-First Architecture**
- Career data remains entirely on local machine in portable JSON format
- User-controlled file location (survives app reinstalls, enables personal backup strategies)
- Only Claude API calls for generation leave the machine
- Single backup file (`career_data.json.bak`) updated before each write
- Atomic file writes with Pydantic validation prevent corruption
- File timestamp monitoring prevents stale cached data

**Zero Setup Friction**
- No external service dependencies (supermemory, MCP servers)
- Single executable download → ready to use
- Automated migration script converts supermemory data to local JSON (one-time run with retry logic and progress tracking)
- Self-contained system ready for standalone distribution

**Provable Anti-Hallucination Architecture (5 Layers)**

**Layer 1: Structured Prompt Requirements**
- Mandatory fields for all discoveries: company/project, timeframe (YYYY-MM format), specific example (min 20 chars), measurable result
- Multi-step questioning prevents vague responses
- No single-field free-text that allows hallucination

**Layer 2: Consistency Validation**
- Timeframe cross-reference: validates against existing job history dates
- Company verification: must exist in job history or be marked as side project
- Duplicate detection: flags existing skills, offers to add additional examples
- Sanity checks: prevents future dates, unreasonable timeframes

**Layer 3: Review Mode**
- Shows all proposed additions before saving
- Displays consistency check results
- User can Save/Edit/Discard
- Final confirmation gate before data persistence

**Layer 4: Format Validation**
- Pydantic models enforce schema (type safety + validation)
- Timeframe format validation (regex patterns)
- Example length validation (20-500 characters)
- Skill name validation (prevents generic claims like "team player")

**Layer 5: Hallucination Detection Patterns**
- Flags vague quantifiers ("many", "several", "various")
- Detects unverifiable claims ("best", "world-class", "leading")
- Identifies placeholder text ([...], {...})
- Similarity check: warns if response >70% matches job description (prevents copy-paste)

**Comprehensive Interactive Intelligence**
- Detailed discovery of missing skills/experiences during generation
- Callback-based architecture (discovery is optional, not blocking)
- Structured prompts require concrete examples (company, timeframe, specific results)
- Five-layer validation ensures factual accuracy
- Review mode shows all additions before saving
- Automatically enriches career data with rich, validated context for future applications

**Scalability Without Limits**
- No usage caps from free-tier external services
- No risk of losing career data access
- In-memory caching with file timestamp invalidation maintains performance
- File-based architecture simple to backup and migrate

## Project Classification

**Technical Type:** desktop_app (Python GUI with PyInstaller distribution)

**Domain:** general (productivity/career tools)

**Complexity:** Medium (file I/O, data validation, interactive workflows, multi-layer validation)

**Project Context:** Brownfield - extending existing Resume Tailor system

**Architecture Constraints:**
- Must maintain existing 4-layer anti-hallucination validation PLUS add 5-layer discovery validation
- Must use centralized config.py pattern
- Must use unified parser approach (resume_parser.py)
- Must preserve existing GUI/CLI dual interface
- Must maintain clean output requirement (PDF/DOCX only)

**Architecture Impact:**

**New Module:** `career_discovery.py`
- Optional callback (not blocking pipeline step)
- Detects missing skills via keyword/semantic matching against career_data.json
- Prompts user via GUI dialog with structured multi-step questions (tkinter)
- Implements 5-layer validation system:
  - Layer 1: Structured prompts with required fields
  - Layer 2: Consistency checks against job history
  - Layer 3: Review mode with Save/Edit/Discard options
  - Layer 4: Pydantic format validation
  - Layer 5: Hallucination pattern detection
- Returns enriched, validated context to generation pipeline

**New Module:** `career_data_manager.py`
- Handles all career_data.json I/O operations
- Pydantic models for schema enforcement (CareerData, Job, Achievement, Skill)
- Atomic writes with validation (prevents corruption)
- Single backup file (`career_data.json.bak`) updated before each write
- In-memory caching with file timestamp checking (reloads if modified externally)
- User-configurable file location (stored in config.py)
- Rollback capability if write fails validation

**New Script:** `migrate_from_supermemory.py`
- One-time migration utility with resilience features
- Queries supermemory MCP for all career entries
- Retry logic with exponential backoff (handles API limits)
- Progress tracking and resume capability
- Validation report (shows entry counts, flags missing categories)
- Preview before final save
- Rollback on failure

**Modified Modules:**
- `generator.py` - Add optional discovery_callback parameter, use career_data_manager with timestamp checking
- `config.py` - Add CAREER_DATA_FILE path (user-configurable), BACKUP_ENABLED, CACHE settings
- `resume_tailor_gui.py` - Discovery mode always enabled, add "Restore from backup" menu option

**New Files:**
- `career_data.json` - Local storage (replaces supermemory)
- `career_data.json.bak` - Single backup file
- `career_discovery.py` - Interactive discovery with 5-layer validation
- `career_data_manager.py` - File I/O, backup, and Pydantic validation
- `migrate_from_supermemory.py` - Resilient migration utility

**Data Format:** JSON with Pydantic validation (matches existing import_career_data.py structure)

**Discovery Callback Pattern:**
```python
# Optional discovery - not blocking pipeline
generator.generate(
    job_description,
    discovery_callback=career_discovery.prompt_user if discovery_enabled else None
)
```

**Migration Scope:**
- One-time automated migration from supermemory (29 entries) via resilient migration script
- Populate career_data.json with Pydantic validation
- Remove supermemory dependency from codebase
- Add backup/restore infrastructure with rollback capability
- Add 5-layer discovery validation system (structured prompts, consistency checks, review mode, Pydantic validation, hallucination detection)

**Risk Mitigations Integrated:**
- ✅ Single backup file prevents data loss (negligible space overhead)
- ✅ Atomic writes with Pydantic validation prevent corruption
- ✅ Rollback capability if validation fails
- ✅ User-controlled file location survives reinstalls
- ✅ Migration script with retry logic and progress tracking
- ✅ 5-layer validation system prevents hallucinations (PROVEN, not claimed)
- ✅ Consistency checks validate against job history
- ✅ Review mode before saving discoveries
- ✅ File timestamp checking prevents stale cached data
- ✅ Discovery as optional callback (doesn't block generation)

---

## Detailed Feature Requirements

### Feature 1: Local Career Data Storage

**Objective:** Replace supermemory MCP dependency with privacy-first, user-controlled local JSON storage.

#### 1.1 Data Structure (Pydantic Models)

```python
class Achievement(BaseModel):
    description: str = Field(min_length=20, max_length=500)
    company: str = Field(min_length=1)
    timeframe: str = Field(pattern=r"^\d{4}-\d{2}$|^\d{4}-\d{2} to \d{4}-\d{2}$")
    result: Optional[str] = Field(max_length=200)
    metrics: Optional[List[str]] = []

class Skill(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category: str  # technical, soft, domain
    proficiency: str  # beginner, intermediate, advanced, expert
    examples: List[Achievement] = Field(min_items=1)
    last_used: str = Field(pattern=r"^\d{4}-\d{2}$")

class Job(BaseModel):
    company: str
    title: str
    start_date: str = Field(pattern=r"^\d{4}-\d{2}$")
    end_date: Optional[str] = Field(pattern=r"^\d{4}-\d{2}$|^Present$")
    description: str
    achievements: List[Achievement] = []
    skills_used: List[str] = []

class CareerData(BaseModel):
    version: str = "1.0"
    last_updated: datetime
    jobs: List[Job] = []
    skills: List[Skill] = []
    education: List[Dict] = []
    certifications: List[Dict] = []
    projects: List[Dict] = []
```

#### 1.2 File Operations (career_data_manager.py)

**Load Operation:**
```python
def load_career_data() -> CareerData:
    """
    Load career data with caching and timestamp validation.

    Features:
    - In-memory cache for performance
    - File timestamp checking (reloads if modified)
    - Automatic schema migration if version mismatch
    - Creates default structure if file missing
    """
    if cache_valid():
        return _cache

    data = read_json(CAREER_DATA_FILE)
    validated = CareerData(**data)  # Pydantic validation
    update_cache(validated)
    return validated
```

**Save Operation:**
```python
def save_career_data(data: CareerData) -> bool:
    """
    Atomic write with backup and rollback.

    Process:
    1. Validate data with Pydantic (raises if invalid)
    2. Create backup (career_data.json.bak)
    3. Write to temp file (career_data.json.tmp)
    4. Validate temp file can be read
    5. Atomic rename (replaces original)
    6. Update cache timestamp
    7. Return True

    On failure:
    - Restore from backup if corrupted
    - Return False with error log
    """
```

**Configuration:**
```python
# config.py additions
CAREER_DATA_FILE = os.getenv('CAREER_DATA_FILE',
                              os.path.join(os.path.expanduser('~'), '.resume_tailor', 'career_data.json'))
BACKUP_ENABLED = True
CACHE_ENABLED = True
CACHE_TTL_SECONDS = 300  # 5 minutes
```

#### 1.3 Migration Script (migrate_from_supermemory.py)

**Resilience Features:**
- Retry logic with exponential backoff (max 5 attempts)
- Progress tracking (saves checkpoint after each 5 entries)
- Resume capability (can continue from checkpoint)
- Validation report before final commit
- Preview mode (shows what will be migrated)
- Rollback on failure

**Execution Flow:**
```
1. Query supermemory for all career entries
2. Parse into structured format (jobs, skills, achievements)
3. Validate with Pydantic models
4. Show preview report:
   - Total entries: 29
   - Jobs: 8
   - Skills: 45
   - Achievements: 67
   - Missing categories flagged
5. User confirmation
6. Create backup of existing data (if any)
7. Write with atomic save
8. Verify read-back succeeds
9. Success confirmation
```

**Error Handling:**
- API timeout → retry with backoff
- Invalid data → skip entry + log warning
- Duplicate entries → merge or keep latest
- Write failure → restore from backup

#### 1.4 Acceptance Criteria

- ✅ All career data stored in user-controlled JSON file
- ✅ File location configurable via environment variable
- ✅ Pydantic validation prevents corrupted data
- ✅ Single backup file updated before each write
- ✅ Atomic writes with rollback capability
- ✅ In-memory caching with timestamp invalidation
- ✅ Migration script successfully converts all 29 supermemory entries
- ✅ Zero supermemory dependencies in final codebase
- ✅ File survives app reinstalls (user-controlled location)
- ✅ Performance: load/save operations < 100ms for 100 entries

---

### Feature 2: Interactive Discovery Mode

**Objective:** Capture missing skills and experiences during generation with provable anti-hallucination validation.

#### 2.1 Discovery Trigger Logic (career_discovery.py)

**Detection Strategy:**
```python
def detect_missing_skills(job_description: str, career_data: CareerData) -> List[str]:
    """
    Identify skills in job description not in career data.

    Methods:
    1. Keyword extraction (spaCy NER + custom rules)
    2. Semantic matching (embedding similarity < 0.7)
    3. Technology detection (regex patterns for frameworks, tools)
    4. Domain-specific terms (ML, cloud, etc.)

    Returns: List of candidate skills to prompt user about
    """
```

**Prompt Timing:**
- After job description loaded
- Before generation starts
- Non-blocking (user can skip)
- Batched (max 5 prompts per session)

#### 2.2 Five-Layer Validation System

**Layer 1: Structured Prompt Requirements**

Multi-step dialog prevents vague responses:

```
Step 1: "Do you have experience with [SKILL]?" (Yes/No)
Step 2: "Which company or project did you use [SKILL]?" (Required text, min 2 chars)
Step 3: "What timeframe? (YYYY-MM format)" (Required, validated regex)
Step 4: "Describe specific example (minimum 20 characters)" (Required text area)
Step 5: "What was the measurable result?" (Optional but encouraged)
```

**Mandatory Fields:**
- Company/Project (prevents generic claims)
- Timeframe (anchors to reality)
- Specific Example (min 20 chars, prevents one-word responses)

**Layer 2: Consistency Validation**

```python
def validate_consistency(response: Dict, career_data: CareerData) -> ValidationResult:
    """
    Cross-reference against existing data.

    Checks:
    1. Timeframe within job history dates
    2. Company exists in job history OR marked as side project
    3. Skill not already documented (offer to add example if exists)
    4. No future dates
    5. Timeframe reasonable (<10 years ago for new skills)
    """
```

**Warning Examples:**
- ⚠️ "This company isn't in your job history. Is this a side project?"
- ⚠️ "This timeframe is outside your employment at {company}. Correct?"
- ⚠️ "You already have {skill} listed. Add this as another example?"

**Layer 3: Review Mode**

Before saving, show formatted preview:

```
────────────────────────────────────────
PROPOSED ADDITION
────────────────────────────────────────
Skill: PostgreSQL Database Design
Company: Foil Industries
Timeframe: 2023-06 to 2024-03
Example: Designed normalized schema for multi-tenant
         SaaS application, reducing query times by 40%
Result: 40% faster queries, 99.9% uptime
────────────────────────────────────────
Consistency Checks:
✅ Timeframe matches job history
✅ Company verified
⚠️  Similar skill "SQL Databases" already exists

[Save]  [Edit]  [Discard]
────────────────────────────────────────
```

**Layer 4: Format Validation (Pydantic)**

```python
class DiscoveredSkill(BaseModel):
    name: str = Field(min_length=2, max_length=100,
                     pattern=r"^[A-Za-z0-9\s\.\-\+#]+$")  # No generic phrases
    company: str = Field(min_length=1)
    timeframe: str = Field(pattern=r"^\d{4}-\d{2}( to \d{4}-\d{2})?$")
    example: str = Field(min_length=20, max_length=500)
    result: Optional[str] = Field(max_length=200)

    @validator('name')
    def validate_skill_name(cls, v):
        banned_generic = ['team player', 'hard worker', 'quick learner',
                          'detail oriented', 'self motivated']
        if v.lower() in banned_generic:
            raise ValueError(f"'{v}' is too generic. Specify technical skill.")
        return v

    @validator('example')
    def validate_example_quality(cls, v):
        if len(v.split()) < 5:
            raise ValueError("Example too short. Provide specific context.")
        return v
```

**Layer 5: Hallucination Detection Patterns**

```python
def detect_hallucination_patterns(text: str, job_description: str) -> List[str]:
    """
    Flag suspicious patterns in user responses.

    Red Flags:
    1. Vague quantifiers: "many", "several", "various", "numerous"
    2. Unverifiable claims: "best", "world-class", "leading", "cutting-edge"
    3. Placeholder text: "[...]", "{...}", "TBD", "TODO"
    4. >70% similarity to job description (copy-paste detection)
    5. Repeated phrases from job posting
    6. Future tense verbs (suggests not done yet)

    Returns: List of warnings to show user
    """
```

**Warning Display:**
```
⚠️  HALLUCINATION WARNINGS:
- Contains vague quantifier "many projects"
- 75% similarity to job description (possible copy-paste)
- Phrase "cutting-edge technology" is unverifiable

Consider revising for specificity.
```

#### 2.3 User Interface (tkinter dialogs)

**Discovery Dialog:**
- Modal window (blocks generation)
- Progress indicator (e.g., "Question 2 of 5")
- Field-by-field validation (immediate feedback)
- Character counter on text areas
- Examples shown for each field
- Skip button (user can defer)

**Review Dialog:**
- Side-by-side: Proposed vs Existing data
- Color-coded consistency checks (green ✅, yellow ⚠️, red ❌)
- Edit button opens original dialog pre-filled
- Discard returns to generation without saving
- Save persists to career_data.json atomically

#### 2.4 Integration with Generation Pipeline

**Callback Architecture:**
```python
# In generator.py
def generate_resume(job_description: str,
                    discovery_callback: Optional[Callable] = None):
    """
    Optional discovery callback doesn't block generation.

    Flow:
    1. Load career data
    2. If discovery_callback provided:
       a. Detect missing skills
       b. Prompt user (via callback)
       c. Validate responses (5 layers)
       d. Save enriched data
       e. Reload career data (with new info)
    3. Proceed with generation using enriched data
    """

    if discovery_callback:
        missing = detect_missing_skills(job_description, career_data)
        if missing:
            discoveries = discovery_callback(missing)  # User interaction
            validated = validate_discoveries(discoveries)  # 5 layers
            career_data = enrich_career_data(career_data, validated)

    # Generation continues with enriched data...
```

**GUI Integration:**
```python
# In resume_tailor_gui.py
discovery_enabled = tk.BooleanVar(value=True)  # Always enabled by default

def generate_clicked():
    callback = career_discovery.prompt_user if discovery_enabled.get() else None
    generator.generate(job_desc.get(), discovery_callback=callback)
```

#### 2.5 Data Enrichment

**Automatic Enhancements:**
- Add discovered skill to career_data.json
- Link to relevant job in job history
- Update last_used timestamp
- Increment example count for skill
- Tag with "discovered_during: {job_title}" metadata

**Future Benefits:**
- Richer career data for next application
- Better keyword matching
- More concrete examples available
- Demonstrates growth over time

#### 2.6 Acceptance Criteria

- ✅ Detects missing skills via keyword + semantic matching
- ✅ Multi-step structured prompts (5 required fields minimum)
- ✅ Layer 1: Mandatory fields enforced (company, timeframe, example)
- ✅ Layer 2: Consistency checks against job history
- ✅ Layer 3: Review mode with Save/Edit/Discard
- ✅ Layer 4: Pydantic validation prevents invalid data
- ✅ Layer 5: Hallucination pattern detection with warnings
- ✅ User can skip discovery (non-blocking)
- ✅ Discoveries persist to career_data.json atomically
- ✅ GUI shows clear validation feedback
- ✅ No generic claims allowed ("team player" blocked)
- ✅ No copy-paste from job description (similarity check)
- ✅ Future-proof: enriched data available for next generation
- ✅ Performance: discovery flow completes in <30 seconds

---

## User Stories and Scenarios

### Primary User Persona: "Sarah - Career Switcher"

**Background:**
- Software developer with 5 years experience
- Applying to 10-15 jobs per week
- Career data spread across LinkedIn, old resumes, mental notes
- Privacy-conscious, doesn't want career data in cloud services
- Frustrated by resume tools that "make stuff up"

**Goals:**
- Generate tailored resumes quickly without setup friction
- Maintain control over career data location
- Build comprehensive career data library over time
- Ensure 100% factual accuracy (zero hallucinations)

---

### User Story 1: First-Time Setup (New User)

**Scenario:** Sarah downloads Resume_Tailor.exe for the first time.

**Flow:**

1. **Double-click executable** → App launches immediately (no installation required)

2. **First launch prompt:**
   ```
   Welcome to Resume Tailor!

   Where would you like to store your career data?

   [Default Location] C:\Users\Sarah\.resume_tailor\career_data.json
   [Custom Location] [Browse...]

   This file will contain your job history, skills, and achievements.
   You control where it lives. It never leaves your machine.

   [Continue]
   ```

3. **Sarah clicks Continue** → File created with empty schema

4. **Data entry options shown:**
   ```
   Your career data file is empty. Let's add your experience:

   Option 1: Import from existing resume (PDF/DOCX) [Not implemented yet]
   Option 2: Manual entry via form [Available]
   Option 3: Build as you go (add skills during generation) [Recommended]

   [Skip for now - I'll add data during my first application]
   ```

5. **Sarah clicks "Skip for now"** → Ready to generate first resume

**Outcome:**
- Zero setup friction
- User understands data location and privacy model
- Can start generating immediately (will be prompted for data during generation)

**Acceptance Criteria:**
- ✅ App launches in <3 seconds
- ✅ File location choice presented clearly
- ✅ Default location explained (no jargon)
- ✅ User can defer data entry
- ✅ Help text emphasizes privacy and local control

---

### User Story 2: Migration from Supermemory (Existing User)

**Scenario:** Sarah has been using Resume Tailor with supermemory MCP (29 entries). New version removes supermemory dependency.

**Flow:**

1. **Launch updated Resume_Tailor.exe**

2. **Migration prompt appears:**
   ```
   ⚡ Migration Available

   We've detected you have career data in supermemory (29 entries).
   This version stores data locally for privacy and reliability.

   Migrate now?
   • All 29 entries will be converted to local JSON
   • Supermemory will no longer be required
   • Backup created before migration
   • Estimated time: 30 seconds

   [Preview Migration] [Migrate Now] [Skip]
   ```

3. **Sarah clicks "Preview Migration"** → Shows report:
   ```
   Migration Preview Report
   ────────────────────────────────────────
   Found in supermemory:
   • Jobs: 8
   • Skills: 45
   • Achievements: 67
   • Projects: 12

   Will be saved to:
   C:\Users\Sarah\.resume_tailor\career_data.json

   Backup location:
   C:\Users\Sarah\.resume_tailor\career_data.json.bak

   ⚠️  Note: 3 entries have incomplete timeframes
           (will use "Unknown" as fallback)

   [Proceed with Migration] [Cancel]
   ```

4. **Sarah clicks "Proceed"** → Progress shown:
   ```
   Migrating... ████████████░░░░ 75% (22/29 entries)

   ✓ Migrated job: Foil Industries
   ✓ Migrated skill: PostgreSQL
   ✓ Migrated skill: Python
   ...
   ```

5. **Migration completes:**
   ```
   ✅ Migration Complete!

   Successfully migrated 29 entries:
   • Jobs: 8 ✓
   • Skills: 45 ✓
   • Achievements: 67 ✓
   • Projects: 12 ✓

   Your career data is now stored locally.
   Supermemory is no longer required.

   Backup saved: career_data.json.bak

   [Continue]
   ```

**Outcome:**
- Seamless transition from supermemory to local storage
- All data preserved with validation
- User understands what happened and why
- Backup created for safety

**Acceptance Criteria:**
- ✅ Auto-detects existing supermemory data
- ✅ Preview shows exactly what will be migrated
- ✅ Progress indicator during migration
- ✅ Retry logic handles API failures gracefully
- ✅ Backup created before any writes
- ✅ Success confirmation with entry counts
- ✅ Migration can be skipped (deferred)

---

### User Story 3: Interactive Discovery During Generation

**Scenario:** Sarah applies for a Senior Backend Engineer role requiring "Kubernetes" (which she has but isn't documented).

**Flow:**

1. **Paste job description** → Click "Generate Resume"

2. **Discovery prompt appears:**
   ```
   💡 Skill Discovery

   The job description mentions skills not in your career data:

   • Kubernetes
   • Docker Compose
   • gRPC

   Would you like to add any of these?

   [Yes, let's add them] [Skip for now]
   ```

3. **Sarah clicks "Yes"** → Multi-step dialog opens:

   **Step 1/5: Confirm Experience**
   ```
   Do you have experience with Kubernetes?

   ( ) Yes, I've used it professionally
   ( ) Yes, in side projects only
   ( ) No / Not sure

   [Next]
   ```

   **Step 2/5: Company/Project**
   ```
   Which company or project did you use Kubernetes?

   [Text input: ___________________]

   Example: "Foil Industries" or "Personal Project: SaaS App"

   [Back] [Next]
   ```
   Sarah enters: "Foil Industries"

   **Step 3/5: Timeframe**
   ```
   What timeframe? (YYYY-MM format)

   Start: [2023-06]
   End:   [2024-03] or [Present]

   [Back] [Next]
   ```

   **Step 4/5: Specific Example**
   ```
   Describe a specific example (minimum 20 characters):

   [Text area - 340 characters remaining]
   ___________________________________________
   ___________________________________________

   Example: "Designed and deployed Kubernetes cluster
   for multi-tenant SaaS app, managing 12 microservices
   with auto-scaling policies that reduced infrastructure
   costs by 30%."

   Character count: 0 / 500

   [Back] [Next]
   ```

   Sarah enters: "Orchestrated migration from Docker Swarm to Kubernetes, managing deployment pipelines for 8 microservices with Helm charts and reducing deployment time from 45 minutes to 8 minutes"

   **Step 5/5: Measurable Result (Optional)**
   ```
   What was the measurable result?

   [Text input: ___________________]

   Examples: "40% faster deployments", "99.9% uptime"

   [Back] [Next]
   ```

   Sarah enters: "82% faster deployments, zero downtime during migration"

4. **Consistency validation runs automatically** → Shows results:
   ```
   Checking consistency...

   ✅ Timeframe matches your employment at Foil Industries
      (2023-06 to 2024-03 ✓)
   ✅ Company verified in job history
   ⚠️  Similarity check: 15% match to job description (acceptable)
   ```

5. **Review mode displays:**
   ```
   ────────────────────────────────────────
   PROPOSED ADDITION - Review Before Saving
   ────────────────────────────────────────
   Skill: Kubernetes
   Category: Technical (Infrastructure)
   Company: Foil Industries
   Timeframe: 2023-06 to 2024-03

   Example:
   Orchestrated migration from Docker Swarm to
   Kubernetes, managing deployment pipelines for
   8 microservices with Helm charts and reducing
   deployment time from 45 minutes to 8 minutes.

   Result: 82% faster deployments, zero downtime
           during migration

   ────────────────────────────────────────
   Consistency Checks:
   ✅ Timeframe matches job history
   ✅ Company verified
   ✅ No hallucination patterns detected
   ✅ Example length appropriate (162 chars)
   ────────────────────────────────────────

   [Save to Career Data] [Edit] [Discard]
   ```

6. **Sarah clicks "Save"** → Data persisted:
   ```
   ✅ Saved to career_data.json

   Kubernetes added to your career data.
   This will be available for future applications.

   Continue with remaining skills?
   • Docker Compose
   • gRPC

   [Yes] [No, generate resume now]
   ```

7. **Sarah adds Docker Compose, skips gRPC** → Generation proceeds with enriched data

8. **Resume generated** → Kubernetes section includes the validated example:
   ```
   TECHNICAL SKILLS
   ────────────────
   Infrastructure & DevOps: Kubernetes, Docker, ...

   PROFESSIONAL EXPERIENCE
   ────────────────────────
   Foil Industries | Senior Backend Developer | Jun 2023 - Mar 2024

   • Orchestrated migration from Docker Swarm to Kubernetes,
     managing deployment pipelines for 8 microservices with
     Helm charts, reducing deployment time from 45 minutes
     to 8 minutes (82% improvement)
   ```

**Outcome:**
- Sarah's career data now includes Kubernetes with concrete example
- Zero hallucinations (all data user-provided and validated)
- Next application requiring Kubernetes will auto-populate
- Data enrichment happens naturally during real workflow

**Acceptance Criteria:**
- ✅ Detects missing skills from job description
- ✅ Multi-step prompts enforce structured data entry
- ✅ Timeframe validated against job history
- ✅ Consistency checks shown in real-time
- ✅ Review mode displays all data before saving
- ✅ User can edit or discard at any step
- ✅ Saved data immediately available for generation
- ✅ Generated resume uses validated examples

---

### User Story 4: Hallucination Prevention in Action

**Scenario:** Sarah tries to add a skill but provides vague/generic responses. Validation catches it.

**Flow:**

1. **Discovery prompts for "Machine Learning"**

2. **Sarah enters in Step 4 (Example):**
   ```
   "Used cutting-edge ML algorithms to deliver world-class
   results on various projects with many successful outcomes."
   ```

3. **Hallucination detection triggers:**
   ```
   ⚠️  HALLUCINATION WARNINGS DETECTED

   Your response contains patterns that may be vague or unverifiable:

   🚩 Vague quantifiers:
      • "various projects" (not specific)
      • "many successful outcomes" (not measurable)

   🚩 Unverifiable claims:
      • "cutting-edge" (subjective)
      • "world-class" (not quantifiable)

   🚩 Missing specifics:
      • No concrete project or result mentioned
      • No measurable metrics provided

   ────────────────────────────────────────
   Suggested improvements:
   • Name the specific project/company
   • Describe exact techniques used (e.g., "Random Forest classifier")
   • Provide measurable result (e.g., "85% accuracy")

   [Edit Response] [Continue Anyway] [Discard]
   ```

4. **Sarah clicks "Edit Response"** → Returns to Step 4 with feedback

5. **Sarah revises:**
   ```
   "Built Random Forest classifier for customer churn
   prediction at Acme Corp, achieving 87% accuracy and
   reducing churn by 12% over 6 months (saving $240k ARR)."
   ```

6. **Validation passes:**
   ```
   ✅ No hallucination patterns detected
   ✅ Specific technique mentioned (Random Forest)
   ✅ Measurable results provided (87% accuracy, 12% reduction)
   ✅ Company specified (Acme Corp)

   [Continue to Review]
   ```

**Outcome:**
- Vague claims prevented from entering career data
- User educated on what constitutes specific vs generic
- Final data is concrete, verifiable, and valuable

**Acceptance Criteria:**
- ✅ Detects vague quantifiers ("many", "various", "several")
- ✅ Flags unverifiable claims ("best", "world-class", "leading")
- ✅ Suggests specific improvements
- ✅ User can edit or override (with warning)
- ✅ Revised text re-validated before proceeding

---

### User Story 5: Data Portability and Backup

**Scenario:** Sarah's laptop crashes. She recovers her career data from backup location.

**Flow:**

1. **Sarah had configured custom location:**
   ```
   C:\Users\Sarah\Dropbox\ResumeTailor\career_data.json
   ```
   (Synced to cloud via Dropbox)

2. **Laptop crashes, requires Windows reinstall**

3. **Sarah reinstalls Dropbox** → career_data.json syncs back

4. **Sarah downloads Resume_Tailor.exe again** (no installer needed)

5. **First launch prompt:**
   ```
   Where would you like to store your career data?

   [Default Location] C:\Users\Sarah\.resume_tailor\career_data.json
   [Custom Location] [Browse...]
   ```

6. **Sarah clicks "Custom Location"** → Browses to:
   ```
   C:\Users\Sarah\Dropbox\ResumeTailor\career_data.json
   ```

7. **App detects existing file:**
   ```
   ✅ Found existing career data!

   File: C:\Users\Sarah\Dropbox\ResumeTailor\career_data.json
   Last updated: 2025-12-20 14:32
   Contains: 8 jobs, 52 skills, 78 achievements

   [Use This File] [Start Fresh]
   ```

8. **Sarah clicks "Use This File"** → All data restored instantly

**Outcome:**
- Zero data loss from hardware failure
- User-controlled backup strategy (via Dropbox/OneDrive/etc)
- Portable across machines
- No vendor lock-in

**Acceptance Criteria:**
- ✅ File location user-configurable
- ✅ Survives app reinstalls (external to app directory)
- ✅ Can be synced via user's cloud service of choice
- ✅ App detects existing file at custom location
- ✅ Preview shows file metadata before loading

---

### User Story 6: Manual Data Correction

**Scenario:** Sarah realizes she entered wrong timeframe for a skill. She manually edits career_data.json.

**Flow:**

1. **Sarah opens career_data.json in VS Code:**
   ```json
   {
     "skills": [
       {
         "name": "PostgreSQL",
         "examples": [{
           "company": "Foil Industries",
           "timeframe": "2023-06 to 2024-03",  // Wrong end date
           "description": "..."
         }]
       }
     ]
   }
   ```

2. **Sarah corrects timeframe:**
   ```json
   "timeframe": "2023-06 to 2024-08",  // Corrected
   ```

3. **Sarah saves file** → File timestamp updated

4. **Sarah generates next resume** → App detects change:
   ```
   (Internal log - not shown to user)
   Career data file modified externally
   Cache invalidated
   Reloading from disk...
   Pydantic validation: ✓
   Cache updated with new timestamp
   ```

5. **Resume generated with corrected timeframe** → No user action needed

**Outcome:**
- Users can manually edit JSON if needed
- App detects external changes automatically
- Pydantic validation ensures edits don't corrupt data
- Transparent caching behavior

**Acceptance Criteria:**
- ✅ File timestamp monitoring detects external edits
- ✅ Cache invalidated on timestamp change
- ✅ Pydantic validation catches schema violations
- ✅ User-friendly error if manual edit breaks schema
- ✅ No restart required (reloads automatically)

---

### Edge Cases and Error Scenarios

#### Scenario 7: Validation Failure During Save

**Flow:**
1. User completes discovery dialog
2. Review mode → User clicks "Save"
3. Pydantic validation fails (corrupted data somehow)
4. Error shown:
   ```
   ❌ Save Failed - Validation Error

   Could not save to career_data.json:
   • Field 'timeframe' has invalid format

   Your data has NOT been saved.
   Previous version restored from backup.

   [Try Again] [Report Bug]
   ```

**Outcome:**
- No data corruption
- Backup preserved
- User informed clearly

#### Scenario 8: Migration Script Failure

**Flow:**
1. Migration starts → supermemory API times out
2. Retry logic activates:
   ```
   ⚠️  Connection timeout
   Retrying in 5 seconds... (Attempt 2/5)
   ```
3. After 5 retries → Partial migration:
   ```
   ⚠️  Migration Incomplete

   Successfully migrated: 22 / 29 entries

   Failed entries saved to:
   migration_errors.log

   Options:
   [Retry Failed Entries] [Save Partial] [Rollback]
   ```
4. User clicks "Retry Failed Entries" → Resumes from checkpoint

**Outcome:**
- Resilient migration
- No data loss
- User maintains control

#### Scenario 9: Duplicate Skill Detection

**Flow:**
1. User adds "Python" during discovery
2. Consistency check detects existing "Python" skill:
   ```
   ⚠️  Duplicate Detected

   You already have "Python" in your career data
   with 3 existing examples.

   Options:
   [Add This as Another Example] [Skip] [View Existing]
   ```
3. User clicks "Add as Another Example"
4. New example added to existing skill's examples list

**Outcome:**
- Prevents duplicate skills
- Allows multiple examples
- Enriches existing data

---

## Key User Experience Principles

### 1. Privacy by Design
- Career data never sent to external services (except Claude API for generation)
- User controls file location
- Transparent about what data goes where

### 2. Zero Hallucination Tolerance
- Multi-layer validation prevents fabricated claims
- User is source of all facts
- AI assists with formatting, not inventing

### 3. Progressive Disclosure
- Simple initial setup
- Complexity revealed only when needed
- Advanced features opt-in

### 4. Graceful Degradation
- Works with empty career data (prompts during generation)
- Migration can be deferred
- Discovery can be skipped

### 5. Trust Through Transparency
- Show all consistency checks
- Explain validation failures clearly
- Preview all changes before saving
- Backup before every write

---

## Success Metrics and Acceptance Criteria

### Phase 1: Local Career Data Storage

#### Functional Requirements

**FR1.1: Data Structure and Validation**
- ✅ Pydantic models defined for CareerData, Job, Skill, Achievement
- ✅ Schema version field supports future migrations
- ✅ All fields have appropriate type constraints and validation
- ✅ Validation errors produce user-friendly messages

**FR1.2: File Operations**
- ✅ Load operation completes in <100ms for 100 entries
- ✅ In-memory cache implemented with timestamp checking
- ✅ Cache invalidates when file modified externally
- ✅ Save operation creates backup before write
- ✅ Atomic write pattern prevents corruption (temp file + rename)
- ✅ Rollback restores from backup on validation failure
- ✅ File location user-configurable via environment variable

**FR1.3: Migration Script**
- ✅ Successfully migrates all 29 entries from supermemory
- ✅ Preview mode shows entry counts before migration
- ✅ Progress indicator updates during migration
- ✅ Retry logic handles API failures (max 5 attempts, exponential backoff)
- ✅ Checkpoint system allows resuming from failures
- ✅ Migration can be skipped/deferred
- ✅ Validation report flags incomplete data

**FR1.4: Zero External Dependencies**
- ✅ No supermemory imports in final codebase
- ✅ App runs without MCP server installed
- ✅ Only dependency: Claude API for generation
- ✅ Single executable with no setup required

#### Performance Metrics

| Operation | Target | Measured | Status |
|-----------|--------|----------|--------|
| Load career_data.json (100 entries) | <100ms | TBD | Pending |
| Save career_data.json (100 entries) | <200ms | TBD | Pending |
| Cache hit (no file change) | <5ms | TBD | Pending |
| Pydantic validation (100 entries) | <50ms | TBD | Pending |
| Migration (29 entries) | <60s | TBD | Pending |
| Backup creation | <100ms | TBD | Pending |

#### Data Integrity Metrics

- **Zero Data Loss:** No career data lost during migration, saves, or errors
- **Zero Corruption:** Pydantic validation prevents invalid schema from persisting
- **Backup Success Rate:** 100% (backup created before every write)
- **Rollback Success Rate:** 100% (failed saves restore from backup)

#### User Experience Metrics

- **Setup Time:** <3 seconds from launch to ready state (first-time user)
- **Migration Time:** <60 seconds for 29 entries (existing user)
- **File Location Choice:** Clear explanation, no technical jargon
- **Error Messages:** User-friendly (no stack traces shown)

---

### Phase 2: Interactive Discovery Mode

#### Functional Requirements

**FR2.1: Skill Detection**
- ✅ Keyword extraction identifies technical terms
- ✅ Semantic matching detects similar but differently-phrased skills
- ✅ Technology detection (regex patterns for frameworks, tools, languages)
- ✅ Batch prompting (max 5 skills per session)
- ✅ User can skip discovery (non-blocking)

**FR2.2: Five-Layer Validation System**

**Layer 1: Structured Prompts**
- ✅ Multi-step dialog (5 steps minimum)
- ✅ Mandatory fields: company, timeframe, example
- ✅ Field-level validation (immediate feedback)
- ✅ Character counters on text areas
- ✅ Examples shown for each field

**Layer 2: Consistency Validation**
- ✅ Timeframe cross-referenced against job history
- ✅ Company verification (must exist or be marked as side project)
- ✅ Duplicate detection (flags existing skills)
- ✅ Future date prevention
- ✅ Reasonability checks (<10 years ago for new skills)

**Layer 3: Review Mode**
- ✅ Formatted preview before save
- ✅ Consistency check results displayed
- ✅ Color-coded indicators (green ✅, yellow ⚠️, red ❌)
- ✅ Save/Edit/Discard options
- ✅ Edit button pre-fills original dialog

**Layer 4: Format Validation (Pydantic)**
- ✅ Skill name validation (no generic phrases like "team player")
- ✅ Timeframe regex validation (YYYY-MM format)
- ✅ Example length validation (20-500 characters)
- ✅ Example quality check (min 5 words)
- ✅ Type safety enforced at runtime

**Layer 5: Hallucination Detection**
- ✅ Vague quantifier detection ("many", "several", "various")
- ✅ Unverifiable claim detection ("best", "world-class", "leading")
- ✅ Placeholder detection ("[...]", "{...}", "TBD")
- ✅ Job description similarity check (>70% flags warning)
- ✅ Future tense detection (suggests not completed)

**FR2.3: User Interface**
- ✅ Modal dialogs block generation until complete
- ✅ Progress indicators ("Step 2 of 5")
- ✅ Back/Next navigation between steps
- ✅ Skip button available (defers to later)
- ✅ Character counters update in real-time
- ✅ Validation errors shown inline (red text, clear messaging)

**FR2.4: Data Enrichment**
- ✅ Discoveries persist to career_data.json atomically
- ✅ Linked to relevant job in job history
- ✅ last_used timestamp updated
- ✅ Metadata added: discovered_during field
- ✅ Example count incremented
- ✅ Available immediately for current generation

#### Performance Metrics

| Operation | Target | Measured | Status |
|-----------|--------|----------|--------|
| Skill detection (per job description) | <2s | TBD | Pending |
| Consistency validation | <500ms | TBD | Pending |
| Hallucination pattern detection | <300ms | TBD | Pending |
| Full discovery flow (1 skill) | <30s | TBD | Pending |
| Save discovered skill | <200ms | TBD | Pending |

#### Anti-Hallucination Effectiveness Metrics

**Validation Layer Success Rates (Target: 100% catch rate for defined patterns)**

| Pattern Type | Target Catch Rate | Measured | Status |
|--------------|-------------------|----------|--------|
| Vague quantifiers | 100% | TBD | Pending |
| Unverifiable claims | 100% | TBD | Pending |
| Placeholder text | 100% | TBD | Pending |
| Generic skill names | 100% | TBD | Pending |
| Copy-paste (>70% similarity) | 100% | TBD | Pending |
| Future dates | 100% | TBD | Pending |
| Timeframe outside job history | 100% | TBD | Pending |
| Example too short (<20 chars) | 100% | TBD | Pending |

**User Correction Rate:**
- **Target:** >80% of flagged responses are edited by user
- **Measured:** TBD
- **Indicates:** Users trust validation feedback

**False Positive Rate:**
- **Target:** <5% (valid responses flagged incorrectly)
- **Measured:** TBD
- **Indicates:** Validation not overly aggressive

#### User Experience Metrics

- **Discovery Completion Rate:** % of prompted skills that users complete
  - Target: >60% (indicates value, not annoyance)
- **Skip Rate:** % of discovery prompts skipped
  - Target: <40% (users find it useful)
- **Edit Rate:** % of review mode edits before saving
  - Target: 10-20% (validation catches issues, but not overly strict)
- **Time to Complete Discovery (1 skill):** <30 seconds
  - Target: Quick enough to not disrupt workflow
- **User Satisfaction:** Subjective feedback
  - Target: "Helps me remember details" vs "Annoying interruption"

---

### Overall Product Success Metrics

#### Adoption Metrics

**First-Time User Success Rate:**
- **Metric:** % of new users who generate first resume within 5 minutes
- **Target:** >90%
- **Indicates:** Zero setup friction achieved

**Migration Success Rate:**
- **Metric:** % of existing users who successfully migrate from supermemory
- **Target:** 100% (with retry logic and clear error handling)
- **Indicates:** Smooth transition path

#### Data Quality Metrics

**Career Data Completeness:**
- **Metric:** Average number of skills with concrete examples per user
- **Target:** Growth from ~5 (initial) to 20+ (after 10 applications)
- **Indicates:** Discovery mode enriches data over time

**Hallucination-Free Rate:**
- **Metric:** % of generated resumes with zero fabricated claims
- **Target:** 100%
- **Indicates:** Core value proposition delivered

**Data Accuracy:**
- **Metric:** % of career data entries with:
  - Specific company/project
  - Validated timeframe
  - Concrete example (>20 chars)
  - Measurable result
- **Target:** 100% (enforced by validation)

#### Reliability Metrics

**Data Loss Incidents:**
- **Target:** 0 (backup + atomic writes prevent this)

**Corruption Incidents:**
- **Target:** 0 (Pydantic validation + rollback prevent this)

**Backup Success Rate:**
- **Target:** 100% (backup created before every write)

**Cache Invalidation Accuracy:**
- **Target:** 100% (timestamp checking detects external edits)

#### Performance Benchmarks

**Application Startup:**
- **Cold start (first launch):** <3 seconds
- **Warm start (subsequent launches):** <1 second

**Resume Generation:**
- **With discovery (5 skills):** <3 minutes total
- **Without discovery:** <15 seconds (existing behavior)

**File Operations:**
- **Load + validate 100 entries:** <100ms
- **Save + backup 100 entries:** <200ms

---

### Acceptance Test Scenarios

#### Test Scenario 1: Fresh Install (New User)

**Given:** User has never used Resume Tailor before
**When:** User downloads and launches Resume_Tailor.exe
**Then:**
- App launches in <3 seconds
- Welcome dialog shows file location choice
- Default location explained clearly
- User can choose custom location
- User can defer data entry (skip)
- App ready to generate resume immediately

**Pass Criteria:**
- ✅ No errors during first launch
- ✅ File location dialog shown
- ✅ career_data.json created (empty schema)
- ✅ Can generate resume (will prompt for data during generation)

---

#### Test Scenario 2: Supermemory Migration

**Given:** User has existing Resume Tailor with supermemory (29 entries)
**When:** User launches updated Resume_Tailor.exe with local storage feature
**Then:**
- Migration prompt appears
- Preview shows 29 entries breakdown
- User clicks "Migrate Now"
- Progress bar shows migration status
- All 29 entries converted successfully
- Supermemory dependency removed
- Backup created
- Success confirmation shown

**Pass Criteria:**
- ✅ All 29 entries migrated with correct structure
- ✅ Pydantic validation passes on migrated data
- ✅ Backup file created (career_data.json.bak)
- ✅ App functions without supermemory MCP
- ✅ No data loss
- ✅ Migration completes in <60 seconds

---

#### Test Scenario 3: Discovery Mode (Happy Path)

**Given:** User has partial career data, applies for job requiring "Kubernetes"
**When:** User pastes job description and clicks "Generate Resume"
**Then:**
- Discovery prompt shows "Kubernetes" detected
- User clicks "Yes, let's add them"
- Multi-step dialog opens (5 steps)
- User enters: Foil Industries, 2023-06 to 2024-03, specific example, result
- Consistency validation passes (timeframe matches job history)
- Review mode shows formatted preview with green checkmarks
- User clicks "Save"
- Data persisted to career_data.json
- Generation proceeds with enriched data
- Resume includes Kubernetes with validated example

**Pass Criteria:**
- ✅ Skill detected correctly
- ✅ All 5 validation layers executed
- ✅ Consistency checks passed
- ✅ Review mode displayed correctly
- ✅ Data saved atomically with backup
- ✅ Generated resume includes new skill
- ✅ Total time <30 seconds

---

#### Test Scenario 4: Hallucination Detection

**Given:** User is adding "Machine Learning" skill
**When:** User enters vague response: "Used cutting-edge ML on various projects with many successes"
**Then:**
- Hallucination detection triggers
- Warning dialog shows specific issues:
  - Vague quantifiers flagged
  - Unverifiable claims flagged
  - Missing specifics noted
- Suggested improvements shown
- User clicks "Edit Response"
- User revises to: "Built Random Forest classifier at Acme Corp, 87% accuracy, reduced churn by 12%"
- Validation passes
- Review mode continues

**Pass Criteria:**
- ✅ Detected "cutting-edge" (unverifiable)
- ✅ Detected "various" (vague quantifier)
- ✅ Detected "many" (vague quantifier)
- ✅ Suggestions specific and helpful
- ✅ Revised text passes validation
- ✅ User can still save original if desired (override)

---

#### Test Scenario 5: Data Corruption Prevention

**Given:** User manually edits career_data.json and introduces invalid timeframe
**When:** User saves file with: "timeframe": "2023-99-99" (invalid format)
**Then:**
- App attempts to load file
- Pydantic validation fails
- User-friendly error shown:
  ```
  ❌ Career Data Validation Error

  Your career_data.json file has invalid data:
  • Field 'timeframe' has invalid format: "2023-99-99"
    Expected: YYYY-MM (e.g., "2023-06")

  Please fix the file manually or restore from backup.

  Backup location: career_data.json.bak

  [Open File] [Restore from Backup] [Cancel]
  ```
- User clicks "Restore from Backup"
- Valid data restored
- App continues normally

**Pass Criteria:**
- ✅ Invalid data detected by Pydantic
- ✅ Corruption does not crash app
- ✅ Error message user-friendly (no stack trace)
- ✅ Backup location shown
- ✅ One-click restore available
- ✅ App recovers gracefully

---

#### Test Scenario 6: External File Modification

**Given:** User has Resume Tailor running with cached career data
**When:** User opens career_data.json in VS Code and modifies a skill
**Then:**
- User saves file (timestamp updated)
- User returns to Resume Tailor and clicks "Generate Resume"
- App detects file timestamp changed
- Cache invalidated
- File reloaded from disk
- Pydantic validation passes
- Generation proceeds with updated data

**Pass Criteria:**
- ✅ Timestamp change detected
- ✅ Cache invalidated automatically
- ✅ No restart required
- ✅ Changes reflected immediately
- ✅ Validation ensures data still valid

---

### Rollout Plan

#### Phase 1: Internal Testing (Week 1)
- Install on fresh Windows machine (no existing Resume Tailor)
- Test first-time user flow
- Verify file location configuration
- Test manual data entry
- Benchmark performance metrics

#### Phase 2: Migration Testing (Week 2)
- Test migration with real supermemory data (29 entries)
- Verify retry logic with simulated API failures
- Test partial migration + resume capability
- Verify backup creation
- Confirm zero data loss

#### Phase 3: Discovery Mode Testing (Week 3)
- Test skill detection accuracy
- Test all 5 validation layers
- Test hallucination detection with known bad inputs
- Test review mode UI
- Test data persistence and rollback
- Benchmark discovery flow performance

#### Phase 4: Integration Testing (Week 4)
- Test full end-to-end workflow (migration → discovery → generation)
- Test data portability (custom location + Dropbox sync)
- Test manual JSON editing + timestamp detection
- Test error scenarios (corruption, validation failures, API failures)
- Performance testing with 100+ entries

#### Phase 5: User Acceptance Testing (Week 5)
- Beta test with 3-5 real users
- Collect feedback on UX friction points
- Measure completion rates for discovery mode
- Measure user satisfaction
- Identify edge cases

#### Phase 6: Production Release (Week 6)
- Final bug fixes from UAT
- Documentation updates
- Build final executable
- Release notes
- Migration guide for existing users

---

### Non-Functional Requirements

#### Security
- ✅ Career data stored locally (not transmitted except to Claude API)
- ✅ No credentials stored in career_data.json
- ✅ File permissions respect OS defaults
- ✅ No sensitive data logged

#### Portability
- ✅ Single executable (no installer required)
- ✅ Works on Windows 10/11
- ✅ File location user-controlled (supports Dropbox, OneDrive, etc.)
- ✅ No registry dependencies
- ✅ Survives OS reinstalls

#### Maintainability
- ✅ Pydantic models centralize validation logic
- ✅ Config.py centralizes configuration
- ✅ Schema version field supports future migrations
- ✅ Clear separation: data layer (career_data_manager) vs UI (discovery)
- ✅ Comprehensive error logging

#### Usability
- ✅ All error messages user-friendly (no jargon)
- ✅ Progress indicators for long operations
- ✅ Consistent dialog patterns (Back/Next, Save/Edit/Discard)
- ✅ Color-coded validation feedback
- ✅ Help text in-context (not separate docs)

#### Scalability
- ✅ Performance target: <100ms for 100 entries
- ✅ In-memory caching prevents repeated file reads
- ✅ JSON format scales to 1000+ entries
- ✅ No database required

---

### Definition of Done

**Feature 1: Local Career Data Storage**
- [ ] Pydantic models implemented and tested
- [ ] career_data_manager.py implements load/save with caching
- [ ] Atomic writes with backup verified
- [ ] Rollback on validation failure tested
- [ ] File location configurable via environment variable
- [ ] Migration script migrates all 29 entries successfully
- [ ] Zero supermemory dependencies in codebase
- [ ] Performance metrics met (<100ms load/save)
- [ ] All acceptance tests pass
- [ ] Documentation updated

**Feature 2: Interactive Discovery Mode**
- [ ] Skill detection implemented (keyword + semantic)
- [ ] Multi-step dialog UI implemented (5 steps)
- [ ] All 5 validation layers implemented
- [ ] Consistency checks against job history
- [ ] Review mode UI with color-coded checks
- [ ] Hallucination detection patterns implemented
- [ ] Data persistence with atomic writes
- [ ] All acceptance tests pass
- [ ] Performance metrics met (<30s full flow)
- [ ] Documentation updated

**Overall Product:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All acceptance tests pass
- [ ] Performance benchmarks met
- [ ] Zero data loss in testing
- [ ] Zero corruption in testing
- [ ] UAT feedback incorporated
- [ ] Executable builds successfully
- [ ] Documentation complete
- [ ] Ready for production release

---

## Implementation Roadmap

### Overview

The implementation is divided into two major phases that can be developed incrementally. Phase 1 (Local Career Data Storage) is a prerequisite for Phase 2 (Interactive Discovery Mode), as discovery mode depends on the local storage infrastructure.

**Total Estimated Duration:** 4-6 weeks (depending on testing thoroughness and iteration)

---

### Phase 1: Local Career Data Storage

**Goal:** Replace supermemory dependency with privacy-first local JSON storage

**Duration:** 2-3 weeks

**Dependencies:** None (foundational feature)

#### Sprint 1.1: Data Models and File Manager (Week 1)

**Tasks:**

1. **Create Pydantic models** (`models.py` or integrated in `career_data_manager.py`)
   - Define `CareerData` root model
   - Define `Job`, `Skill`, `Achievement` models
   - Add validation rules (regex patterns, min/max lengths)
   - Add custom validators for skill name quality, timeframe format
   - Include schema version field ("1.0")
   - **Estimated:** 1 day

2. **Implement `career_data_manager.py`**
   - Implement `load_career_data()` with caching
   - Implement file timestamp checking
   - Implement `save_career_data()` with atomic writes
   - Implement backup creation (career_data.json.bak)
   - Implement rollback on validation failure
   - Add configuration options to `config.py` (CAREER_DATA_FILE, BACKUP_ENABLED, CACHE_TTL)
   - **Estimated:** 2 days

3. **Unit tests for data manager**
   - Test load with valid/invalid data
   - Test cache hit/miss scenarios
   - Test timestamp invalidation
   - Test atomic write pattern
   - Test backup creation
   - Test rollback on failure
   - **Estimated:** 1 day

4. **Integration with existing codebase**
   - Update `generator.py` to use `career_data_manager` instead of supermemory
   - Remove supermemory imports
   - Test resume generation with local data
   - **Estimated:** 1 day

**Deliverables:**
- ✅ Pydantic models defined and tested
- ✅ career_data_manager.py implements all file operations
- ✅ Unit tests passing
- ✅ Resume generation works with local storage
- ✅ Supermemory dependency removed from generator.py

---

#### Sprint 1.2: Migration Script (Week 2)

**Tasks:**

1. **Implement `migrate_from_supermemory.py`**
   - Query supermemory MCP for all career entries
   - Parse entries into structured format (jobs, skills, achievements)
   - Pydantic validation on parsed data
   - Preview mode with entry counts
   - Progress tracking (checkpoint after each 5 entries)
   - Retry logic with exponential backoff (max 5 attempts)
   - Resume capability (from checkpoint)
   - **Estimated:** 2 days

2. **Add migration UI to GUI** (`resume_tailor_gui.py`)
   - Detect existing supermemory data on launch
   - Show migration prompt dialog
   - Implement preview report dialog
   - Implement progress indicator
   - Implement success/failure confirmation
   - Add "Migrate Now" / "Skip" options
   - **Estimated:** 1 day

3. **Migration testing**
   - Test with real supermemory data (29 entries)
   - Test retry logic (simulate API failures)
   - Test partial migration + resume
   - Test validation report
   - Verify zero data loss
   - **Estimated:** 1 day

4. **First-time user flow**
   - Implement file location choice dialog (first launch)
   - Create empty career_data.json with schema
   - Add "Custom Location" option (file picker)
   - Test fresh install scenario
   - **Estimated:** 1 day

**Deliverables:**
- ✅ Migration script successfully migrates 29 entries
- ✅ Retry logic handles API failures gracefully
- ✅ GUI shows migration prompts and progress
- ✅ First-time user flow implemented
- ✅ Zero data loss verified

---

#### Sprint 1.3: Error Handling and Polish (Week 3)

**Tasks:**

1. **Error handling improvements**
   - User-friendly error messages (no stack traces)
   - Corruption detection with restore option
   - External edit detection with cache invalidation
   - Validation error dialogs with [Restore from Backup] button
   - **Estimated:** 1 day

2. **Add "Restore from Backup" feature to GUI**
   - Menu option: File → Restore from Backup
   - Confirmation dialog before restore
   - Success/failure feedback
   - **Estimated:** 0.5 days

3. **Performance optimization**
   - Benchmark load/save operations
   - Optimize caching strategy if needed
   - Ensure <100ms for 100 entries
   - **Estimated:** 0.5 days

4. **Integration testing**
   - Test full workflow: first launch → migration → generation
   - Test data portability (custom location + Dropbox sync)
   - Test manual JSON editing + timestamp detection
   - Test all error scenarios
   - **Estimated:** 1 day

5. **Documentation**
   - Update README with local storage information
   - Document file location configuration
   - Document migration process
   - Document backup/restore process
   - **Estimated:** 1 day

**Deliverables:**
- ✅ All error scenarios handled gracefully
- ✅ Performance benchmarks met
- ✅ Integration tests passing
- ✅ Documentation updated
- ✅ Phase 1 complete and production-ready

---

### Phase 2: Interactive Discovery Mode

**Goal:** Add intelligent skill discovery with 5-layer anti-hallucination validation

**Duration:** 2-3 weeks

**Dependencies:** Phase 1 (Local Career Data Storage) must be complete

#### Sprint 2.1: Skill Detection and Discovery UI (Week 4)

**Tasks:**

1. **Implement skill detection** (`career_discovery.py`)
   - Keyword extraction (spaCy or simple regex)
   - Technology detection (regex patterns for frameworks, tools)
   - Semantic matching (optional: embedding similarity)
   - Batch filtering (max 5 skills per session)
   - **Estimated:** 1.5 days

2. **Implement multi-step discovery dialog** (tkinter)
   - Step 1: Confirm experience (Yes/No/Not sure)
   - Step 2: Company/Project (text input)
   - Step 3: Timeframe (YYYY-MM format, validated)
   - Step 4: Specific example (text area, character counter)
   - Step 5: Measurable result (optional text input)
   - Back/Next navigation
   - Progress indicator ("Step 2 of 5")
   - Skip button
   - **Estimated:** 2 days

3. **Field-level validation**
   - Real-time validation feedback (red text for errors)
   - Character counters on text areas
   - Timeframe format validation (regex)
   - Example length validation (min 20, max 500)
   - **Estimated:** 0.5 days

**Deliverables:**
- ✅ Skill detection identifies missing skills from job description
- ✅ Multi-step dialog implemented and functional
- ✅ Field-level validation provides immediate feedback
- ✅ UI is intuitive and easy to navigate

---

#### Sprint 2.2: Validation Layers (Week 5)

**Tasks:**

1. **Layer 1: Structured Prompts**
   - Already implemented in Sprint 2.1 (multi-step dialog)
   - Ensure mandatory fields enforced
   - **Estimated:** 0 days (done)

2. **Layer 2: Consistency Validation**
   - Implement timeframe cross-reference against job history
   - Implement company verification
   - Implement duplicate skill detection
   - Implement future date prevention
   - Implement reasonability checks
   - **Estimated:** 1 day

3. **Layer 3: Review Mode**
   - Implement formatted preview dialog
   - Display consistency check results (color-coded)
   - Implement Save/Edit/Discard buttons
   - Edit button pre-fills original dialog
   - **Estimated:** 1 day

4. **Layer 4: Format Validation (Pydantic)**
   - Create `DiscoveredSkill` Pydantic model
   - Add skill name validation (ban generic phrases)
   - Add example quality validation
   - Add timeframe validation
   - **Estimated:** 0.5 days

5. **Layer 5: Hallucination Detection**
   - Implement vague quantifier detection
   - Implement unverifiable claim detection
   - Implement placeholder text detection
   - Implement job description similarity check
   - Implement future tense detection
   - Display warnings in review dialog
   - **Estimated:** 1.5 days

6. **Unit tests for validation layers**
   - Test each layer independently
   - Test known bad inputs (vague, generic, copy-paste)
   - Test known good inputs (specific, measurable)
   - Verify 100% catch rate for defined patterns
   - **Estimated:** 1 day

**Deliverables:**
- ✅ All 5 validation layers implemented
- ✅ Unit tests verify 100% catch rate for defined patterns
- ✅ Review mode shows color-coded validation results
- ✅ User can edit or override with warnings

---

#### Sprint 2.3: Data Enrichment and Integration (Week 6)

**Tasks:**

1. **Implement data enrichment**
   - Save discovered skill to career_data.json atomically
   - Link to relevant job in job history
   - Update last_used timestamp
   - Add metadata: discovered_during field
   - Increment example count
   - **Estimated:** 1 day

2. **Integrate with generation pipeline** (`generator.py`)
   - Add `discovery_callback` parameter (optional)
   - Detect missing skills before generation
   - Call discovery callback if provided
   - Validate discovered data (5 layers)
   - Reload career data with enriched info
   - Proceed with generation
   - **Estimated:** 1 day

3. **GUI integration** (`resume_tailor_gui.py`)
   - Add "Enable Discovery Mode" checkbox (default: True)
   - Pass callback to generator if enabled
   - Handle discovery prompts during generation
   - **Estimated:** 0.5 days

4. **Integration testing**
   - Test full discovery flow (detection → prompts → validation → save → generation)
   - Test skip functionality
   - Test edit functionality in review mode
   - Test hallucination detection with known bad inputs
   - Test data persistence
   - Verify enriched data available immediately
   - **Estimated:** 1.5 days

5. **Performance optimization**
   - Benchmark skill detection (<2s)
   - Benchmark consistency validation (<500ms)
   - Benchmark hallucination detection (<300ms)
   - Optimize if needed
   - **Estimated:** 0.5 days

6. **Documentation**
   - Document discovery mode feature
   - Document validation layers
   - Document how to skip/enable discovery
   - Add examples of good vs bad responses
   - **Estimated:** 0.5 days

**Deliverables:**
- ✅ Discovery mode integrated with generation pipeline
- ✅ Data enrichment working correctly
- ✅ All integration tests passing
- ✅ Performance benchmarks met
- ✅ Documentation updated
- ✅ Phase 2 complete and production-ready

---

### Testing and Quality Assurance

#### Unit Testing Strategy

**Phase 1 Tests:**
- Pydantic model validation (valid/invalid data)
- File operations (load, save, cache, timestamp)
- Atomic writes and rollback
- Backup creation
- Migration script (retry logic, progress tracking)

**Phase 2 Tests:**
- Skill detection (keyword extraction, regex patterns)
- Each validation layer independently
- Hallucination pattern detection
- Data enrichment logic
- Callback integration

**Test Coverage Target:** >85%

---

#### Integration Testing Strategy

**Phase 1 Integration Tests:**
- Fresh install flow (first launch → file creation → ready state)
- Migration flow (detection → preview → migrate → success)
- Generation with local storage (load → generate → save)
- External edit detection (edit file → cache invalidation → reload)
- Corruption recovery (invalid data → error → restore from backup)

**Phase 2 Integration Tests:**
- Full discovery flow (detection → prompts → validation → save → generation)
- Multi-skill discovery (batching, skip, edit)
- Hallucination detection in context
- Data portability (custom location, Dropbox sync)

---

#### Acceptance Testing Strategy

**UAT Plan (Week 5-6):**
1. Recruit 3-5 beta testers (mix of new and existing users)
2. Provide test scenarios (fresh install, migration, discovery)
3. Collect feedback on:
   - Setup friction
   - Migration clarity
   - Discovery usefulness vs annoyance
   - Validation feedback clarity
   - Error message friendliness
4. Measure:
   - Time to first resume
   - Migration success rate
   - Discovery completion rate
   - Skip rate
   - User satisfaction

**Success Criteria:**
- >90% complete first resume within 5 minutes
- 100% migration success rate
- >60% discovery completion rate
- >4/5 user satisfaction rating

---

### Risk Management

#### Risk 1: Supermemory API Changes During Migration

**Likelihood:** Low
**Impact:** High (blocks migration)
**Mitigation:**
- Implement retry logic with exponential backoff
- Checkpoint system allows resume from failure
- Fallback: Manual export from supermemory → import to JSON

#### Risk 2: Performance Degradation with Large Career Data (>100 entries)

**Likelihood:** Low
**Impact:** Medium (slow UX)
**Mitigation:**
- In-memory caching prevents repeated file reads
- JSON format is lightweight and fast
- Benchmark with 100+ entries during testing
- Fallback: Pagination or lazy loading if needed

#### Risk 3: User Confusion with Discovery Prompts

**Likelihood:** Medium
**Impact:** Medium (users skip, defeating purpose)
**Mitigation:**
- Clear in-context help text
- Examples shown for each field
- Skip button always available (non-blocking)
- UAT feedback will surface confusion points

#### Risk 4: False Positives in Hallucination Detection

**Likelihood:** Medium
**Impact:** Low (users can override)
**Mitigation:**
- Users can always click "Continue Anyway" (override with warning)
- Target <5% false positive rate
- UAT feedback will surface overly aggressive patterns
- Iterative tuning based on real data

#### Risk 5: Data Corruption from Manual JSON Edits

**Likelihood:** Low
**Impact:** High (career data lost)
**Mitigation:**
- Pydantic validation catches schema violations
- Backup created before every write
- One-click restore from backup
- User-friendly error messages guide recovery

---

### Dependency Graph

```
Phase 1: Local Career Data Storage
├── Sprint 1.1: Data Models and File Manager
│   ├── Pydantic models ✓
│   ├── career_data_manager.py ✓
│   └── Integration with generator.py ✓
├── Sprint 1.2: Migration Script
│   ├── migrate_from_supermemory.py ✓
│   ├── Migration UI in GUI ✓
│   └── First-time user flow ✓
└── Sprint 1.3: Error Handling and Polish
    ├── Error handling improvements ✓
    ├── Restore from Backup feature ✓
    └── Performance optimization ✓

Phase 2: Interactive Discovery Mode (Depends on Phase 1)
├── Sprint 2.1: Skill Detection and Discovery UI
│   ├── Skill detection logic ✓
│   └── Multi-step dialog UI ✓
├── Sprint 2.2: Validation Layers
│   ├── Layers 1-5 implementation ✓
│   └── Review mode UI ✓
└── Sprint 2.3: Data Enrichment and Integration
    ├── Save enriched data ✓
    ├── Generator integration ✓
    └── GUI integration ✓
```

---

### Implementation Checklist

#### Phase 1: Local Career Data Storage
- [ ] Week 1: Data Models and File Manager
  - [ ] Pydantic models implemented
  - [ ] career_data_manager.py complete
  - [ ] Unit tests passing
  - [ ] Generator.py updated
- [ ] Week 2: Migration Script
  - [ ] migrate_from_supermemory.py complete
  - [ ] Migration UI in GUI
  - [ ] First-time user flow
  - [ ] Migration testing complete
- [ ] Week 3: Error Handling and Polish
  - [ ] Error handling improved
  - [ ] Restore from Backup feature
  - [ ] Performance optimized
  - [ ] Integration tests passing
  - [ ] Documentation updated
  - [ ] **Phase 1 Complete ✓**

#### Phase 2: Interactive Discovery Mode
- [ ] Week 4: Skill Detection and Discovery UI
  - [ ] Skill detection implemented
  - [ ] Multi-step dialog UI complete
  - [ ] Field-level validation working
- [ ] Week 5: Validation Layers
  - [ ] All 5 layers implemented
  - [ ] Review mode complete
  - [ ] Unit tests passing (100% catch rate)
- [ ] Week 6: Data Enrichment and Integration
  - [ ] Data enrichment working
  - [ ] Generator integration complete
  - [ ] GUI integration complete
  - [ ] Integration tests passing
  - [ ] Performance optimized
  - [ ] Documentation updated
  - [ ] **Phase 2 Complete ✓**

#### Final Steps
- [ ] UAT feedback incorporated
- [ ] All acceptance tests passing
- [ ] Executable built and tested
- [ ] Release notes written
- [ ] Migration guide for existing users
- [ ] **Production Release Ready ✓**

---

### Post-Release Roadmap (Future Enhancements)

**V2.0 Features (Not in scope for this PRD):**
1. **Import from existing resume** (PDF/DOCX parsing)
2. **Manual data entry form** (GUI for adding jobs/skills without discovery)
3. **Career data analytics** (skills over time, gaps analysis)
4. **Multi-language support** (detect languages in job descriptions)
5. **Export career data** (to LinkedIn, PDF portfolio, etc.)
6. **Cloud sync option** (optional encrypted cloud backup)
7. **Advanced semantic matching** (embedding-based skill detection)

**Priority:** TBD based on user feedback and demand

---

## Conclusion

This PRD defines a comprehensive transformation of Resume Tailor from a supermemory-dependent tool into a privacy-first, standalone desktop application with intelligent discovery capabilities and provable anti-hallucination guarantees.

**Key Differentiators:**
- ✅ Zero external dependencies (beyond Claude API)
- ✅ Privacy-first architecture (local data storage, user-controlled location)
- ✅ Zero setup friction (single executable, no installation)
- ✅ Provable anti-hallucination (5-layer validation system)
- ✅ Data enrichment over time (discovery mode builds career library)
- ✅ Portable and reliable (survives reinstalls, no vendor lock-in)

**Success will be measured by:**
- 100% migration success rate (existing users)
- >90% first-resume-in-5-minutes rate (new users)
- 100% hallucination-free rate (zero fabricated claims)
- >60% discovery completion rate (users find it valuable)

**Implementation timeline:** 4-6 weeks (2 phases, fully tested and documented)

This PRD is ready for implementation. All requirements are well-defined, success metrics are clear, and risks are mitigated. The phased approach allows for incremental delivery and testing, ensuring high quality and reliability.
