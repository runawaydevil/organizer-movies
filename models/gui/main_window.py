"""
Main GUI window for Movie Organizer
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import Optional, List, Callable
import logging


class MainWindow:
    """
    Main application window for Movie Organizer
    """
    
    def __init__(self):
        """Initialize the main window"""
        self.root = tk.Tk()
        self.logger = logging.getLogger(__name__)
        
        # Window configuration
        self.root.title("Movie Organizer - AI-Powered Movie File Organizer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set window icon
        self._set_window_icon()
        
        # Application state
        self.source_directory = tk.StringVar()
        self.api_key = tk.StringVar()
        self.selected_files = []
        self.file_list_data = []
        
        # Callbacks for main application logic
        self.on_scan_callback: Optional[Callable] = None
        self.on_process_callback: Optional[Callable] = None
        self.on_settings_callback: Optional[Callable] = None
        self.on_metadata_edit_callback: Optional[Callable] = None
        self.on_reanalyze_callback: Optional[Callable] = None
        
        # Create GUI components
        self._create_menu()
        self._create_widgets()
        self._setup_layout()
        self._setup_bindings()
        
        # Configure styles
        self._configure_styles()
        
        self.logger.info("Main window initialized")
    
    def _set_window_icon(self):
        """Set the window icon"""
        try:
            # Try to find icon file in the same directory as the script
            current_dir = Path(__file__).parent.parent
            icon_path = current_dir / "icon.ico"
            
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
                self.logger.debug(f"Window icon set: {icon_path}")
            else:
                self.logger.warning(f"Icon file not found: {icon_path}")
        except Exception as e:
            self.logger.warning(f"Could not set window icon: {e}")
    
    def _create_menu(self):
        """Create the application menu"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Folder...", command=self._browse_folder, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Settings...", command=self._show_settings, accelerator="Ctrl+,")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Movie Organizer...", command=self._show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self._browse_folder())
        self.root.bind('<Control-comma>', lambda e: self._show_settings())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    def _show_about(self):
        """Show the About window"""
        try:
            from gui.about_window import AboutWindow
            AboutWindow(self.root)
        except Exception as e:
            self.logger.error(f"Error showing About window: {e}")
            messagebox.showerror("Error", f"Could not open About window: {str(e)}")
    
    def _show_settings(self):
        """Show settings window"""
        if self.on_settings_callback:
            self.on_settings_callback()
    
    def _browse_folder(self):
        """Browse for folder"""
        folder_path = filedialog.askdirectory(
            title="Select folder containing movie files",
            initialdir=self.source_directory.get() or os.path.expanduser("~")
        )
        if folder_path:
            self.source_directory.set(folder_path)
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Header section
        self._create_header_section()
        
        # Folder selection section
        self._create_folder_section()
        
        # File list section
        self._create_file_list_section()
        
        # Control buttons section
        self._create_control_section()
        
        # Status bar
        self._create_status_bar()
    
    def _create_header_section(self):
        """Create header with title and logo"""
        self.header_frame = ttk.Frame(self.main_frame)
        
        # Title
        title_label = ttk.Label(
            self.header_frame,
            text="Movie Organizer",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = ttk.Label(
            self.header_frame,
            text="AI-Powered Movie File Organization",
            font=("Arial", 12)
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # About button
        about_btn = ttk.Button(
            self.header_frame,
            text="ℹ️ About",
            command=self._show_about
        )
        about_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Settings button
        settings_btn = ttk.Button(
            self.header_frame,
            text="⚙️ Settings",
            command=self._on_settings_click
        )
        settings_btn.pack(side=tk.RIGHT)
    
    def _create_folder_section(self):
        """Create folder selection section"""
        self.folder_frame = ttk.LabelFrame(self.main_frame, text="Source Directory", padding="10")
        
        # Folder path display
        folder_path_frame = ttk.Frame(self.folder_frame)
        
        ttk.Label(folder_path_frame, text="Selected Folder:").pack(side=tk.LEFT)
        
        self.folder_path_label = ttk.Label(
            folder_path_frame,
            textvariable=self.source_directory,
            font=("Consolas", 10),
            foreground="blue"
        )
        self.folder_path_label.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        folder_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Folder controls
        folder_controls_frame = ttk.Frame(self.folder_frame)
        
        browse_btn = ttk.Button(
            folder_controls_frame,
            text="📁 Browse Folder",
            command=self._browse_folder
        )
        browse_btn.pack(side=tk.LEFT)
        
        scan_btn = ttk.Button(
            folder_controls_frame,
            text="🔍 Scan for Movies",
            command=self._scan_folder
        )
        scan_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Recursive scan option
        self.recursive_scan_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(
            folder_controls_frame,
            text="📂 Include subfolders",
            variable=self.recursive_scan_var
        )
        recursive_check.pack(side=tk.LEFT, padx=(15, 0))
        
        # Folder statistics
        self.stats_label = ttk.Label(
            folder_controls_frame,
            text="No folder selected",
            font=("Arial", 10)
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        folder_controls_frame.pack(fill=tk.X)
    
    def _create_file_list_section(self):
        """Create file list with checkboxes and details"""
        self.file_list_frame = ttk.LabelFrame(self.main_frame, text="Movie Files", padding="10")
        
        # File list controls
        list_controls_frame = ttk.Frame(self.file_list_frame)
        
        select_all_btn = ttk.Button(
            list_controls_frame,
            text="✓ Select All",
            command=self._select_all_files
        )
        select_all_btn.pack(side=tk.LEFT)
        
        select_none_btn = ttk.Button(
            list_controls_frame,
            text="✗ Select None",
            command=self._select_no_files
        )
        select_none_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Select low confidence files
        select_low_confidence_btn = ttk.Button(
            list_controls_frame,
            text="⚠️ Select Uncertain",
            command=self._select_low_confidence_files
        )
        select_low_confidence_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Edit button
        edit_btn = ttk.Button(
            list_controls_frame,
            text="✏️ Edit Selected",
            command=self._edit_selected_file
        )
        edit_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Filter controls
        ttk.Label(list_controls_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(list_controls_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side=tk.LEFT)
        filter_entry.bind('<KeyRelease>', self._filter_files)
        
        list_controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File list with scrollbars
        list_container = ttk.Frame(self.file_list_frame)
        
        # Create Treeview for file list
        columns = ("selected", "filename", "location", "size", "analysis", "proposed_folder")
        self.file_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.file_tree.heading("selected", text="✓")
        self.file_tree.heading("filename", text="Filename")
        self.file_tree.heading("location", text="Location")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("analysis", text="AI Analysis")
        self.file_tree.heading("proposed_folder", text="Proposed Folder")
        
        # Configure tags for confidence levels
        self.file_tree.tag_configure("high_confidence", background="#d4edda")  # Light green
        self.file_tree.tag_configure("medium_confidence", background="#fff3cd")  # Light yellow
        self.file_tree.tag_configure("low_confidence", background="#f8d7da")  # Light red
        
        self.file_tree.column("selected", width=50, minwidth=50)
        self.file_tree.column("filename", width=250, minwidth=150)
        self.file_tree.column("location", width=200, minwidth=100)
        self.file_tree.column("size", width=100, minwidth=80)
        self.file_tree.column("analysis", width=200, minwidth=150)
        self.file_tree.column("proposed_folder", width=250, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Context menu is created in _create_widgets method
        
        # Legend frame
        legend_frame = ttk.Frame(self.file_list_frame)
        legend_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(legend_frame, text="Legend:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(legend_frame, text="🟢 High confidence (>90%)", font=("Arial", 8), foreground="green").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(legend_frame, text="🔴 Low confidence (<90%) - Review needed", font=("Arial", 8), foreground="red").pack(side=tk.LEFT, padx=(10, 0))
        
        # Configure tags for confidence colors
        self.file_tree.tag_configure("low_confidence", background="#ffcccc", foreground="#cc0000")  # Light red background, dark red text
        self.file_tree.tag_configure("high_confidence", background="#ccffcc", foreground="#006600")  # Light green background, dark green text
        
        # Bind double-click for editing metadata
        self.file_tree.bind("<Double-1>", self._edit_file_metadata)
        
        # Context menu for right-click
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✓ Toggle Selection", command=self._toggle_selected_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Edit Metadata", command=self._edit_selected_file)
        self.context_menu.add_command(label="🔍 Re-analyze with AI", command=self._reanalyze_selected_file)
        self.context_menu.add_command(label="🎬 Manual TMDB Search", command=self._manual_tmdb_search)
        
        self.file_tree.bind("<Button-3>", self._show_context_menu)
    
    def _create_control_section(self):
        """Create control buttons section"""
        self.control_frame = ttk.Frame(self.main_frame)
        
        # Process button
        self.process_btn = ttk.Button(
            self.control_frame,
            text="🚀 Start Organization",
            command=self._start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT)
        
        # Preview button
        preview_btn = ttk.Button(
            self.control_frame,
            text="👁️ Preview Changes",
            command=self._preview_changes
        )
        preview_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.control_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Progress label
        self.progress_label = ttk.Label(self.control_frame, text="Ready")
        self.progress_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ttk.Frame(self.main_frame)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready - Select a folder to begin",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, side=tk.LEFT)
        
        # Analyzer status indicator
        self.analyzer_status_label = ttk.Label(
            self.status_frame,
            text="AI Only",
            foreground="blue",
            font=("TkDefaultFont", 8)
        )
        self.analyzer_status_label.pack(side=tk.RIGHT, padx=(10, 10))
        
        # Version info
        version_label = ttk.Label(self.status_frame, text="v1.0.0")
        version_label.pack(side=tk.RIGHT)
    
    def _setup_layout(self):
        """Setup the layout of all components"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.folder_frame.pack(fill=tk.X, pady=(0, 10))
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.status_frame.pack(fill=tk.X)
    
    def _setup_bindings(self):
        """Setup event bindings"""
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self._browse_folder())
        self.root.bind("<Control-s>", lambda e: self._scan_folder())
        self.root.bind("<F5>", lambda e: self._scan_folder())
    
    def _configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        
        # Configure accent button style
        style.configure(
            "Accent.TButton",
            font=("Arial", 11, "bold")
        )
    
    # Event handlers
    def _browse_folder(self):
        """Handle browse folder button click"""
        folder = filedialog.askdirectory(
            title="Select folder containing movie files",
            initialdir=os.path.expanduser("~")
        )
        
        if folder:
            self.source_directory.set(folder)
            self.update_status(f"Selected folder: {folder}")
            self.logger.info(f"Selected source directory: {folder}")
    
    def _scan_folder(self):
        """Handle scan folder button click"""
        if not self.source_directory.get():
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return
        
        if self.on_scan_callback:
            self.on_scan_callback(self.source_directory.get())
    
    def _on_settings_click(self):
        """Handle settings button click"""
        if self.on_settings_callback:
            self.on_settings_callback()
    
    def _show_about(self):
        """Show about dialog"""
        try:
            from gui.about_window import AboutWindow
            AboutWindow(self.root)
        except ImportError as e:
            messagebox.showinfo("About Movie Organizer", 
                              "Movie Organizer v1.0.0\n\n"
                              "Developed by Pablo Murad\n"
                              "© 2025 - All Rights Reserved\n\n"
                              "AI-Powered Movie File Organization")
    
    def _select_all_files(self):
        """Select all files in the list"""
        for item in self.file_tree.get_children():
            self.file_tree.set(item, "selected", "✓")
    
    def _select_no_files(self):
        """Deselect all files in the list"""
        for item in self.file_tree.get_children():
            self.file_tree.set(item, "selected", "")
    
    def _select_low_confidence_files(self):
        """Select only files with low confidence (uncertain analysis)"""
        for item in self.file_tree.get_children():
            # Check if item has low confidence tag
            tags = self.file_tree.item(item, "tags")
            if "low_confidence" in tags:
                self.file_tree.set(item, "selected", "✓")
            else:
                self.file_tree.set(item, "selected", "")
    
    def _filter_files(self, event=None):
        """Filter files based on search term"""
        filter_text = self.filter_var.get().lower()
        
        for item in self.file_tree.get_children():
            filename = self.file_tree.set(item, "filename").lower()
            if filter_text in filename:
                self.file_tree.reattach(item, "", tk.END)
            else:
                self.file_tree.detach(item)
    
    def _edit_file_metadata(self, event):
        """Edit file metadata on double-click"""
        selection = self.file_tree.selection()
        if selection:
            self._edit_metadata_for_item(selection[0])
    
    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the item under cursor
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _toggle_selected_file(self):
        """Toggle selection of currently selected file"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            current = self.file_tree.set(item, "selected")
            new_value = "" if current == "✓" else "✓"
            self.file_tree.set(item, "selected", new_value)
    
    def _edit_selected_file(self):
        """Edit metadata of selected file"""
        selection = self.file_tree.selection()
        if selection:
            self._edit_metadata_for_item(selection[0])
        else:
            messagebox.showwarning("No Selection", "Please select a file to edit.")
    
    def _reanalyze_selected_file(self):
        """Re-analyze selected file with AI"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            filename = self.file_tree.set(item, "filename")
            if self.on_reanalyze_callback:
                self.on_reanalyze_callback(filename)
        else:
            messagebox.showwarning("No Selection", "Please select a file to re-analyze.")
    
    def _edit_metadata_for_item(self, item):
        """Edit metadata for a specific tree item"""
        filename = self.file_tree.set(item, "filename")
        
        # Find current metadata
        current_metadata = None
        for file_data in self.file_list_data:
            if file_data.get("filename") == filename:
                current_metadata = file_data.get("metadata")
                break
        
        # Open edit window
        try:
            from gui.edit_metadata_window import EditMetadataWindow
            edit_window = EditMetadataWindow(self.root, filename, current_metadata)
            edit_window.set_save_callback(lambda metadata, reanalyze=False: self._on_metadata_edited(filename, metadata, reanalyze))
        except ImportError as e:
            messagebox.showerror("Import Error", f"Could not open edit window: {e}")
    
    def _manual_tmdb_search(self):
        """Open manual TMDB search dialog for selected file"""
        selection = self.file_tree.selection()
        
        if selection:
            item = selection[0]
            filename = self.file_tree.set(item, "filename")
            
            if hasattr(self, 'on_manual_search_callback') and self.on_manual_search_callback:
                self.on_manual_search_callback(filename)
            else:
                messagebox.showinfo("Manual Search", f"Manual TMDB search for: {filename}")
        else:
            messagebox.showwarning("No Selection", "Please select a file to search manually.")
    
    def _on_metadata_edited(self, filename: str, new_metadata, reanalyze: bool = False):
        """Handle metadata edit completion"""
        # Update file list data
        for file_data in self.file_list_data:
            if file_data.get("filename") == filename:
                file_data["metadata"] = new_metadata
                break
        
        # Update UI display
        analysis_text = f"{new_metadata.title}"
        if new_metadata.year:
            analysis_text += f" ({new_metadata.year})"
        analysis_text += f" [Manual: {new_metadata.confidence_score:.1%}]"
        
        # Get proposed folder name
        if new_metadata.year:
            proposed_folder = f"{new_metadata.sanitize_title()} - {new_metadata.year}"
        else:
            proposed_folder = new_metadata.sanitize_title()
        
        self.update_file_analysis(filename, analysis_text, proposed_folder, new_metadata.confidence_score)
        
        # Notify main application
        if self.on_metadata_edit_callback:
            self.on_metadata_edit_callback(filename, new_metadata, reanalyze)
        
        if reanalyze:
            self.update_status(f"Updated metadata for: {filename} - Re-analyzing with AI...")
        else:
            self.update_status(f"Updated metadata for: {filename}")
    
    def _show_confidence_legend(self):
        """Show confidence level legend"""
        if hasattr(self, 'legend_shown'):
            return
        
        legend_frame = ttk.Frame(self.file_list_frame)
        legend_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(legend_frame, text="Legend:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(legend_frame, text="✅ High confidence (>80%)", font=("Arial", 8), foreground="green").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(legend_frame, text="⚠️ Medium confidence (50-80%)", font=("Arial", 8), foreground="orange").pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(legend_frame, text="❌ Low confidence (<50%) - Review needed", font=("Arial", 8), foreground="red").pack(side=tk.LEFT, padx=(5, 0))
        
        self.legend_shown = True
    
    def _start_processing(self):
        """Handle start processing button click"""
        selected_files = self._get_selected_files()
        
        if not selected_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
            return
        
        if self.on_process_callback:
            self.on_process_callback(selected_files)
    
    def _preview_changes(self):
        """Handle preview changes button click"""
        selected_files = self._get_selected_files()
        
        if not selected_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to preview.")
            return
        
        # Show preview dialog
        self._show_preview_dialog(selected_files)
    
    def _get_selected_files(self) -> List[str]:
        """Get list of selected files"""
        selected = []
        for item in self.file_tree.get_children():
            if self.file_tree.set(item, "selected") == "✓":
                filename = self.file_tree.set(item, "filename")
                selected.append(filename)
        return selected
    
    def _show_preview_dialog(self, selected_files: List[str]):
        """Show preview dialog with proposed changes"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Changes")
        preview_window.geometry("800x600")
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        # Preview content
        preview_frame = ttk.Frame(preview_window, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(preview_frame, text="Proposed Changes:", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        
        # Preview list
        preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=20)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        for filename in selected_files:
            # Find the proposed folder for this file
            for item in self.file_tree.get_children():
                if self.file_tree.set(item, "filename") == filename:
                    proposed_folder = self.file_tree.set(item, "proposed_folder")
                    preview_text.insert(tk.END, f"{filename}\n  → {proposed_folder}\n\n")
                    break
        
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(preview_frame, text="Close", command=preview_window.destroy).pack(pady=(10, 0))
    
    def _on_closing(self):
        """Handle window closing with proper cleanup"""
        if messagebox.askokcancel("Quit", "Do you want to quit Movie Organizer?"):
            self.logger.info("Application shutting down by user request")
            
            # Stop any ongoing processing
            self._stop_all_processing()
            
            # Properly close all resources
            try:
                # Cancel any pending operations
                self._cancel_pending_operations()
                
                # Destroy the main window
                self.root.destroy()
                
                # Force quit the application
                self.root.quit()
                
                # Exit the Python process completely
                import sys
                sys.exit(0)
                
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
                # Force exit even if there's an error
                import os
                os._exit(0)
    
    def _stop_all_processing(self):
        """Stop all background processing"""
        try:
            # Stop any ongoing analysis or processing
            if hasattr(self, 'on_process_callback') and self.on_process_callback:
                # Signal to stop processing
                self.logger.info("Stopping all background processing")
        except Exception as e:
            self.logger.warning(f"Error stopping processing: {e}")
    
    def _cancel_pending_operations(self):
        """Cancel any pending operations"""
        try:
            # Cancel any pending file operations
            self.logger.info("Cancelling pending operations")
            
            # Clear any pending callbacks
            self.on_scan_callback = None
            self.on_process_callback = None
            self.on_settings_callback = None
            self.on_metadata_edit_callback = None
            self.on_reanalyze_callback = None
            
        except Exception as e:
            self.logger.warning(f"Error cancelling operations: {e}")
    
    # Public methods for external control
    def set_scan_callback(self, callback: Callable):
        """Set callback for scan operation"""
        self.on_scan_callback = callback
    
    def set_process_callback(self, callback: Callable):
        """Set callback for process operation"""
        self.on_process_callback = callback
    
    def set_settings_callback(self, callback: Callable):
        """Set callback for settings operation"""
        self.on_settings_callback = callback
    
    def set_metadata_edit_callback(self, callback: Callable):
        """Set callback for metadata edit operation"""
        self.on_metadata_edit_callback = callback
    
    def set_reanalyze_callback(self, callback: Callable):
        """Set callback for re-analyze operation"""
        self.on_reanalyze_callback = callback
    
    def set_manual_search_callback(self, callback: Callable):
        """Set callback for manual TMDB search operation"""
        self.on_manual_search_callback = callback
    
    def update_file_list(self, files_data: List[dict]):
        """Update the file list with new data"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add new items
        for file_data in files_data:
            item_id = self.file_tree.insert("", tk.END, values=(
                "✓",  # selected by default
                file_data.get("filename", ""),
                file_data.get("location", ""),
                file_data.get("size", ""),
                file_data.get("analysis", "Pending..."),
                file_data.get("proposed_folder", "Analyzing...")
            ))
            # Default to medium confidence until analysis is done
            self.file_tree.item(item_id, tags=("medium_confidence",))
        
        # Update statistics
        self.stats_label.config(text=f"Found {len(files_data)} movie files")
        self.file_list_data = files_data
        
        # Show legend
        self._show_confidence_legend()
    
    def update_file_analysis(self, filename: str, analysis: str, proposed_folder: str, confidence: float = 1.0):
        """Update analysis results for a specific file"""
        for item in self.file_tree.get_children():
            if self.file_tree.set(item, "filename") == filename:
                self.file_tree.set(item, "analysis", analysis)
                self.file_tree.set(item, "proposed_folder", proposed_folder)
                
                # Color code based on confidence
                if confidence >= 0.8:
                    # High confidence - green
                    tag = "high_confidence"
                    icon = "✅"
                elif confidence >= 0.5:
                    # Medium confidence - yellow
                    tag = "medium_confidence" 
                    icon = "⚠️"
                else:
                    # Low confidence - red
                    tag = "low_confidence"
                    icon = "❌"
                
                self.file_tree.set(item, "analysis", f"{icon} {analysis}")
                self.file_tree.item(item, tags=(tag,))
                break
    
    def update_progress(self, value: float, text: str = ""):
        """Update progress bar and label"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.logger.debug(f"Status: {message}")
    
    def update_analyzer_status(self, analyzer_type: str, tmdb_enabled: bool = False):
        """
        Update analyzer status indicator
        
        Args:
            analyzer_type: Type of analyzer ("AI Only", "Hybrid (AI + TMDB)")
            tmdb_enabled: Whether TMDB is enabled
        """
        if tmdb_enabled:
            self.analyzer_status_label.config(
                text="🎬 AI + TMDB",
                foreground="green",
                font=("TkDefaultFont", 8, "bold")
            )
        else:
            self.analyzer_status_label.config(
                text="🤖 AI Only",
                foreground="blue",
                font=("TkDefaultFont", 8)
            )
    
    def show_tmdb_loading(self, show: bool = True):
        """
        Show/hide TMDB loading indicator
        
        Args:
            show: Whether to show loading indicator
        """
        if show:
            self.analyzer_status_label.config(
                text="🎬 TMDB Loading...",
                foreground="orange",
                font=("TkDefaultFont", 8, "bold")
            )
        else:
            # Restore normal status
            self.update_analyzer_status("Hybrid", tmdb_enabled=True)
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info dialog"""
        messagebox.showinfo(title, message)
    
    def run(self):
        """Start the GUI main loop with proper shutdown handling"""
        try:
            self.logger.info("Starting GUI main loop")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("GUI interrupted by keyboard")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.logger.info("GUI main loop ended")
            # Ensure complete shutdown
            try:
                self._cleanup_resources()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
            finally:
                # Force exit if window still exists
                try:
                    if self.root.winfo_exists():
                        self.root.destroy()
                except:
                    pass
                
                # Final exit
                import sys
                sys.exit(0)
    
    def _cleanup_resources(self):
        """Clean up all resources before shutdown"""
        try:
            # Cancel any pending operations
            self._cancel_pending_operations()
            
            # Clear file list data
            self.file_list_data = []
            self.selected_files = []
            
            # Clear any remaining callbacks
            self.on_scan_callback = None
            self.on_process_callback = None
            self.on_settings_callback = None
            self.on_metadata_edit_callback = None
            self.on_reanalyze_callback = None
            
            self.logger.info("Resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up resources: {e}")