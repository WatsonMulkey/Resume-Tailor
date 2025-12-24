# Migration Guide: Supermemory → Local Storage

This guide explains the migration from supermemory-based storage to local JSON storage in Resume Tailor v2.0.

## What Changed?

**Previous Version (v1.x):**
- Career data stored in supermemory MCP
- Required external MCP server running
- Data location not user-controlled

**New Version (v2.0):**
- Career data stored in local JSON file
- No external dependencies (except Claude API)
- User-controlled file location
- Automatic backup & recovery
- Privacy-first architecture

## Benefits of Local Storage

✅ **Privacy**: Your career data never leaves your machine
✅ **Reliability**: No external dependencies to fail
✅ **Performance**: Faster access with in-memory caching
✅ **Control**: You choose where your data lives
✅ **Portability**: Easy to back up or sync via your preferred method

## Migration Process

### Automatic Migration (GUI)

When you launch Resume Tailor v2.0 for the first time:

1. **Migration Prompt appears** if supermemory data is detected
2. Click **"Preview Migration"** to see what will be migrated
3. Click **"Migrate Now"** to start migration
4. Progress is shown in real-time
5. Success confirmation displays file location

**Migration Time:** <30 seconds for typical data (~20-30 entries)

### Manual Migration (Command Line)

```bash
# Preview migration (shows what will be migrated, doesn't save)
python migrate_from_supermemory.py --preview

# Run migration
python migrate_from_supermemory.py
```

## What Gets Migrated?

✅ Contact information
✅ Job history (company, title, dates, responsibilities)
✅ Skills with evidence
✅ Achievements
✅ Personal values
✅ Writing style preferences

## File Location

**Default location:** `~/.resume_tailor/career_data.json`

**Windows:** `C:\Users\{YourName}\.resume_tailor\career_data.json`
**Mac/Linux:** `~/.resume_tailor/career_data.json`

**Custom location:** Set environment variable:
```bash
export CAREER_DATA_FILE="/path/to/your/career_data.json"
```

## Backup & Recovery

### Automatic Backups

Resume Tailor automatically creates a backup before each save:
- **Backup file:** `career_data.json.bak`
- **Location:** Same directory as main file
- **Frequency:** Before every write operation

### Manual Restore

**Via GUI:**
1. Menu → File → Restore from Backup
2. Confirm restoration
3. Data restored from `.bak` file

**Via Python:**
```python
from career_data_manager import get_manager

manager = get_manager()
manager._restore_from_backup()
```

## Troubleshooting

### Migration Failed

**Problem:** Migration script reports errors

**Solutions:**
1. Run preview mode to see what's failing:
   ```bash
   python migrate_from_supermemory.py --preview
   ```
2. Check `migration_errors.log` for details
3. Retry failed entries or contact support

### File Corruption

**Problem:** Career data file is corrupted

**Solutions:**
1. **GUI:** Menu → File → Restore from Backup
2. **Manual:** Copy `.bak` file over main file
   ```bash
   cp career_data.json.bak career_data.json
   ```

### Validation Errors

**Problem:** Data doesn't match expected format

**Cause:** Manual edits to JSON file

**Solutions:**
1. Restore from backup (contains last valid state)
2. Fix JSON manually (check against models.py for schema)
3. Use GUI to edit data (validates automatically)

## Data Portability

### Sync Across Devices

**Option 1: Cloud Sync (Recommended)**
```bash
# Point career data to cloud-synced folder
export CAREER_DATA_FILE="~/Dropbox/ResumeTailor/career_data.json"
```

**Option 2: Manual Export/Import**
```bash
# Export (just copy the file)
cp ~/.resume_tailor/career_data.json backup/

# Import (copy back)
cp backup/career_data.json ~/.resume_tailor/
```

### Version Control

You can track career data in git:
```bash
cd ~/.resume_tailor
git init
git add career_data.json
git commit -m "Career data snapshot"
```

## Performance

**Benchmarks (100 jobs, 100 skills):**
- Load: ~2ms (avg)
- Save: ~15ms (avg)
- Cache hit: 0.03ms (avg)

**Targets:** <100ms for load/save ✅

## FAQ

**Q: Can I still use supermemory?**
A: No, v2.0 removes supermemory dependency. Migrate to local storage.

**Q: What happens to my supermemory data?**
A: It's not deleted. Migration copies it to local JSON.

**Q: Can I customize the file location?**
A: Yes, set `CAREER_DATA_FILE` environment variable.

**Q: Is my data encrypted?**
A: No. The file is plain JSON. Use OS-level encryption if needed.

**Q: How do I share data across machines?**
A: Use cloud sync (Dropbox, OneDrive) or manual file copies.

**Q: Can I edit the JSON manually?**
A: Yes, but be careful. Invalid JSON will be rejected. Always backup first.

## Support

**Issues?** Create an issue on GitHub with:
- Error messages
- Steps to reproduce
- Contents of `migration_errors.log` (if available)

**Questions?** Check the main README or open a discussion.
