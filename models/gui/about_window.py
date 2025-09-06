"""
About window for Movie Organizer
"""
import tkinter as tk
from tkinter import ttk
import webbrowser
import sys
import platform
from datetime import datetime
from pathlib import Path


class AboutWindow:
    """
    About/Credits window for Movie Organizer
    """
    
    def __init__(self, parent):
        """
        Initialize about window
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("About Movie Organizer")
        self.window.geometry("600x750")
        self.window.resizable(True, True)
        self.window.minsize(500, 600)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self._center_window()
        
        # Create GUI
        self._create_widgets()
    
    def _get_technology_info(self):
        """Get dynamic technology information"""
        tech_info = []
        
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        tech_info.append(f"Python {python_version}")
        
        # Platform information
        system_info = f"{platform.system()} {platform.release()}"
        tech_info.append(f"Platform: {system_info}")
        
        # GUI Framework
        tk_version = tk.TkVersion
        tech_info.append(f"tkinter (Tk {tk_version})")
        
        # Try to get library versions
        try:
            import openai
            tech_info.append("OpenAI API Client")
        except ImportError:
            tech_info.append("OpenAI API (not available)")
        
        try:
            import pathlib
            tech_info.append("pathlib (File Operations)")
        except ImportError:
            pass
        
        # Build tools
        tech_info.append("PyInstaller (Executable Creation)")
        
        # Core libraries
        tech_info.append("threading (Async Operations)")
        tech_info.append("logging (Error Tracking)")
        tech_info.append("json (Configuration)")
        tech_info.append("re (Pattern Matching)")
        
        return tech_info
    
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
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App icon/logo area (placeholder)
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=(0, 20))
        
        # App title
        title_label = ttk.Label(
            logo_frame,
            text="🎬 Movie Organizer",
            font=("Arial", 24, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(
            logo_frame,
            text="AI-Powered Movie File Organization",
            font=("Arial", 12),
            foreground="#7f8c8d"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Version info
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(pady=(0, 20))
        
        version_label = ttk.Label(
            version_frame,
            text="Version 1.0.0",
            font=("Arial", 11, "bold")
        )
        version_label.pack()
        
        # Developer info
        dev_frame = ttk.LabelFrame(main_frame, text="Developer", padding="15")
        dev_frame.pack(fill=tk.X, pady=(0, 20))
        
        dev_info = ttk.Label(
            dev_frame,
            text="Developed by Pablo Murad\n© 2025 - All Rights Reserved",
            font=("Arial", 11),
            justify=tk.CENTER
        )
        dev_info.pack()
        
        # App description
        desc_frame = ttk.LabelFrame(main_frame, text="About This Application", padding="15")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        description = """Movie Organizer is an intelligent application that uses OpenAI's GPT technology to automatically analyze and organize your movie collection.

Key Features:
• AI-powered filename analysis
• Automatic extraction of original movie titles
• Recursive folder scanning
• Manual metadata editing
• Safe file organization with integrity checks
• Support for multiple video formats
• Intelligent confidence scoring"""
        
        desc_label = ttk.Label(
            desc_frame,
            text=description,
            font=("Arial", 10),
            justify=tk.LEFT,
            wraplength=420
        )
        desc_label.pack()
        
        # Technology info
        tech_frame = ttk.LabelFrame(main_frame, text="Technology Stack", padding="15")
        tech_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get dynamic technology information
        tech_list = self._get_technology_info()
        
        # Create scrollable text widget for technology info
        tech_text_frame = ttk.Frame(tech_frame)
        tech_text_frame.pack(fill=tk.BOTH, expand=True)
        
        tech_text = tk.Text(
            tech_text_frame,
            height=8,
            width=50,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f8f9fa",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        
        # Add scrollbar
        tech_scrollbar = ttk.Scrollbar(tech_text_frame, orient=tk.VERTICAL, command=tech_text.yview)
        tech_text.configure(yscrollcommand=tech_scrollbar.set)
        
        # Core Technologies section
        tech_text.insert(tk.END, "🔧 Core Technologies:\n", "header")
        for i, tech in enumerate(tech_list[:4]):  # First 4 are core
            tech_text.insert(tk.END, f"  • {tech}\n")
        
        tech_text.insert(tk.END, "\n🚀 AI & Analysis:\n", "header")
        tech_text.insert(tk.END, "  • OpenAI GPT-3.5/4 API for intelligent filename analysis\n")
        tech_text.insert(tk.END, "  • Advanced regex parsing for fallback processing\n")
        tech_text.insert(tk.END, "  • Confidence scoring algorithms\n")
        
        tech_text.insert(tk.END, "\n📦 Build & Deployment:\n", "header")
        for tech in tech_list[4:]:  # Remaining technologies
            if any(keyword in tech.lower() for keyword in ['pyinstaller', 'threading', 'logging', 'json', 'pathlib']):
                tech_text.insert(tk.END, f"  • {tech}\n")
        
        tech_text.insert(tk.END, "\n🎯 Key Features:\n", "header")
        tech_text.insert(tk.END, "  • Cross-platform file system operations\n")
        tech_text.insert(tk.END, "  • Robust error handling and logging\n")
        tech_text.insert(tk.END, "  • Safe file movement with integrity checks\n")
        tech_text.insert(tk.END, "  • Recursive directory scanning\n")
        tech_text.insert(tk.END, "  • Manual metadata editing capabilities\n")
        
        # Configure text tags for headers
        tech_text.tag_configure("header", font=("Arial", 10, "bold"), foreground="#2c3e50")
        
        # Make text read-only
        tech_text.config(state=tk.DISABLED)
        
        # Pack text widget and scrollbar
        tech_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tech_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(pady=(10, 20))
        
        # GitHub link (placeholder)
        github_btn = ttk.Button(
            links_frame,
            text="🌐 View on GitHub",
            command=self._open_github
        )
        github_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Support link
        support_btn = ttk.Button(
            links_frame,
            text="💬 Support",
            command=self._open_support
        )
        support_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.window.destroy,
            width=15
        )
        close_btn.pack(pady=(10, 0))
        
        # Copyright footer
        footer_label = ttk.Label(
            main_frame,
            text=f"Built with ❤️ in {datetime.now().year}",
            font=("Arial", 9),
            foreground="#95a5a6"
        )
        footer_label.pack(pady=(20, 0))
    
    def _open_github(self):
        """Open GitHub repository (placeholder)"""
        # You can replace this with your actual GitHub URL
        try:
            webbrowser.open("https://github.com/pablomurad/movie-organizer")
        except:
            pass
    
    def _open_support(self):
        """Open support page (placeholder)"""
        # You can replace this with your support email or page
        try:
            webbrowser.open("mailto:pablo.murad@example.com?subject=Movie Organizer Support")
        except:
            pass