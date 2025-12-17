# Resume Tailor Skill - Instructions for Claude

When this skill is invoked, help the user set up or use the resume-tailor system.

## User Intent Detection

Determine what the user wants:

1. **Setup**: First-time setup of the resume-tailor system
2. **Import Data**: Add new career data to supermemory
3. **Generate Documents**: Create resume/cover letter for a job
4. **Update**: Modify existing career data
5. **Help**: Learn how to use the system

## Setup Flow

If this is the first time using the skill:

1. Check if `resume-tailor/` directory exists
2. If not, create project structure:
   - resume_tailor.py (main CLI)
   - generator.py (core logic)
   - import_career_data.py (data import)
   - requirements.txt
   - test_job.txt (sample)

3. Ask user for career documents:
   - Current resume (PDF/DOCX)
   - 2-3 cover letter examples
   - LinkedIn export (optional)

4. Parse documents and populate supermemory with:
   - Job history entries
   - Quantifiable achievements
   - Skills with evidence
   - Writing style patterns
   - Personal values/stories

5. Install dependencies: `pip install -r requirements.txt`

6. Guide user to set ANTHROPIC_API_KEY

## Import Data Flow

When user wants to add new career data:

1. Ask what type of data:
   - New job role
   - Achievement/metric
   - Skill with evidence
   - Cover letter example
   - Personal story/value

2. Collect structured information:
   - For achievements: company, context, metrics, scope, methods
   - For skills: evidence examples, tools used, context
   - For jobs: title, company, dates, context, responsibilities

3. Store in supermemory with appropriate tags

4. Confirm data added and show total entry count

## Generate Documents Flow

When user wants to create tailored documents:

1. Get job description:
   - From file path
   - Pasted text
   - URL (if fetchable)

2. Ask for company name (optional, for file naming)

3. Ask for output preferences:
   - Both resume and cover letter (default)
   - Resume only
   - Cover letter only
   - Output directory

4. Run the CLI tool:
   ```bash
   python resume_tailor.py --job [path] --company-name "[name]" --verbose
   ```

5. Show generated files and next steps

## Key Principles

### Anti-Hallucination
- **NEVER invent career facts** - only use what's in supermemory
- Always verify information is factual before storing
- If unsure about a detail, ask the user to clarify

### Data Structure
- Store granular, atomic facts (not summaries)
- Include metrics wherever possible
- Link evidence to claims
- Tag appropriately for retrieval

### Writing Style Preservation
- Capture tone patterns from user's examples
- Note common phrases and structures
- Preserve user's authentic voice
- Don't impose a different style

### User Experience
- Guide user through setup step-by-step
- Provide clear next steps
- Show what was created/modified
- Make it easy to verify outputs

## Supermemory Structure

Store career data in these categories:

### JOB HISTORY
```
JOB: [Title] at [Company] ([Dates])
Location: [City, State]
Company Context: [What company does, who they serve]
Key Responsibilities:
- [Responsibility 1]
- [Responsibility 2]
```

### ACHIEVEMENTS
```
ACHIEVEMENT: [Brief description with metric]
Company: [Company name]
Context: [What problem solved, situation]
Metrics: [Quantified results]
Scope: [Scale/impact]
Methods Used: [How accomplished]
```

### SKILLS
```
SKILL: [Skill name]
Evidence:
- [Specific example 1]
- [Specific example 2]
Context: [Where/how used]
Tools: [Specific tools if applicable]
```

### WRITING STYLE
```
WRITING STYLE - Cover Letter Structure:
- [Pattern 1]
- [Pattern 2]
Tone Patterns:
- [Tone characteristic 1]
Common Phrases:
- "[Exact phrase from examples]"
```

### PERSONAL VALUES
```
[CATEGORY]: [Description]
[Relevant story or context]
[How this manifests in work]
```

## Example Interactions

### Example 1: First-Time Setup
```
User: I want to set up resume tailor
Assistant: Great! I'll help you set up the resume-tailor system. First, let me create the project structure...
[Creates files]
Now, please share your current resume and 2-3 cover letter examples so I can populate your career data.
```

### Example 2: Adding Achievement
```
User: I want to add a new achievement
Assistant: Excellent! Let me collect the details:
- What's the achievement? (include metric if possible)
- Which company?
- What was the context/situation?
- What methods did you use?
- What was the scope/scale of impact?
```

### Example 3: Generating Documents
```
User: Generate a resume for this job [paste]
Assistant: I'll create tailored documents for you. What's the company name?
User: TechCorp
Assistant: [Runs tool]
Generated:
- Watson_Mulkey_Resume_TechCorp.md
- Watson_Mulkey_TechCorp_CoverLetter.md

Next steps:
1. Review the documents
2. Verify all facts are accurate
3. Customize any sections for personal touch
```

## Error Handling

### Missing API Key
- Guide user to https://console.anthropic.com/
- Show how to set environment variable
- Explain offline mode still works with templates

### Empty Supermemory
- Check if data import has been run
- Guide through import process
- Verify data was stored successfully

### Hallucination Detected
- If user reports invented information:
  - Ask for specifics
  - Remove or correct in supermemory
  - Update prompts to be more strict
  - Apologize and fix immediately

## Commands to Remember

Install dependencies:
```bash
pip install -r requirements.txt
```

Set API key (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

Generate documents:
```bash
python resume_tailor.py --job job.txt --verbose
```

Test with sample:
```bash
python resume_tailor.py --job test_job.txt --company-name "TestCo"
```

## Success Criteria

A successful invocation results in:
1. User has working resume-tailor system
2. Career data stored in supermemory (verified)
3. User can generate documents independently
4. All facts in generated documents are accurate
5. User understands how to maintain/update data
