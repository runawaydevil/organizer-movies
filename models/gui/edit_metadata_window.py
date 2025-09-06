"""
Edit metadata window for manual correction of movie information
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import logging
from models.movie_metadata import MovieMetadata


class EditMetadataWindow:
    """
    Window for manually editing movie metadata
    """
    
    def __init__(self, parent, filename: str, current_metadata: Optional[MovieMetadata] = None):
        """
        Initialize edit metadata window
        
        Args:
            parent: Parent window
            filename: Original filename
            current_metadata: Current metadata (if any)
        """
        self.parent = parent
        self.filename = filename
        self.current_metadata = current_metadata
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.on_save_callback: Optional[Callable] = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edit Metadata - {filename}")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self._center_window()
        
        # Create GUI
        self._create_widgets()
        self._load_current_data()
        
        self.logger.info(f"Edit metadata window opened for: {filename}")
    
    def _center_window(self):
        """Center the window on the parent"""
        self.window.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create all widgets"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File info section
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text="Original Filename:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        ttk.Label(info_frame, text=self.filename, font=("Consolas", 9), foreground="blue").pack(anchor=tk.W, pady=(0, 10))
        
        # Current AI analysis (if available)
        if self.current_metadata:
            ttk.Label(info_frame, text="Current AI Analysis:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
            ai_text = f"Title: {self.current_metadata.title}"
            if self.current_metadata.year:
                ai_text += f", Year: {self.current_metadata.year}"
            ai_text += f" (Confidence: {self.current_metadata.confidence_score:.1%})"
            ttk.Label(info_frame, text=ai_text, font=("Arial", 9), foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        # Edit section
        edit_frame = ttk.LabelFrame(main_frame, text="Edit Movie Information", padding="10")
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Movie title
        ttk.Label(edit_frame, text="Movie Title:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(edit_frame, textvariable=self.title_var, font=("Arial", 11), width=50)
        title_entry.pack(fill=tk.X, pady=(5, 15))
        title_entry.focus()
        
        # Year section
        year_frame = ttk.Frame(edit_frame)
        year_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(year_frame, text="Year:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.year_var = tk.StringVar()
        year_entry = ttk.Entry(year_frame, textvariable=self.year_var, font=("Arial", 11), width=10)
        year_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Year validation
        year_entry.bind('<KeyRelease>', self._validate_year)
        
        # Clear year button
        ttk.Button(year_frame, text="Clear", command=self._clear_year, width=8).pack(side=tk.LEFT, padx=(10, 0))
        
        # Suggestions section
        suggestions_frame = ttk.LabelFrame(edit_frame, text="Quick Suggestions", padding="10")
        suggestions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Auto-extract button
        ttk.Button(
            suggestions_frame,
            text="🔍 Auto-extract from filename",
            command=self._auto_extract_from_filename
        ).pack(side=tk.LEFT)
        
        # Common patterns button
        ttk.Button(
            suggestions_frame,
            text="📝 Common patterns",
            command=self._show_common_patterns
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Preview section
        preview_frame = ttk.LabelFrame(edit_frame, text="Folder Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(preview_frame, text="Proposed folder name:", font=("Arial", 9)).pack(anchor=tk.W)
        self.preview_label = ttk.Label(
            preview_frame, 
            text="", 
            font=("Consolas", 10, "bold"), 
            foreground="green"
        )
        self.preview_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Update preview when fields change
        self.title_var.trace('w', self._update_preview)
        self.year_var.trace('w', self._update_preview)
        
        # Options section
        options_frame = ttk.LabelFrame(edit_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.reanalyze_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="�  Re-analyze with AI after saving (recommended)",
            variable=self.reanalyze_var
        ).pack(anchor=tk.W)
        
        # Info label
        info_label = ttk.Label(
            options_frame,
            text="💡 AI will always return the original movie title (English/original language)",
            font=("Arial", 9),
            foreground="blue"
        )
        info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save and Cancel buttons
        save_btn = ttk.Button(
            buttons_frame,
            text="Save & Apply",
            command=self._save_metadata,
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._cancel,
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT)
        
        # Reset button
        reset_btn = ttk.Button(
            buttons_frame,
            text="Reset to AI",
            command=self._reset_to_ai,
            width=12
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Make save button the default
        save_btn.focus_set()
        self.window.bind('<Return>', lambda e: self._save_metadata())
        
        # Configure styles
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    def _load_current_data(self):
        """Load current metadata into the form"""
        if self.current_metadata:
            self.title_var.set(self.current_metadata.title)
            if self.current_metadata.year:
                self.year_var.set(str(self.current_metadata.year))
        else:
            # If no metadata, try to extract from filename
            self._auto_extract_from_filename()
        
        self._update_preview()
    
    def _validate_year(self, event=None):
        """Validate year input"""
        year_text = self.year_var.get()
        
        # Allow empty
        if not year_text:
            return
        
        # Check if it's a valid year
        try:
            year = int(year_text)
            if year < 1800 or year > 2030:
                # Invalid year range - could show warning
                pass
        except ValueError:
            # Not a number - could show warning
            pass
    
    def _clear_year(self):
        """Clear the year field"""
        self.year_var.set("")
    
    def _auto_extract_from_filename(self):
        """Auto-extract title and year from filename using fallback parser"""
        try:
            from services.fallback_parser import FallbackParser
            parser = FallbackParser()
            metadata = parser.parse_filename(self.filename)
            
            if metadata.title and metadata.title != self.filename:
                self.title_var.set(metadata.title)
            
            if metadata.year:
                self.year_var.set(str(metadata.year))
                
        except Exception as e:
            self.logger.error(f"Error auto-extracting from filename: {e}")
            # Fallback to simple extraction
            self._simple_extract_from_filename()
    
    def _simple_extract_from_filename(self):
        """Simple extraction from filename"""
        import re
        
        # Remove extension
        name = self.filename
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # Try to find year
        year_match = re.search(r'\b(19\d{2}|20[0-3]\d)\b', name)
        if year_match:
            year = year_match.group(1)
            self.year_var.set(year)
            # Remove year from title
            name = name.replace(year, '').strip()
        
        # Clean up title
        title = re.sub(r'[._-]', ' ', name)
        title = re.sub(r'\b(BD|DVD|HD|720p|1080p|x264|x265|HDTV|WEB-DL|BluRay)\b', '', title, flags=re.IGNORECASE)
        title = ' '.join(title.split())  # Clean up spaces
        title = title.title()
        
        if title:
            self.title_var.set(title)
    
    def _show_common_patterns(self):
        """Show common naming patterns help"""
        help_text = """Common Movie Filename Patterns:

