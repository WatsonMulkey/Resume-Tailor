"""
Discovery Dialog UI Components

Multi-step dialogs for capturing skill information with validation.
Prevents hallucinations through structured, mandatory input fields.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Optional, Callable, Dict, Any

from models import DiscoveredSkill
from career_discovery import (
    validate_discovered_skill,
    detect_hallucinations
)


class MultiStepDiscoveryDialog:
    """
    Multi-step dialog for discovering new skills.

    5 steps:
    1. Confirm experience (Yes/No)
    2. Company/Project (required text)
    3. Timeframe (YYYY-MM format, validated)
    4. Specific example (min 20 chars, required)
    5. Measurable result (optional)
    """

    def __init__(
        self,
        parent,
        skill_name: str,
        job_description: str = "",
        on_complete: Optional[Callable] = None
    ):
        self.parent = parent
        self.skill_name = skill_name
        self.job_description = job_description
        self.on_complete = on_complete

        # Dialog data
        self.has_experience = None
        self.company = ""
        self.timeframe_start = ""
        self.timeframe_end = ""
        self.example = ""
        self.result = ""

        # Current step
        self.current_step = 1
        self.max_steps = 5

        # Colors (matching main GUI theme)
        self.bg_color = "#1a1a1a"
        self.fg_color = "#00ff00"
        self.text_bg = "#0d0d0d"
        self.accent_color = "#00aaff"
        self.error_color = "#ff0000"
        self.warning_color = "#ffaa00"

        self.mono_font = ("Courier New", 10)
        self.mono_font_bold = ("Courier New", 10, "bold")

        self._create_dialog()

    def _create_dialog(self):
        """Create the main dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Add Skill: {self.skill_name}")
        self.dialog.geometry("700x500")
        self.dialog.configure(bg=self.bg_color)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Header
        self.header_label = tk.Label(
            self.dialog,
            text=f"",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.header_label.pack(pady=10)

        # Content frame (will be replaced for each step)
        self.content_frame = tk.Frame(self.dialog, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Navigation buttons
        nav_frame = tk.Frame(self.dialog, bg=self.bg_color)
        nav_frame.pack(pady=10)

        self.back_btn = tk.Button(
            nav_frame,
            text="<< Back",
            font=self.mono_font,
            fg=self.bg_color,
            bg=self.fg_color,
            command=self._go_back,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(
            nav_frame,
            text="Next >>",
            font=self.mono_font_bold,
            fg=self.bg_color,
            bg=self.accent_color,
            command=self._go_next
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.skip_btn = tk.Button(
            nav_frame,
            text="Skip",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            command=self.dialog.destroy
        )
        self.skip_btn.pack(side=tk.LEFT, padx=5)

        # Show first step
        self._show_step(1)

    def _show_step(self, step: int):
        """Display the specified step."""
        self.current_step = step

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update header
        self.header_label.config(
            text=f"Step {step}/{self.max_steps}: Adding '{self.skill_name}'"
        )

        # Show appropriate step
        if step == 1:
            self._show_step1_confirm()
        elif step == 2:
            self._show_step2_company()
        elif step == 3:
            self._show_step3_timeframe()
        elif step == 4:
            self._show_step4_example()
        elif step == 5:
            self._show_step5_result()

        # Update navigation buttons
        self.back_btn.config(state=tk.NORMAL if step > 1 else tk.DISABLED)
        self.next_btn.config(
            text="Finish" if step == self.max_steps else "Next >>"
        )

    def _show_step1_confirm(self):
        """Step 1: Confirm experience."""
        tk.Label(
            self.content_frame,
            text=f"Do you have experience with {self.skill_name}?",
            font=self.mono_font_bold,
            fg=self.fg_color,
            bg=self.bg_color,
            justify=tk.LEFT
        ).pack(pady=20)

        self.experience_var = tk.StringVar(value="yes")

        tk.Radiobutton(
            self.content_frame,
            text="Yes, I've used it professionally",
            variable=self.experience_var,
            value="yes",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color
        ).pack(anchor=tk.W, padx=40, pady=5)

        tk.Radiobutton(
            self.content_frame,
            text="Yes, in side projects only",
            variable=self.experience_var,
            value="side",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color
        ).pack(anchor=tk.W, padx=40, pady=5)

        tk.Radiobutton(
            self.content_frame,
            text="No / Not sure",
            variable=self.experience_var,
            value="no",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.text_bg,
            activebackground=self.bg_color
        ).pack(anchor=tk.W, padx=40, pady=5)

    def _show_step2_company(self):
        """Step 2: Company/Project (required)."""
        tk.Label(
            self.content_frame,
            text=f"Which company or project did you use {self.skill_name}?",
            font=self.mono_font_bold,
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(pady=10)

        tk.Label(
            self.content_frame,
            text='Example: "Acme Corp" or "Personal Project: Portfolio Site"',
            font=self.mono_font,
            fg=self.warning_color,
            bg=self.bg_color
        ).pack(pady=5)

        self.company_entry = tk.Entry(
            self.content_frame,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            width=50
        )
        self.company_entry.pack(pady=10)
        self.company_entry.insert(0, self.company)
        self.company_entry.focus()

    def _show_step3_timeframe(self):
        """Step 3: Timeframe (YYYY-MM format)."""
        tk.Label(
            self.content_frame,
            text="What timeframe? (YYYY-MM format)",
            font=self.mono_font_bold,
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(pady=10)

        # Start date
        start_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        start_frame.pack(pady=5)

        tk.Label(
            start_frame,
            text="Start:",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)

        self.start_entry = tk.Entry(
            start_frame,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            width=10
        )
        self.start_entry.pack(side=tk.LEFT)
        self.start_entry.insert(0, self.timeframe_start)

        tk.Label(
            start_frame,
            text="(e.g., 2023-06)",
            font=self.mono_font,
            fg=self.warning_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=10)

        # End date
        end_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        end_frame.pack(pady=5)

        tk.Label(
            end_frame,
            text="End:  ",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)

        self.end_entry = tk.Entry(
            end_frame,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            width=10
        )
        self.end_entry.pack(side=tk.LEFT)
        self.end_entry.insert(0, self.timeframe_end)

        tk.Label(
            end_frame,
            text='(or "Present")',
            font=self.mono_font,
            fg=self.warning_color,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=10)

    def _show_step4_example(self):
        """Step 4: Specific example (min 20 chars, required)."""
        tk.Label(
            self.content_frame,
            text=f"Describe a specific example of using {self.skill_name}",
            font=self.mono_font_bold,
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(pady=10)

        tk.Label(
            self.content_frame,
            text="Minimum 20 characters. Be specific and concrete.",
            font=self.mono_font,
            fg=self.warning_color,
            bg=self.bg_color
        ).pack(pady=5)

        self.example_text = scrolledtext.ScrolledText(
            self.content_frame,
            height=8,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            wrap=tk.WORD
        )
        self.example_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.example_text.insert('1.0', self.example)

        # Character counter
        self.char_count_label = tk.Label(
            self.content_frame,
            text="0 / 500 characters (min 20)",
            font=self.mono_font,
            fg=self.warning_color,
            bg=self.bg_color
        )
        self.char_count_label.pack()

        def update_char_count(*args):
            text = self.example_text.get('1.0', tk.END).strip()
            count = len(text)
            color = self.fg_color if count >= 20 else self.error_color
            self.char_count_label.config(
                text=f"{count} / 500 characters (min 20)",
                fg=color
            )

        self.example_text.bind('<KeyRelease>', update_char_count)
        update_char_count()

    def _show_step5_result(self):
        """Step 5: Measurable result (optional)."""
        tk.Label(
            self.content_frame,
            text="What was the measurable result? (Optional)",
            font=self.mono_font_bold,
            fg=self.fg_color,
            bg=self.bg_color
        ).pack(pady=10)

        tk.Label(
            self.content_frame,
            text='Examples: "40% faster deployments", "99.9% uptime", "Saved $50K annually"',
            font=self.mono_font,
            fg=self.warning_color,
            bg=self.bg_color
        ).pack(pady=5)

        self.result_entry = tk.Entry(
            self.content_frame,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            width=50
        )
        self.result_entry.pack(pady=10)
        self.result_entry.insert(0, self.result)

    def _go_back(self):
        """Go to previous step."""
        if self.current_step > 1:
            # Save current data
            self._save_current_step()
            # Show previous step
            self._show_step(self.current_step - 1)

    def _go_next(self):
        """Go to next step or finish."""
        # Validate current step
        if not self._validate_current_step():
            return

        # Save current data
        self._save_current_step()

        if self.current_step == self.max_steps:
            # Finish - show review dialog
            self._finish()
        else:
            # Next step
            self._show_step(self.current_step + 1)

    def _save_current_step(self):
        """Save data from current step."""
        if self.current_step == 1:
            self.has_experience = self.experience_var.get()
        elif self.current_step == 2:
            self.company = self.company_entry.get().strip()
        elif self.current_step == 3:
            self.timeframe_start = self.start_entry.get().strip()
            self.timeframe_end = self.end_entry.get().strip()
        elif self.current_step == 4:
            self.example = self.example_text.get('1.0', tk.END).strip()
        elif self.current_step == 5:
            self.result = self.result_entry.get().strip()

    def _validate_current_step(self) -> bool:
        """Validate current step data."""
        if self.current_step == 1:
            if not hasattr(self, 'experience_var'):
                return True
            if self.experience_var.get() == "no":
                messagebox.showinfo(
                    "No Experience",
                    f"Okay, we won't add {self.skill_name} to your career data."
                )
                self.dialog.destroy()
                return False

        elif self.current_step == 2:
            company = self.company_entry.get().strip()
            if not company or len(company) < 2:
                messagebox.showerror(
                    "Company Required",
                    "Please enter a company name or project.\n\n"
                    "This is required to provide context for your experience."
                )
                return False

        elif self.current_step == 3:
            start = self.start_entry.get().strip()
            end = self.end_entry.get().strip()

            # Validate format
            import re
            pattern = r'^\d{4}-\d{2}$'

            if not re.match(pattern, start):
                messagebox.showerror(
                    "Invalid Format",
                    "Start date must be in YYYY-MM format.\n\n"
                    "Example: 2023-06"
                )
                return False

            if end != "Present" and not re.match(pattern, end):
                messagebox.showerror(
                    "Invalid Format",
                    'End date must be in YYYY-MM format or "Present".\n\n'
                    "Example: 2024-03 or Present"
                )
                return False

        elif self.current_step == 4:
            example = self.example_text.get('1.0', tk.END).strip()

            if len(example) < 20:
                messagebox.showerror(
                    "Example Too Short",
                    f"Please provide at least 20 characters ({len(example)}/20).\n\n"
                    "Be specific about what you did and how you used the skill."
                )
                return False

            if len(example) > 500:
                messagebox.showerror(
                    "Example Too Long",
                    f"Please keep it under 500 characters ({len(example)}/500)."
                )
                return False

        return True

    def _finish(self):
        """Complete discovery and show review dialog."""
        # Create DiscoveredSkill
        timeframe = self.timeframe_start
        if self.timeframe_end:
            timeframe += f" to {self.timeframe_end}"

        try:
            discovered = DiscoveredSkill(
                name=self.skill_name,
                company=self.company,
                timeframe=timeframe,
                example=self.example,
                result=self.result if self.result else None,
                category="technical"
            )

            # Close this dialog
            self.dialog.destroy()

            # Show review dialog
            ReviewDialog(
                self.parent,
                discovered,
                self.job_description,
                on_save=self.on_complete
            )

        except Exception as e:
            messagebox.showerror(
                "Validation Error",
                f"Failed to create skill entry:\n\n{str(e)}"
            )


class ReviewDialog:
    """Review mode dialog before saving discovered skill."""

    def __init__(
        self,
        parent,
        discovered: DiscoveredSkill,
        job_description: str = "",
        on_save: Optional[Callable] = None
    ):
        self.parent = parent
        self.discovered = discovered
        self.job_description = job_description
        self.on_save = on_save

        # Colors
        self.bg_color = "#1a1a1a"
        self.fg_color = "#00ff00"
        self.text_bg = "#0d0d0d"
        self.accent_color = "#00aaff"
        self.error_color = "#ff0000"
        self.warning_color = "#ffaa00"

        self.mono_font = ("Courier New", 10)
        self.mono_font_bold = ("Courier New", 10, "bold")

        self._create_dialog()

    def _create_dialog(self):
        """Create review dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Review Before Saving")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg=self.bg_color)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Header
        tk.Label(
            self.dialog,
            text="╔═══════════════════════════════════════════════════════════╗\n"
                 "║          REVIEW BEFORE SAVING                         ║\n"
                 "╚═══════════════════════════════════════════════════════════╝",
            font=self.mono_font_bold,
            fg=self.accent_color,
            bg=self.bg_color,
            justify=tk.LEFT
        ).pack(pady=10)

        # Content area
        content_text = scrolledtext.ScrolledText(
            self.dialog,
            height=20,
            font=self.mono_font,
            bg=self.text_bg,
            fg=self.fg_color,
            state=tk.DISABLED
        )
        content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Build review content
        review_text = self._build_review_text()

        content_text.config(state=tk.NORMAL)
        content_text.insert('1.0', review_text)
        content_text.config(state=tk.DISABLED)

        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=self.bg_color)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Save to Career Data",
            font=self.mono_font_bold,
            fg=self.bg_color,
            bg=self.accent_color,
            command=self._save
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Edit",
            font=self.mono_font,
            fg=self.bg_color,
            bg=self.fg_color,
            command=self._edit
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Discard",
            font=self.mono_font,
            fg=self.fg_color,
            bg=self.bg_color,
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _build_review_text(self) -> str:
        """Build review text with validation results."""
        text = "PROPOSED ADDITION\n"
        text += "─" * 60 + "\n\n"

        text += f"Skill: {self.discovered.name}\n"
        text += f"Company: {self.discovered.company}\n"
        text += f"Timeframe: {self.discovered.timeframe}\n\n"

        text += "Example:\n"
        text += f"{self.discovered.example}\n\n"

        if self.discovered.result:
            text += f"Result: {self.discovered.result}\n\n"

        text += "─" * 60 + "\n"
        text += "VALIDATION CHECKS\n"
        text += "─" * 60 + "\n\n"

        # Run validations
        validation = validate_discovered_skill(self.discovered)
        hallucinations = detect_hallucinations(
            self.discovered.example,
            self.job_description
        )

        # Show results
        if validation['valid'] and not hallucinations:
            text += "[OK] All checks passed\n"
        else:
            if validation['errors']:
                for error in validation['errors']:
                    text += f"[ERROR] {error}\n"

            if validation['warnings']:
                for warning in validation['warnings']:
                    text += f"[WARN] {warning}\n"

            if hallucinations:
                for warning in hallucinations:
                    text += f"[WARN] {warning}\n"

        return text

    def _save(self):
        """Save discovered skill to career data."""
        try:
            if self.on_save:
                self.on_save(self.discovered)

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(
                "Save Failed",
                f"Failed to save skill:\n\n{str(e)}"
            )

    def _edit(self):
        """Go back to edit."""
        # TODO: Re-open discovery dialog with pre-filled data
        messagebox.showinfo(
            "Edit",
            "Edit functionality: Close this dialog and start over.\n\n"
            "(Full edit mode coming in next update)"
        )
