from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLineEdit,
                             QFileDialog, QLabel, QSlider, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
import os

class RecordingControls(QWidget):
    """Widget for controlling data recording and playback."""
    
    # Custom signals
    record_started = pyqtSignal(str)  # Filename
    record_stopped = pyqtSignal()
    playback_started = pyqtSignal(str)  # Filename
    playback_stopped = pyqtSignal()
    playback_paused = pyqtSignal(bool)  # Is paused
    playback_position_changed = pyqtSignal(float)  # Position in percent
    
    def __init__(self, parent=None):
        """Initialize the recording controls widget."""
        super().__init__(parent)
        
        # Internal state
        self.recording = False
        self.playing = False
        self.paused = False
        self.current_file = ""
        
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
        
        # Record button
        self.record_btn = QPushButton("Record")
        self.record_btn.setMinimumWidth(80)
        layout.addWidget(self.record_btn)
        
        # File path
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Recording file path...")
        layout.addWidget(self.file_path)
        
        # Browse button
        self.browse_btn = QPushButton("...")
        self.browse_btn.setMaximumWidth(30)
        layout.addWidget(self.browse_btn)
        
        # Separator
        layout.addWidget(QLabel("|"))
        
        # Playback controls
        self.play_btn = QPushButton("Play")
        self.play_btn.setMinimumWidth(80)
        layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumWidth(80)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setMinimum(0)
        self.position_slider.setMaximum(100)
        self.position_slider.setValue(0)
        self.position_slider.setEnabled(False)
        layout.addWidget(self.position_slider)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.record_btn.clicked.connect(self._on_record_clicked)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        self.play_btn.clicked.connect(self._on_play_clicked)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.position_slider.sliderMoved.connect(self._on_slider_moved)
    
    @pyqtSlot()
    def _on_record_clicked(self):
        """Handle record button click."""
        if not self.recording:
            # Check if file path is set
            file_path = self.file_path.text()
            if not file_path:
                # TODO: Show error message
                return
            
            # Start recording
            self.recording = True
            self.record_btn.setText("Stop Recording")
            self.current_file = file_path
            self.record_started.emit(file_path)
        else:
            # Stop recording
            self.recording = False
            self.record_btn.setText("Record")
            self.record_stopped.emit()
    
    @pyqtSlot()
    def _on_browse_clicked(self):
        """Handle browse button click."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Recording File",
            os.path.expanduser("~"),
            "Binary Files (*.bin);;All Files (*)"
        )
        
        if file_path:
            # Ensure it has .bin extension
            if not file_path.lower().endswith(".bin"):
                file_path += ".bin"
            
            self.file_path.setText(file_path)
    
    @pyqtSlot()
    def _on_play_clicked(self):
        """Handle play button click."""
        if not self.playing:
            # Check if file path is set
            file_path = self.file_path.text()
            if not file_path or not os.path.exists(file_path):
                # TODO: Show error message
                return
            
            # Start playback
            self.playing = True
            self.play_btn.setText("Pause")
            self.stop_btn.setEnabled(True)
            self.position_slider.setEnabled(True)
            self.current_file = file_path
            self.playback_started.emit(file_path)
        else:
            # If already playing, toggle pause
            self.paused = not self.paused
            if self.paused:
                self.play_btn.setText("Resume")
            else:
                self.play_btn.setText("Pause")
            
            self.playback_paused.emit(self.paused)
    
    @pyqtSlot()
    def _on_stop_clicked(self):
        """Handle stop button click."""
        if self.playing:
            # Stop playback
            self.playing = False
            self.paused = False
            self.play_btn.setText("Play")
            self.stop_btn.setEnabled(False)
            self.position_slider.setEnabled(False)
            self.position_slider.setValue(0)
            self.playback_stopped.emit()
    
    @pyqtSlot(int)
    def _on_slider_moved(self, position):
        """Handle position slider movement."""
        if self.playing:
            # Convert to percentage
            percent = position / 100.0
            self.playback_position_changed.emit(percent)
    
    def update_playback_position(self, position_percent):
        """Update the playback position slider from external source."""
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(int(position_percent * 100))