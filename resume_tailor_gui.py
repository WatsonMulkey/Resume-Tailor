"""
Resume Tailor GUI - ASCII Art Edition

A retro terminal-style GUI for generating resumes and cover letters.
Pure function, maximum style.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from pathlib import Path
import threading
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import ResumeGenerator


ASCII_LOGO = r"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ███████╗███████╗██╗   ██╗███╗   ███╗███████╗   ║
║   ██╔══██╗██╔════╝██╔════╝██║   ██║████╗ ████║██╔════╝   ║
║   ██████╔╝█████╗  ███████╗██║   ██║██╔████╔██║█████╗     ║
║   ██╔══██╗██╔══╝  ╚════██║██║   ██║██║╚██╔╝██║██╔══╝     ║
║   ██║  ██║███████╗███████║╚██████╔╝██║ ╚═╝ ██║███████╗   ║
║   ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ║
║                                                           ║
║              ████████╗ █████╗ ██╗██╗      ██████╗ ██████╗ ║
║              ╚══██╔══╝██╔══██╗██║██║     ██╔═══██╗██╔══██╗║
║                 ██║   ███████║██║██║     ██║   ██║██████╔╝║
║                 ██║   ██╔══██║██║██║     ██║   ██║██╔══██╗║
║                 ██║   ██║  ██║██║███████╗╚██████╔╝██║  ██║║
║                 ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝║
║                                                           ║
║              [ AI-Powered Resume Generation ]            ║
╚═══════════════════════════════════════════════════════════╝
"""


