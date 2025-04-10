import sys
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QDir, QFile, QIODevice, QTextStream
import os

# Define resources path
if hasattr(sys, "_MEIPASS"):  # Running as PyInstaller bundle
    RESOURCES_PATH = os.path.join(sys._MEIPASS, "resources")
else:
    RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "resources")

def get_icon(name):
    """
    Get an icon from the resources.
    
    Args:
        name: Icon name without extension
        
    Returns:
        QIcon object or None if not found
    """
    # Check for icons in different formats
    for ext in [".png", ".svg"]:
        icon_path = os.path.join(RESOURCES_PATH, "icons", name + ext)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
    
    return None

def get_pixmap(name):
    """
    Get a pixmap from the resources.
    
    Args:
        name: Image name with extension
        
    Returns:
        QPixmap object or None if not found
    """
    image_path = os.path.join(RESOURCES_PATH, "images", name)
    if os.path.exists(image_path):
        return QPixmap(image_path)
    
    return None

def load_stylesheet(name):
    """
    Load a stylesheet from the resources.
    
    Args:
        name: Stylesheet name with extension
        
    Returns:
        Stylesheet content as string or empty string if not found
    """
    stylesheet_path = os.path.join(RESOURCES_PATH, "styles", name)
    
    if os.path.exists(stylesheet_path):
        stylesheet_file = QFile(stylesheet_path)
        if stylesheet_file.open(QIODevice.ReadOnly | QIODevice.Text):
            stream = QTextStream(stylesheet_file)
            stylesheet = stream.readAll()
            stylesheet_file.close()
            return stylesheet
    
    return 