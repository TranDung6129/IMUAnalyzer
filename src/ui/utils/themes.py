from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.ui.utils.resources import load_stylesheet

class Theme:
    """Class representing a UI theme."""
    
    def __init__(self, name, stylesheet="", is_dark=False):
        """Initialize a theme."""
        self.name = name
        self.stylesheet = stylesheet
        self.is_dark = is_dark
        self.palette = self._create_palette(is_dark)
    
    def _create_palette(self, is_dark):
        """Create a color palette for the theme."""
        palette = QPalette()
        
        if is_dark:
            # Dark theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        else:
            # Light theme - use default palette
            pass
        
        return palette

class ThemeManager:
    """Manager for UI themes."""
    
    def __init__(self):
        """Initialize the theme manager."""
        self.themes = {}
        self.current_theme = None
        
        # Create default themes
        self._create_default_themes()
    
    def _create_default_themes(self):
        """Create default themes."""
        # Light theme (default Qt)
        self.themes["Light"] = Theme("Light", is_dark=False)
        
        # Dark theme
        dark_stylesheet = load_stylesheet("dark.qss")
        self.themes["Dark"] = Theme("Dark", stylesheet=dark_stylesheet, is_dark=True)
        
        # Material dark theme
        material_stylesheet = load_stylesheet("material_dark.qss")
        self.themes["Material Dark"] = Theme("Material Dark", stylesheet=material_stylesheet, is_dark=True)
    
    def apply_theme(self, theme_name):
        """
        Apply a theme to the application.
        
        Args:
            theme_name: Name of the theme to apply
            
        Returns:
            True if theme was applied, False otherwise
        """
        if theme_name not in self.themes:
            return False
        
        theme = self.themes[theme_name]
        app = QApplication.instance()
        
        # Apply palette
        app.setPalette(theme.palette)
        
        # Apply stylesheet
        app.setStyleSheet(theme.stylesheet)
        
        # Store current theme
        self.current_theme = theme_name
        
        return True
    
    def get_theme_names(self):
        """
        Get a list of available theme names.
        
        Returns:
            List of theme names
        """
        return list(self.themes.keys())
    
    def get_current_theme(self):
        """
        Get the current theme name.
        
        Returns:
            Current theme name or None if no theme is applied
        """
        return self.current_theme
    
    def add_theme(self, theme):
        """
        Add a new theme.
        
        Args:
            theme: Theme object to add
            
        Returns:
            True if theme was added, False if a theme with the same name already exists
        """
        if theme.name in self.themes:
            return False
        
        self.themes[theme.name] = theme
        return True

# Create global theme manager instance
theme_manager = ThemeManager()

def apply_theme(theme_name):
    """
    Apply a theme to the application.
    
    Args:
        theme_name: Name of the theme to apply
        
    Returns:
        True if theme was applied, False otherwise
    """
    return theme_manager.apply_theme(theme_name)

def get_theme_names():
    """
    Get a list of available theme names.
    
    Returns:
        List of theme names
    """
    return theme_manager.get_theme_names()

def get_current_theme():
    """
    Get the current theme name.
    
    Returns:
        Current theme name or None if no theme is applied
    """
    return theme_manager.get_current_theme()