• Movie.Title.Year.Quality.mkv
• Movie Title (Year) [Quality].mkv  
• Movie_Title_Year_Quality.mkv
• Year.Movie.Title.Quality.mkv
• [Year] Movie Title [Quality].mkv

Tips:
- Look for 4-digit years (1900-2030)
- Ignore technical terms (720p, x264, etc.)
- Replace dots/underscores with spaces
- Use proper capitalization"""
        
        messagebox.showinfo("Common Patterns", help_text)
    
    def _update_preview(self, *args):
        """Update the folder name preview"""
        title = self.title_var.get().strip()
        year_text = self.year_var.get().strip()
        
        if not title:
            self.preview_label.config(text="[Enter a title to see preview]", foreground="gray")
            return
        
        # Sanitize title for folder name
        import re
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
        clean_title = clean_title.strip().rstrip('.')
        
        # Create folder name
        if year_text and year_text.isdigit():
            folder_name = f"{clean_title} - {year_text}"
        else:
            folder_name = clean_title
        
        self.preview_label.config(text=folder_name, foreground="green")
    
    def _save_metadata(self):
        """Save the edited metadata"""
        self.logger.info("Save button clicked")
        
        title = self.title_var.get().strip()
        year_text = self.year_var.get().strip()
        
        self.logger.info(f"Title: '{title}', Year: '{year_text}'")
        
        # Validate input
        if not title:
            messagebox.showwarning("Invalid Input", "Please enter a movie title.")
            return
        
        # Validate year
        year = None
        if year_text:
            try:
                year = int(year_text)
                if year < 1800 or year > 2030:
                    messagebox.showwarning("Invalid Year", "Please enter a valid year between 1800 and 2030.")
                    return
            except ValueError:
                messagebox.showwarning("Invalid Year", "Year must be a number.")
                return
        
        # Create new metadata
        new_metadata = MovieMetadata(
            title=title,
            year=year,
            original_filename=self.filename,
            confidence_score=1.0  # Manual edit = 100% confidence
        )
        
        # Call save callback with re-analyze option
        if self.on_save_callback:
            self.on_save_callback(new_metadata, self.reanalyze_var.get())
        
        self.logger.info(f"Metadata saved for {self.filename}: {title} ({year}) - Reanalyze: {self.reanalyze_var.get()}")
        self.window.destroy()
    
    def _reset_to_ai(self):
        """Reset to original AI analysis"""
        if self.current_metadata:
            self.title_var.set(self.current_metadata.title)
            if self.current_metadata.year:
                self.year_var.set(str(self.current_metadata.year))
            else:
                self.year_var.set("")
        else:
            messagebox.showinfo("No AI Data", "No AI analysis available to reset to.")
    
    def _cancel(self):
        """Cancel and close window"""
        self.window.destroy()
    
    def set_save_callback(self, callback: Callable):
        """Set callback for save operation"""
        self.on_save_callback = callback