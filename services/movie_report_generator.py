#!/usr/bin/env python3
"""
Movie Report Generator - Creates PDF reports of organized movies
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.01
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from version import get_version_string, VERSION, AUTHOR, COPYRIGHT


@dataclass
class OrganizedMovie:
    """Information about an organized movie"""
    title: str
    year: int
    original_filename: str
    folder_path: str
    organized_date: str
    source: str  # "AI", "TMDB", "Manual"
    confidence_score: float


class MovieReportGenerator:
    """
    Generates PDF reports of organized movies and maintains a database
    
    Author: Pablo Murad (runawaydevil)
    Version: 0.01
    """
    
    def __init__(self, database_file: str = "organized_movies.json"):
        """
        Initialize report generator
        
        Args:
            database_file: Path to JSON database file (relative to program directory)
        """
        self.logger = logging.getLogger(__name__)
        
        # Get the directory where the program is running
        # For executable, use the directory where the .exe is located
        if getattr(sys, 'frozen', False):
            # Running as executable
            self.program_directory = Path(sys.executable).parent
        else:
            # Running as script
            self.program_directory = Path.cwd()
        
        # Database file in program directory
        self.database_file = self.program_directory / database_file
        self.organized_movies: List[OrganizedMovie] = []
        
        self.logger.info(f"{get_version_string()} - Movie report generator initialized in: {self.program_directory}")
        
        # Load existing database
        self._load_database()
    
    def add_organized_movie(self, title: str, year: int, original_filename: str, 
                          folder_path: str, source: str = "AI", confidence_score: float = 0.0):
        """
        Add a movie to the organized movies database
        
        Args:
            title: Movie title
            year: Movie year
            original_filename: Original filename
            folder_path: Path where movie was organized
            source: Source of identification (AI, TMDB, Manual)
            confidence_score: Confidence score of identification
        """
        # Check if movie already exists (avoid duplicates)
        if self._movie_exists(original_filename):
            self.logger.debug(f"Movie already in database: {original_filename}")
            return
        
        movie = OrganizedMovie(
            title=title,
            year=year,
            original_filename=original_filename,
            folder_path=folder_path,
            organized_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            source=source,
            confidence_score=confidence_score
        )
        
        self.organized_movies.append(movie)
        self.logger.info(f"Added organized movie: {title} ({year})")
        
        # Save to database
        self._save_database()
    
    def is_movie_already_organized(self, filename: str) -> bool:
        """
        Check if a movie file has already been organized
        
        Args:
            filename: Original filename to check
            
        Returns:
            bool: True if movie was already organized
        """
        return self._movie_exists(filename)
    
    def get_organized_movie_info(self, filename: str) -> Dict[str, Any]:
        """
        Get information about an already organized movie
        
        Args:
            filename: Original filename
            
        Returns:
            Dict: Movie information or empty dict if not found
        """
        for movie in self.organized_movies:
            if movie.original_filename == filename:
                return {
                    'title': movie.title,
                    'year': movie.year,
                    'folder_path': movie.folder_path,
                    'organized_date': movie.organized_date,
                    'source': movie.source,
                    'confidence_score': movie.confidence_score
                }
        return {}
    
    def generate_pdf_report(self, output_file: str = "organized_movies_report.pdf") -> bool:
        """
        Generate PDF report of all organized movies in the program directory
        
        Args:
            output_file: Output PDF filename (will be saved in program directory)
            
        Returns:
            bool: True if successful
        """
        try:
            # Try to import reportlab
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib import colors
                from reportlab.lib.units import inch
            except ImportError:
                self.logger.error("reportlab not installed. Install with: pip install reportlab")
                return False
            
            if not self.organized_movies:
                self.logger.warning("No organized movies to report")
                return False
            
            # Create PDF document in program directory
            pdf_path = self.program_directory / output_file
            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title with version
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=20,
                alignment=1  # Center alignment
            )
            
            title = Paragraph(f"Movie Organizer v{VERSION} - Organized Movies Report", title_style)
            story.append(title)
            
            # Version and author info
            version_style = ParagraphStyle(
                'VersionInfo',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=20,
                alignment=1  # Center alignment
            )
            
            version_info = Paragraph(
                f"{get_version_string()}<br/>"
                f"{COPYRIGHT}<br/>"
                f"Repository: https://github.com/runawaydevil/organizer-movies.git",
                version_style
            )
            story.append(version_info)
            
            # Report info
            report_info = Paragraph(
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
                f"Total organized movies: {len(self.organized_movies)}",
                styles['Normal']
            )
            story.append(report_info)
            story.append(Spacer(1, 20))
            
            # Statistics
            stats = self._get_statistics()
            stats_text = f"""
            <b>Statistics:</b><br/>
            • Total organized movies: {len(self.organized_movies)}<br/>
            • Most recent organization: {stats['most_recent']}<br/>
            • Oldest organization: {stats['oldest']}
            """
            
            stats_para = Paragraph(stats_text, styles['Normal'])
            story.append(stats_para)
            story.append(Spacer(1, 20))
            
            # Movies table
            table_title = Paragraph("<b>Organized Movies List</b>", styles['Heading2'])
            story.append(table_title)
            story.append(Spacer(1, 10))
            
            # Prepare table data
            table_data = [
                ['Title', 'Year', 'Original Filename', 'Organized Date']
            ]
            
            # Sort movies by organized date (most recent first)
            sorted_movies = sorted(
                self.organized_movies, 
                key=lambda x: x.organized_date, 
                reverse=True
            )
            
            for movie in sorted_movies:
                # Truncate long filenames for better display
                filename = movie.original_filename
                if len(filename) > 30:
                    filename = filename[:27] + "..."
                
                table_data.append([
                    movie.title,
                    str(movie.year) if movie.year else "N/A",
                    filename,
                    movie.organized_date.split(' ')[0]  # Just date, not time
                ])
            
            # Create table
            table = Table(table_data, colWidths=[2.5*inch, 0.8*inch, 2.5*inch, 1.2*inch])
            
            # Style the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(table)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated successfully: {pdf_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")
            return False
    
    def _movie_exists(self, filename: str) -> bool:
        """Check if movie already exists in database"""
        return any(movie.original_filename == filename for movie in self.organized_movies)
    
    def _load_database(self):
        """Load organized movies database from JSON file"""
        try:
            if self.database_file.exists():
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.organized_movies = []
                for movie_data in data:
                    movie = OrganizedMovie(**movie_data)
                    self.organized_movies.append(movie)
                
                self.logger.info(f"Loaded {len(self.organized_movies)} organized movies from database")
            else:
                self.logger.info("No existing database found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Error loading database: {e}")
            self.organized_movies = []
    
    def _save_database(self):
        """Save organized movies database to JSON file"""
        try:
            data = []
            for movie in self.organized_movies:
                data.append({
                    'title': movie.title,
                    'year': movie.year,
                    'original_filename': movie.original_filename,
                    'folder_path': movie.folder_path,
                    'organized_date': movie.organized_date,
                    'source': movie.source,
                    'confidence_score': movie.confidence_score
                })
            
            with open(self.database_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Database saved with {len(self.organized_movies)} movies")
            
        except Exception as e:
            self.logger.error(f"Error saving database: {e}")
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Get statistics about organized movies"""
        if not self.organized_movies:
            return {
                'ai_count': 0,
                'tmdb_count': 0,
                'manual_count': 0,
                'avg_confidence': 0.0,
                'most_recent': 'N/A',
                'oldest': 'N/A'
            }
        
        ai_count = sum(1 for m in self.organized_movies if 'AI' in m.source.upper())
        tmdb_count = sum(1 for m in self.organized_movies if 'TMDB' in m.source.upper())
        manual_count = sum(1 for m in self.organized_movies if 'MANUAL' in m.source.upper())
        
        avg_confidence = sum(m.confidence_score for m in self.organized_movies) / len(self.organized_movies)
        
        dates = [m.organized_date for m in self.organized_movies]
        most_recent = max(dates) if dates else 'N/A'
        oldest = min(dates) if dates else 'N/A'
        
        return {
            'ai_count': ai_count,
            'tmdb_count': tmdb_count,
            'manual_count': manual_count,
            'avg_confidence': avg_confidence,
            'most_recent': most_recent,
            'oldest': oldest
        }
    
    def get_statistics_summary(self) -> str:
        """Get a text summary of statistics"""
        stats = self._get_statistics()
        
        return f"""
Organized Movies Statistics:
• Total movies: {len(self.organized_movies)}
• AI organized: {stats['ai_count']}
• TMDB organized: {stats['tmdb_count']}
• Manual organized: {stats['manual_count']}
• Average confidence: {stats['avg_confidence']:.1%}
• Most recent: {stats['most_recent']}
• Oldest: {stats['oldest']}
        """.strip()
    
    def clear_database(self) -> bool:
        """Clear all organized movies from database"""
        try:
            self.organized_movies = []
            self._save_database()
            self.logger.info("Database cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing database: {e}")
            return False