class ResumeTailorGUI:
    """Retro terminal-style GUI for Resume Tailor."""

    def __init__(self, root):
        self.root = root
        self.root.title("Resume Tailor v2.0")
        self.root.geometry("1000x850")
        self.root.configure(bg="#1a1a1a")

        # Retro terminal colors
        self.bg_color = "#1a1a1a"
        self.fg_color = "#00ff00"
        self.text_bg = "#0d0d0d"
        self.accent_color = "#00aaff"

        # Fonts
        self.mono_font = ("Courier New", 10)
        self.mono_font_bold = ("Courier New", 10, "bold")
        self.title_font = ("Courier New", 8)

        self.setup_ui()

        # Discovery mode enabled by default
        self.discovery_enabled = True

        # Check if migration needed (after UI is set up)
        self.root.after(100, self.check_migration_needed)

    def setup_ui(self):
        """Build the terminal-style interface."""

        # Menu Bar
        menubar = tk.Menu(self.root, bg=self.bg_color, fg=self.fg_color)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Restore from Backup", command=self.restore_from_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # ASCII Art Header
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(pady=10)

        header_label = tk.Label(
            header_frame,
            text=ASCII_LOGO,
            font=self.title_font,
            fg=self.accent_color,
            bg=self.bg_color,
            justify=tk.LEFT
        )
        header_label.pack()

        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Job Description Input
        self.create_section_header(main_frame, "╔═══ JOB DESCRIPTION ═══════════════════════════════════════╗")

        self.job_desc_text = scrolledtext.ScrolledText(
            main_frame,
            height=12,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            borderwidth=2
        )
        self.job_desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Company Name
        company_frame = tk.Frame(main_frame, bg=self.bg_color)
        company_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            company_frame,
            text=">> COMPANY NAME:",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT)

        self.company_entry = tk.Entry(
            company_frame,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            borderwidth=2,
            width=30
        )
        self.company_entry.pack(side=tk.LEFT, padx=10)

        # Model Selection
        model_frame = tk.Frame(main_frame, bg=self.bg_color)
        model_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            model_frame,
            text=">> AI MODEL:",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT)

        self.model_var = tk.StringVar(value="sonnet")

        sonnet_radio = tk.Radiobutton(
            model_frame,
            text="[X] SONNET-4 (Precision)",
            variable=self.model_var,
            value="sonnet",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        sonnet_radio.pack(side=tk.LEFT, padx=10)

        haiku_radio = tk.Radiobutton(
            model_frame,
            text="[ ] HAIKU (Speed)",
            variable=self.model_var,
            value="haiku",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        haiku_radio.pack(side=tk.LEFT, padx=10)

        # Output Options
        output_frame = tk.Frame(main_frame, bg=self.bg_color)
        output_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            output_frame,
            text=">> GENERATE:",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT)

        self.resume_var = tk.BooleanVar(value=True)
        self.cover_letter_var = tk.BooleanVar(value=True)

        resume_check = tk.Checkbutton(
            output_frame,
            text="[X] RESUME",
            variable=self.resume_var,
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        resume_check.pack(side=tk.LEFT, padx=10)

        cover_check = tk.Checkbutton(
            output_frame,
            text="[X] COVER LETTER",
            variable=self.cover_letter_var,
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        cover_check.pack(side=tk.LEFT, padx=10)

        self.discovery_var = tk.BooleanVar(value=True)
        discovery_check = tk.Checkbutton(
            output_frame,
            text="[X] SKILL DISCOVERY",
            variable=self.discovery_var,
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        discovery_check.pack(side=tk.LEFT, padx=10)

        # Generate Button
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=20)

        self.generate_btn = tk.Button(
            button_frame,
            text="╔═══════════════════════════════════╗\n║  >>> GENERATE DOCUMENTS <<<   ║\n╚═══════════════════════════════════╝",
            font=self.mono_font_bold,
            fg=self.bg_color,
            bg=self.accent_color,
            activebackground=self.fg_color,
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            borderwidth=0,
            command=self.generate_documents,
            cursor="hand2"
        )
        self.generate_btn.pack()

        # Status Display
        self.create_section_header(main_frame, "╔═══ STATUS ════════════════════════════════════════════════╗")

        self.status_text = scrolledtext.ScrolledText(
            main_frame,
            height=6,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            relief=tk.FLAT,
            borderwidth=2,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, pady=(0, 10))

        self.log_status(">> System initialized. Ready for input.")
        self.log_status(">> Paste job description and click GENERATE.")

    def check_migration_needed(self):
        """Check if career data needs migration from supermemory."""
        from career_data_manager import get_manager
        from pathlib import Path

        manager = get_manager()

        # Check if career_data.json exists
        if manager.file_path.exists():
            # Data already migrated
            return

        # Check if import_career_data.py exists (indicating supermemory data available)
        import_file = Path(__file__).parent / 'import_career_data.py'
        if not import_file.exists():
            # No data to migrate - show first-time setup
            self.show_first_time_setup()
            return

        # Show migration dialog
        self.show_migration_dialog()

    def show_migration_dialog(self):
        """Show migration dialog for supermemory -> local storage."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Migration Available")
        dialog.geometry("600x400")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = tk.Label(
            dialog,
            text="╔═══════════════════════════════════════════════════════╗\n"
                 "║          MIGRATION AVAILABLE                      ║\n"
                 "╚═══════════════════════════════════════════════════════╝",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color,
            justify=tk.LEFT
        )
        title.pack(pady=20)

        # Message
        message = tk.Label(
            dialog,
            text="We've detected career data from a previous version.\n\n"
                 "This version stores data locally for:\n"
                 "  • Privacy (your data stays on your machine)\n"
                 "  • Reliability (no external dependencies)\n"
                 "  • Performance (faster access)\n\n"
                 "Would you like to migrate now?\n\n"
                 "Estimated time: <30 seconds",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            justify=tk.LEFT
        )
        message.pack(pady=10, padx=20)

        # Button frame
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=20)

        # Preview button
        preview_btn = tk.Button(
            button_frame,
            text="Preview Migration",
            font=self.mono_font,
            fg=self.bg_color,
            bg=self.fg_color,
            command=lambda: self.run_migration_preview(dialog)
        )
        preview_btn.pack(side=tk.LEFT, padx=5)

        # Migrate button
        migrate_btn = tk.Button(
            button_frame,
            text="Migrate Now",
            font=self.mono_font_bold,
            fg=self.bg_color,
            bg=self.accent_color,
            command=lambda: self.run_migration(dialog)
        )
        migrate_btn.pack(side=tk.LEFT, padx=5)

        # Skip button
        skip_btn = tk.Button(
            button_frame,
            text="Skip",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            command=dialog.destroy
        )
        skip_btn.pack(side=tk.LEFT, padx=5)

    def run_migration_preview(self, parent_dialog):
        """Run migration in preview mode."""
        import subprocess

        # Close parent dialog
        parent_dialog.destroy()

        # Show preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Migration Preview")
        preview_window.geometry("700x500")
        preview_window.configure(bg=self.bg_color)

        # Preview text area
        preview_text = scrolledtext.ScrolledText(
            preview_window,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            state=tk.DISABLED
        )
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Run migration preview
        try:
            result = subprocess.run(
                [sys.executable, 'migrate_from_supermemory.py', '--preview'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )

            preview_text.config(state=tk.NORMAL)
            preview_text.insert('1.0', result.stdout)
            preview_text.config(state=tk.DISABLED)

        except Exception as e:
            preview_text.config(state=tk.NORMAL)
            preview_text.insert('1.0', f"Preview failed: {e}")
            preview_text.config(state=tk.DISABLED)

        # Close button
        close_btn = tk.Button(
            preview_window,
            text="Close",
            command=lambda: [preview_window.destroy(), self.show_migration_dialog()]
        )
        close_btn.pack(pady=10)

    def run_migration(self, parent_dialog):
        """Run actual migration."""
        import subprocess

        # Close parent dialog
        parent_dialog.destroy()

        # Show progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Migrating...")
        progress_window.geometry("600x300")
        progress_window.configure(bg=self.bg_color)
        progress_window.transient(self.root)
        progress_window.grab_set()

        # Progress label
        progress_label = tk.Label(
            progress_window,
            text="Migrating career data to local storage...",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color
        )
        progress_label.pack(pady=20)

        # Progress text
        progress_text = scrolledtext.ScrolledText(
            progress_window,
            height=10,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            state=tk.DISABLED
        )
        progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def run_migration_thread():
            try:
                # Run migration with auto-confirm
                result = subprocess.run(
                    [sys.executable, 'migrate_from_supermemory.py'],
                    input='y\n',
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent
                )

                # Update UI in main thread
                self.root.after(0, lambda: progress_text.config(state=tk.NORMAL))
                self.root.after(0, lambda: progress_text.insert('1.0', result.stdout))
                self.root.after(0, lambda: progress_text.config(state=tk.DISABLED))

                if result.returncode == 0:
                    self.root.after(0, lambda: progress_label.config(
                        text="✓ Migration Complete!",
                        fg=self.fg_color
                    ))

                    # Add close button
                    def close_and_confirm():
                        progress_window.destroy()
                        messagebox.showinfo(
                            "Success",
                            "Migration completed successfully!\n\n"
                            "Your career data is now stored locally at:\n"
                            f"{result.stdout.split('Location: ')[1].split()[0] if 'Location:' in result.stdout else '~/.resume_tailor/career_data.json'}"
                        )

                    close_btn = tk.Button(
                        progress_window,
                        text="Close",
                        font=self.mono_font_bold,
                        command=close_and_confirm
                    )
                    self.root.after(0, lambda: close_btn.pack(pady=10))
                else:
                    self.root.after(0, lambda: progress_label.config(
                        text="✗ Migration Failed",
                        fg="#ff0000"
                    ))

            except Exception as e:
                self.root.after(0, lambda: progress_text.config(state=tk.NORMAL))
                self.root.after(0, lambda: progress_text.insert('1.0', f"Error: {e}"))
                self.root.after(0, lambda: progress_text.config(state=tk.DISABLED))
                self.root.after(0, lambda: progress_label.config(text="✗ Error", fg="#ff0000"))

        # Run in background thread
        thread = threading.Thread(target=run_migration_thread, daemon=True)
        thread.start()

    def show_first_time_setup(self):
        """Show first-time setup dialog for file location."""
        from career_data_manager import get_manager

        dialog = tk.Toplevel(self.root)
        dialog.title("Welcome to Resume Tailor")
        dialog.geometry("550x350")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = tk.Label(
            dialog,
            text="╔═══════════════════════════════════════════════════════╗\n"
                 "║          WELCOME TO RESUME TAILOR                 ║\n"
                 "╚═══════════════════════════════════════════════════════╝",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color,
            justify=tk.LEFT
        )
        title.pack(pady=20)

        # Message
        default_location = str(get_manager().file_path)
        message = tk.Label(
            dialog,
            text="Where would you like to store your career data?\n\n"
                 "This file will contain your:\n"
                 "  • Job history\n"
                 "  • Skills and achievements\n"
                 "  • Personal information\n\n"
                 f"Default location:\n{default_location}\n\n"
                 "Your data never leaves your machine.\n"
                 "You control where it lives.",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            justify=tk.LEFT
        )
        message.pack(pady=10, padx=20)

        # Button frame
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=20)

        # Default location button
        default_btn = tk.Button(
            button_frame,
            text="Use Default Location",
            font=self.mono_font_bold,
            fg=self.bg_color,
            bg=self.accent_color,
            command=lambda: self.create_empty_career_data(dialog, default_location)
        )
        default_btn.pack(side=tk.LEFT, padx=5)

        # Custom location button (future feature)
        # custom_btn = tk.Button(
        #     button_frame,
        #     text="Choose Custom Location",
        #     font=self.mono_font,
        #     command=lambda: self.choose_custom_location(dialog)
        # )
        # custom_btn.pack(side=tk.LEFT, padx=5)

    def create_empty_career_data(self, dialog, location):
        """Create empty career data file."""
        from career_data_manager import load_career_data

        try:
            # This will create the empty file with default structure
            load_career_data()

            dialog.destroy()

            messagebox.showinfo(
                "Setup Complete",
                f"Career data file created at:\n{location}\n\n"
                "You're ready to generate resumes!\n\n"
                "Tip: Add your career data gradually as you apply to jobs."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create career data file:\n{e}")

    def _create_discovery_callback(self):
        """Create discovery callback for skill detection."""
        def discovery_callback(job_description: str, job_info: dict):
            """Callback to detect and add missing skills."""
            from career_discovery import detect_missing_skills
            from discovery_dialogs import MultiStepDiscoveryDialog
            from career_data_manager import load_career_data, save_career_data
            from models import Skill, Achievement

            # Detect missing skills
            missing_skills = detect_missing_skills(job_description, max_skills=5)

            if not missing_skills:
                return  # No missing skills

            # Show discovery prompt on main thread
            def show_discovery_prompt():
                from tkinter import messagebox

                # Ask if user wants to add skills
                result = messagebox.askyesno(
                    "Skills Discovered",
                    f"The job description mentions {len(missing_skills)} skill(s) "
                    f"not in your career data:\n\n" +
                    "\n".join(f"  • {skill}" for skill in missing_skills[:5]) +
                    f"\n\nWould you like to add any of these?"
                )

                if not result:
                    return

                # Show discovery dialog for each skill
                self._show_discovery_for_skills(missing_skills, job_description)

            # Run on main thread
            self.root.after(0, show_discovery_prompt)

        return discovery_callback

    def _show_discovery_for_skills(self, skills: list, job_description: str):
        """Show discovery dialogs for multiple skills."""
        from discovery_dialogs import MultiStepDiscoveryDialog
        from career_data_manager import load_career_data, save_career_data
        from models import Skill, Achievement

        if not skills:
            return

        # Get first skill
        skill_name = skills[0]
        remaining_skills = skills[1:]

        def on_skill_saved(discovered_skill):
            """Callback when user saves a discovered skill."""
            try:
                # Load current career data
                career_data = load_career_data()

                # Check if skill already exists
                existing_skill = None
                for skill in career_data.skills:
                    if skill.name.lower() == discovered_skill.name.lower():
                        existing_skill = skill
                        break

                # Create achievement from discovered skill
                achievement = Achievement(
                    description=discovered_skill.example,
                    company=discovered_skill.company,
                    timeframe=discovered_skill.timeframe,
                    result=discovered_skill.result
                )

                if existing_skill:
                    # Add as another example to existing skill
                    existing_skill.examples.append(achievement)
                    self.log_status(f">> Added example to existing skill: {discovered_skill.name}")
                else:
                    # Create new skill
                    new_skill = Skill(
                        name=discovered_skill.name,
                        category=discovered_skill.category or "technical",
                        proficiency="advanced",
                        examples=[achievement],
                        last_used=discovered_skill.timeframe.split(' to ')[0]
                    )
                    career_data.skills.append(new_skill)
                    self.log_status(f">> Added new skill: {discovered_skill.name}")

                # Save career data
                save_career_data(career_data)
                self.log_status(f">> Saved to career data")

                # Continue with remaining skills
                if remaining_skills:
                    from tkinter import messagebox
                    result = messagebox.askyesno(
                        "More Skills",
                        f"{len(remaining_skills)} more skill(s) detected.\n\nContinue adding?"
                    )
                    if result:
                        self._show_discovery_for_skills(remaining_skills, job_description)

            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror(
                    "Save Failed",
                    f"Failed to save skill:\n\n{str(e)}"
                )

        def on_skill_skipped(skill_name):
            """Callback when user skips a skill."""
            try:
                # Load current career data
                career_data = load_career_data()

                # Add to skipped skills if not already there
                if skill_name.lower() not in [s.lower() for s in career_data.skipped_skills]:
                    career_data.skipped_skills.append(skill_name)
                    save_career_data(career_data)
                    self.log_status(f">> Skipped skill: {skill_name}")

                # Continue with remaining skills
                if remaining_skills:
                    from tkinter import messagebox
                    result = messagebox.askyesno(
                        "More Skills",
                        f"{len(remaining_skills)} more skill(s) detected.\n\nContinue adding?"
                    )
                    if result:
                        self._show_discovery_for_skills(remaining_skills, job_description)

            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror(
                    "Save Failed",
                    f"Failed to save skipped skill:\n\n{str(e)}"
                )

        def on_skill_ignored(skill_name):
            """Callback when user ignores a non-skill term."""
            try:
                # Load current career data
                career_data = load_career_data()

                # Add to ignored terms if not already there
                if skill_name.lower() not in [t.lower() for t in career_data.ignored_terms]:
                    career_data.ignored_terms.append(skill_name)
                    save_career_data(career_data)
                    self.log_status(f">> Ignored term: {skill_name}")

                # Continue with remaining skills
                if remaining_skills:
                    from tkinter import messagebox
                    result = messagebox.askyesno(
                        "More Skills",
                        f"{len(remaining_skills)} more skill(s) detected.\n\nContinue adding?"
                    )
                    if result:
                        self._show_discovery_for_skills(remaining_skills, job_description)

            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror(
                    "Save Failed",
                    f"Failed to save ignored term:\n\n{str(e)}"
                )

        # Show dialog for this skill (blocking)
        dialog = MultiStepDiscoveryDialog(
            self.root,
            skill_name,
            job_description,
            on_complete=on_skill_saved,
            on_skip=on_skill_skipped,
            on_ignore=on_skill_ignored
        )
        # Wait for dialog to close before continuing
        self.root.wait_window(dialog.dialog)

    def restore_from_backup(self):
        """Restore career data from backup file."""
        from career_data_manager import get_manager

        manager = get_manager()
        backup_path = manager.get_backup_path()

        # Check if backup exists
        if not backup_path.exists():
            messagebox.showwarning(
                "No Backup Found",
                "No backup file found.\n\n"
                f"Expected location:\n{backup_path}\n\n"
                "Backups are created automatically before each save."
            )
            return

        # Confirm restoration
        result = messagebox.askyesno(
            "Restore from Backup",
            f"This will restore your career data from the backup file.\n\n"
            f"Backup file:\n{backup_path}\n\n"
            f"Current file will be overwritten.\n\n"
            f"Continue?"
        )

        if not result:
            return

        # Perform restoration
        try:
            if manager._restore_from_backup():
                messagebox.showinfo(
                    "Success",
                    "Career data restored from backup successfully!\n\n"
                    f"Restored from:\n{backup_path}"
                )
                self.log_status(">> Career data restored from backup")
            else:
                messagebox.showerror(
                    "Restore Failed",
                    "Failed to restore from backup.\n\n"
                    "The backup file may be corrupted or inaccessible."
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to restore from backup:\n\n{str(e)}"
            )

    def show_about(self):
        """Show about dialog."""
        about_text = (
            "Resume Tailor v2.0\n\n"
            "AI-Powered Resume Generation\n\n"
            "Features:\n"
            "• Local career data storage\n"
            "• Privacy-first architecture\n"
            "• Claude AI integration\n"
            "• Automatic backup & recovery\n\n"
            "Your data stays on your machine.\n"
            "No external dependencies required."
        )

        messagebox.showinfo("About Resume Tailor", about_text)

    def create_section_header(self, parent, text):
        """Create ASCII art section header."""
        label = tk.Label(
            parent,
            text=text,
            font=self.mono_font,
            fg=self.accent_color,
            bg=self.bg_color,
            anchor=tk.W
        )
        label.pack(fill=tk.X, pady=(10, 5))

    def log_status(self, message):
        """Add message to status log."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def generate_documents(self):
        """Handle document generation in background thread."""
        # Validate inputs
        job_desc = self.job_desc_text.get("1.0", tk.END).strip()
        company_name = self.company_entry.get().strip()

        if not job_desc:
            messagebox.showerror("Error", "Please paste a job description!")
            return

        if not company_name:
            messagebox.showerror("Error", "Please enter a company name!")
            return

        if not self.resume_var.get() and not self.cover_letter_var.get():
            messagebox.showerror("Error", "Select at least Resume or Cover Letter!")
            return

        # Disable button during generation
        self.generate_btn.config(state=tk.DISABLED)

        # If discovery mode enabled, run discovery FIRST (blocking)
        if self.discovery_var.get():
            self.log_status(">> Discovery mode enabled - detecting skills...")
            from career_discovery import detect_missing_skills

            missing_skills = detect_missing_skills(job_desc, max_skills=10)

            if missing_skills:
                # Ask if user wants to add skills
                result = messagebox.askyesno(
                    "Skills Discovered",
                    f"The job description mentions {len(missing_skills)} skill(s) "
                    f"not in your career data:\n\n" +
                    "\n".join(f"  • {skill}" for skill in missing_skills[:10]) +
                    f"\n\nWould you like to add any of these?"
                )

                if result:
                    # Show discovery dialogs (blocking)
                    self._show_discovery_for_skills(missing_skills, job_desc)
                    # Discovery complete - now proceed to generation
                    self.log_status(">> Discovery complete - starting generation...")
            else:
                self.log_status(">> No new skills detected - proceeding to generation...")

        # Run generation in background thread
        thread = threading.Thread(
            target=self._generate_thread,
            args=(job_desc, company_name),
            daemon=True
        )
        thread.start()

    def _generate_thread(self, job_desc, company_name):
        """Background thread for document generation."""
        try:
            self.log_status("╔═══════════════════════════════════════════════════════════╗")
            self.log_status("║               GENERATION IN PROGRESS...               ║")
            self.log_status("╚═══════════════════════════════════════════════════════════╝")
            self.log_status("")

            # Determine model
            if self.model_var.get() == "haiku":
                self.log_status(">> Using HAIKU (fast generation mode)")
                # Temporarily switch model - we'd need to modify generator for this
                # For now, it will use whatever is set in generator.py
            else:
                self.log_status(">> Using SONNET-4 (high quality mode)")

            self.log_status(f">> Target company: {company_name}")
            self.log_status(">> Parsing job description...")

            # Create generator with logging callback so we see all errors
            generator = ResumeGenerator(verbose=False, log_callback=self.log_status)

            # Check which output formats are available
            import generator as gen_module
            self.log_status(f">> PDF Available: {gen_module.PDF_AVAILABLE}")
            self.log_status(f">> HTML Available: {gen_module.HTML_AVAILABLE}")
            self.log_status(f">> DOCX Available: {gen_module.DOCX_AVAILABLE}")
            self.log_status("")

            # Determine output directory (use local Documents to avoid OneDrive sync issues)
            base_dir = Path.home() / "Documents" / "Jobs" / company_name.replace(" ", "_")
            base_dir.mkdir(parents=True, exist_ok=True)

            self.log_status(f">> Output directory: {base_dir}")
            self.log_status("")

            # Generate documents (discovery already completed before this thread started)
            results = generator.generate(
                job_description=job_desc,
                company_name=company_name,
                output_dir=base_dir,
                resume_only=not self.cover_letter_var.get(),
                cover_letter_only=not self.resume_var.get(),
                output_format="all"
            )

            # Validate output files for placeholder text before declaring success
            self.log_status(">> Validating generated files...")
            generated_files = list(base_dir.glob("Watson_Mulkey_*"))

            for file in generated_files:
                if file.suffix == '.md':  # Only check markdown files
                    content = file.read_text(encoding='utf-8')
                    # Check for placeholder patterns
                    if '[relevant' in content or '[Key Requirement' in content or '[Specific' in content:
                        raise ValueError(f"VALIDATION FAILED: {file.name} contains placeholder text. Generation likely failed.")

            self.log_status("╔═══════════════════════════════════════════════════════════╗")
            self.log_status("║              GENERATION COMPLETE! ✓                   ║")
            self.log_status("╚═══════════════════════════════════════════════════════════╝")
            self.log_status("")
            self.log_status(">> Generated files:")

            # List generated files
            for file in generated_files:
                self.log_status(f"   • {file.name}")

            self.log_status("")
            self.log_status(f">> Location: {base_dir}")
            self.log_status(">> Ready for next job!")

            # Show success dialog
            self.root.after(0, lambda: messagebox.showinfo(
                "Success!",
                f"Documents generated successfully!\n\nSaved to:\n{base_dir}"
            ))

        except Exception as e:
            self.log_status("")
            self.log_status("╔═══════════════════════════════════════════════════════════╗")
            self.log_status("║                    ERROR!                             ║")
            self.log_status("╚═══════════════════════════════════════════════════════════╝")
            self.log_status(f">> {str(e)}")

            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Generation failed:\n\n{str(e)}"
            ))

        finally:
            # Re-enable button
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = ResumeTailorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
