"""
Draggable widget container for visualizers.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class DraggableVisualizerWidget(QFrame):
    """Widget container that can be dragged and resized."""
    
    # Tín hiệu
    close_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    
    def __init__(self, content_widget, title="Visualizer", widget_id=None, parent=None):
        """Initialize draggable visualizer widget."""
        super().__init__(parent)
        
        # Lưu widget ID
        self.widget_id = widget_id
        
        # Setup UI
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        
        # Title bar
        self.title_bar = self._create_title_bar(title)
        self.main_layout.addWidget(self.title_bar)
        
        # Content widget
        self.content_widget = content_widget
        self.main_layout.addWidget(content_widget)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def _create_title_bar(self, title):
        """Create title bar with controls."""
        title_bar = QWidget()
        title_bar.setMinimumHeight(24)
        title_bar.setMaximumHeight(24)
        title_bar.setStyleSheet("background-color: #E0E0E0;")
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(2, 0, 2, 0)
        
        # Title label
        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)
        
        # Spacer
        layout.addStretch(1)
        
        # Maximize button
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(20, 20)
        self.maximize_btn.clicked.connect(self.maximize_requested)
        layout.addWidget(self.maximize_btn)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.close_requested)
        layout.addWidget(self.close_btn)
        
        return title_bar
    
    def sizeHint(self):
        """Suggested size hint."""
        return QSize(300, 200)