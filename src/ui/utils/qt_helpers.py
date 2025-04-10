from PyQt6.QtWidgets import (QMessageBox, QFileDialog, QApplication, 
                             QDialog, QVBoxLayout, QLabel, QProgressBar, 
                             QPushButton)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
import sys

def show_error(parent, title, message):
    """
    Show an error message dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Error message
    """
    QMessageBox.critical(parent, title, message)

def show_warning(parent, title, message):
    """
    Show a warning message dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Warning message
    """
    QMessageBox.warning(parent, title, message)

def show_info(parent, title, message):
    """
    Show an information message dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Information message
    """
    QMessageBox.information(parent, title, message)

def show_question(parent, title, message):
    """
    Show a question dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Question message
        
    Returns:
        True if user clicked Yes, False otherwise
    """
    reply = QMessageBox.question(
        parent, 
        title, 
        message, 
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes

def get_open_file(parent, title, directory="", filter="All Files (*)"):
    """
    Show an open file dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory
        filter: File filter
        
    Returns:
        Selected file path or empty string if cancelled
    """
    file_path, _ = QFileDialog.getOpenFileName(parent, title, directory, filter)
    return file_path

def get_save_file(parent, title, directory="", filter="All Files (*)"):
    """
    Show a save file dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory
        filter: File filter
        
    Returns:
        Selected file path or empty string if cancelled
    """
    file_path, _ = QFileDialog.getSaveFileName(parent, title, directory, filter)
    return file_path

def get_existing_directory(parent, title, directory=""):
    """
    Show a directory selection dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory
        
    Returns:
        Selected directory path or empty string if cancelled
    """
    directory = QFileDialog.getExistingDirectory(parent, title, directory)
    return directory

class ProgressDialog(QDialog):
    """Custom progress dialog with cancel button."""
    
    def __init__(self, parent=None, title="Please Wait", label_text="Operation in progress...", 
                 minimum=0, maximum=100, cancelable=True):
        """Initialize the progress dialog."""
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(300)
        
        # Setup layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Label
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        if cancelable:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.reject)
            layout.addWidget(self.cancel_button)
        else:
            self.cancel_button = None
    
    def set_progress(self, value):
        """Set the current progress value."""
        self.progress_bar.setValue(value)
    
    def set_label_text(self, text):
        """Set the label text."""
        self.label.setText(text)
    
    def enable_cancel(self, enable):
        """Enable or disable the cancel button."""
        if self.cancel_button:
            self.cancel_button.setEnabled(enable)

class SignalBridge(QObject):
    """Bridge for connecting non-Qt code to Qt signals."""
    
    # Define signals
    string_signal = pyqtSignal(str)
    int_signal = pyqtSignal(int)
    float_signal = pyqtSignal(float)
    dict_signal = pyqtSignal(dict)
    object_signal = pyqtSignal(object)
    
    def __init__(self):
        """Initialize the signal bridge."""
        super().__init__()