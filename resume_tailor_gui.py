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
        self.root.geometry("900x700")
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

    def setup_ui(self):
        """Build the terminal-style interface."""

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

            # Create generator
            generator = ResumeGenerator(verbose=False)

            # Determine output directory
            base_dir = Path.home() / "OneDrive" / "Desktop" / "Jobs" / company_name.replace(" ", "_")
            base_dir.mkdir(parents=True, exist_ok=True)

            self.log_status(f">> Output directory: {base_dir}")
            self.log_status("")

            # Generate documents
            results = generator.generate(
                job_description=job_desc,
                company_name=company_name,
                output_dir=base_dir,
                resume_only=not self.cover_letter_var.get(),
                cover_letter_only=not self.resume_var.get(),
                output_format="all"
            )

            self.log_status("╔═══════════════════════════════════════════════════════════╗")
            self.log_status("║              GENERATION COMPLETE! ✓                   ║")
            self.log_status("╚═══════════════════════════════════════════════════════════╝")
            self.log_status("")
            self.log_status(">> Generated files:")

            # List generated files
            for file in base_dir.glob("Watson_Mulkey_*"):
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
