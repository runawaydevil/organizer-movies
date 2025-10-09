"""
Manual TMDB Search Dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Callable
import logging
import threading


class ManualSearchDialog:
    """
    Dialog for manual TMDB search when automatic identification fails
    """
    
    def __init__(self, parent, filename: str, tmdb_service=None):
        """
        Initialize manual search dialog
        
        Args:
            parent: Parent window
            filename: Original filename being searched
            tmdb_service: TMDB service instance for searching
        """
        self.parent = parent
        self.filename = filename
        self.tmdb_service = tmdb_service
        self.logger = logging.getLogger(__name__)
        
        # Result
        self.selected_result = None
        self.manual_title = None
        self.manual_year = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Manual Search - {filename}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create GUI
        self._create_widgets()
        
        # Focus on search entry
        self.search_entry.focus_set()
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            main_frame,
            text=f"Search TMDB for: {self.filename}",
            font=("TkDefaultFont", 12, "bold")
        )
        header_label.pack(pady=(0, 20))
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search TMDB", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Search entry
        ttk.Label(search_frame, text="Movie Title:").pack(anchor=tk.W)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_input_frame,
            textvariable=self.search_var,
            font=("TkDefaultFont", 11)
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.search_button = ttk.Button(
            search_input_frame,
            text="Search",
            command=self._perform_search
        )
        self.search_button.pack(side=tk.RIGHT)
        
        # Year entry (optional)
        year_frame = ttk.Frame(search_frame)
        year_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(year_frame, text="Year (optional):").pack(side=tk.LEFT)
        
        self.year_var = tk.StringVar()
        year_entry = ttk.Entry(
            year_frame,
            textvariable=self.year_var,
            width=10
        )
        year_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Results listbox with scrollbar
        results_list_frame = ttk.Frame(results_frame)
        results_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for results
        columns = ("title", "year", "rating")
        self.results_tree = ttk.Treeview(
            results_list_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        # Configure columns
        self.results_tree.heading("title", text="Title")
        self.results_tree.heading("year", text="Year")
        self.results_tree.heading("rating", text="Rating")
        
        self.results_tree.column("title", width=300)
        self.results_tree.column("year", width=80)
        self.results_tree.column("rating", width=80)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(
            results_list_frame,
            orient=tk.VERTICAL,
            command=self.results_tree.yview
        )
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Manual entry section
        manual_frame = ttk.LabelFrame(main_frame, text="Or Enter Manually", padding="10")
        manual_frame.pack(fill=tk.X, pady=(0, 20))
        
        manual_input_frame = ttk.Frame(manual_frame)
        manual_input_frame.pack(fill=tk.X)
        
        # Manual title
        ttk.Label(manual_input_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.manual_title_var = tk.StringVar()
        manual_title_entry = ttk.Entry(
            manual_input_frame,
            textvariable=self.manual_title_var,
            width=30
        )
        manual_title_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Manual year
        ttk.Label(manual_input_frame, text="Year:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.manual_year_var = tk.StringVar()
        manual_year_entry = ttk.Entry(
            manual_input_frame,
            textvariable=self.manual_year_var,
            width=10
        )
        manual_year_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Use Manual Entry",
            command=self._use_manual_entry
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Use Selected",
            command=self._use_selected_result
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Bind events
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        self.results_tree.bind("<Double-1>", lambda e: self._use_selected_result())
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground="gray"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Store search results
        self.search_results = []
    
    def _perform_search(self):
        """Perform TMDB search"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Search Error", "Please enter a movie title to search.")
            return
        
        if not self.tmdb_service:
            messagebox.showerror("Search Error", "TMDB service not available.")
            return
        
        # Clear previous results
        self._clear_results()
        
        # Show searching status
        self.status_var.set("Searching TMDB...")
        self.search_button.config(state=tk.DISABLED)
        self.dialog.update()
        
        # Perform search in thread to avoid blocking UI
        def search_thread():
            try:
                # Get year if provided
                year = None
                year_text = self.year_var.get().strip()
                if year_text:
                    try:
                        year = int(year_text)
                    except ValueError:
                        pass
                
                # Search TMDB
                results = self.tmdb_service.search_movie(search_term, year)
                
                # Update UI in main thread
                self.dialog.after(0, self._display_search_results, results)
                
            except Exception as e:
                self.logger.error(f"TMDB search error: {e}")
                self.dialog.after(0, self._search_error, str(e))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def _display_search_results(self, results):
        """Display search results in the tree"""
        self.search_results = results
        
        # Clear tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not results:
            self.status_var.set("No results found")
        else:
            # Add results to tree
            for i, result in enumerate(results):
                self.results_tree.insert(
                    "",
                    tk.END,
                    values=(
                        result.get_display_title(),
                        result.year or "Unknown",
                        f"{result.vote_average:.1f}" if result.vote_average else "N/A"
                    ),
                    tags=(str(i),)
                )
            
            self.status_var.set(f"Found {len(results)} results")
        
        # Re-enable search button
        self.search_button.config(state=tk.NORMAL)
    
    def _search_error(self, error_message):
        """Handle search error"""
        self.status_var.set(f"Search failed: {error_message}")
        self.search_button.config(state=tk.NORMAL)
    
    def _clear_results(self):
        """Clear search results"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.search_results = []
    
    def _use_selected_result(self):
        """Use selected TMDB result"""
        selection = self.results_tree.selection()
        
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a movie from the search results.")
            return
        
        # Get selected item
        item = selection[0]
        values = self.results_tree.item(item, "values")
        
        if not values:
            return
        
        # Find corresponding result
        try:
            # Get the index from tags
            tags = self.results_tree.item(item, "tags")
            if tags:
                index = int(tags[0])
                if 0 <= index < len(self.search_results):
                    self.selected_result = self.search_results[index]
                    self.dialog.destroy()
                    return
        except (ValueError, IndexError):
            pass
        
        messagebox.showerror("Selection Error", "Could not get selected result.")
    
    def _use_manual_entry(self):
        """Use manual entry"""
        title = self.manual_title_var.get().strip()
        year_text = self.manual_year_var.get().strip()
        
        if not title:
            messagebox.showwarning("Manual Entry Error", "Please enter a movie title.")
            return
        
        # Parse year
        year = None
        if year_text:
            try:
                year = int(year_text)
            except ValueError:
                messagebox.showwarning("Manual Entry Error", "Year must be a number.")
                return
        
        self.manual_title = title
        self.manual_year = year
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel dialog"""
        self.selected_result = None
        self.manual_title = None
        self.manual_year = None
        self.dialog.destroy()
    
    def show_dialog(self):
        """
        Show dialog and wait for result
        
        Returns:
            tuple: (tmdb_result, manual_title, manual_year) or (None, None, None) if cancelled
        """
        # Pre-fill search with cleaned filename
        cleaned_name = self._clean_filename_for_search(self.filename)
        self.search_var.set(cleaned_name)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.selected_result, self.manual_title, self.manual_year
    
    def _clean_filename_for_search(self, filename: str) -> str:
        """
        Clean filename for better search results
        
        Args:
            filename: Original filename
            
        Returns:
            str: Cleaned filename suitable for search
        """
        import re
        
        # Remove file extension
        name = filename
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # Remove common patterns
        patterns_to_remove = [
            r'\b\d{4}\b',  # Years
            r'\b(1080p|720p|480p|4k|uhd|hd)\b',  # Quality
            r'\b(bluray|blu-ray|brrip|webrip|web-dl|dvdrip|hdtv)\b',  # Source
            r'\b(x264|x265|h264|h265|hevc|xvid|divx)\b',  # Codecs
            r'\[.*?\]',  # Brackets
            r'\(.*?\)',  # Parentheses
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Clean up separators
        name = re.sub(r'[._-]', ' ', name)
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name.strip()