from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QCheckBox,
                             QLabel, QComboBox, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon

class PipelineControls(QWidget):
    """Widget for controlling the data processing pipeline."""
    
    # Custom signals
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the pipeline controls widget."""
        super().__init__(parent)
        
        # Internal state
        self.running = False
        self.paused = False
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Start/Stop button
        self.start_stop_btn = QPushButton("Start")
        self.start_stop_btn.setMinimumWidth(80)
        layout.addWidget(self.start_stop_btn)
        
        # Pause button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setMinimumWidth(80)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)
        
        # Add stretcher to push buttons to the left
        layout.addStretch(1)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.start_stop_btn.clicked.connect(self._on_start_stop_clicked)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
    
    @pyqtSlot()
    def _on_start_stop_clicked(self):
        """Handle start/stop button click."""
        if not self.running:
            # Start pipeline
            self.running = True
            self.start_stop_btn.setText("Stop")
            self.pause_btn.setEnabled(True)
            self.start_clicked.emit()
        else:
            # Stop pipeline
            self.running = False
            self.paused = False
            self.start_stop_btn.setText("Start")
            self.pause_btn.setText("Pause")
            self.pause_btn.setEnabled(False)
            self.stop_clicked.emit()
    
    @pyqtSlot()
    def _on_pause_clicked(self):
        """Handle pause button click."""
        if not self.paused:
            # Pause pipeline
            self.paused = True
            self.pause_btn.setText("Resume")
        else:
            # Resume pipeline
            self.paused = False
            self.pause_btn.setText("Pause")
        
        self.pause_clicked.emit()