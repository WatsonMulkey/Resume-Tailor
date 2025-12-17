# Resume Tailor GUI - Quick Start Guide

## 🚀 Using the GUI

### Option 1: Run Directly (Python Required)
```bash
python resume_tailor_gui.py
```

### Option 2: Build Executable (No Python Needed After Build)
```bash
# Double-click this file:
build_executable.bat

# Or run manually:
pip install pyinstaller
pyinstaller --onefile --windowed --name "Resume Tailor" resume_tailor_gui.py
```

The executable will be created at: `dist\Resume Tailor.exe`

---

## 📋 How to Use

1. **Paste Job Description**
   - Copy entire job posting from company website
   - Paste into large text box

2. **Enter Company Name**
   - Type company name (e.g., "ClassDojo")
   - Used for folder organization

3. **Choose AI Model**
   - **Sonnet-4**: Higher quality, better accuracy (~$0.10/resume)
   - **Haiku**: Faster, cheaper (~$0.01/resume)
   - *Recommendation: Use Sonnet-4 for best results*

4. **Select Output**
   - ☑ Resume - Generate tailored resume
   - ☑ Cover Letter - Generate cover letter
   - *You can select both!*

5. **Click GENERATE**
   - Watch status log for progress
   - Files saved to: `C:\Users\watso\OneDrive\Desktop\Jobs\[Company]\`

---

## 📁 Output Files

For each company, you'll get:
- `Watson_Mulkey_Resume_[Company].md` - Markdown version
- `Watson_Mulkey_Resume_[Company].pdf` - PDF version
- `Watson_Mulkey_Resume_[Company].docx` - Word version (ATS-friendly)
- `Watson_Mulkey_Resume_[Company].html` - HTML version
- `Watson_Mulkey_[Company]_CoverLetter.md` - Cover letter

---

## 🎨 GUI Features

### Retro Terminal Aesthetic
- Green-on-black terminal colors
- ASCII art header
- Monospace fonts
- Pure function, maximum style

### Real-time Status
- Live generation progress
- Error messages if something fails
- Success notification with file location

### Background Processing
- GUI stays responsive during generation
- Can queue multiple jobs
- No freezing or hanging

---

## 🔧 Troubleshooting

### "No module named anthropic"
```bash
pip install anthropic python-dotenv
```

### "API key not found"
Make sure `.env` file exists with:
```
ANTHROPIC_API_KEY=your-key-here
```

### GUI won't start on double-click (executable)
- Right-click → "Run as Administrator"
- Check Windows Defender didn't block it

### Generation fails
- Check internet connection (needs API access)
- Verify API key is valid
- Check status log for error details

---

## 💡 Tips

1. **Keep job description complete** - Include full posting for best results
2. **Use company's actual name** - Helps with folder organization
3. **Sonnet-4 for important applications** - Quality worth the extra $0.09
4. **Review before sending** - AI is good but always fact-check
5. **Save originals** - Keep .md files to manually edit if needed

---

## 🎯 Keyboard Shortcuts

- `Ctrl+A` in job description box - Select all
- `Ctrl+V` - Paste job description
- `Enter` in company name field - Focus moves to next field
- `Tab` - Navigate between fields

---

## 📊 Cost Tracking

Approximate costs per generation:

| Model | Resume | Cover Letter | Both | 30 Applications |
|-------|--------|--------------|------|-----------------|
| Sonnet-4 | $0.05 | $0.05 | $0.10 | $3.00 |
| Haiku | $0.005 | $0.005 | $0.01 | $0.30 |

*All costs are pay-as-you-go. No monthly fees.*

---

## 🐛 Known Issues

- None yet! Report issues by updating this file.

---

## 🎨 Future Enhancements (Optional)

- [ ] Drag-and-drop file support
- [ ] Save/load job descriptions
- [ ] History of generated applications
- [ ] Custom output directory picker
- [ ] Dark/light theme toggle
- [ ] Progress bar during generation
- [ ] Cost tracker (running total)
